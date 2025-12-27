use ratatui::{prelude::*, Frame};
use crossterm::event::{self, Event, KeyCode, KeyEvent};
use tokio::sync::mpsc;
use std::time::Duration;
use crate::screens::{Screen, ScreenResult, ScreenAsAny};
use crate::screens::menu::MenuScreen;
use crate::screens::install::InstallScreen;
use crate::utils::{state::InstallState, system::SystemInfo};
use crate::installers::{DependencyInstaller, PanelInstaller, WingsInstaller};
use crate::error::Result;

pub enum AppEvent {
    Key(KeyEvent),
    Tick,
    Progress(u16, String),
    InstallComplete(anyhow::Result<()>),
    RetryInstallation,
}

pub struct App {
    state: InstallState,
    screen_stack: Vec<Box<dyn Screen>>,
    event_rx: mpsc::UnboundedReceiver<AppEvent>,
    event_tx: mpsc::UnboundedSender<AppEvent>,
    installing: bool,
    installer_task: Option<tokio::task::JoinHandle<()>>,
}

impl App {
    pub fn new() -> Result<Self> {
        let system_info = SystemInfo::detect()?;
        let mut state = InstallState::default();
        state.os_name = system_info.os_name;
        state.os_version = system_info.os_version;
        state.panel_installed = system_info.panel_installed;
        state.wings_installed = system_info.wings_installed;
        
        let (event_tx, event_rx) = mpsc::unbounded_channel();
        
        Ok(Self {
            state,
            screen_stack: vec![Box::new(MenuScreen::new(
                system_info.panel_installed,
                system_info.wings_installed,
            ))],
            event_rx,
            event_tx,
            installing: false,
            installer_task: None,
        })
    }
    
    pub async fn run(&mut self, terminal: &mut Terminal<ratatui::backend::CrosstermBackend<std::io::Stdout>>) -> Result<()> {
        let tick_rate = Duration::from_millis(250);
        let mut last_tick = std::time::Instant::now();
        
        loop {
            // Draw
            terminal.draw(|f| {
                if let Some(screen) = self.screen_stack.last_mut() {
                    let size = f.size();
                    let _ = screen.render(size, f, &self.state);
                }
            })?;
            
            // Handle events
            let timeout = tick_rate.saturating_sub(last_tick.elapsed());
            
            tokio::select! {
                // Event from channel
                Some(event) = self.event_rx.recv() => {
                    match event {
                        AppEvent::Key(key) => {
                            if let Some(screen) = self.screen_stack.last_mut() {
                                match screen.handle_key(key, &mut self.state)? {
                                    ScreenResult::Next(new_screen) => {
                                        new_screen.on_mount(&mut self.state)?;
                                        self.screen_stack.push(new_screen);
                                        
                                        // Check if new screen is InstallScreen and start installation
                                        if let Some(screen) = new_screen.as_any().downcast_ref::<InstallScreen>() {
                                            if screen.is_installation_started() {
                                                self.start_installation();
                                            }
                                        }
                                    }
                                    ScreenResult::Back => {
                                        self.screen_stack.pop();
                                    }
                                    ScreenResult::Exit => {
                                        self.cleanup_installation();
                                        return Ok(());
                                    }
                                    ScreenResult::None => {}
                                }
                            }
                        }
                        AppEvent::Progress(percentage, message) => {
                            self.state.progress = percentage;
                            self.state.progress_message = message.clone();
                            
                            // Update install screen
                            if let Some(screen) = self.screen_stack.last_mut() {
                                if let Some(install_screen) = screen.as_any().downcast_ref::<InstallScreen>() {
                                    install_screen.update_progress(percentage, message);
                                }
                            }
                        }
                        AppEvent::InstallComplete(result) => {
                            self.installing = false;
                            self.installer_task = None;
                            
                            match result {
                                Ok(_) => {
                                    self.state.installation_complete = true;
                                    self.state.clear_error();
                                    
                                    // Update install screen
                                    if let Some(screen) = self.screen_stack.last_mut() {
                                        if let Some(install_screen) = screen.as_any().downcast_mut::<InstallScreen>() {
                                            install_screen.set_complete();
                                        }
                                    }
                                }
                                Err(e) => {
                                    self.state.set_error(e.to_string());
                                    
                                    // Update install screen with error
                                    if let Some(screen) = self.screen_stack.last_mut() {
                                        if let Some(install_screen) = screen.as_any().downcast_mut::<InstallScreen>() {
                                            install_screen.set_error(&self.state.installation_error.as_ref().unwrap());
                                        }
                                    }
                                }
                            }
                        }
                        AppEvent::RetryInstallation => {
                            self.state.reset_installation();
                            self.start_installation();
                        }
                        _ => {}
                    }
                }
                
                // Tick event
                _ = tokio::time::sleep(timeout) => {
                    let _ = self.event_tx.send(AppEvent::Tick);
                    last_tick = std::time::Instant::now();
                }
            }
            
            // Poll for keyboard events
            if event::poll(Duration::from_millis(10))? {
                if let Event::Key(key) = event::read()? {
                    let _ = self.event_tx.send(AppEvent::Key(key));
                }
            }
        }
    }
    
    fn start_installation(&mut self) {
        self.installing = true;
        self.state.clear_error();
        self.state.reset_installation();
        
        let event_tx = self.event_tx.clone();
        let state = self.state.clone();
        
        let task = tokio::spawn(async move {
            let result = Self::run_installation_internal(state, event_tx.clone()).await;
            let _ = event_tx.send(AppEvent::InstallComplete(result));
        });
        
        self.installer_task = Some(task);
    }
    
    fn cleanup_installation(&mut self) {
        if let Some(task) = self.installer_task.take() {
            task.abort();
        }
        self.installing = false;
    }
    
    async fn run_installation_internal(state: InstallState, event_tx: mpsc::UnboundedSender<AppEvent>) -> anyhow::Result<()> {
        // Progress callback
        let progress_callback = |percentage: u16, message: String| {
            let _ = event_tx.send(AppEvent::Progress(percentage, message));
        };
        
        // Phase 1: Install dependencies
        progress_callback(5, "Installing Dependencies".to_string());
        let mut dep_installer = DependencyInstaller::new(progress_callback);
        dep_installer.install(&state).await?;
        
        // Phase 2: Install Panel or Wings
        match state.component {
            Some(crate::utils::state::ComponentType::Panel) => {
                progress_callback(50, "Installing Panel".to_string());
                let mut panel_installer = PanelInstaller::new(progress_callback);
                panel_installer.install(&state).await?;
            }
            Some(crate::utils::state::ComponentType::Wings) => {
                progress_callback(50, "Installing Wings".to_string());
                let mut wings_installer = WingsInstaller::new(progress_callback);
                wings_installer.install(&state).await?;
            }
            None => {
                return Err(anyhow::anyhow!("No component selected"));
            }
        }
        
        progress_callback(100, "Installation Complete".to_string());
        Ok(())
    }
}

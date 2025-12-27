use crate::screens::{Screen, ScreenResult};
use crate::ui::components::ProgressWidget;
use crate::utils::state::{InstallState, ComponentType};
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;
use crossterm::event::KeyEvent;

pub struct InstallScreen {
    progress: ProgressWidget,
    logs: Vec<String>,
    installation_started: bool,
    installation_complete: bool,
    show_retry: bool,
}

impl InstallScreen {
    pub fn new() -> Self {
        Self {
            progress: ProgressWidget::new("Installation Progress"),
            logs: Vec::new(),
            installation_started: false,
            installation_complete: false,
            show_retry: false,
        }
    }
    
    pub fn update_progress(&mut self, percentage: u16, message: String) {
        self.progress.set_progress(percentage);
        self.progress.set_label(message.clone());
        self.logs.push(message);
        
        // Keep only last 20 log entries
        if self.logs.len() > 20 {
            self.logs.drain(0..self.logs.len() - 20);
        }
    }
    
    pub fn set_complete(&mut self) {
        self.installation_complete = true;
        self.progress.set_label("Installation complete!".to_string());
    }
    
    pub fn set_error(&mut self, error: &str) {
        self.installation_complete = true;
        self.show_retry = true;
        self.progress.set_label(format!("Installation failed: {}", error));
    }
    
    pub fn start_installation(&mut self) {
        self.installation_started = true;
        self.logs.push("Initializing installation...".to_string());
    }
    
    pub fn is_installation_started(&self) -> bool {
        self.installation_started
    }
    
    pub fn should_show_retry(&self) -> bool {
        self.show_retry
    }
    
    pub fn reset_for_retry(&mut self) {
        self.progress.set_progress(0);
        self.progress.set_label("Installation Progress".to_string());
        self.logs.clear();
        self.installation_started = false;
        self.installation_complete = false;
        self.show_retry = false;
    }
}

impl Screen for InstallScreen {
    fn on_mount(&mut self, _state: &mut InstallState) -> crate::error::Result<()> {
        self.start_installation();
        Ok(())
    }
    
    fn render(&mut self, area: Rect, frame: &mut Frame, state: &InstallState) -> crate::error::Result<()> {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .margin(1)
            .constraints([
                Constraint::Length(3),  // Title
                Constraint::Length(5),  // Progress bar
                Constraint::Min(10),   // Logs
                Constraint::Length(2),  // Hint
                Constraint::Length(3),  // Footer
            ])
            .split(area);
        
        // Title
        let component_name = match state.component {
            Some(ComponentType::Panel) => "Panel",
            Some(ComponentType::Wings) => "Wings",
            None => "Component",
        };
        let title = Paragraph::new(format!("Installing {}", component_name))
            .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center);
        frame.render_widget(title, chunks[0]);
        
        // Progress bar
        self.progress.render(chunks[1], frame.buffer_mut());
        
        // Error message if present
        if let Some(error) = &state.installation_error {
            let error_para = Paragraph::new(format!("ERROR: {}", error))
                .style(Style::default().fg(Color::Red))
                .alignment(Alignment::Center)
                .wrap(ratatui::widgets::Wrap { trim: true });
            frame.render_widget(error_para, chunks[2]);
        } else {
            // Logs
            let log_text = if self.logs.is_empty() {
                "Initializing...".to_string()
            } else {
                self.logs.join("\n")
            };
            
            let logs_para = Paragraph::new(log_text)
                .style(Style::default().fg(Color::Gray))
                .alignment(Alignment::Center)
                .wrap(ratatui::widgets::Wrap { trim: true });
            frame.render_widget(logs_para, chunks[2]);
        }
        
        // Hint
        let hint_text = if self.show_retry {
            "Retry: r | Close: c"
        } else if self.installation_complete {
            "Press n to continue"
        } else {
            "Installation in progress..."
        };
        let hint = Paragraph::new(hint_text)
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Center);
        frame.render_widget(hint, chunks[3]);
        
        // Footer
        let footer_text = if self.show_retry {
            "Retry (r) | Close (c)"
        } else if self.installation_complete {
            "Next (n) | Close (c)"
        } else {
            "Close (c)"
        };
        let footer = Paragraph::new(footer_text)
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Center);
        frame.render_widget(footer, chunks[4]);
        
        Ok(())
    }
    
    fn handle_key(&mut self, key: KeyEvent, _state: &mut InstallState) -> crate::error::Result<ScreenResult> {
        use crossterm::event::KeyCode;
        
        match key.code {
            KeyCode::Char('n') if self.installation_complete && !self.show_retry => {
                return Ok(ScreenResult::Next(Box::new(super::summary::SummaryScreen::new())));
            }
            KeyCode::Char('r') if self.show_retry => {
                self.reset_for_retry();
                // Signal to retry installation
                return Ok(ScreenResult::Next(Box::new(super::install::InstallScreen::new())));
            }
            KeyCode::Char('c') => return Ok(ScreenResult::Exit),
            _ => {}
        }
        Ok(ScreenResult::None)
    }
}

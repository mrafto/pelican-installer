use crate::screens::{Screen, ScreenResult};
use crate::ui::components::SelectMenu;
use crate::utils::state::{InstallState, ComponentType};
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;
use crossterm::event::KeyEvent;

pub struct MenuScreen {
    menu: SelectMenu,
}

impl MenuScreen {
    pub fn new(panel_installed: bool, wings_installed: bool) -> Self {
        let mut items = Vec::new();
        
        if !panel_installed {
            items.push("1) Install Panel".to_string());
        } else {
            items.push("1) Update/Reinstall Panel".to_string());
            items.push("2) Uninstall Panel".to_string());
        }
        
        if !wings_installed {
            items.push(format!("{}) Install Wings", items.len() + 1));
        } else {
            items.push(format!("{}) Update/Reinstall Wings", items.len() + 1));
            items.push(format!("{}) Uninstall Wings", items.len() + 1));
        }
        
        Self { menu: SelectMenu::new(items) }
    }
}

impl Screen for MenuScreen {
    fn render(&mut self, area: Rect, frame: &mut Frame, state: &InstallState) -> crate::error::Result<()> {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .margin(1)
            .constraints([
                Constraint::Length(3),  // Title
                Constraint::Length(2),  // System info
                Constraint::Min(10),   // Menu
                Constraint::Length(2),  // Hint
                Constraint::Length(3),  // Footer
            ])
            .split(area);
        
        // Title
        let title = Paragraph::new("Pelican Panel Installer")
            .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center);
        frame.render_widget(title, chunks[0]);
        
        // System info
        let sys_info = format!("OS: {} {}", state.os_name, state.os_version);
        let info_para = Paragraph::new(sys_info)
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(info_para, chunks[1]);
        
        // Menu
        self.menu.render(chunks[2], frame.buffer_mut());
        
        // Hint
        let hint = Paragraph::new("Use ↑↓, 1-9, Enter to select | Close: c")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(hint, chunks[3]);
        
        // Footer
        let footer = Paragraph::new("Press c to close")
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Center);
        frame.render_widget(footer, chunks[4]);
        
        Ok(())
    }
    
    fn handle_key(&mut self, key: KeyEvent, state: &mut InstallState) -> crate::error::Result<ScreenResult> {
        use crossterm::event::{KeyCode, KeyModifiers};
        
        match key.code {
            KeyCode::Up | KeyCode::Char('k') => {
                self.menu.previous();
            }
            KeyCode::Down | KeyCode::Char('j') => {
                self.menu.next();
            }
            KeyCode::Enter => {
                let selected = self.menu.selected_text().ok_or_else(|| {
                    crate::error::InstallerError::InvalidInput("No item selected".to_string())
                })?;
                
                if selected.contains("install panel") && !selected.contains("uninstall") {
                    state.component = Some(ComponentType::Panel);
                    return Ok(ScreenResult::Next(Box::new(super::webserver::WebserverScreen::new())));
                } else if selected.contains("install wings") && !selected.contains("uninstall") {
                    state.component = Some(ComponentType::Wings);
                    return Ok(ScreenResult::Next(Box::new(super::install::InstallScreen::new())));
                } else if selected.contains("update") || selected.contains("reinstall") {
                    if selected.contains("panel") {
                        state.component = Some(ComponentType::Panel);
                        return Ok(ScreenResult::Next(Box::new(super::webserver::WebserverScreen::new())));
                    } else if selected.contains("wings") {
                        state.component = Some(ComponentType::Wings);
                        return Ok(ScreenResult::Next(Box::new(super::install::InstallScreen::new())));
                    }
                } else if selected.contains("uninstall") {
                    // TODO: Implement uninstall
                    return Ok(ScreenResult::Back);
                }
            }
            KeyCode::Char('c') => {
                return Ok(ScreenResult::Exit);
            }
            KeyCode::Char(c) if c.is_ascii_digit() => {
                let idx = c.to_digit(10).unwrap() as usize;
                if idx > 0 && idx <= self.menu.selected_index() + 1 {
                    self.menu.select_by_index(idx - 1);
                }
            }
            _ => {}
        }
        Ok(ScreenResult::None)
    }
}

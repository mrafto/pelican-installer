use crate::screens::{Screen, ScreenResult};
use crate::ui::components::SelectMenu;
use crate::utils::state::{InstallState, WebserverType};
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;
use crossterm::event::KeyEvent;

pub struct WebserverScreen {
    menu: SelectMenu,
}

impl WebserverScreen {
    pub fn new() -> Self {
        let items = vec![
            "1) Nginx (recommended)".to_string(),
            "2) Apache".to_string(),
            "3) Caddy".to_string(),
        ];
        Self { menu: SelectMenu::new(items) }
    }
}

impl Screen for WebserverScreen {
    fn render(&mut self, area: Rect, frame: &mut Frame, _state: &InstallState) -> crate::error::Result<()> {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .margin(1)
            .constraints([
                Constraint::Length(3),  // Title
                Constraint::Length(2),  // Subtitle
                Constraint::Min(10),   // Menu
                Constraint::Length(2),  // Hint
                Constraint::Length(3),  // Footer
            ])
            .split(area);
        
        // Title
        let title = Paragraph::new("Webserver Configuration")
            .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center);
        frame.render_widget(title, chunks[0]);
        
        // Subtitle
        let subtitle = Paragraph::new("Select your preferred webserver:")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(subtitle, chunks[1]);
        
        // Menu
        self.menu.render(chunks[2], frame.buffer_mut());
        
        // Hint
        let hint = Paragraph::new("Use ↑↓, 1-3, Enter to select")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(hint, chunks[3]);
        
        // Footer
        let footer = Paragraph::new("Back: b | Close: c")
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Center);
        frame.render_widget(footer, chunks[4]);
        
        Ok(())
    }
    
    fn handle_key(&mut self, key: KeyEvent, state: &mut InstallState) -> crate::error::Result<ScreenResult> {
        use crossterm::event::KeyCode;
        
        match key.code {
            KeyCode::Up | KeyCode::Char('k') => self.menu.previous(),
            KeyCode::Down | KeyCode::Char('j') => self.menu.next(),
            KeyCode::Enter => {
                match self.menu.selected_index() {
                    0 => state.webserver = WebserverType::Nginx,
                    1 => state.webserver = WebserverType::Apache,
                    2 => state.webserver = WebserverType::Caddy,
                    _ => {}
                }
                return Ok(ScreenResult::Next(Box::new(super::protocol::ProtocolScreen::new())));
            }
            KeyCode::Char('b') => return Ok(ScreenResult::Back),
            KeyCode::Char('c') => return Ok(ScreenResult::Exit),
            KeyCode::Char(c) if c.is_ascii_digit() => {
                let idx = c.to_digit(10).unwrap() as usize;
                if idx > 0 && idx <= 3 {
                    self.menu.select_by_index(idx - 1);
                }
            }
            _ => {}
        }
        Ok(ScreenResult::None)
    }
}

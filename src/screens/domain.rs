use crate::screens::{Screen, ScreenResult};
use crate::ui::components::TextInput;
use crate::utils::state::{InstallState, ProtocolType};
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;
use crossterm::event::KeyEvent;

pub struct DomainScreen {
    input: TextInput,
    can_proceed: bool,
}

impl DomainScreen {
    pub fn new() -> Self {
        Self {
            input: TextInput::new("panel.example.com"),
            can_proceed: false,
        }
    }
}

impl Screen for DomainScreen {
    fn on_mount(&mut self, _state: &mut InstallState) -> crate::error::Result<()> {
        self.input.set_focused(true);
        Ok(())
    }
    
    fn render(&mut self, area: Rect, frame: &mut Frame, state: &InstallState) -> crate::error::Result<()> {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .margin(1)
            .constraints([
                Constraint::Length(3),  // Title
                Constraint::Length(2),  // Subtitle
                Constraint::Length(5),  // Input
                Constraint::Length(2),  // Example
                Constraint::Length(2),  // Hint
                Constraint::Length(3),  // Footer
            ])
            .split(area);
        
        // Title
        let title = Paragraph::new("Domain Configuration")
            .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center);
        frame.render_widget(title, chunks[0]);
        
        // Subtitle
        let protocol_text = state.protocol.title();
        let subtitle = Paragraph::new(format!("Enter your domain or IP address ({}):", protocol_text))
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(subtitle, chunks[1]);
        
        // Input
        self.input.render(chunks[2], frame.buffer_mut());
        
        // Example
        let example = Paragraph::new("Example: panel.example.com or 192.168.1.100")
            .style(Style::default().fg(Color::DarkGray))
            .alignment(Alignment::Center);
        frame.render_widget(example, chunks[3]);
        
        // Hint
        let hint = Paragraph::new("Type domain/IP and press Next (n)")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(hint, chunks[4]);
        
        // Footer
        let footer = Paragraph::new("Back: b | Next: n | Close: c")
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Center);
        frame.render_widget(footer, chunks[5]);
        
        Ok(())
    }
    
    fn handle_key(&mut self, key: KeyEvent, state: &mut InstallState) -> crate::error::Result<ScreenResult> {
        use crossterm::event::KeyCode;
        
        match key.code {
            KeyCode::Char(c) => {
                self.input.handle_char(c);
                self.validate();
            }
            KeyCode::Backspace => {
                self.input.backspace();
                self.validate();
            }
            KeyCode::Delete => {
                self.input.delete();
                self.validate();
            }
            KeyCode::Left => self.input.move_left(),
            KeyCode::Right => self.input.move_right(),
            KeyCode::Home => self.input.move_home(),
            KeyCode::End => self.input.move_end(),
            KeyCode::Enter | KeyCode::Char('n') => {
                if self.can_proceed {
                    state.domain = self.input.value().to_string();
                    if state.protocol == ProtocolType::Https {
                        return Ok(ScreenResult::Next(Box::new(super::ssl::SSLScreen::new())));
                    } else {
                        return Ok(ScreenResult::Next(Box::new(super::install::InstallScreen::new())));
                    }
                }
            }
            KeyCode::Char('b') => return Ok(ScreenResult::Back),
            KeyCode::Char('c') => return Ok(ScreenResult::Exit),
            _ => {}
        }
        Ok(ScreenResult::None)
    }
}

impl DomainScreen {
    fn validate(&mut self) {
        let value = self.input.value().trim();
        self.can_proceed = !value.is_empty() && !value.contains(' ');
    }
}

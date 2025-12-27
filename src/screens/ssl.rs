use crate::screens::{Screen, ScreenResult};
use crate::ui::components::TextInput;
use crate::utils::state::InstallState;
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;
use crossterm::event::KeyEvent;

pub struct SSLScreen {
    input: TextInput,
    can_proceed: bool,
}

impl SSLScreen {
    pub fn new() -> Self {
        Self {
            input: TextInput::new("admin@example.com"),
            can_proceed: false,
        }
    }
}

impl Screen for SSLScreen {
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
                Constraint::Length(2),  // Domain info
                Constraint::Length(5),  // Input
                Constraint::Length(2),  // Hint
                Constraint::Length(3),  // Footer
            ])
            .split(area);
        
        // Title
        let title = Paragraph::new("SSL Certificate Setup")
            .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center);
        frame.render_widget(title, chunks[0]);
        
        // Subtitle
        let subtitle = Paragraph::new("Let's Encrypt will generate free SSL certificates")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(subtitle, chunks[1]);
        
        // Domain info
        let domain_info = Paragraph::new(format!("Domain: {}", state.domain))
            .style(Style::default().fg(Color::Cyan))
            .alignment(Alignment::Center);
        frame.render_widget(domain_info, chunks[2]);
        
        // Input label
        let input_label = Paragraph::new("Email for certificate notifications:")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(input_label, Rect {
            x: chunks[3].x,
            y: chunks[3].y,
            width: chunks[3].width,
            height: 1,
        });
        
        // Input
        self.input.render(Rect {
            x: chunks[3].x,
            y: chunks[3].y + 1,
            width: chunks[3].width,
            height: 3,
        }, frame.buffer_mut());
        
        // Hint
        let hint = Paragraph::new("Enter email and press Next (n)")
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
                    state.ssl_email = self.input.value().to_string();
                    return Ok(ScreenResult::Next(Box::new(super::install::InstallScreen::new())));
                }
            }
            KeyCode::Char('b') => return Ok(ScreenResult::Back),
            KeyCode::Char('c') => return Ok(ScreenResult::Exit),
            _ => {}
        }
        Ok(ScreenResult::None)
    }
}

impl SSLScreen {
    fn validate(&mut self) {
        let value = self.input.value().trim();
        self.can_proceed = value.contains('@') && value.contains('.');
    }
}

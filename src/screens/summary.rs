use crate::screens::{Screen, ScreenResult};
use crate::utils::state::{InstallState, ComponentType};
use ratatui::prelude::*;
use ratatui::widgets::Paragraph;
use crossterm::event::KeyEvent;

pub struct SummaryScreen;

impl SummaryScreen {
    pub fn new() -> Self {
        Self
    }
}

impl Screen for SummaryScreen {
    fn render(&mut self, area: Rect, frame: &mut Frame, state: &InstallState) -> crate::error::Result<()> {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .margin(1)
            .constraints([
                Constraint::Length(3),  // Title
                Constraint::Min(15),   // Summary
                Constraint::Length(2),  // Next steps
                Constraint::Length(2),  // Hint
                Constraint::Length(3),  // Footer
            ])
            .split(area);
        
        // Title
        let title = Paragraph::new("Installation Complete! ✓")
            .style(Style::default().fg(Color::Green).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center);
        frame.render_widget(title, chunks[0]);
        
        // Summary content
        let component_name = match state.component {
            Some(ComponentType::Panel) => "Panel",
            Some(ComponentType::Wings) => "Wings",
            None => "Component",
        };
        
        let mut summary_lines = vec![
            "INSTALLATION SUMMARY".to_string(),
            "".to_string(),
            format!("✓ Component: {}", component_name),
        ];
        
        if state.component == Some(ComponentType::Panel) {
            summary_lines.push(format!("✓ Webserver: {}", state.webserver.title()));
            summary_lines.push(format!("✓ Protocol: {}", state.protocol.title()));
            summary_lines.push(format!("✓ Domain: {}", state.domain));
            
            if state.use_ssl {
                summary_lines.push(format!("✓ SSL Certificate: {}", state.domain));
            }
        }
        
        summary_lines.extend_from_slice(&[
            "".to_string(),
            "✓ Dependencies installed".to_string(),
            format!("✓ {} configured", component_name),
        ]);
        
        let summary_text = summary_lines.join("\n");
        let summary_para = Paragraph::new(summary_text)
            .style(Style::default().fg(Color::White))
            .alignment(Alignment::Left);
        frame.render_widget(summary_para, chunks[1]);
        
        // Next steps
        let next_steps = if state.component == Some(ComponentType::Panel) {
            format!("Access Panel: {}://{}/installer", state.protocol.as_str(), state.domain)
        } else {
            "Configure Wings through Panel dashboard".to_string()
        };
        let steps_para = Paragraph::new(next_steps)
            .style(Style::default().fg(Color::Cyan))
            .alignment(Alignment::Center);
        frame.render_widget(steps_para, chunks[2]);
        
        // Hint
        let hint = Paragraph::new("Installation complete! Press Exit to close.")
            .style(Style::default().fg(Color::Gray))
            .alignment(Alignment::Center);
        frame.render_widget(hint, chunks[3]);
        
        // Footer
        let footer = Paragraph::new("Exit (c)")
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Center);
        frame.render_widget(footer, chunks[4]);
        
        Ok(())
    }
    
    fn handle_key(&mut self, key: KeyEvent, _state: &mut InstallState) -> crate::error::Result<ScreenResult> {
        use crossterm::event::KeyCode;
        
        match key.code {
            KeyCode::Char('c') | KeyCode::Enter => {
                return Ok(ScreenResult::Exit);
            }
            _ => {}
        }
        Ok(ScreenResult::None)
    }
}

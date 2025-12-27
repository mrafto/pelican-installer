use ratatui::{
    prelude::*,
    widgets::{Block, Borders, Gauge, Paragraph, Wrap},
};
use unicode_width::UnicodeWidthStr;

/// Selectable menu widget
pub struct SelectMenu {
    items: Vec<String>,
    selected: usize,
}

impl SelectMenu {
    pub fn new(items: Vec<String>) -> Self {
        Self { items, selected: 0 }
    }
    
    pub fn next(&mut self) {
        if !self.items.is_empty() {
            self.selected = (self.selected + 1) % self.items.len();
        }
    }
    
    pub fn previous(&mut self) {
        if !self.items.is_empty() {
            self.selected = self.selected.saturating_sub(1);
            if self.selected >= self.items.len() {
                self.selected = self.items.len() - 1;
            }
        }
    }
    
    pub fn select_by_index(&mut self, index: usize) -> bool {
        if index < self.items.len() {
            self.selected = index;
            true
        } else {
            false
        }
    }
    
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let block = Block::default().borders(Borders::ALL);
        let inner = block.inner(area);
        block.render(area, buf);
        
        for (i, item) in self.items.iter().enumerate() {
            if i as u16 >= inner.height {
                break;
            }
            
            let y = inner.y + i as u16;
            let style = if i == self.selected {
                Style::default()
                    .fg(Color::Cyan)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default()
            };
            
            let line = Span::styled(item.clone(), style);
            buf.set_span(inner.x, y, &line, inner.width);
        }
    }
    
    pub fn selected_index(&self) -> usize {
        self.selected
    }
    
    pub fn selected_text(&self) -> Option<&str> {
        self.items.get(self.selected).map(|s| s.as_str())
    }
}

/// Text input widget
pub struct TextInput {
    value: String,
    placeholder: String,
    focused: bool,
    cursor_pos: usize,
}

impl TextInput {
    pub fn new(placeholder: &str) -> Self {
        Self {
            value: String::new(),
            placeholder: placeholder.to_string(),
            focused: false,
            cursor_pos: 0,
        }
    }
    
    pub fn value(&self) -> &str {
        &self.value
    }
    
    pub fn set_value(&mut self, value: String) {
        self.value = value;
        self.cursor_pos = self.value.width();
    }
    
    pub fn set_focused(&mut self, focused: bool) {
        self.focused = focused;
    }
    
    pub fn is_focused(&self) -> bool {
        self.focused
    }
    
    pub fn handle_char(&mut self, c: char) {
        if !c.is_control() {
            let mut s = self.value.chars().collect::<Vec<_>>();
            s.insert(self.cursor_pos, c);
            self.value = s.into_iter().collect();
            self.cursor_pos += c.len_utf8();
        }
    }
    
    pub fn backspace(&mut self) {
        let mut chars = self.value.chars().collect::<Vec<_>>();
        if self.cursor_pos > 0 {
            self.cursor_pos -= 1;
            chars.remove(self.cursor_pos);
            self.value = chars.into_iter().collect();
        }
    }
    
    pub fn delete(&mut self) {
        let mut chars = self.value.chars().collect::<Vec<_>>();
        if self.cursor_pos < chars.len() {
            chars.remove(self.cursor_pos);
            self.value = chars.into_iter().collect();
        }
    }
    
    pub fn move_left(&mut self) {
        self.cursor_pos = self.cursor_pos.saturating_sub(1);
    }
    
    pub fn move_right(&mut self) {
        let value_len = self.value.chars().count();
        if self.cursor_pos < value_len {
            self.cursor_pos += 1;
        }
    }
    
    pub fn move_home(&mut self) {
        self.cursor_pos = 0;
    }
    
    pub fn move_end(&mut self) {
        self.cursor_pos = self.value.chars().count();
    }
    
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let display = if self.value.is_empty() {
            self.placeholder.as_str()
        } else {
            &self.value
        };
        
        let style = if self.focused {
            Style::default()
                .fg(Color::Cyan)
                .add_modifier(Modifier::UNDERLINED)
        } else {
            Style::default()
        };
        
        let block = Block::default().borders(Borders::ALL);
        let inner = block.inner(area);
        block.render(area, buf);
        
        let paragraph = Paragraph::new(display)
            .style(style)
            .wrap(Wrap { trim: true });
        
        paragraph.render(inner, buf);
        
        // Render cursor if focused
        if self.focused && !self.value.is_empty() {
            let cursor_offset = self.value.chars()
                .take(self.cursor_pos)
                .collect::<String>()
                .width();
            
            if let Some(cell) = buf.cell_mut(inner.x + cursor_offset as u16, inner.y) {
                cell.set_style(Style::default()
                    .fg(Color::Black)
                    .bg(Color::Cyan)
                    .add_modifier(Modifier::REVERSED));
            }
        }
    }
}

/// Progress bar widget
pub struct ProgressWidget {
    percentage: u16,
    label: String,
}

impl ProgressWidget {
    pub fn new(label: &str) -> Self {
        Self {
            percentage: 0,
            label: label.to_string(),
        }
    }
    
    pub fn set_progress(&mut self, percentage: u16) {
        self.percentage = percentage.min(100);
    }
    
    pub fn set_label(&mut self, label: String) {
        self.label = label;
    }
    
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let gauge = Gauge::default()
            .block(Block::default().title(&self.label).borders(Borders::ALL))
            .gauge_style(Style::default().fg(Color::Cyan))
            .percent(self.percentage);
        
        gauge.render(area, buf);
    }
}

use ratatui::{prelude::*, Frame};
use crossterm::event::KeyEvent;
use crate::error::Result;
use crate::utils::state::InstallState;

pub enum ScreenResult {
    None,
    Next(Box<dyn Screen>),
    Back,
    Exit,
}

pub trait Screen: Send + ScreenAsAny {
    fn render(&mut self, area: Rect, frame: &mut Frame, state: &InstallState) -> Result<()>;
    fn handle_key(&mut self, key: KeyEvent, state: &mut InstallState) -> Result<ScreenResult>;
    fn on_mount(&mut self, _state: &mut InstallState) -> Result<()> {
        Ok(())
    }
}

pub trait ScreenAsAny: Send {
    fn as_any(&self) -> &dyn std::any::Any;
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any;
}

// Implement ScreenAsAny for all Screen types
impl<T: Screen + 'static> ScreenAsAny for T {
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

pub mod menu;
pub mod webserver;
pub mod protocol;
pub mod domain;
pub mod ssl;
pub mod install;
pub mod summary;

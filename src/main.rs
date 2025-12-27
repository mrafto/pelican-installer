mod app;
mod screens;
mod installers;
mod ui;
mod utils;
mod error;

use app::App;
use crossterm::{
    event::DisableMouseCapture,
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use std::io;

fn check_root() -> bool {
    #[cfg(unix)]
    {
        use nix::unistd::Uid;
        return Uid::effective().is_root();
    }
    #[cfg(not(unix))]
    {
        // On Windows, just return true (installer is for Linux anyway)
        return true;
    }
}

fn main() -> anyhow::Result<()> {
    // Check sudo/root
    if !check_root() {
        eprintln!("⚠️  This installer requires root privileges.");
        eprintln!("   Please run with sudo:");
        eprintln!("   sudo {}", std::env::args().next().unwrap());
        std::process::exit(1);
    }
    
    // Initialize logger
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();
    
    // Setup terminal
    enable_raw_mode()?;
    execute!(
        io::stdout(),
        EnterAlternateScreen,
        DisableMouseCapture
    )?;
    
    let mut terminal = ratatui::Terminal::new(ratatui::backend::CrosstermBackend::new(io::stdout()))?;
    
    // Run application
    let result = tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(async {
            let mut app = App::new()?;
            app.run(&mut terminal).await?;
            Ok::<(), anyhow::Error>(())
        });
    
    // Restore terminal
    disable_raw_mode()?;
    execute!(
        io::stdout(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    
    result
}

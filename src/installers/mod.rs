use std::process::{Command, Stdio};
use std::fs::OpenOptions;
use std::io::Write;
use tokio::io::{AsyncBufReadExt, BufReader};
use crate::error::{Result, InstallerError};

pub struct CommandExecutor<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    pub progress_callback: F,
    log_file: Option<std::fs::File>,
}

impl<F> CommandExecutor<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    pub fn new(progress_callback: F) -> Self {
        // Open log file
        let log_file = OpenOptions::new()
            .create(true)
            .append(true)
            .open("/var/log/pelican-installer.log")
            .ok();
        
        Self {
            progress_callback,
            log_file,
        }
    }
    
    fn log(&self, message: &str) {
        if let Some(ref mut file) = self.log_file {
            let _ = writeln!(file, "[{}] {}", chrono::Local::now().format("%Y-%m-%d %H:%M:%S"), message);
            let _ = file.flush();
        }
    }
    
    pub async fn run_streaming(&self, cmd: &str) -> Result<i32> {
        self.log(&format!("Executing: {}", cmd));
        
        let mut child = Command::new("bash")
            .args(["-c", cmd])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| InstallerError::CommandFailed(format!("Failed to spawn: {}", e)))?;
        
        // Stream stdout line-by-line
        if let Some(stdout) = child.stdout.take() {
            let reader = BufReader::new(stdout);
            let mut lines = reader.lines();
            
            while let Some(line) = lines.next_line().await.map_err(|e| 
                InstallerError::Io(e)
            )? {
                // Check for progress markers: PROGRESS:<percentage>:<message>
                if line.starts_with("PROGRESS:") {
                    if let Some((progress_part, message)) = line[9..].split_once(':') {
                        if let Ok(percentage) = progress_part.parse::<u16>() {
                            self.log(&format!("Progress: {}% - {}", percentage, message));
                            (self.progress_callback)(percentage, message.to_string());
                        }
                    }
                } else if line.starts_with("ERROR:") {
                    let error_msg = line[6..].to_string();
                    self.log(&format!("Error: {}", error_msg));
                    (self.progress_callback)(0, error_msg);
                } else {
                    // Just log and pass through
                    self.log(&format!("Output: {}", line));
                }
            }
        }
        
        // Also stream stderr
        if let Some(stderr) = child.stderr.take() {
            let reader = BufReader::new(stderr);
            let mut lines = reader.lines();
            
            while let Some(line) = lines.next_line().await.map_err(|e| 
                InstallerError::Io(e)
            )? {
                self.log(&format!("Stderr: {}", line));
                if line.starts_with("ERROR:") {
                    let error_msg = line[6..].to_string();
                    (self.progress_callback)(0, error_msg);
                }
            }
        }
        
        let status = child.wait()
            .map_err(|e| InstallerError::CommandFailed(format!("Failed to wait: {}", e)))?;
        
        let exit_code = status.code().unwrap_or(-1);
        self.log(&format!("Exit code: {}", exit_code));
        Ok(exit_code)
    }
    
    pub async fn run_simple(&self, cmd: &str) -> Result<i32> {
        self.run_streaming(cmd).await
    }
}

pub mod base;
pub mod dependencies;
pub mod panel;
pub mod wings;

pub use base::*;
pub use dependencies::*;
pub use panel::*;
pub use wings::*;

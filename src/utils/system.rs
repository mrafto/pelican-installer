use std::path::Path;
use crate::error::{Result, InstallerError};

#[derive(Debug, Clone)]
pub struct SystemInfo {
    pub os_name: String,
    pub os_version: String,
    pub panel_installed: bool,
    pub wings_installed: bool,
}

impl SystemInfo {
    pub fn detect() -> Result<Self> {
        let os_name = Self::read_os_release_field("ID")?;
        let os_version = Self::read_os_release_field("VERSION_ID")?;
        let panel_installed = Path::new("/var/www/pelican").exists();
        let wings_installed = Path::new("/usr/local/bin/wings").exists();
        
        Ok(Self {
            os_name,
            os_version,
            panel_installed,
            wings_installed,
        })
    }
    
    fn read_os_release_field(field: &str) -> Result<String> {
        let content = std::fs::read_to_string("/etc/os-release")
            .map_err(|e| InstallerError::SystemDetection(format!("Failed to read /etc/os-release: {}", e)))?;
        
        for line in content.lines() {
            if let Some(value) = line.strip_prefix(&format!("{}=", field)) {
                let cleaned = value.trim_matches('"').to_string();
                if !cleaned.is_empty() {
                    return Ok(cleaned);
                }
            }
        }
        
        Ok("Unknown".to_string())
    }
    
    pub fn get_menu_title(&self) -> String {
        format!("OS: {} {}", self.os_name, self.os_version)
    }
}

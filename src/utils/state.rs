use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ComponentType {
    Panel,
    Wings,
}

impl ComponentType {
    pub fn as_str(&self) -> &str {
        match self {
            ComponentType::Panel => "panel",
            ComponentType::Wings => "wings",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum WebserverType {
    Nginx,
    Apache,
    Caddy,
}

impl WebserverType {
    pub fn as_str(&self) -> &str {
        match self {
            WebserverType::Nginx => "nginx",
            WebserverType::Apache => "apache",
            WebserverType::Caddy => "caddy",
        }
    }
    
    pub fn title(&self) -> &str {
        match self {
            WebserverType::Nginx => "Nginx",
            WebserverType::Apache => "Apache",
            WebserverType::Caddy => "Caddy",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ProtocolType {
    Http,
    Https,
}

impl ProtocolType {
    pub fn as_str(&self) -> &str {
        match self {
            ProtocolType::Http => "http",
            ProtocolType::Https => "https",
        }
    }
    
    pub fn title(&self) -> &str {
        match self {
            ProtocolType::Http => "HTTP",
            ProtocolType::Https => "HTTPS",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstallState {
    pub component: Option<ComponentType>,
    pub webserver: WebserverType,
    pub protocol: ProtocolType,
    pub domain: String,
    pub use_ssl: bool,
    pub ssl_email: String,
    pub dependencies_installed: bool,
    pub panel_installed: bool,
    pub wings_installed: bool,
    pub os_name: String,
    pub os_version: String,
    pub current_phase: String,
    pub installation_complete: bool,
    pub progress: u16,
    pub progress_message: String,
    pub installation_error: Option<String>,
    pub retry_count: u32,
}

impl Default for InstallState {
    fn default() -> Self {
        Self {
            component: None,
            webserver: WebserverType::Nginx,
            protocol: ProtocolType::Https,
            domain: String::new(),
            use_ssl: true,
            ssl_email: String::new(),
            dependencies_installed: false,
            panel_installed: false,
            wings_installed: false,
            os_name: String::new(),
            os_version: String::new(),
            current_phase: "menu".to_string(),
            installation_complete: false,
            progress: 0,
            progress_message: String::new(),
            installation_error: None,
            retry_count: 0,
        }
    }
}

impl InstallState {
    pub fn reset_installation(&mut self) {
        self.progress = 0;
        self.progress_message = String::new();
        self.installation_complete = false;
        self.installation_error = None;
        self.retry_count += 1;
    }
    
    pub fn set_error(&mut self, error: String) {
        self.installation_error = Some(error);
    }
    
    pub fn clear_error(&mut self) {
        self.installation_error = None;
    }
}

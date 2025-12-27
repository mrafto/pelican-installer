use thiserror::Error;

#[derive(Error, Debug)]
pub enum InstallerError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Command execution failed: {0}")]
    CommandFailed(String),
    
    #[error("System detection failed: {0}")]
    SystemDetection(String),
    
    #[error("Installation failed: {0}")]
    InstallationFailed(String),
    
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    
    #[error("Parsing error: {0}")]
    ParseError(String),
}

pub type Result<T> = std::result::Result<T, InstallerError>;

use super::CommandExecutor;
use crate::utils::state::InstallState;
use crate::error::Result;

pub struct WingsInstaller<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    executor: CommandExecutor<F>,
}

impl<F> WingsInstaller<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    pub fn new(progress_callback: F) -> Self {
        Self {
            executor: CommandExecutor::new(progress_callback),
        }
    }
    
    pub async fn install(&self, _state: &InstallState) -> Result<()> {
        let script_path = "./scripts/install_wings.sh";
        let cmd = script_path.to_string();
        
        let exit_code = self.executor.run_simple(&cmd).await?;
        if exit_code != 0 {
            return Err(crate::error::InstallerError::InstallationFailed(
                format!("Wings installation failed with exit code {}", exit_code)
            ));
        }
        
        Ok(())
    }
}

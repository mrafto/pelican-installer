use super::CommandExecutor;
use crate::utils::state::InstallState;
use crate::error::Result;

pub struct PanelInstaller<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    executor: CommandExecutor<F>,
}

impl<F> PanelInstaller<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    pub fn new(progress_callback: F) -> Self {
        Self {
            executor: CommandExecutor::new(progress_callback),
        }
    }
    
    pub async fn install(&self, state: &InstallState) -> Result<()> {
        let script_path = "./scripts/install_panel.sh";
        let cmd = format!(
            "{} --domain {} --protocol {} --webserver {} --ssl-email {}",
            script_path,
            state.domain,
            state.protocol.as_str(),
            state.webserver.as_str(),
            state.ssl_email
        );
        
        let exit_code = self.executor.run_simple(&cmd).await?;
        if exit_code != 0 {
            return Err(crate::error::InstallerError::InstallationFailed(
                format!("Panel installation failed with exit code {}", exit_code)
            ));
        }
        
        Ok(())
    }
}

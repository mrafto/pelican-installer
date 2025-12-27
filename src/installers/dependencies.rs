use super::CommandExecutor;
use crate::utils::state::InstallState;
use crate::error::Result;

pub struct DependencyInstaller<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    executor: CommandExecutor<F>,
}

impl<F> DependencyInstaller<F>
where
    F: Fn(u16, String) + Send + Sync,
{
    pub fn new(progress_callback: F) -> Self {
        Self {
            executor: CommandExecutor::new(progress_callback),
        }
    }
    
    pub async fn install(&mut self, state: &InstallState) -> Result<()> {
        match state.component {
            Some(crate::utils::state::ComponentType::Panel) => {
                self.install_panel_deps(state).await
            }
            Some(crate::utils::state::ComponentType::Wings) => {
                self.install_wings_deps(state).await
            }
            None => Err(crate::error::InstallerError::InvalidInput("No component selected".to_string())),
        }
    }
    
    async fn install_panel_deps(&mut self, state: &InstallState) -> Result<()> {
        let script_path = "./scripts/install_dependencies.sh";
        let cmd = format!(
            "{} --component panel --webserver {}",
            script_path,
            state.webserver.as_str()
        );
        
        let exit_code = self.executor.run_simple(&cmd).await?;
        if exit_code != 0 {
            return Err(crate::error::InstallerError::InstallationFailed(
                format!("Dependency installation failed with exit code {}", exit_code)
            ));
        }
        
        Ok(())
    }
    
    async fn install_wings_deps(&mut self, _state: &InstallState) -> Result<()> {
        let script_path = "./scripts/install_dependencies.sh";
        let cmd = format!("{} --component wings", script_path);
        
        let exit_code = self.executor.run_simple(&cmd).await?;
        if exit_code != 0 {
            return Err(crate::error::InstallerError::InstallationFailed(
                format!("Docker installation failed with exit code {}", exit_code)
            ));
        }
        
        Ok(())
    }
}

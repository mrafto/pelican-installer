"""Installation modules for Pelican Panel and Wings."""

from pelican_installer.installers.dependencies import DependencyInstaller
from pelican_installer.installers.panel import PanelInstaller
from pelican_installer.installers.wings import WingsInstaller

__all__ = ["DependencyInstaller", "PanelInstaller", "WingsInstaller"]


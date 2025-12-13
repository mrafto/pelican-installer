"""Screen modules for the installer."""

from pelican_installer.screens.domain import DomainScreen
from pelican_installer.screens.install import InstallScreen
from pelican_installer.screens.menu import MenuScreen
from pelican_installer.screens.protocol import ProtocolScreen
from pelican_installer.screens.ssl import SSLScreen
from pelican_installer.screens.summary import SummaryScreen
from pelican_installer.screens.webserver import WebserverScreen

__all__ = [
    "DomainScreen",
    "InstallScreen",
    "MenuScreen",
    "ProtocolScreen",
    "SSLScreen",
    "SummaryScreen",
    "WebserverScreen",
]

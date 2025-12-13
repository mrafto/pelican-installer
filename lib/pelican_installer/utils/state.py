"""Installation state management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ComponentType = Literal["panel", "wings"]
WebserverType = Literal["nginx", "apache", "caddy"]
ProtocolType = Literal["https", "http"]


@dataclass
class InstallState:
    """Global installation state shared across screens."""

    # Component selection
    component: ComponentType | None = None

    # Webserver configuration
    webserver: WebserverType = "nginx"
    protocol: ProtocolType = "https"

    # Domain/SSL configuration
    domain: str = ""
    use_ssl: bool = True
    ssl_email: str = ""

    # Installation status
    dependencies_installed: bool = False
    panel_installed: bool = False
    wings_installed: bool = False

    # System info (populated on startup)
    os_name: str = ""
    os_version: str = ""

    # Progress tracking
    current_phase: str = "menu"
    installation_complete: bool = False

    def reset(self) -> None:
        """Reset state to defaults."""
        self.component = None
        self.webserver = "nginx"
        self.protocol = "https"
        self.domain = ""
        self.use_ssl = True
        self.ssl_email = ""
        self.dependencies_installed = False
        self.current_phase = "menu"
        self.installation_complete = False

    def to_dict(self) -> dict:
        """Convert state to dictionary for display."""
        return {
            "Component": self.component or "None",
            "Webserver": self.webserver.capitalize() if self.component == "panel" else "N/A",
            "Protocol": self.protocol.upper() if self.component == "panel" else "N/A",
            "Domain": self.domain or "Not set",
            "SSL": "Yes" if self.use_ssl and self.protocol == "https" else "No",
        }


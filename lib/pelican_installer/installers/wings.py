"""Wings installation."""

from __future__ import annotations

import platform
from pathlib import Path

from pelican_installer.installers.base import BaseInstaller


class WingsInstaller(BaseInstaller):
    """Install Pelican Wings."""

    WINGS_BINARY = Path("/usr/local/bin/wings")
    CONFIG_DIR = Path("/etc/pelican")
    GITHUB_RELEASE_BASE = "https://github.com/pelican-dev/wings/releases/latest/download"

    def install(self) -> None:
        """Install Wings."""
        self.update_progress(10, "Creating directories...")
        self._create_directories()

        self.update_progress(30, "Downloading Wings binary...")
        self._download_wings()

        self.update_progress(60, "Setting up systemd service...")
        self._setup_systemd_service()

        self.update_progress(80, "Configuring Docker network...")
        self._configure_docker()

        self.update_progress(100, "Wings installed successfully!")

    def _create_directories(self) -> None:
        """Create required directories for Wings."""
        directories = [
            self.CONFIG_DIR,
            Path("/var/run/wings"),
            Path("/var/lib/pelican/volumes"),
            Path("/var/lib/pelican/backups"),
        ]

        for directory in directories:
            self.run_command(["mkdir", "-p", str(directory)], use_sudo=True)

    def _download_wings(self) -> None:
        """Download Wings binary for the current architecture."""
        # Detect architecture
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            arch = "amd64"
        elif machine in ["aarch64", "arm64"]:
            arch = "arm64"
        else:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        download_url = f"{self.GITHUB_RELEASE_BASE}/wings_linux_{arch}"

        # Download
        self.run_command(
            ["curl", "-L", "-o", str(self.WINGS_BINARY), download_url],
            use_sudo=True,
        )

        # Make executable
        self.run_command(["chmod", "u+x", str(self.WINGS_BINARY)], use_sudo=True)

    def _setup_systemd_service(self) -> None:
        """Create and enable Wings systemd service."""
        service_file = "/etc/systemd/system/wings.service"
        service_content = """[Unit]
Description=Wings Daemon
After=docker.service
Requires=docker.service
PartOf=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/etc/pelican
LimitNOFILE=4096
PIDFile=/var/run/wings/daemon.pid
ExecStart=/usr/local/bin/wings
Restart=on-failure
RestartSec=5s
StartLimitInterval=180
StartLimitBurst=30

[Install]
WantedBy=multi-user.target
"""

        # Write service file
        self.run_command(
            ["bash", "-c", f"cat > {service_file} << 'EOF'\n{service_content}\nEOF"],
            use_sudo=True,
            shell=False,
        )

        # Reload systemd and enable service (but don't start yet - needs config)
        self.run_command(["systemctl", "daemon-reload"], use_sudo=True)
        self.run_command(["systemctl", "enable", "wings"], use_sudo=True, check=False)

    def _configure_docker(self) -> None:
        """Configure Docker for Wings."""
        # Create Docker network for Pelican
        self.run_command(
            [
                "docker",
                "network",
                "create",
                "--driver=bridge",
                "pelican_network",
            ],
            use_sudo=True,
            check=False,  # Don't fail if network already exists
        )

        # Configure Docker daemon
        daemon_config = Path("/etc/docker/daemon.json")
        if not daemon_config.exists():
            config_content = """{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
"""
            self.run_command(
                ["bash", "-c", f"echo '{config_content}' > {daemon_config}"],
                use_sudo=True,
                shell=False,
            )

            # Restart Docker to apply config
            self.run_command(
                ["systemctl", "restart", "docker"],
                use_sudo=True,
                check=False,
            )


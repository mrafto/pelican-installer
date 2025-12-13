"""System detection and validation utilities."""

from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SystemInfo:
    """System information."""

    os_name: str
    os_version: str
    architecture: str
    panel_installed: bool
    wings_installed: bool


class SystemDetector:
    """Detect system information and installation status."""

    PANEL_PATH = Path("/var/www/pelican")
    WINGS_PATH = Path("/usr/local/bin/wings")

    @classmethod
    def detect(cls) -> SystemInfo:
        """Detect current system information."""
        return SystemInfo(
            os_name=cls._get_os_name(),
            os_version=cls._get_os_version(),
            architecture=platform.machine(),
            panel_installed=cls.is_panel_installed(),
            wings_installed=cls.is_wings_installed(),
        )

    @classmethod
    def is_panel_installed(cls) -> bool:
        """Check if Pelican Panel is installed."""
        return cls.PANEL_PATH.exists()

    @classmethod
    def is_wings_installed(cls) -> bool:
        """Check if Wings is installed."""
        return cls.WINGS_PATH.exists()

    @classmethod
    def _get_os_name(cls) -> str:
        """Get OS name."""
        try:
            # Try to read /etc/os-release
            if Path("/etc/os-release").exists():
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("NAME="):
                            return line.split("=")[1].strip().strip('"')
        except Exception:
            pass
        return platform.system()

    @classmethod
    def _get_os_version(cls) -> str:
        """Get OS version."""
        try:
            if Path("/etc/os-release").exists():
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("VERSION_ID="):
                            return line.split("=")[1].strip().strip('"')
        except Exception:
            pass
        return platform.release()

    @classmethod
    def check_command_exists(cls, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @classmethod
    def check_port_available(cls, port: int) -> bool:
        """Check if a port is available."""
        try:
            result = subprocess.run(
                ["lsof", f"-i:{port}"],
                capture_output=True,
                timeout=5,
            )
            # If lsof returns 0, port is in use
            return result.returncode != 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If lsof not found or times out, assume port is available
            return True

    @classmethod
    def has_sudo(cls) -> bool:
        """Check if user has sudo privileges."""
        return os.geteuid() == 0 or cls.check_command_exists("sudo")


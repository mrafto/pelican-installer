"""Base installer class with common utilities."""

from __future__ import annotations

import os
import subprocess
from typing import Callable


class BaseInstaller:
    """Base class for all installers."""

    def __init__(self, progress_callback: Callable[[int, str], None] | None = None):
        """
        Initialize installer.

        Args:
            progress_callback: Function to call with (progress, status_message)
        """
        self.progress_callback = progress_callback
        self._current_progress = 0

    def update_progress(self, progress: int, message: str) -> None:
        """Update installation progress."""
        self._current_progress = progress
        if self.progress_callback:
            self.progress_callback(progress, message)

    def run_command(
        self,
        cmd: list[str],
        use_sudo: bool = False,
        capture: bool = True,
        check: bool = True,
        shell: bool = False,
    ) -> subprocess.CompletedProcess:
        """
        Run a system command.

        Args:
            cmd: Command and arguments
            use_sudo: Whether to prepend sudo
            capture: Whether to capture output
            check: Whether to raise on non-zero exit
            shell: Whether to run in shell

        Returns:
            CompletedProcess object

        Raises:
            subprocess.CalledProcessError: If command fails and check=True
        """
        if use_sudo and os.geteuid() != 0:
            if isinstance(cmd, list):
                cmd = ["sudo"] + cmd
            else:
                cmd = f"sudo {cmd}"

        kwargs = {
            "check": check,
            "capture_output": capture,
            "text": True,
            "shell": shell,
        }

        return subprocess.run(cmd, **kwargs)

    def check_package_installed(self, package: str) -> bool:
        """Check if a package is installed via dpkg."""
        try:
            result = self.run_command(
                ["dpkg", "-s", package],
                capture=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            self.run_command(["which", command], capture=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False


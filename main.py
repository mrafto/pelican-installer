#!/usr/bin/env python3
"""Pelican Panel Installer - Main Entry Point."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_lib_on_path() -> None:
    repo_root = Path(__file__).resolve().parent
    lib_dir = repo_root / "lib"
    sys.path.insert(0, str(lib_dir))


def check_sudo() -> None:
    """Check if running with sudo privileges."""
    if os.geteuid() != 0:
        print("\n⚠️  WARNING: This installer requires root privileges.")
        print("   Please run with sudo:")
        print(f"   sudo python3 {sys.argv[0]}\n")
        sys.exit(1)


def main() -> None:
    # Check for sudo/root access
    check_sudo()

    _ensure_lib_on_path()
    from pelican_installer.app import PelicanInstallerApp

    PelicanInstallerApp().run()


if __name__ == "__main__":
    main()



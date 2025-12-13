#!/bin/bash

################################################################################
# Pelican Panel Installer - Quick Launch Script
# 
# Downloads and runs the Pelican Panel TUI installer
# Usage: curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh | bash
################################################################################

set -e

# Configuration
REPO_URL="https://github.com/username/pelican-installer"
INSTALL_DIR="/tmp/pelican-installer-$$"

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Error: git is required but not installed." >&2
    exit 1
fi

# Clone repository to temp directory
git clone --depth 1 -q "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
    echo "Error: Failed to download installer" >&2
    exit 1
}

cd "$INSTALL_DIR"

# Install dependencies silently
python3 -m pip install -q -r requirements.txt 2>/dev/null || {
    echo "Error: Failed to install dependencies" >&2
    rm -rf "$INSTALL_DIR"
    exit 1
}

# Launch the TUI
python3 main.py

# Cleanup
cd /
rm -rf "$INSTALL_DIR"

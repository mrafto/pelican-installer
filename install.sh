#!/bin/bash

################################################################################
# Pelican Panel Installer - Quick Launch Script
# 
# Downloads and runs the Pelican Panel TUI installer
# Usage: curl -fsSL https://raw.githubusercontent.com/mrafto/pelican-installer/main/install.sh | bash
################################################################################

# Configuration
REPO_URL="https://github.com/mrafto/pelican-installer"
INSTALL_DIR="/tmp/pelican-installer-$$"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Pelican Panel Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs sudo privileges to install system packages."
    echo "   Please run with sudo or enter your password when prompted."
    echo ""
fi

# Install system dependencies
echo "→ Installing system dependencies..."

# Check and install git
if ! command -v git &> /dev/null; then
    echo "  Installing git..."
    sudo apt-get update -qq
    sudo apt-get install -y git
    echo "  ✓ git installed"
else
    echo "  ✓ git already installed"
fi

# Check and install curl (needed by the actual installer)
if ! command -v curl &> /dev/null; then
    echo "  Installing curl..."
    sudo apt-get install -y curl
    echo "  ✓ curl installed"
else
    echo "  ✓ curl already installed"
fi

# Check and install Rust
if ! command -v cargo &> /dev/null; then
    echo "  Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    echo "  ✓ Rust installed"
else
    echo "  ✓ Rust already installed"
fi

echo "✓ All system dependencies installed"
echo ""

# Clone repository
echo "→ Downloading installer..."
if ! git clone --depth 1 -q "$REPO_URL" "$INSTALL_DIR" 2>&1; then
    echo "✗ Error: Failed to download installer from $REPO_URL" >&2
    echo "  Check your internet connection or repository URL" >&2
    exit 1
fi

cd "$INSTALL_DIR" || exit 1
echo "✓ Installer downloaded"
echo ""

# Ensure cargo is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Build Rust application
echo "→ Building Rust installer..."
if ! cargo build --release 2>&1; then
    echo "✗ Error: Failed to build Rust installer" >&2
    echo "  Check Rust installation and try again" >&2
    exit 1
fi
echo "✓ Rust installer built"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Launching Installer (requires sudo)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Launch the TUI with sudo
sudo ./target/release/pelican-installer

# Cleanup
EXIT_CODE=$?
echo ""
echo "→ Cleaning up..."
cd /
rm -rf "$INSTALL_DIR"
echo "✓ Cleanup complete"

exit $EXIT_CODE

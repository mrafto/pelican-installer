#!/bin/bash

################################################################################
# Pelican Panel Installer - Quick Launch Script
# 
# Downloads and runs the Pelican Panel TUI installer
# Usage: curl -fsSL https://raw.githubusercontent.com/mrafto/pelican-installer/main/install.sh | bash
################################################################################

set -e

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

# Check and install python3
if ! command -v python3 &> /dev/null; then
    echo "  Installing python3..."
    sudo apt-get update -qq
    sudo apt-get install -y python3
    echo "  ✓ python3 installed"
else
    echo "  ✓ python3 already installed"
fi

# Check and install pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "  Installing pip..."
    
    # Method 1: Try ensurepip first (modern method)
    echo "    Trying ensurepip..."
    if python3 -m ensurepip --default-pip 2>&1; then
        echo "  ✓ pip installed via ensurepip"
    # Method 2: Download and run pip installer
    else
        echo "    ensurepip failed, trying bootstrap..."
        if curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && python3 /tmp/get-pip.py; then
            echo "  ✓ pip installed via bootstrap"
        # Method 3: Try apt-get (for older systems)
        else
            echo "    bootstrap failed, trying apt-get..."
            if sudo apt-get install -y python3-pip 2>&1; then
                echo "  ✓ pip installed via apt"
            else
                echo "  ✗ All pip installation methods failed" >&2
                echo "    Please install pip manually: https://pip.pypa.io/en/stable/installation/" >&2
                exit 1
            fi
        fi
    fi
else
    echo "  ✓ pip already installed"
fi

# Check and install git
if ! command -v git &> /dev/null; then
    echo "  Installing git..."
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

# Install Python packages for the TUI
echo "→ Installing Python packages (textual)..."

# Try different installation methods
if python3 -m pip install --user -r requirements.txt &> /dev/null; then
    echo "✓ Python packages installed"
elif python3 -m pip install --user --break-system-packages -r requirements.txt &> /dev/null; then
    # Fallback for newer Debian/Ubuntu with PEP 668
    echo "✓ Python packages installed"
elif sudo python3 -m pip install -r requirements.txt &> /dev/null; then
    # System-wide installation (requires sudo)
    echo "✓ Python packages installed (system-wide)"
else
    echo "✗ Warning: Could not install Python packages automatically" >&2
    echo "  Attempting to continue anyway..." >&2
    echo "" >&2
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Launching Installer (requires sudo)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Launch the TUI with sudo
sudo python3 main.py

# Cleanup
EXIT_CODE=$?
echo ""
echo "→ Cleaning up..."
cd /
rm -rf "$INSTALL_DIR"
echo "✓ Cleanup complete"

exit $EXIT_CODE

#!/bin/bash

set -e

# Function to emit progress markers
progress() {
    echo "PROGRESS:$1:$2"
}

# Function to emit error markers
error() {
    echo "ERROR:$1"
    exit 1
}

progress 10 "Checking system requirements..."

# Check kernel compatibility
KERNEL=$(uname -r)
if [[ "$KERNEL" == *"-grs-"* ]] || [[ "$KERNEL" == *"-mod-std-"* ]]; then
    error "Kernel not compatible with Docker. Contact your hosting provider."
fi

progress 20 "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
fi

progress 60 "Downloading Wings binary..."
WINGS_PATH="/usr/local/bin/wings"
curl -L -o "$WINGS_PATH" https://github.com/pelican-dev/wings/releases/latest/download/wings_linux_amd64
chmod +x "$WINGS_PATH"

progress 80 "Creating Wings service..."
# Create systemd service file
cat > /etc/systemd/system/wings.service <<EOF
[Unit]
Description=Wings Daemon
After=docker.service
Requires=docker.service

[Service]
User=root
WorkingDirectory=/etc/pelican
ExecStart=/usr/local/bin/wings
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Create working directory
mkdir -p /etc/pelican

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable wings

progress 100 "Wings installed successfully!"

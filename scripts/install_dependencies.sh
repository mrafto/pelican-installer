#!/bin/bash

set -e

COMPONENT="$1"
WEBSERVER="${2:-nginx}"

# Function to emit progress markers
progress() {
    echo "PROGRESS:$1:$2"
}

# Function to emit error markers
error() {
    echo "ERROR:$1"
    exit 1
}

progress 5 "Checking system requirements..."

# Update package lists
progress 10 "Updating package lists..."
apt-get update -qq

if [ "$COMPONENT" = "panel" ]; then
    PHP_VERSION="8.3"
    
    progress 20 "Installing PHP ${PHP_VERSION}..."
    apt-get install -y php${PHP_VERSION} php${PHP_VERSION}-fpm php${PHP_VERSION}-gd \
        php${PHP_VERSION}-mysql php${PHP_VERSION}-mbstring php${PHP_VERSION}-bcmath \
        php${PHP_VERSION}-xml php${PHP_VERSION}-curl php${PHP_VERSION}-zip \
        php${PHP_VERSION}-intl php${PHP_VERSION}-sqlite3 2>&1 | grep -v "^Selecting\|^Preparing\|^Unpacking\|^Setting" || true
    
    progress 50 "Installing ${WEBSERVER}..."
    case "$WEBSERVER" in
        nginx)
            apt-get install -y nginx
            ;;
        apache)
            apt-get install -y apache2 libapache2-mod-php${PHP_VERSION}
            a2enmod rewrite ssl
            ;;
        caddy)
            apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
            curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
                gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
            curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt" | \
                tee /etc/apt/sources.list.d/caddy-stable.list
            apt-get update
            apt-get install -y caddy
            ;;
    esac
    
    progress 70 "Installing additional tools..."
    apt-get install -y curl tar unzip git
    
    progress 80 "Installing Composer..."
    if ! command -v composer &> /dev/null; then
        curl -sS https://getcomposer.org/installer -o /tmp/composer-setup.php
        php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer
        rm /tmp/composer-setup.php
    fi
    
    progress 100 "Dependencies installed successfully!"
    
elif [ "$COMPONENT" = "wings" ]; then
    progress 20 "Checking kernel compatibility..."
    KERNEL=$(uname -r)
    if [[ "$KERNEL" == *"-grs-"* ]] || [[ "$KERNEL" == *"-mod-std-"* ]]; then
        error "Kernel not compatible with Docker. Contact your hosting provider."
    fi
    
    progress 40 "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    
    progress 80 "Enabling Docker service..."
    systemctl enable docker
    systemctl start docker
    
    progress 100 "Docker installed successfully!"
fi

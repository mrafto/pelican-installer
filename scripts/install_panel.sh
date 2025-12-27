#!/bin/bash

set -e

DOMAIN="$1"
PROTOCOL="$2"
WEBSERVER="$3"
SSL_EMAIL="$4"

PANEL_DIR="/var/www/pelican"

# Function to emit progress markers
progress() {
    echo "PROGRESS:$1:$2"
}

# Function to emit error markers
error() {
    echo "ERROR:$1"
    exit 1
}

progress 5 "Preparing installation..."

# Create panel directory
if [ ! -d "$PANEL_DIR" ]; then
    mkdir -p "$PANEL_DIR"
fi

progress 10 "Downloading panel files..."
curl -L https://github.com/pelican-dev/panel/releases/latest/download/panel.tar.gz | \
    tar -xz -C "$PANEL_DIR"

progress 30 "Installing PHP dependencies..."
cd "$PANEL_DIR"
composer install --no-dev --optimize-autoloader

progress 50 "Configuring ${WEBSERVER}..."

# Configure webserver based on type
case "$WEBSERVER" in
    nginx)
        CONFIG_PATH="/etc/nginx/sites-available/pelican.conf"
        PROTOCOL_NUM=443
        if [ "$PROTOCOL" = "http" ]; then
            PROTOCOL_NUM=80
        fi
        
        cat > "$CONFIG_PATH" <<EOF
server {
    listen ${PROTOCOL_NUM};
    listen [::]:${PROTOCOL_NUM};
    server_name ${DOMAIN};
    root ${PANEL_DIR}/public;
    index index.php;

    access_log /var/log/nginx/pelican.app-access.log;
    error_log  /var/log/nginx/pelican.app-error.log error;

    client_max_body_size 100M;
    client_body_timeout 120s;

    sendfile off;

    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param PHP_VALUE "upload_max_filesize = 100M \\n post_max_size=100M";
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_intercept_errors off;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_read_timeout 300;
        include /etc/nginx/fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
EOF
        
        # Enable site
        ln -sf "$CONFIG_PATH" /etc/nginx/sites-enabled/pelican.conf
        
        # Test and reload Nginx
        nginx -t
        systemctl reload nginx
        ;;
        
    apache)
        CONFIG_PATH="/etc/apache2/sites-available/pelican.conf"
        PROTOCOL_NUM=443
        if [ "$PROTOCOL" = "http" ]; then
            PROTOCOL_NUM=80
        fi
        
        cat > "$CONFIG_PATH" <<EOF
<VirtualHost *:${PROTOCOL_NUM}>
    ServerName ${DOMAIN}
    DocumentRoot "${PANEL_DIR}/public"

    AllowEncodedSlashes NoDecode

    <Directory "${PANEL_DIR}/public">
        Require all granted
        AllowOverride all
    </Directory>

    ErrorLog /var/log/apache2/pelican.app-error.log
    CustomLog /var/log/apache2/pelican.app-access.log combined
</VirtualHost>
EOF
        
        # Enable site
        a2ensite pelican.conf
        systemctl reload apache2
        ;;
        
    caddy)
        CONFIG_PATH="/etc/caddy/Caddyfile"
        
        cat >> "$CONFIG_PATH" <<EOF
${DOMAIN} {
    root * ${PANEL_DIR}/public
    file_server

    php_fastcgi unix//run/php/php8.3-fpm.sock

    header {
        -Server
        -X-Powered-By
        Referrer-Policy "same-origin"
        X-Frame-Options "deny"
        X-XSS-Protection "1; mode=block"
        X-Content-Type-Options "nosniff"
    }
}
EOF
        
        systemctl reload caddy
        ;;
esac

progress 70 "Setting up SSL (if HTTPS)..."
if [ "$PROTOCOL" = "https" ]; then
    case "$WEBSERVER" in
        nginx)
            certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$SSL_EMAIL" || true
            ;;
        apache)
            certbot --apache -d "$DOMAIN" --non-interactive --agree-tos -m "$SSL_EMAIL" || true
            ;;
        caddy)
            # Caddy handles SSL automatically
            ;;
    esac
fi

progress 85 "Setting permissions..."
chown -R www-data:www-data "$PANEL_DIR"
chmod -R 755 "$PANEL_DIR/storage"
chmod -R 755 "$PANEL_DIR/bootstrap/cache"

progress 100 "Panel installed successfully!"

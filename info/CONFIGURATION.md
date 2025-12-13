# Pelican Panel Installer - Configuration Reference

This document provides detailed configuration information and reference for the Pelican Panel installer.

## Installation Flow Diagram

```
START
  ↓
[System Requirements Check]
  ↓ Pass
[Main Menu Selection]
  ├─ Install Panel → [Webserver Selection]
  ├─ Install Wings → [Docker Setup]
  ├─ Update/Reinstall → [Update Specific Component]
  └─ Uninstall → [Remove Component + Dependencies]
  ↓
[For Panel]:
  ├─ Webserver Selection (Nginx/Apache/Caddy)
  ├─ Protocol Selection (HTTP/HTTPS)
  ├─ Domain Input
  ├─ [If HTTPS] SSL Certificate Setup
  ├─ Dependency Installation
  ├─ PHP Configuration
  ├─ Panel Installation
  └─ Web Installer Access
  ↓
[For Wings]:
  ├─ Kernel Compatibility Check
  ├─ Docker Installation
  ├─ Wings Binary Download
  └─ Node Configuration (via Panel)
  ↓
[Summary & Next Steps]
  ↓
END
```

## Supported Operating Systems

| OS | Version | Support | Notes |
|---|---------|---------|-------|
| Ubuntu | 22.04 | ✅ Full | Fully supported |
| Ubuntu | 24.04 | ✅ Full | Recommended version |
| Debian | 12 | ✅ Full | Fully supported |
| Debian | 11 | ⚠️ Partial | No SQLite support |
| Rocky Linux | 10 | ✅ Full | Supported |
| Rocky Linux | 9 | ⚠️ Partial | No SQLite support |
| Alma Linux | 10 | ✅ Full | Supported |
| Alma Linux | 9 | ⚠️ Partial | No SQLite support |
| CentOS | 10 | ✅ Full | Supported |

**Note**: OpenVZ without specific configuration is NOT supported for Wings.

## System Requirements

### Minimum
- **CPU**: 2 cores (3 GHz+)
- **RAM**: 2 GB
- **Disk**: 5 GB
- **Network**: 100 Mbps

### Recommended
- **CPU**: 4 cores (3.5 GHz+)
- **RAM**: 4-8 GB (add 2GB per Wings node)
- **Disk**: 50+ GB (SSD recommended)
- **Network**: 1 Gbps

## Dependencies Reference

### Panel Dependencies

**PHP & Extensions** (8.4, 8.3, or 8.2):
```
php8.4
php8.4-fpm
php8.4-gd          # Image processing
php8.4-mysql       # Database support
php8.4-mbstring    # Multi-byte string support
php8.4-bcmath      # Arbitrary precision math
php8.4-xml         # XML parsing
php8.4-curl        # HTTP requests
php8.4-zip         # ZIP file handling
php8.4-intl        # Internationalization
php8.4-sqlite3     # SQLite database (optional)
```

**Webservers** (choose one):
```
nginx              # Nginx web server
apache2            # Apache web server
libapache2-mod-php # PHP module for Apache
caddy              # Caddy web server
```

**Tools & Libraries**:
```
curl               # Download files
tar                # Extract archives
unzip              # Extract zip files
composer           # PHP dependency manager
```

**Databases** (optional):
```
mysql-server       # MySQL server 8.0+
mariadb-server     # MariaDB server 10.6+
```

### Wings Dependencies

**Docker**:
```
docker.io          # Docker container engine
docker-ce          # Docker community edition
```

**System Requirements**:
- Linux kernel 4.15+ (without `-grs-` or `-mod-std-` flags)
- 512 MB RAM per container (minimum)
- 1 GB disk space per container (minimum)

## Webserver Configuration Details

### NGINX Configuration

**Config Location**: `/etc/nginx/sites-available/pelican.conf`

**Key Settings**:
```nginx
listen 443 ssl http2;           # HTTPS with HTTP/2
server_name <domain>;
root /var/www/pelican/public;

fastcgi_pass unix:/run/php/php8.4-fpm.sock;
upload_max_filesize = 100M;
post_max_size = 100M;
```

**Recommended Directives**:
- `http2 enabled`: Faster protocol
- `gzip on`: Compression
- `upstream` blocks: For load balancing
- `fastcgi_cache`: Response caching

### Apache Configuration

**Config Location**: `/etc/apache2/sites-available/pelican.conf`

**Required Modules**:
```
mod_php
mod_rewrite        # URL rewriting
mod_ssl            # SSL/TLS support
mod_proxy          # Reverse proxy
```

**Enable**: 
```bash
sudo a2enmod rewrite ssl
sudo a2ensite pelican.conf
```

### Caddy Configuration

**Config Location**: `/etc/caddy/Caddyfile`

**Features**:
- Automatic HTTPS
- Automatic certificate renewal
- Simple syntax
- Built-in auto-redirect HTTP→HTTPS

```caddy
<domain> {
    root * /var/www/pelican/public
    file_server
    php_fastcgi unix//run/php/php8.4-fpm.sock
}
```

## SSL/TLS Certificate Configuration

### Automatic (Certbot)

**Installation by Webserver**:
```bash
# Nginx
sudo apt install -y python3-certbot-nginx

# Apache  
sudo apt install -y python3-certbot-apache

# Other
sudo apt install -y certbot
```

**Certbot Command**:
```bash
sudo certbot certonly --non-interactive \
  --agree-tos \
  -m admin@example.com \
  -d panel.example.com \
  --webroot \
  -w /var/www/pelican/public
```

**Auto-Renewal**:
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Manual Certificates

If you have existing certificates:

```bash
# Copy certificate files
sudo cp mycert.crt /etc/letsencrypt/live/domain.com/fullchain.pem
sudo cp mykey.key /etc/letsencrypt/live/domain.com/privkey.pem

# Set permissions
sudo chown -R root:root /etc/letsencrypt/
sudo chmod -R 755 /etc/letsencrypt/live/
```

### CloudFlare DNS Challenge

For advanced users with access restrictions:

```bash
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials ~/.cloudflare/cloudflare.ini \
  -d panel.example.com
```

## Port Requirements

### Inbound (Server)

| Port | Protocol | Service | Required |
|------|----------|---------|----------|
| 80 | TCP | HTTP | ✅ (redirect to 443) |
| 443 | TCP | HTTPS | ✅ |
| 25565 | TCP/UDP | Game Servers | ✅ (Wings) |
| 27015 | TCP/UDP | Game Servers | ✅ (Wings) |
| Custom | TCP/UDP | Game Servers | ✅ (Wings) |

### Outbound (Installation)

| Host | Port | Purpose |
|------|------|---------|
| github.com | 443 | Download releases |
| api.github.com | 443 | Check latest versions |
| packagecloud.io | 443 | Package repositories |
| acme-v02.api.letsencrypt.org | 443 | SSL certificates |
| archive.ubuntu.com | 80/443 | Package mirrors |

## Database Configuration

### MySQL/MariaDB Setup

**Create Database**:
```bash
mysql -u root -p << EOF
CREATE DATABASE panel;
CREATE USER 'pelican'@'127.0.0.1' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON panel.* TO 'pelican'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;
EOF
```

**Environment File** (`/var/www/pelican/.env`):
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=panel
DB_USERNAME=pelican
DB_PASSWORD=your_secure_password
```

### SQLite Setup

**Database File**:
```bash
sudo touch /var/www/pelican/storage/database.sqlite
sudo chown www-data:www-data /var/www/pelican/storage/database.sqlite
sudo chmod 644 /var/www/pelican/storage/database.sqlite
```

**Environment File** (`/var/www/pelican/.env`):
```env
DB_CONNECTION=sqlite
DB_DATABASE=/var/www/pelican/storage/database.sqlite
```

## PHP Configuration Tuning

### Upload Limits

Edit `/etc/php/8.4/fpm/php.ini`:

```ini
; Default: 2M
upload_max_filesize = 100M

; Default: 8M
post_max_size = 100M

; Default: 30 seconds
max_execution_time = 300

; Default: 30 seconds
max_input_time = 300
```

### Memory Limits

```ini
; Default: 128M
memory_limit = 256M

; Default: 8M
max_file_uploads = 50
```

### OPcache Settings

```ini
zend_extension=opcache.so

; Enable OPcache
opcache.enable = 1

; Size in MB
opcache.memory_consumption = 128

; Number of cached files
opcache.max_accelerated_files = 10000

; Validation interval (0 = check on every request)
opcache.validate_timestamps = 0
```

## Wings Configuration

### Configuration File Location
```
/etc/pelican/config.yml
```

### Auto-Generated Configuration

The Panel generates this during Node creation. Key sections:

```yaml
debug: false
uuid: node-uuid-here
token_id: token-id
token: token-secret
remote: https://panel.example.com
api:
  host: 0.0.0.0
  port: 8080
  ssl:
    enabled: true
    cert: /etc/letsencrypt/live/domain/fullchain.pem
    key: /etc/letsencrypt/live/domain/privkey.pem
system:
  data: /var/lib/pelican
  arch: linux/amd64
docker:
  network:
    name: pelican_network
    driver: bridge
```

### Wings Service Setup

**Service File** (`/etc/systemd/system/wings.service`):

```ini
[Unit]
Description=Wings Daemon
After=docker.service
Requires=docker.service
PartOf=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/etc/pelican
ExecStart=/usr/local/bin/wings
Restart=on-failure
RestartSec=5s
StartLimitInterval=180
StartLimitBurst=30
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
```

**Start Wings**:
```bash
sudo systemctl enable wings
sudo systemctl start wings
sudo systemctl status wings
```

## Docker Configuration for Wings

### Network Setup

```bash
# Create dedicated network
docker network create --driver bridge pelican_network

# Inspect network
docker network inspect pelican_network
```

### Resource Limits

For production, set container limits in Panel Node settings:

- **Memory**: Limit per container in MB
- **CPU**: Share percentage (100 = 1 core)
- **Disk**: Quota per container in MB

### Storage Considerations

**Server Data**: `/var/lib/pelican/servers/[uuid]/`
- Each server folder: 1-10 GB typical
- Disk space = (# of servers) × (average game size)

**Backups**: `/var/lib/pelican/backups/`
- Consider separate disk/partition
- Regular cleanup recommended

## Firewall Configuration

### UFW (Ubuntu Firewall)

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow game server ports
sudo ufw allow 25565:25575/tcp
sudo ufw allow 25565:25575/udp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### firewalld (CentOS/Rocky)

```bash
# Allow HTTP/HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Allow game ports
sudo firewall-cmd --permanent --add-port=25565-25575/tcp
sudo firewall-cmd --permanent --add-port=25565-25575/udp

# Reload
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

## Monitoring & Logs

### Panel Logs

```bash
# Web server logs
sudo tail -f /var/log/nginx/pelican.app-error.log      # Nginx
sudo tail -f /var/log/apache2/error.log                 # Apache

# PHP-FPM logs
sudo tail -f /var/log/php8.4-fpm.log

# Application logs
sudo tail -f /var/www/pelican/storage/logs/laravel.log

# Queue worker
sudo journalctl -u pelican-queue -f
```

### Wings Logs

```bash
# Systemd journal
sudo journalctl -u wings -f

# With filters
sudo journalctl -u wings -f --grep="error"
sudo journalctl -u wings --since="1 hour ago"

# Log file (if enabled)
tail -f /var/log/wings/wings.log
```

### System Metrics

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check Docker
docker ps
docker stats

# Check service status
sudo systemctl status nginx          # or apache2, caddy
sudo systemctl status php8.4-fpm
sudo systemctl status mysql          # or mariadb
sudo systemctl status wings
```

## Troubleshooting Reference

### Installation Failures

**Problem**: Download fails
```bash
# Check internet connectivity
curl -I https://github.com

# Check DNS
nslookup github.com

# Try with verbose flag
curl -v https://github.com/...
```

**Problem**: Permission denied
```bash
# Check current user
whoami

# Check sudoers
sudo -l

# Check file permissions
ls -la /var/www/pelican
```

### Runtime Issues

**Problem**: Port already in use
```bash
# Find process using port
sudo lsof -i :80
sudo lsof -i :443

# Stop the service
sudo systemctl stop <service>
```

**Problem**: SSL certificate expired
```bash
# Check certificate
sudo openssl x509 -in /etc/letsencrypt/live/domain/fullchain.pem -text -noout

# Renew manually
sudo certbot renew --force-renewal

# Verify renewal
sudo certbot certificates
```

**Problem**: Panel not responding
```bash
# Check webserver
sudo systemctl status nginx     # or apache2, caddy

# Check PHP-FPM
sudo systemctl status php8.4-fpm

# Check database
sudo systemctl status mysql     # or mariadb

# Check logs
sudo tail -f /var/log/nginx/error.log
```

## Upgrade Path

### Panel Updates

```bash
cd /var/www/pelican

# Backup first
sudo tar -czf panel-backup-$(date +%Y%m%d).tar.gz /var/www/pelican

# Download latest
curl -L https://github.com/pelican-dev/panel/releases/latest/download/panel.tar.gz | sudo tar -xzv

# Run migrations
sudo composer install --no-dev --optimize-autoloader
```

### Wings Updates

```bash
# Stop service
sudo systemctl stop wings

# Backup config
sudo cp /etc/pelican/config.yml /etc/pelican/config.yml.backup

# Download latest
sudo curl -L -o /usr/local/bin/wings "https://github.com/pelican-dev/wings/releases/latest/download/wings_linux_amd64"
sudo chmod +x /usr/local/bin/wings

# Start service
sudo systemctl start wings
```

## Performance Optimization

### PHP OPcache

Enable and configure:
```ini
opcache.enable=1
opcache.memory_consumption=256
opcache.max_accelerated_files=20000
opcache.interned_strings_buffer=16
opcache.fast_shutdown=1
```

### Nginx Tuning

```nginx
# Worker connections
events {
    worker_connections 4096;
}

# Caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;

# Gzip
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json;
```

### Docker Resource Limits

In `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
```

## Security Hardening

1. **SSH Key-Only Authentication**
2. **Fail2Ban** for brute-force protection
3. **SELinux/AppArmor** for application isolation
4. **Regular Security Updates**
5. **File Integrity Monitoring**
6. **Container Image Scanning**

---

For more details, visit: https://pelican.dev/docs

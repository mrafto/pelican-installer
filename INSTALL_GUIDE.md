# Pelican Panel Installer - Installation Guide

## ⚠️ Important Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04+ or Debian 12+ (other distros may work but untested)
- **RAM**: 2GB minimum (4GB+ recommended)
- **Disk**: 10GB+ free space
- **Network**: Outbound internet access
- **Privileges**: Root or sudo access

### Pre-Installation Checklist
- [ ] Fresh server or clean system
- [ ] Root/sudo access verified
- [ ] Domain pointed to server IP (if using HTTPS)
- [ ] Ports 80 and 443 available
- [ ] No conflicting services (nginx/apache/docker)

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/username/repo/main/install.sh | bash
```

This will:
1. Clone the repository
2. Install Python dependencies
3. Launch the TUI installer automatically

### Method 2: Manual Install

```bash
# Clone repository
git clone https://github.com/username/pelican-installer.git
cd pelican-installer

# Install dependencies
pip install -r requirements.txt

# Run with sudo
sudo python main.py
```

## What Gets Installed

### For Panel Installation

**System Packages:**
- PHP 8.3 + 10 extensions (gd, mysql, mbstring, bcmath, xml, curl, zip, intl, sqlite3, fpm)
- Webserver (Nginx/Apache/Caddy - your choice)
- Composer (PHP package manager)
- Certbot (if using HTTPS)
- curl, tar, unzip, git

**Panel Components:**
- Panel files in `/var/www/pelican`
- Webserver configuration
- SSL certificates (if HTTPS)
- Proper file permissions

### For Wings Installation

**System Packages:**
- Docker CE (Community Edition)
- Docker network for Pelican

**Wings Components:**
- Wings binary in `/usr/local/bin/wings`
- Configuration directory `/etc/pelican`
- Systemd service
- Docker network configuration

## Step-by-Step Guide

### Step 1: Launch Installer

```bash
sudo python main.py
```

You'll see the main menu with your OS information and available options.

### Step 2: Choose Component

Select what to install:
- **Install Panel** - For the web management interface
- **Install Wings** - For the game server daemon

Use arrow keys or type `1` or `2`, then press Enter.

### Step 3: Configure Panel (if selected)

**A. Choose Webserver:**
- `1` for Nginx (recommended) - Fast, lightweight
- `2` for Apache - Traditional, well-supported
- `3` for Caddy - Modern, auto-HTTPS

**B. Select Protocol:**
- `1` for HTTPS (recommended) - Secure, encrypted
- `2` for HTTP - Development only, not secure

**C. Enter Domain:**
- For HTTPS: Enter your domain (e.g., `panel.example.com`)
- For HTTP: Enter domain or IP address

**D. SSL Setup (if HTTPS):**
- Enter email for Let's Encrypt notifications
- Certbot will automatically generate certificates

### Step 4: Wait for Installation

The installer will:
1. **Check system** (5%)
2. **Update packages** (10-25%)
3. **Install dependencies** (25-50%)
4. **Configure services** (50-70%)
5. **Set up Panel/Wings** (70-95%)
6. **Finalize** (95-100%)

Progress is shown in real-time with status messages.

### Step 5: Review Summary

After installation completes:
- ✅ Installed components listed
- ✅ Configuration summary shown
- ✅ Next steps provided

Press `n` to continue or `c` to close.

## Post-Installation Steps

### For Panel

1. **Access Web Installer:**
   ```
   https://your-domain.com/installer
   ```

2. **Complete Setup Wizard:**
   - Create admin account
   - Configure database (MySQL/MariaDB or SQLite)
   - Set application settings

3. **Secure Your Installation:**
   - Remove installer files after setup
   - Configure firewall
   - Set up backups

### For Wings

1. **Configure Wings via Panel:**
   - Log into Panel admin area
   - Go to **Admin → Nodes**
   - Click **Create Node**
   - Copy the auto-generated `config.yml`

2. **Apply Configuration:**
   ```bash
   sudo nano /etc/pelican/config.yml
   # Paste the configuration
   ```

3. **Start Wings:**
   ```bash
   sudo systemctl start wings
   sudo systemctl status wings
   ```

## Troubleshooting

### Permission Denied
**Problem**: `Permission denied` errors during installation

**Solution**:
```bash
# Ensure you're using sudo
sudo python main.py

# Check if you have sudo access
sudo -l
```

### Port Already in Use
**Problem**: Ports 80/443 already in use

**Solution**:
```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Stop the conflicting service
sudo systemctl stop <service-name>
```

### SSL Certificate Fails
**Problem**: Certbot fails to generate certificate

**Solution**:
- Ensure domain points to your server IP
- Check port 80 is accessible from internet
- Verify email address is valid
- Try manual certbot command:
  ```bash
  sudo certbot --nginx -d your-domain.com
  ```

### Docker Installation Fails
**Problem**: Docker won't install or kernel incompatible

**Solution**:
```bash
# Check kernel version
uname -r

# If kernel has -grs- or -mod-std-, contact hosting provider
# Otherwise, try manual Docker install:
curl -fsSL https://get.docker.com | sh
```

### Installation Hangs
**Problem**: Installation seems stuck

**Solution**:
- Wait at least 5 minutes (package downloads can be slow)
- Check internet connection
- Press `c` to cancel and try again
- Check `/var/log/syslog` for errors

## Verification

### Verify Panel Installation

```bash
# Check files exist
ls -la /var/www/pelican

# Check webserver is running
sudo systemctl status nginx  # or apache2, caddy

# Check PHP-FPM is running
sudo systemctl status php8.3-fpm

# Test SSL certificate (if HTTPS)
sudo certbot certificates
```

### Verify Wings Installation

```bash
# Check Wings binary
which wings
wings --version

# Check Docker is running
sudo systemctl status docker
sudo docker ps

# Check Wings service
sudo systemctl status wings
```

## Uninstallation

### Remove Panel

```bash
# Stop services
sudo systemctl stop nginx php8.3-fpm

# Remove files
sudo rm -rf /var/www/pelican

# Remove webserver config
sudo rm /etc/nginx/sites-enabled/pelican.conf

# Restart webserver
sudo systemctl restart nginx
```

### Remove Wings

```bash
# Stop service
sudo systemctl stop wings
sudo systemctl disable wings

# Remove files
sudo rm /usr/local/bin/wings
sudo rm -rf /etc/pelican
sudo rm /etc/systemd/system/wings.service

# Optionally remove server data
sudo rm -rf /var/lib/pelican
```

## Security Best Practices

1. **Keep System Updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Configure Firewall:**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **Regular Backups:**
   ```bash
   # Panel
   sudo tar -czf panel-backup-$(date +%Y%m%d).tar.gz /var/www/pelican

   # Wings
   sudo tar -czf wings-backup-$(date +%Y%m%d).tar.gz /var/lib/pelican
   ```

4. **Monitor Logs:**
   ```bash
   # Panel logs
   sudo tail -f /var/log/nginx/pelican.app-error.log

   # Wings logs
   sudo journalctl -u wings -f
   ```

5. **Use Strong Passwords:**
   - Admin panel password
   - Database password (if MySQL/MariaDB)

## Getting Help

- **Documentation**: https://pelican.dev/docs
- **Discord Community**: https://discord.gg/pelican
- **GitHub Issues**: https://github.com/pelican-dev/panel/issues

## Advanced Configuration

For advanced configuration options (database setup, firewall rules, performance tuning), see:
- `info/CONFIGURATION.md` - Detailed configuration reference
- `info/pelican-installer-plan.md` - Full installation plan

---

**Questions?** Open an issue or ask in the Discord community!


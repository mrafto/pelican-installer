# Pelican Panel Installer

A modern, user-friendly text-based user interface (TUI) installer for **Pelican Panel** and **Wings** (game server manager). Built with Python and Rich for beautiful terminal interfaces.

## Features

✨ **Modern TUI Interface**
- Color-coded interface with panels and tables
- Responsive keyboard and mouse navigation
- Real-time progress indicators
- Cancel button always accessible (press `C`)

🚀 **Smart Installation**
- Auto-detects existing installations
- Automatically checks and installs dependencies
- Supports multiple webservers (Nginx, Apache, Caddy)
- Automatic SSL certificate generation via Let's Encrypt
- Works with both HTTP and HTTPS

🛡️ **Security First**
- HTTPS is default and recommended
- Automatic SSL certificate renewal
- Proper file permissions and ownership
- Sudo access used only when needed

👥 **User-Friendly**
- No command-line knowledge required
- Descriptive prompts and error messages
- Support for both keyboard (arrows, numbers) and mouse interactions
- Progress bars for all operations

## Requirements

- **OS**: Ubuntu 22.04+ (24.04 recommended) or Debian 12+
- **Memory**: 2GB minimum (4GB+ recommended)
- **Disk Space**: 5GB minimum
- **Network**: Outbound access to package repositories and GitHub
- **Privileges**: Root or sudo access

## Quick Start

The easiest way to install is with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/username/repo/main/install.sh | bash
```

Replace `username/repo` with your actual repository path.

### Step-by-Step Installation

1. **SSH into your server**:
   ```bash
   ssh user@your-server.com
   ```

2. **Run the installer**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/username/repo/main/install.sh | bash
   ```

3. **Follow the prompts**:
   - Select what to install (Panel, Wings, or both)
   - Choose your webserver (Nginx recommended)
   - Select HTTPS (recommended) or HTTP
   - Provide your domain name
   - Configure SSL certificates (optional)

4. **Access the Panel**:
   - Navigate to `https://your-domain.com/installer`
   - Complete the web-based setup wizard
   - Create your admin account

## Usage Guide

### Main Menu

When you run the installer, you'll see the main menu:

```
Select what to install:

[1] Install Panel                              (new installation)
[2] Install Wings                              (game server manager)

Navigation: [↑↓] Navigate | [1-4] Quick Select | [C] Cancel | [Enter] Select
```

**Keyboard Controls**:
- `↑↓` - Navigate options
- `1-9` - Select directly
- `Enter` - Confirm selection
- `C` - Cancel

**Mouse Support**:
- Click on any option to select
- Click buttons to confirm

### Installation Phases

#### 1. Component Selection
Choose what you want to install:
- **Panel**: The web interface for game server management
- **Wings**: The daemon for running game servers in Docker containers

#### 2. Dependency Installation
The installer automatically:
- Detects your OS and package manager
- Checks what's already installed
- Installs missing dependencies
- Shows real-time progress

Dependencies installed:
- PHP 8.4 with required extensions
- Composer (for PHP dependencies)
- Webserver (Nginx, Apache, or Caddy)
- Docker (for Wings)
- Various system utilities

#### 3. Webserver Selection
Choose your preferred web server:

| Webserver | Pros | Cons |
|-----------|------|------|
| **Nginx** (default) | Fast, lightweight, modern | Simpler config |
| **Apache** | Traditional, extensive modules | Heavier, more complex |
| **Caddy** | Auto HTTPS, simple config | Newer, less tested |

#### 4. Protocol Selection
Choose between:
- **HTTPS** (recommended): Encrypted, secure, production-ready
- **HTTP**: Unencrypted, faster setup, development-only

#### 5. Domain Configuration
Provide your domain or IP address:
- For HTTPS: Use a domain name (not IP)
- For HTTP: Can use domain or IP address

#### 6. SSL Certificate Setup
For HTTPS installations:
- Auto-generate with Let's Encrypt (Certbot) - **recommended**
- Use existing certificates
- Provide email for certificate notifications

#### 7. PHP & Webserver Setup
Automatically configures:
- PHP-FPM socket connections
- Webserver virtual host
- Upload limits
- FastCGI settings

#### 8. Wings Setup (optional)
If selected:
- Installs Docker Engine
- Downloads Wings binary
- Creates configuration directories
- Shows configuration steps

### After Installation

After successful installation:

1. **Access the Web Installer**:
   ```
   https://your-domain.com/installer
   ```

2. **Complete Setup Wizard**:
   - Set admin credentials
   - Configure database (MySQL/MariaDB or SQLite)
   - Configure application settings
   - Create first user account

3. **Configure Wings** (if installed):
   - Go to Admin Panel → Nodes
   - Click "Create New Node"
   - Copy the auto-generated configuration
   - On your Wings server, create `/etc/pelican/config.yml` with the config
   - Start Wings: `sudo systemctl start wings`

## File Locations

After installation, files are located at:

```
/var/www/pelican/              # Panel installation directory
/var/www/pelican/public/       # Web-accessible files
/var/www/pelican/storage/      # Logs and cache
/etc/nginx/sites-enabled/      # Webserver config (Nginx)
/etc/apache2/sites-enabled/    # Webserver config (Apache)
/etc/caddy/Caddyfile           # Webserver config (Caddy)
/etc/pelican/config.yml        # Wings configuration
/var/lib/pelican/              # Wings server data
/var/log/pelican-installer.log # Installation logs
```

## Troubleshooting

### Common Issues

**Port 80/443 Already in Use**
```bash
sudo lsof -i :80
sudo lsof -i :443
```
Stop the conflicting service or use different ports.

**Permission Denied Errors**
The installer needs sudo access. Ensure you have sudo privileges:
```bash
sudo -l
```

**SSL Certificate Generation Failed**
- Check domain points to correct IP: `nslookup your-domain.com`
- Ensure port 80 is open for verification
- Check email is valid for Let's Encrypt

**Wings Docker Issues**
- Check kernel compatibility: `uname -r`
- Should not end in `-grs-` or `-mod-std-`
- Contact hosting provider for standard kernel

**PHP Extensions Not Loaded**
```bash
php -m | grep -E "gd|mysql|bcmath|curl"
sudo systemctl restart php8.4-fpm
```

### Viewing Logs

```bash
# View installation logs
tail -f /var/log/pelican-installer.log

# View Nginx logs
sudo tail -f /var/log/nginx/pelican.app-error.log

# View PHP-FPM logs
sudo tail -f /var/log/php8.4-fpm.log

# View Wings logs
sudo journalctl -u wings -f
```

## Advanced Configuration

### Manual Database Setup

If you want to use a specific database:

```bash
mysql -u root -p
CREATE DATABASE panel;
CREATE USER 'pelican'@'127.0.0.1' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON panel.* TO 'pelican'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;
```

### Using Existing SSL Certificates

If you have existing certificates:

```bash
# Copy to locations expected by certbot
sudo cp your-cert.crt /etc/letsencrypt/live/your-domain.com/fullchain.pem
sudo cp your-key.key /etc/letsencrypt/live/your-domain.com/privkey.pem
sudo chown -R root:root /etc/letsencrypt/live/
```

### Custom PHP Settings

Edit `/etc/php/8.4/fpm/php.ini`:

```ini
upload_max_filesize = 100M
post_max_size = 100M
max_execution_time = 300
```

Restart PHP-FPM:
```bash
sudo systemctl restart php8.4-fpm
```

## Uninstalling

To uninstall Pelican Panel or Wings:

1. Run the installer again
2. Select "Uninstall Panel" or "Uninstall Wings"
3. Confirm the action

Or manually:

```bash
# Uninstall Panel
sudo rm -rf /var/www/pelican
sudo rm /etc/nginx/sites-enabled/pelican.conf
sudo systemctl restart nginx

# Uninstall Wings
sudo systemctl disable --now wings
sudo rm /usr/local/bin/wings
sudo rm -rf /etc/pelican
```

## Security Recommendations

1. **Always use HTTPS** in production
2. **Keep systems updated**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

3. **Set strong database passwords**
4. **Use firewall** to restrict access:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

5. **Regular backups** of Panel and Wings data:
   ```bash
   sudo tar -czf panel-backup-$(date +%Y%m%d).tar.gz /var/www/pelican
   sudo tar -czf wings-backup-$(date +%Y%m%d).tar.gz /var/lib/pelican
   ```

6. **Monitor logs** for suspicious activity
7. **Keep SSH keys** secure and use key-based auth

## Support & Documentation

- **Official Docs**: https://pelican.dev/docs
- **Discord Community**: https://discord.gg/pelican
- **GitHub Issues**: https://github.com/pelican-dev/panel/issues
- **GitHub Discussions**: https://github.com/pelican-dev/panel/discussions

## Contributing

To contribute to this installer:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This installer is provided as-is. Pelican Panel is open-source under the appropriate license.

## Changelog

### v1.0 (Initial Release)
- ✅ Panel installation and configuration
- ✅ Wings installation
- ✅ Automatic dependency detection
- ✅ Multiple webserver support
- ✅ Automatic SSL certificate generation
- ✅ Modern TUI interface
- ✅ Keyboard and mouse support
- ✅ Real-time progress indicators

## FAQ

**Q: Can I use this installer on CentOS/Rocky Linux/Alma Linux?**
A: Currently only Ubuntu/Debian are fully supported. Others may work but aren't tested.

**Q: Do I need a domain for installation?**
A: For HTTPS (recommended), yes. For HTTP (dev only), you can use an IP address.

**Q: How long does installation take?**
A: Typically 5-10 minutes depending on internet speed and system performance.

**Q: Can I reinstall without losing data?**
A: Use the "Update/Reinstall" option in the menu. Your database and configs won't be touched.

**Q: What if installation fails?**
A: Check the logs at `/var/log/pelican-installer.log` and review the troubleshooting section.

**Q: Can I use the same server for Panel and Wings?**
A: Yes, but it's not recommended for production due to resource contention.

---

**Questions or issues?** Open an issue on GitHub or ask in the Discord community!

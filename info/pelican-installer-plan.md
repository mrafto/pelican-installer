# Pelican Panel Installer - Comprehensive Plan

## Project Overview

A Python-based text-based user interface (TUI) installer script for Pelican Panel that provides an intuitive, modern installation experience for users of all technical levels.

---

## Phase 1: User Selection Menu

### Main Menu Screen
```
╔════════════════════════════════════════════╗
║      Pelican Panel Installer v1.0          ║
║        Installation & Configuration        ║
╚════════════════════════════════════════════╝

Select what to install:

[1] Install Panel                              (new installation)
[2] Install Wings                              (game server manager)

  or

[1] Update/Reinstall Panel                     (existing installation detected)
[2] Uninstall Panel                            (remove all files)
[3] Update/Reinstall Wings                     (existing installation detected)
[4] Uninstall Wings                            (remove all files)

Navigation: [↑↓] Navigate | [1-4] Quick Select | [C] Cancel | [Enter] Select
```

### Detection Logic
- Check if `/var/www/pelican` exists → Panel is installed
- Check if `/usr/local/bin/wings` exists → Wings is installed
- Display appropriate options based on system state

### Uninstall Procedures
**Panel Uninstall:**
- Remove files: `sudo rm -rf /var/www/pelican`
- Remove webserver config (NGINX/Apache/Caddy)
- Remove queue worker service
- Optionally remove database

**Wings Uninstall:**
- Disable service: `systemctl disable --now wings`
- Remove service file: `sudo rm /etc/systemd/system/wings.service`
- Remove binary: `sudo rm /usr/local/bin/wings`
- Remove config: `sudo rm -rf /etc/pelican`
- Optionally remove server data: `sudo rm -rf /var/lib/pelican`

---

## Phase 2: Dependency Installation

### Dependency Detection & Installation

**Panel Dependencies:**
- PHP 8.4, 8.3, or 8.2 with extensions:
  - gd, mysql, mbstring, bcmath, xml, curl, zip, intl, sqlite3, fpm
- Webserver: Apache, NGINX, or Caddy (user selectable, default: NGINX)
- Database: MySQL 8.0+ or MariaDB 10.6+ (optional)
- Tools: curl, tar, unzip, composer

**Wings Dependencies:**
- Docker CE
- Linux kernel without `-grs-` or `-mod-std-` modifications

### Installation Screen

```
╔════════════════════════════════════════════╗
║      Installing Dependencies                ║
╚════════════════════════════════════════════╝

Checking system...

✓ Ubuntu 24.04 detected
✓ curl installed
- php8.4 NOT FOUND
- php8.4-gd NOT FOUND
- php8.4-mysql NOT FOUND
- nginx NOT FOUND

Installing required packages...

[████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 15%
Installing: php8.4

[████████████████░░░░░░░░░░░░░░░░░] 45%
Installing: php8.4-fpm

[████████████████████████████░░░░░░] 75%
Installing: nginx

[████████████████████████████████░░] 95%
Installing: composer

[████████████████████████████████████] 100%
All dependencies installed!

Webserver Configuration: Nginx (default)
Database: MySQL/MariaDB (optional)
PHP Version: 8.4

Press [Enter] to continue...

[C] Cancel
```

### Auto-Detection & Installation
- Run `apt list --installed` to check what's already installed
- Only install missing dependencies
- Show real-time installation progress
- Use `apt update && apt install -y [packages]`

---

## Phase 3: Webserver Selection

### Webserver Configuration Menu

```
╔════════════════════════════════════════════╗
║      Webserver Configuration                ║
╚════════════════════════════════════════════╝

Select your preferred webserver:

[1] ● Nginx                            (recommended, default)
    Fast, lightweight, high performance

[2] Apache                             (traditional, feature-rich)
    Widely supported, extensive modules

[3] Caddy                              (modern, auto-HTTPS ready)
    Simple configuration, automatic HTTPS

Navigation: [↑↓] Navigate | [1-3] Quick Select | [Enter] Select | [C] Cancel
```

### Selected Webserver Effect
- NGINX: Default, smallest footprint, best performance
- Apache: Traditional choice, good for complex configurations
- Caddy: Modern choice, simplest SSL setup

---

## Phase 4: HTTPS/HTTP Selection

### Protocol Selection Menu

```
╔════════════════════════════════════════════╗
║      Connection Protocol                    ║
╚════════════════════════════════════════════╝

Select connection protocol:

[1] HTTPS (SSL/TLS)                    [RECOMMENDED]
    Secure, encrypted connection
    Required for production use

[2] HTTP                               (development only)
    Unencrypted, faster setup
    Not recommended for production

Navigation: [↑↓] Navigate | [1-2] Quick Select | [Enter] Select | [C] Cancel
```

---

## Phase 5: Domain/IP Configuration

### HTTPS Path

```
╔════════════════════════════════════════════╗
║      Domain Configuration (HTTPS)           ║
╚════════════════════════════════════════════╝

Enter your domain or IP address:

[Domain Input Field]
Example: panel.example.com

Auto-create SSL Certificates?

[●] Yes (recommended - uses Certbot)    [SELECTED]
[ ] No (use existing certificates)

Description: Certbot will automatically generate and manage
free SSL certificates from Let's Encrypt. Renewal is automatic.

Navigation: [↑↓] Select | [Enter] Confirm | [C] Cancel
```

**If HTTPS + Certbot Selected:**
```
╔════════════════════════════════════════════╗
║      SSL Certificate Setup                  ║
╚════════════════════════════════════════════╝

Email for Let's Encrypt notifications:

[Email Input Field]
Example: admin@example.com

This email will be used for SSL certificate renewal notifications.
You'll receive emails if certificate renewal fails.

Navigation: [↑↓] Select | [Enter] Confirm | [C] Cancel
```

**Installation:**
```
╔════════════════════════════════════════════╗
║      Generating SSL Certificate             ║
╚════════════════════════════════════════════╝

Setting up Certbot...

[████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20%
Installing certbot for nginx

[████████████░░░░░░░░░░░░░░░░░░░░░░] 40%
Running Certbot validation

[████████████████████░░░░░░░░░░░░░░] 60%
Waiting for Let's Encrypt confirmation

[████████████████████████████░░░░░░] 80%
SSL certificate successfully created

[████████████████████████████████░░] 95%
Configuring webserver

[████████████████████████████████████] 100%
SSL Certificate Created Successfully!

Certificate: panel.example.com
Valid for: 90 days (auto-renews)
Issuer: Let's Encrypt

[✓] Certificate setup complete

Press [Enter] to continue...
[C] Cancel
```

**Certbot Installation by Webserver:**
- Nginx: `sudo apt install -y python3-certbot-nginx`
- Apache: `sudo apt install -y python3-certbot-apache`
- Caddy/Other: `sudo apt install -y certbot`

### HTTP Path

```
╔════════════════════════════════════════════╗
║      Address Configuration (HTTP)           ║
╚════════════════════════════════════════════╝

Choose your address:

[1] Enter Domain Name
    Example: panel.example.com

[2] Use Computer IP Address
    Current IP: 192.168.1.100

Navigation: [↑↓] Navigate | [1-2] Quick Select | [Enter] Select | [C] Cancel
```

---

## Phase 6: PHP Setup

### PHP Configuration

```
╔════════════════════════════════════════════╗
║      Setting Up PHP                         ║
╚════════════════════════════════════════════╝

Configuring PHP 8.4 FPM...

[████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20%
Loading PHP configuration

[████████████░░░░░░░░░░░░░░░░░░░░░░] 40%
Setting permissions

[████████████████████░░░░░░░░░░░░░░] 60%
Enabling extensions

[████████████████████████████░░░░░░] 80%
Starting PHP-FPM service

[████████████████████████████████░░] 95%
Verifying installation

[████████████████████████████████████] 100%
PHP Successfully Configured!

Extensions Enabled:
✓ gd
✓ mysql
✓ mbstring
✓ bcmath
✓ xml
✓ curl
✓ zip
✓ intl
✓ sqlite3
✓ fpm

Press [Enter] to continue...
[C] Cancel
```

**PHP Setup Steps:**
- Create Panel directory: `sudo mkdir -p /var/www/pelican`
- Download panel files: `curl -L https://github.com/pelican-dev/panel/releases/latest/download/panel.tar.gz | sudo tar -xzv`
- Install Composer
- Install PHP dependencies
- Set permissions: `sudo chmod -R 755 storage/* bootstrap/cache/`
- Set ownership based on webserver

---

## Phase 7: Wings Setup (if selected)

### Docker Installation

```
╔════════════════════════════════════════════╗
║      Setting Up Wings & Docker              ║
╚════════════════════════════════════════════╝

Initializing Docker installation...

[████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 15%
Downloading Docker installation script

[████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 30%
Verifying kernel compatibility

[████████████░░░░░░░░░░░░░░░░░░░░░░] 45%
Installing Docker Engine

[████████████████░░░░░░░░░░░░░░░░░░] 60%
Starting Docker service

[████████████████████░░░░░░░░░░░░░░] 75%
Creating Wings directories

[████████████████████████░░░░░░░░░░] 85%
Downloading Wings binary

[████████████████████████████░░░░░░] 95%
Verifying installation

[████████████████████████████████████] 100%
Docker & Wings Successfully Installed!

Docker Version: 27.0.1
Wings Binary: /usr/local/bin/wings
Configuration: /etc/pelican/config.yml

Next: Configure Wings through the Panel dashboard

Press [Enter] to continue...
[C] Cancel
```

**Docker Installation:**
```bash
curl -sSL https://get.docker.com/ | CHANNEL=stable sudo sh
```

**Wings Installation:**
```bash
sudo mkdir -p /etc/pelican /var/run/wings
sudo curl -L -o /usr/local/bin/wings "https://github.com/pelican-dev/wings/releases/latest/download/wings_linux_$(uname -m)"
sudo chmod u+x /usr/local/bin/wings
```

---

## Phase 8: Installation Summary

### Completion Screen

```
╔════════════════════════════════════════════╗
║   Installation Complete! ✓                  ║
╚════════════════════════════════════════════╝

Pelican Panel has been successfully installed and configured!

═══════════════════════════════════════════════

INSTALLATION SUMMARY

Component Status:
✓ Panel                                    Installed
✓ Dependencies                             Installed
✓ Webserver (Nginx)                        Configured
✓ PHP 8.4 with Extensions                  Configured
✓ SSL Certificate                          Created (panel.example.com)
✓ Database Permissions                     Set

Optionally Installed:
✓ Docker                                   Installed
✓ Wings                                    Installed (not configured yet)

═══════════════════════════════════════════════

IMPORTANT NEXT STEPS:

1. Access the Panel:
   https://panel.example.com/installer

2. Complete the web-based setup wizard
   - Set admin user credentials
   - Configure database
   - Set application settings

3. Configure Wings (if installed):
   - Create a Node in the panel dashboard
   - Copy the auto-generated configuration
   - Run: sudo wings

4. Keep your system updated:
   - sudo apt update && sudo apt upgrade

═══════════════════════════════════════════════

Additional Resources:
- Documentation: https://pelican.dev/docs
- Community: https://discord.gg/pelican
- Issues: https://github.com/pelican-dev/panel

═══════════════════════════════════════════════

[Enter] Exit | [View Logs] Show installation logs | [C] Cancel
```

---

## Technical Architecture

### Technology Stack
- **Language:** Python 3.9+
- **TUI Framework:** Rich (terminal UI library)
- **Installation Method:** curl-piped bash script
- **System Requirements:** Ubuntu 22.04+ (officially 24.04 recommended)

### Key Features
1. **Responsive UI:** Uses Rich library for modern, color-coded interface
2. **Keyboard & Mouse Support:** Full navigation with keyboard shortcuts and mouse clicks
3. **Progress Tracking:** Real-time installation progress with visual indicators
4. **Error Handling:** Graceful error messages with recovery options
5. **Logging:** Detailed installation logs for debugging
6. **Cancellation:** Cancel button always visible (press 'C')
7. **State Management:** Remembers user selections across phases

### File Structure
```
/var/www/pelican/              # Panel installation
/etc/pelican/                  # Wings configuration
/etc/nginx/sites-*/pelican.conf # Webserver config
/usr/local/bin/wings           # Wings binary
/var/lib/pelican/              # Server data
/var/log/pelican-installer.log # Installation logs
```

---

## Error Handling

### Common Issues & Recovery
1. **Insufficient Permissions:** Automatically use sudo where needed
2. **Port Conflicts:** Check ports 80/443 are available
3. **Network Issues:** Retry downloads up to 3 times
4. **Certbot Failure:** Offer manual SSL certificate setup
5. **Docker Installation Failure:** Provide manual installation instructions

### Rollback Strategy
- Save system state before installation
- Offer to rollback on critical failures
- Provide uninstall option for failed installations

---

## Security Considerations

1. **Sudo Usage:** Only request sudo when necessary
2. **Credential Handling:** Never log passwords or sensitive data
3. **File Permissions:** Set proper ownership for web server user
4. **SSL Enforcement:** Default to HTTPS, warn about HTTP
5. **Database Security:** Encourage strong passwords during setup
6. **Firewall:** Recommend firewall configuration

---

## Testing Checklist

- [ ] Fresh Ubuntu 24.04 system
- [ ] All UI screens render correctly
- [ ] Keyboard navigation works (arrows, numbers, C key)
- [ ] Mouse interaction works (clicking options)
- [ ] Progress bars animate smoothly
- [ ] Error messages are clear and helpful
- [ ] Cancel button stops installation gracefully
- [ ] Logs are written correctly
- [ ] Panel loads at domain/IP after installation
- [ ] Web installer accessible
- [ ] Wings can be configured through Panel
- [ ] Uninstall procedures work correctly

---

## Future Enhancements

1. Support for multiple OS (Debian, Rocky, Alma, CentOS)
2. MariaDB/MySQL configuration in TUI
3. Automatic firewall configuration (ufw, firewalld)
4. Health check dashboard
5. Multi-language support
6. Backup and restore functions
7. Update checking and installation
8. Remote node deployment wizard

---

## Installation Command

```bash
# Simple one-liner installation
curl -fsSL https://raw.githubusercontent.com/username/repo/main/install.sh | bash

# Or with custom options
curl -fsSL https://raw.githubusercontent.com/username/repo/main/install.sh | bash -s -- --no-docker --webserver apache
```

---

## References

- Pelican Documentation: https://pelican.dev/docs
- Panel Setup: https://pelican.dev/docs/panel/getting-started
- Webserver Config: https://pelican.dev/docs/panel/webserver-config
- SSL Setup: https://pelican.dev/docs/guides/ssl
- Docker Guide: https://pelican.dev/docs/guides/docker
- Uninstalling: https://pelican.dev/docs/guides/uninstalling

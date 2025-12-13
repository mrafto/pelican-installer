# Pelican Panel Installer

A modern, comprehensive text-based user interface (TUI) installer for **Pelican Panel** and **Wings** (game server manager). Built with Python and Textual for beautiful terminal interfaces.

## Features

✨ **Modern Multi-Screen TUI**
- Beautiful, color-coded interface with multiple installation phases
- Responsive keyboard and mouse navigation
- Real-time progress indicators
- Always-accessible Close button (press `c`)

🚀 **Complete Installation Flow**
- Main menu with detection of existing installations
- Webserver selection (Nginx/Apache/Caddy)
- Protocol selection (HTTP/HTTPS)
- Domain/IP configuration
- SSL certificate setup (Let's Encrypt)
- Dependency installation with progress tracking
- Installation summary screen

🛡️ **Smart Detection**
- Auto-detects existing Panel/Wings installations
- Shows Update/Reinstall options for existing components
- System information detection (OS, version, architecture)
- Port availability checking
- Sudo privilege verification

👥 **User-Friendly Navigation**
- Keyboard: `↑↓` arrows, `1-9` quick select, `Enter` confirm, `b` back, `c` close, `n` next
- Mouse: Click options, buttons, and input fields
- Context-aware hints on every screen
- Smooth navigation between screens

## Requirements

- **OS**: Ubuntu 22.04+ (24.04 recommended) or Debian 12+
- **Python**: 3.9 or later
- **Memory**: 2GB minimum (4GB+ recommended)
- **Disk Space**: 5GB minimum
- **Network**: Outbound access to package repositories and GitHub
- **Privileges**: Root or sudo access

## Quick Start

### Installation

**⚠️ IMPORTANT: This installer requires root privileges to install packages and configure system services.**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the installer with sudo
sudo python main.py
```

**Note**: The installer will:
- Install system packages (PHP, Nginx/Apache/Caddy, Docker)
- Configure webservers
- Set up SSL certificates
- Modify system files and permissions
- Create systemd services

## Project Structure

```
pelican-installer/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── lib/
    └── pelican_installer/
        ├── __init__.py
        ├── app.py             # Main application orchestration
        ├── styles.tcss        # Textual CSS styling
        ├── components/        # Reusable UI components
        │   ├── __init__.py
        │   └── menu.py        # InstallerMenu component
        ├── screens/           # Installation screens
        │   ├── __init__.py
        │   ├── menu.py        # Main menu with detection
        │   ├── webserver.py   # Webserver selection
        │   ├── protocol.py    # HTTP/HTTPS selection
        │   ├── domain.py      # Domain/IP configuration
        │   ├── ssl.py         # SSL certificate setup
        │   ├── install.py     # Dependency installation
        │   └── summary.py     # Installation complete
        └── utils/             # Utility modules
            ├── __init__.py
            ├── state.py       # Installation state management
            └── system.py      # System detection utilities
```

## Installation Flow

### 1. Main Menu
- Detects existing installations
- Shows Install/Update/Uninstall options
- Choose between Panel and Wings

### 2. Webserver Selection (Panel only)
- **Nginx** (recommended) - Fast, lightweight
- **Apache** - Traditional, feature-rich
- **Caddy** - Modern, auto-HTTPS

### 3. Protocol Selection (Panel only)
- **HTTPS** (recommended) - Secure, encrypted
- **HTTP** - Development only

### 4. Domain Configuration
- Enter domain name or IP address
- Validation for proper format

### 5. SSL Setup (HTTPS only)
- Let's Encrypt certificate generation
- Email for certificate notifications
- Automatic renewal setup

### 6. Dependency Installation
- Real-time progress bar
- Status updates for each phase:
  - System requirements check
  - Package list updates
  - Dependency installation
  - Service configuration
  - Permission setup
  - Finalization

### 7. Installation Summary
- Complete installation report
- Access information
- Next steps guide

## Keyboard Shortcuts

- `↑/↓` - Navigate menu options
- `1-9` - Quick select menu items
- `Enter` - Confirm selection / Submit input
- `b` - Go back to previous screen
- `n` - Proceed to next step
- `c` - Close/Exit application

## State Management

The installer maintains state across screens:
- Selected component (Panel/Wings)
- Webserver choice
- Protocol (HTTP/HTTPS)
- Domain/IP address
- SSL configuration
- Installation progress

## System Detection

The installer automatically detects:
- OS name and version
- System architecture
- Existing Panel installation (`/var/www/pelican`)
- Existing Wings installation (`/usr/local/bin/wings`)
- Available commands (curl, docker, etc.)
- Port availability (80, 443)
- Sudo privileges

## Styling

The TUI uses a consistent color scheme:
- **Background**: Dark gray with subtle hatch pattern
- **Card**: Centered panel with rounded borders
- **Highlighted options**: Teal background
- **Buttons**: Gray with focus states
- **Text**: White titles, blue-gray hints
- **Inputs**: Dark background with focus indicators

## Development

### Adding New Screens

1. Create screen class in `lib/pelican_installer/screens/`
2. Inherit from `Screen[str]`
3. Implement `compose()` for layout
4. Add navigation handlers (`@on` decorators)
5. Use `self.dismiss(result)` to return to app
6. Register in `screens/__init__.py`
7. Wire navigation in `app.py`

### Adding New Components

1. Create component in `lib/pelican_installer/components/`
2. Inherit from appropriate Textual widget
3. Add custom behavior and styling
4. Export from `components/__init__.py`

### Styling Guide

Edit `lib/pelican_installer/styles.tcss`:
- Use CSS-like syntax for Textual CSS
- Target by ID (`#card`) or class (`.summary-item`)
- Supported properties: colors, borders, padding, alignment, etc.
- See Textual docs for full CSS reference

## Customization

### Colors

Edit `styles.tcss` to change colors:
- Background: `background: #222222;`
- Borders: `border: round #777777;`
- Highlights: `background: #0f2e3a;`
- Text: `color: #e9f6ff;`

### Card Size

Adjust in `styles.tcss`:
```css
#card {
  width: 70;
  min-height: 20;
  max-height: 28;
}
```

### Progress Speed

Adjust timer interval in `install.py`:
```python
self.set_interval(1 / 10, self.advance_progress)  # 10 updates/sec
```

## Troubleshooting

### Import Errors
If you see "textual" import errors, ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Screen Rendering Issues
Try running in a modern terminal:
- macOS: iTerm2, Ghostty, Kitty, WezTerm
- Windows: Windows Terminal
- Linux: Most terminals support Textual

### Navigation Not Working
- Ensure focus is not on an input field (press `Esc`)
- Check keyboard shortcuts are not conflicting with terminal

## Testing

Run a full flow test:
```bash
python main.py
```

Navigate through all screens:
1. Select "Install Panel"
2. Choose webserver
3. Select HTTPS
4. Enter domain
5. Provide SSL email
6. Watch dependency installation
7. Review summary

## Future Enhancements

- [ ] Actual installation logic (currently placeholders)
- [ ] Support for more Linux distributions
- [ ] Database configuration screen
- [ ] Firewall configuration
- [ ] Health check dashboard
- [ ] Backup/restore functionality
- [ ] Multi-language support
- [ ] Remote deployment wizard

## Resources

- **Pelican Panel**: https://pelican.dev
- **Documentation**: https://pelican.dev/docs
- **Textual Framework**: https://textual.textualize.io
- **Discord Community**: https://discord.gg/pelican

## License

This installer is provided as-is for the Pelican Panel community.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

---

Built with ❤️ using [Textual](https://textual.textualize.io)

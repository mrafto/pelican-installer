#!/usr/bin/env python3
"""
Pelican Panel Installer
A modern, user-friendly TUI-based installer for Pelican Panel and Wings
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.text import Text
except ImportError:
    print("Installing required dependencies...")
    subprocess.run(["sudo", "pip3", "install", "rich"], check=True)
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.text import Text

console = Console()

# ============================================================================
# Constants & Enums
# ============================================================================

class InstallComponent(Enum):
    """Components that can be installed"""
    PANEL = "panel"
    WINGS = "wings"

class WebServer(Enum):
    """Supported webservers"""
    NGINX = "nginx"
    APACHE = "apache"
    CADDY = "caddy"

class Protocol(Enum):
    """Connection protocols"""
    HTTP = "http"
    HTTPS = "https"

# ============================================================================
# System Detection
# ============================================================================

class SystemDetector:
    """Detect system state and installed components"""
    
    @staticmethod
    def is_panel_installed() -> bool:
        """Check if Panel is already installed"""
        return Path("/var/www/pelican").exists()
    
    @staticmethod
    def is_wings_installed() -> bool:
        """Check if Wings is already installed"""
        return Path("/usr/local/bin/wings").exists()
    
    @staticmethod
    def is_package_installed(package: str) -> bool:
        """Check if a package is installed via apt"""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_ip_address() -> str:
        """Get the server's IP address"""
        try:
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split()[0]
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def check_kernel_compatibility() -> bool:
        """Check if kernel supports Docker"""
        try:
            result = subprocess.run(
                ["uname", "-r"],
                capture_output=True,
                text=True,
                check=True
            )
            kernel = result.stdout.strip()
            # Check for restricted kernels
            if "-grs-" in kernel or "-mod-std-" in kernel:
                return False
            return True
        except Exception:
            return True

# ============================================================================
# Installation Manager
# ============================================================================

class InstallationManager:
    """Manages the installation process"""
    
    def __init__(self):
        self.config: Dict = {
            "components": [],
            "webserver": WebServer.NGINX.value,
            "protocol": Protocol.HTTPS.value,
            "domain": "",
            "use_certbot": True,
            "certbot_email": "",
            "use_docker": True,
        }
        self.detector = SystemDetector()
    
    def run_command(self, cmd: List[str], sudo: bool = False, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command"""
        if sudo and os.geteuid() != 0:
            cmd = ["sudo"] + cmd
        
        return subprocess.run(
            cmd,
            check=check,
            capture_output=False,
            text=True
        )
    
    def show_welcome(self):
        """Display welcome screen"""
        console.clear()
        welcome_text = Text()
        welcome_text.append("Pelican Panel Installer v1.0\n", style="bold cyan")
        welcome_text.append("Installation & Configuration\n\n", style="cyan")
        
        panel = Panel(
            welcome_text,
            border_style="cyan",
            padding=(1, 2),
            expand=False
        )
        console.print(panel)
        console.print()
    
    def show_main_menu(self):
        """Display main menu and get user selection"""
        console.clear()
        self.show_welcome()
        
        panel_installed = self.detector.is_panel_installed()
        wings_installed = self.detector.is_wings_installed()
        
        options = []
        descriptions = []
        
        if not panel_installed:
            options.append("Install Panel")
            descriptions.append("Fresh Panel installation")
        else:
            options.append("Update/Reinstall Panel")
            descriptions.append("Update existing Panel")
            options.append("Uninstall Panel")
            descriptions.append("Remove Panel completely")
        
        if not wings_installed:
            options.append("Install Wings")
            descriptions.append("Game server manager")
        else:
            options.append("Update/Reinstall Wings")
            descriptions.append("Update existing Wings")
            options.append("Uninstall Wings")
            descriptions.append("Remove Wings completely")
        
        console.print("Select what to install:\n")
        
        for i, (option, desc) in enumerate(zip(options, descriptions), 1):
            console.print(f"[{i}] {option:<30} {desc}")
        
        console.print("\n[C] Cancel installation\n")
        
        choice = Prompt.ask(
            "Select option",
            choices=[str(i) for i in range(1, len(options) + 1)] + ["c", "C"],
            show_choices=False
        ).lower()
        
        if choice == "c":
            console.print("[red]Installation cancelled[/red]")
            sys.exit(0)
        
        return options[int(choice) - 1]
    
    def select_webserver(self) -> WebServer:
        """Select preferred webserver"""
        console.clear()
        self.show_welcome()
        
        console.print("Select your preferred webserver:\n")
        console.print("[1] Nginx (default)       Fast, lightweight, high performance")
        console.print("[2] Apache                Widely supported, extensive modules")
        console.print("[3] Caddy                 Modern, auto-HTTPS ready\n")
        console.print("[C] Cancel\n")
        
        choice = Prompt.ask(
            "Select webserver",
            choices=["1", "2", "3", "c", "C"],
            show_choices=False,
            default="1"
        ).lower()
        
        if choice == "c":
            console.print("[red]Installation cancelled[/red]")
            sys.exit(0)
        
        servers = {
            "1": WebServer.NGINX,
            "2": WebServer.APACHE,
            "3": WebServer.CADDY,
        }
        return servers[choice]
    
    def select_protocol(self) -> Protocol:
        """Select connection protocol"""
        console.clear()
        self.show_welcome()
        
        console.print("Select connection protocol:\n")
        console.print("[1] HTTPS (SSL/TLS)       [RECOMMENDED]")
        console.print("    Secure, encrypted connection")
        console.print("    Required for production\n")
        console.print("[2] HTTP                  (development only)")
        console.print("    Unencrypted, faster setup\n")
        console.print("[C] Cancel\n")
        
        choice = Prompt.ask(
            "Select protocol",
            choices=["1", "2", "c", "C"],
            show_choices=False,
            default="1"
        ).lower()
        
        if choice == "c":
            console.print("[red]Installation cancelled[/red]")
            sys.exit(0)
        
        return Protocol.HTTPS if choice == "1" else Protocol.HTTP
    
    def get_domain(self, protocol: Protocol) -> str:
        """Get domain or IP address"""
        console.clear()
        self.show_welcome()
        
        if protocol == Protocol.HTTPS:
            console.print("Domain Configuration (HTTPS)\n")
            console.print("Enter your domain name (not IP):")
            console.print("Example: panel.example.com\n")
            domain = Prompt.ask("Domain", default="panel.example.com")
            return domain
        else:
            console.print("Address Configuration (HTTP)\n")
            console.print("[1] Enter Domain Name")
            console.print("[2] Use Computer IP Address\n")
            
            current_ip = self.detector.get_ip_address()
            console.print(f"Current IP: {current_ip}\n")
            
            choice = Prompt.ask(
                "Select option",
                choices=["1", "2", "c", "C"],
                show_choices=False
            ).lower()
            
            if choice == "c":
                sys.exit(0)
            elif choice == "1":
                return Prompt.ask("Domain/IP")
            else:
                return current_ip
    
    def configure_ssl(self, webserver: WebServer, domain: str) -> tuple[bool, str]:
        """Configure SSL certificates"""
        console.clear()
        self.show_welcome()
        
        console.print(f"SSL Certificate Setup for {domain}\n")
        console.print("Automatically create SSL Certificates?\n")
        console.print("[1] Yes (recommended - uses Certbot)")
        console.print("[2] No (use existing certificates)\n")
        
        choice = Prompt.ask(
            "Select option",
            choices=["1", "2", "c", "C"],
            show_choices=False,
            default="1"
        ).lower()
        
        if choice == "c":
            sys.exit(0)
        
        if choice == "2":
            return False, ""
        
        # Get email for Certbot
        console.print("\nEmail for Let's Encrypt notifications:\n")
        email = Prompt.ask("Email", default="admin@example.com")
        
        return True, email
    
    def install_dependencies(self, webserver: WebServer, for_wings: bool = False):
        """Install system dependencies"""
        console.clear()
        self.show_welcome()
        
        packages = []
        
        if not for_wings:
            # Panel dependencies
            if not self.detector.is_package_installed("php8.4"):
                packages.extend(["php8.4", "php8.4-fpm", "php8.4-gd", "php8.4-mysql",
                               "php8.4-mbstring", "php8.4-bcmath", "php8.4-xml",
                               "php8.4-curl", "php8.4-zip", "php8.4-intl", "php8.4-sqlite3"])
            
            # Webserver
            if webserver == WebServer.NGINX and not self.detector.is_package_installed("nginx"):
                packages.append("nginx")
            elif webserver == WebServer.APACHE and not self.detector.is_package_installed("apache2"):
                packages.extend(["apache2", "libapache2-mod-php"])
            elif webserver == WebServer.CADDY and not self.detector.is_package_installed("caddy"):
                packages.append("caddy")
            
            # Other tools
            if not self.detector.is_package_installed("curl"):
                packages.append("curl")
            if not self.detector.is_package_installed("composer"):
                # Composer needs special handling
                pass
        
        if for_wings:
            # Wings dependencies
            if not self.detector.is_package_installed("docker.io"):
                packages.append("docker.io")
        
        if not packages:
            console.print("[green]All dependencies already installed![/green]")
            return
        
        console.print("Installing Dependencies\n")
        
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Installing packages...", total=100)
            
            # Update package list
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            progress.update(task, advance=20)
            
            # Install packages
            cmd = ["sudo", "apt", "install", "-y"] + packages
            subprocess.run(cmd, check=True, capture_output=True)
            progress.update(task, advance=70)
            
            progress.update(task, advance=10)
        
        console.print("[green]✓ Dependencies installed successfully![/green]\n")
    
    def install_certbot(self, webserver: WebServer):
        """Install Certbot for SSL certificates"""
        console.clear()
        self.show_welcome()
        
        packages = []
        
        if webserver == WebServer.NGINX:
            packages = ["python3-certbot-nginx"]
        elif webserver == WebServer.APACHE:
            packages = ["python3-certbot-apache"]
        else:
            packages = ["certbot"]
        
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Installing Certbot...", total=100)
            
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + packages,
                check=True,
                capture_output=True
            )
            progress.update(task, advance=100)
        
        console.print("[green]✓ Certbot installed successfully![/green]\n")
    
    def run_certbot(self, domain: str, email: str):
        """Run Certbot to generate SSL certificate"""
        console.clear()
        self.show_welcome()
        
        console.print(f"Generating SSL Certificate for {domain}\n")
        
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Running Certbot...", total=100)
            
            cmd = [
                "sudo", "certbot", "certonly", "--non-interactive",
                "--agree-tos", "-m", email,
                "-d", domain,
                "--webroot", "-w", "/var/www/pelican/public"
            ]
            
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True
            )
            
            progress.update(task, advance=100)
        
        if result.returncode == 0:
            console.print(f"[green]✓ SSL Certificate created successfully![/green]\n")
            console.print(f"Certificate: {domain}")
            console.print("Valid for: 90 days (auto-renews)\n")
            return True
        else:
            console.print(f"[yellow]⚠ Certbot completed with status: {result.returncode}[/yellow]\n")
            return False
    
    def install_panel(self):
        """Install Pelican Panel"""
        console.clear()
        self.show_welcome()
        
        console.print("Installing Pelican Panel\n")
        
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Installing Panel...", total=100)
            
            # Create directory
            subprocess.run(["sudo", "mkdir", "-p", "/var/www/pelican"], check=True, capture_output=True)
            progress.update(task, advance=20)
            
            # Download and extract
            cmd = "curl -L https://github.com/pelican-dev/panel/releases/latest/download/panel.tar.gz | sudo tar -xzv -C /var/www/pelican"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            progress.update(task, advance=40)
            
            # Install Composer dependencies
            cmd = "cd /var/www/pelican && sudo curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            progress.update(task, advance=20)
            
            # Install PHP dependencies
            os.chdir("/var/www/pelican")
            subprocess.run(["sudo", "composer", "install", "--no-dev", "--optimize-autoloader"], check=True, capture_output=True)
            progress.update(task, advance=15)
            
            # Set permissions
            subprocess.run(["sudo", "chmod", "-R", "755", "storage/", "bootstrap/cache/"], check=True, capture_output=True)
            progress.update(task, advance=5)
        
        console.print("[green]✓ Pelican Panel installed successfully![/green]\n")
    
    def install_wings(self):
        """Install Wings (game server manager)"""
        console.clear()
        self.show_welcome()
        
        # First check kernel compatibility
        if not self.detector.check_kernel_compatibility():
            console.print("[red]✗ Your kernel is not compatible with Docker![/red]")
            console.print("Please contact your hosting provider for a non-modified kernel.\n")
            return False
        
        console.print("Installing Wings & Docker\n")
        
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Installing Wings...", total=100)
            
            # Install Docker
            cmd = "curl -sSL https://get.docker.com/ | CHANNEL=stable sudo sh"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            progress.update(task, advance=40)
            
            # Create directories
            subprocess.run(["sudo", "mkdir", "-p", "/etc/pelican", "/var/run/wings"], check=True, capture_output=True)
            progress.update(task, advance=20)
            
            # Download Wings binary
            arch = "amd64" if subprocess.run(["uname", "-m"], capture_output=True, text=True).stdout.strip() == "x86_64" else "arm64"
            url = f"https://github.com/pelican-dev/wings/releases/latest/download/wings_linux_{arch}"
            subprocess.run(["sudo", "curl", "-L", "-o", "/usr/local/bin/wings", url], check=True, capture_output=True)
            progress.update(task, advance=30)
            
            # Make executable
            subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/wings"], check=True, capture_output=True)
            progress.update(task, advance=10)
        
        console.print("[green]✓ Wings installed successfully![/green]\n")
        console.print("Next: Create a Node in the Panel dashboard to configure Wings.\n")
        return True
    
    def show_summary(self, config: Dict):
        """Show installation summary"""
        console.clear()
        self.show_welcome()
        
        console.print("[green bold]Installation Complete! ✓[/green bold]\n")
        console.print("Pelican Panel has been successfully installed and configured!\n")
        
        # Summary table
        table = Table(show_header=False, box=None)
        table.add_column(style="cyan")
        table.add_column()
        
        table.add_row("Panel", "[green]✓ Installed[/green]")
        table.add_row("Dependencies", "[green]✓ Installed[/green]")
        table.add_row("Webserver", f"[green]✓ {config['webserver'].upper()}[/green]")
        table.add_row("Protocol", f"[green]✓ {config['protocol'].upper()}[/green]")
        table.add_row("Domain", f"[green]✓ {config['domain']}[/green]")
        table.add_row("SSL Certificate", "[green]✓ Configured[/green]" if config.get('use_certbot') else "[yellow]⚠ Pending[/yellow]")
        
        console.print(table)
        console.print()
        
        console.print("[bold]Important Next Steps:[/bold]\n")
        console.print(f"1. Access the Panel: https://{config['domain']}/installer")
        console.print("2. Complete the web-based setup wizard")
        console.print("3. Set admin user credentials")
        console.print("4. Configure database connection\n")
        
        if "wings" in config['components']:
            console.print("[bold]Wings Configuration:[/bold]\n")
            console.print("1. Create a Node in the panel dashboard")
            console.print("2. Copy the auto-generated configuration")
            console.print("3. Run: sudo wings\n")
        
        console.print("[bold]Additional Resources:[/bold]\n")
        console.print("Documentation: https://pelican.dev/docs")
        console.print("Community: https://discord.gg/pelican")
        console.print("Issues: https://github.com/pelican-dev/panel\n")
        
        Prompt.ask("Press [Enter] to exit", default="")
    
    def run(self):
        """Main installation flow"""
        try:
            self.show_welcome()
            
            # Main menu
            selection = self.show_main_menu()
            
            if "Panel" in selection:
                if "Uninstall" in selection:
                    console.print("[red]Panel uninstall not yet implemented[/red]")
                    return
                
                # Install/Update Panel
                self.config['components'].append("panel")
                self.config['webserver'] = self.select_webserver().value
                self.config['protocol'] = self.select_protocol().value
                self.config['domain'] = self.get_domain(Protocol(self.config['protocol']))
                
                # Install dependencies
                self.install_dependencies(WebServer(self.config['webserver']))
                
                # SSL configuration
                if self.config['protocol'] == "https":
                    self.install_certbot(WebServer(self.config['webserver']))
                    use_certbot, email = self.configure_ssl(WebServer(self.config['webserver']), self.config['domain'])
                    if use_certbot:
                        self.config['use_certbot'] = True
                        self.config['certbot_email'] = email
                        self.run_certbot(self.config['domain'], email)
                
                # Install Panel
                self.install_panel()
            
            elif "Wings" in selection:
                if "Uninstall" in selection:
                    console.print("[red]Wings uninstall not yet implemented[/red]")
                    return
                
                # Install/Update Wings
                self.config['components'].append("wings")
                self.install_dependencies(WebServer.NGINX, for_wings=True)
                if self.install_wings():
                    pass
            
            # Show summary
            if self.config['components']:
                self.show_summary(self.config)
            
        except KeyboardInterrupt:
            console.print("\n[red]Installation cancelled by user[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error during installation: {e}[/red]")
            import traceback
            traceback.print_exc()
            sys.exit(1)

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    # Check if running as root or with sudo
    if os.geteuid() != 0:
        console.print("[yellow]Warning: This installer requires sudo access[/yellow]")
        # Script will use sudo for individual commands
    
    manager = InstallationManager()
    manager.run()

if __name__ == "__main__":
    main()

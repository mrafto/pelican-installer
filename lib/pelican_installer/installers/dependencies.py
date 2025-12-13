"""Dependency installation for Panel and Wings."""

from __future__ import annotations

from pelican_installer.installers.base import BaseInstaller
from pelican_installer.utils.state import InstallState


class DependencyInstaller(BaseInstaller):
    """Install system dependencies for Panel or Wings."""

    PHP_VERSION = "8.3"  # Can be 8.2, 8.3, or 8.4
    PHP_EXTENSIONS = [
        "fpm",
        "gd",
        "mysql",
        "mbstring",
        "bcmath",
        "xml",
        "curl",
        "zip",
        "intl",
        "sqlite3",
    ]

    def install(self, state: InstallState) -> None:
        """
        Install all required dependencies.

        Args:
            state: Installation state with configuration
        """
        if state.component == "panel":
            self._install_panel_dependencies(state)
        elif state.component == "wings":
            self._install_wings_dependencies()

    def _install_panel_dependencies(self, state: InstallState) -> None:
        """Install Panel dependencies."""
        self.update_progress(5, "Checking system requirements...")

        # Update package lists
        self.update_progress(10, "Updating package lists...")
        self.run_command(["apt-get", "update"], use_sudo=True)

        # Install PHP and extensions
        self.update_progress(25, f"Installing PHP {self.PHP_VERSION}...")
        php_packages = [f"php{self.PHP_VERSION}"]
        php_packages.extend([f"php{self.PHP_VERSION}-{ext}" for ext in self.PHP_EXTENSIONS])

        packages_to_install = []
        for pkg in php_packages:
            if not self.check_package_installed(pkg):
                packages_to_install.append(pkg)

        if packages_to_install:
            self.run_command(
                ["apt-get", "install", "-y"] + packages_to_install,
                use_sudo=True,
            )

        # Install webserver
        self.update_progress(50, f"Installing {state.webserver}...")
        self._install_webserver(state.webserver)

        # Install other tools
        self.update_progress(70, "Installing additional tools...")
        tools = ["curl", "tar", "unzip", "git"]
        tools_to_install = [t for t in tools if not self.check_command_exists(t)]
        if tools_to_install:
            self.run_command(
                ["apt-get", "install", "-y"] + tools_to_install,
                use_sudo=True,
            )

        # Install Composer
        self.update_progress(80, "Installing Composer...")
        if not self.check_command_exists("composer"):
            self._install_composer()

        # Install Certbot if HTTPS
        if state.protocol == "https":
            self.update_progress(90, "Installing Certbot...")
            self._install_certbot(state.webserver)

        self.update_progress(100, "Dependencies installed successfully!")

    def _install_wings_dependencies(self) -> None:
        """Install Wings dependencies (Docker)."""
        self.update_progress(10, "Checking system requirements...")

        # Check kernel compatibility
        result = self.run_command(["uname", "-r"], capture=True)
        kernel = result.stdout.strip()
        if "-grs-" in kernel or "-mod-std-" in kernel:
            raise RuntimeError(
                "Kernel not compatible with Docker. Contact your hosting provider."
            )

        # Update package lists
        self.update_progress(20, "Updating package lists...")
        self.run_command(["apt-get", "update"], use_sudo=True)

        # Install Docker
        self.update_progress(40, "Installing Docker...")
        if not self.check_command_exists("docker"):
            self._install_docker()

        self.update_progress(100, "Docker installed successfully!")

    def _install_webserver(self, webserver: str) -> None:
        """Install the selected webserver."""
        if webserver == "nginx":
            if not self.check_package_installed("nginx"):
                self.run_command(["apt-get", "install", "-y", "nginx"], use_sudo=True)
        elif webserver == "apache":
            packages = ["apache2", f"libapache2-mod-php{self.PHP_VERSION}"]
            to_install = [p for p in packages if not self.check_package_installed(p)]
            if to_install:
                self.run_command(["apt-get", "install", "-y"] + to_install, use_sudo=True)
                # Enable required Apache modules
                self.run_command(["a2enmod", "rewrite"], use_sudo=True, check=False)
                self.run_command(["a2enmod", "ssl"], use_sudo=True, check=False)
        elif webserver == "caddy":
            if not self.check_package_installed("caddy"):
                # Caddy requires special installation
                self.run_command(
                    ["apt-get", "install", "-y", "debian-keyring", "debian-archive-keyring", "apt-transport-https"],
                    use_sudo=True,
                )
                self.run_command(
                    [
                        "bash",
                        "-c",
                        "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg",
                    ],
                    shell=False,
                    use_sudo=False,
                )
                self.run_command(
                    [
                        "bash",
                        "-c",
                        'curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt" | sudo tee /etc/apt/sources.list.d/caddy-stable.list',
                    ],
                    shell=False,
                    use_sudo=False,
                )
                self.run_command(["apt-get", "update"], use_sudo=True)
                self.run_command(["apt-get", "install", "-y", "caddy"], use_sudo=True)

    def _install_composer(self) -> None:
        """Install Composer globally."""
        # Download installer
        self.run_command(
            [
                "curl",
                "-sS",
                "https://getcomposer.org/installer",
                "-o",
                "/tmp/composer-setup.php",
            ],
        )

        # Install
        self.run_command(
            [
                "php",
                "/tmp/composer-setup.php",
                "--install-dir=/usr/local/bin",
                "--filename=composer",
            ],
            use_sudo=True,
        )

        # Cleanup
        self.run_command(["rm", "/tmp/composer-setup.php"])

    def _install_certbot(self, webserver: str) -> None:
        """Install Certbot for SSL certificates."""
        if webserver == "nginx":
            package = "python3-certbot-nginx"
        elif webserver == "apache":
            package = "python3-certbot-apache"
        else:
            package = "certbot"

        if not self.check_package_installed(package):
            self.run_command(["apt-get", "install", "-y", package], use_sudo=True)

    def _install_docker(self) -> None:
        """Install Docker using the official installation script."""
        # Download and run Docker installation script
        cmd = "curl -fsSL https://get.docker.com | sh"
        self.run_command(cmd, use_sudo=True, shell=True)

        # Start and enable Docker service
        self.run_command(["systemctl", "enable", "docker"], use_sudo=True, check=False)
        self.run_command(["systemctl", "start", "docker"], use_sudo=True, check=False)


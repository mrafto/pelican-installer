"""Pelican Panel installation."""

from __future__ import annotations

import os
from pathlib import Path

from pelican_installer.installers.base import BaseInstaller
from pelican_installer.utils.state import InstallState


class PanelInstaller(BaseInstaller):
    """Install Pelican Panel."""

    PANEL_DIR = Path("/var/www/pelican")
    GITHUB_RELEASE = "https://github.com/pelican-dev/panel/releases/latest/download/panel.tar.gz"

    def install(self, state: InstallState) -> None:
        """
        Install Pelican Panel.

        Args:
            state: Installation state with configuration
        """
        self.update_progress(5, "Preparing installation...")

        # Create panel directory
        self.update_progress(10, "Creating panel directory...")
        self._create_directory()

        # Download and extract panel files
        self.update_progress(20, "Downloading panel files...")
        self._download_panel()

        # Install PHP dependencies via Composer
        self.update_progress(50, "Installing PHP dependencies...")
        self._install_php_dependencies()

        # Configure webserver
        self.update_progress(70, "Configuring webserver...")
        self._configure_webserver(state)

        # Setup SSL if HTTPS
        if state.protocol == "https" and state.ssl_email:
            self.update_progress(85, "Setting up SSL certificate...")
            self._setup_ssl(state)

        # Set permissions
        self.update_progress(95, "Setting permissions...")
        self._set_permissions(state.webserver)

        self.update_progress(100, "Panel installed successfully!")

    def _create_directory(self) -> None:
        """Create panel directory."""
        self.run_command(["mkdir", "-p", str(self.PANEL_DIR)], use_sudo=True)

    def _download_panel(self) -> None:
        """Download and extract panel files."""
        cmd = f"curl -L {self.GITHUB_RELEASE} | tar -xz -C {self.PANEL_DIR}"
        self.run_command(cmd, use_sudo=True, shell=True)

    def _install_php_dependencies(self) -> None:
        """Install PHP dependencies via Composer."""
        # Change to panel directory and run composer
        original_dir = os.getcwd()
        try:
            os.chdir(self.PANEL_DIR)
            self.run_command(
                ["composer", "install", "--no-dev", "--optimize-autoloader"],
                use_sudo=True,
            )
        finally:
            os.chdir(original_dir)

    def _configure_webserver(self, state: InstallState) -> None:
        """Configure the webserver for Panel."""
        if state.webserver == "nginx":
            self._configure_nginx(state)
        elif state.webserver == "apache":
            self._configure_apache(state)
        elif state.webserver == "caddy":
            self._configure_caddy(state)

    def _configure_nginx(self, state: InstallState) -> None:
        """Configure Nginx for Panel."""
        config_path = "/etc/nginx/sites-available/pelican.conf"
        protocol = "https" if state.protocol == "https" else "http"
        port = 443 if protocol == "https" else 80
        php_version = "8.3"  # Should match DependencyInstaller.PHP_VERSION

        config = f"""server {{
    listen {port};
    {'listen [::]:' + str(port) + ';' if port == 80 else 'listen [::]:443 ssl http2;'}
    server_name {state.domain};
    root /var/www/pelican/public;
    index index.php;

    access_log /var/log/nginx/pelican.app-access.log;
    error_log  /var/log/nginx/pelican.app-error.log error;

    client_max_body_size 100M;
    client_body_timeout 120s;

    sendfile off;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \\.php$ {{
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_pass unix:/run/php/php{php_version}-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param PHP_VALUE "upload_max_filesize = 100M \\n post_max_size=100M";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_intercept_errors off;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_read_timeout 300;
        include /etc/nginx/fastcgi_params;
    }}

    location ~ /\\.ht {{
        deny all;
    }}
}}
"""

        # Write config file
        self.run_command(
            ["bash", "-c", f"echo '{config}' > {config_path}"],
            use_sudo=True,
            shell=False,
        )

        # Enable site
        self.run_command(
            ["ln", "-sf", config_path, "/etc/nginx/sites-enabled/pelican.conf"],
            use_sudo=True,
            check=False,
        )

        # Test and reload Nginx
        self.run_command(["nginx", "-t"], use_sudo=True)
        self.run_command(["systemctl", "reload", "nginx"], use_sudo=True)

    def _configure_apache(self, state: InstallState) -> None:
        """Configure Apache for Panel."""
        config_path = "/etc/apache2/sites-available/pelican.conf"
        protocol = "https" if state.protocol == "https" else "http"
        port = 443 if protocol == "https" else 80

        config = f"""<VirtualHost *:{port}>
    ServerName {state.domain}
    DocumentRoot "/var/www/pelican/public"

    AllowEncodedSlashes NoDecode

    <Directory "/var/www/pelican/public">
        Require all granted
        AllowOverride all
    </Directory>

    ErrorLog /var/log/apache2/pelican.app-error.log
    CustomLog /var/log/apache2/pelican.app-access.log combined
</VirtualHost>
"""

        # Write config file
        self.run_command(
            ["bash", "-c", f"echo '{config}' > {config_path}"],
            use_sudo=True,
            shell=False,
        )

        # Enable site and required modules
        self.run_command(["a2ensite", "pelican.conf"], use_sudo=True, check=False)
        self.run_command(["a2enmod", "rewrite"], use_sudo=True, check=False)

        # Reload Apache
        self.run_command(["systemctl", "reload", "apache2"], use_sudo=True)

    def _configure_caddy(self, state: InstallState) -> None:
        """Configure Caddy for Panel."""
        config_path = "/etc/caddy/Caddyfile"
        php_version = "8.3"

        config = f"""{state.domain} {{
    root * /var/www/pelican/public
    file_server

    php_fastcgi unix//run/php/php{php_version}-fpm.sock

    header {{
        -Server
        -X-Powered-By
        Referrer-Policy "same-origin"
        X-Frame-Options "deny"
        X-XSS-Protection "1; mode=block"
        X-Content-Type-Options "nosniff"
    }}
}}
"""

        # Write config file
        self.run_command(
            ["bash", "-c", f"echo '{config}' > {config_path}"],
            use_sudo=True,
            shell=False,
        )

        # Reload Caddy
        self.run_command(["systemctl", "reload", "caddy"], use_sudo=True)

    def _setup_ssl(self, state: InstallState) -> None:
        """Setup SSL certificate via Certbot."""
        if state.webserver == "nginx":
            # Certbot nginx plugin
            self.run_command(
                [
                    "certbot",
                    "--nginx",
                    "-d",
                    state.domain,
                    "--non-interactive",
                    "--agree-tos",
                    "-m",
                    state.ssl_email,
                ],
                use_sudo=True,
                check=False,  # Don't fail if cert already exists
            )
        elif state.webserver == "apache":
            # Certbot apache plugin
            self.run_command(
                [
                    "certbot",
                    "--apache",
                    "-d",
                    state.domain,
                    "--non-interactive",
                    "--agree-tos",
                    "-m",
                    state.ssl_email,
                ],
                use_sudo=True,
                check=False,
            )
        else:  # Caddy handles SSL automatically
            pass

    def _set_permissions(self, webserver: str) -> None:
        """Set proper file permissions."""
        # Determine web user
        if webserver in ["nginx", "caddy"]:
            web_user = "www-data"
        elif webserver == "apache":
            web_user = "www-data"
        else:
            web_user = "www-data"

        # Set ownership
        self.run_command(
            ["chown", "-R", f"{web_user}:{web_user}", str(self.PANEL_DIR)],
            use_sudo=True,
        )

        # Set permissions
        self.run_command(
            ["chmod", "-R", "755", f"{self.PANEL_DIR}/storage"],
            use_sudo=True,
            check=False,
        )
        self.run_command(
            ["chmod", "-R", "755", f"{self.PANEL_DIR}/bootstrap/cache"],
            use_sudo=True,
            check=False,
        )


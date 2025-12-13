"""Main Pelican Panel Installer application."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from pelican_installer.screens import (
    DomainScreen,
    InstallScreen,
    MenuScreen,
    ProtocolScreen,
    SSLScreen,
    SummaryScreen,
    WebserverScreen,
)
from pelican_installer.utils.state import InstallState
from pelican_installer.utils.system import SystemDetector


class PelicanInstallerApp(App[None]):
    """Pelican Panel Installer TUI application."""

    TITLE = "Pelican Panel Installer"
    CSS_PATH = str(Path(__file__).with_name("styles.tcss"))

    BINDINGS = [
        ("c", "request_close", "Close"),
        ("b", "go_back", "Back"),
        ("n", "next_action", "Next"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.state = InstallState()
        self.system_info = SystemDetector.detect()

    def on_mount(self) -> None:
        """Initialize the app and show the main menu."""
        # Populate system info in state
        self.state.os_name = self.system_info.os_name
        self.state.os_version = self.system_info.os_version
        self.state.panel_installed = self.system_info.panel_installed
        self.state.wings_installed = self.system_info.wings_installed

        # Show main menu
        self.push_screen(
            MenuScreen(
                self.state,
                self.system_info.panel_installed,
                self.system_info.wings_installed,
            ),
            self._handle_menu_result,
        )

    def _handle_menu_result(self, result: str) -> None:
        """Handle result from main menu."""
        if result == "webserver":
            # Panel installation: go to webserver selection
            self.push_screen(
                WebserverScreen(self.state),
                self._handle_webserver_result,
            )
        elif result == "dependencies":
            # Wings installation: skip to dependencies
            self.push_screen(
                InstallScreen(self.state),
                self._handle_install_result,
            )
        elif result == "uninstall_panel":
            self.notify("Panel uninstall (placeholder)", timeout=2)
            self._show_menu()
        elif result == "uninstall_wings":
            self.notify("Wings uninstall (placeholder)", timeout=2)
            self._show_menu()
        elif result == "back":
            self._show_menu()

    def _handle_webserver_result(self, result: str) -> None:
        """Handle result from webserver selection."""
        if result == "protocol":
            self.push_screen(
                ProtocolScreen(self.state),
                self._handle_protocol_result,
            )
        elif result == "back":
            self._show_menu()

    def _handle_protocol_result(self, result: str) -> None:
        """Handle result from protocol selection."""
        if result == "domain":
            self.push_screen(
                DomainScreen(self.state),
                self._handle_domain_result,
            )
        elif result == "back":
            self.push_screen(
                WebserverScreen(self.state),
                self._handle_webserver_result,
            )

    def _handle_domain_result(self, result: str) -> None:
        """Handle result from domain configuration."""
        if result == "ssl":
            # HTTPS selected, go to SSL setup
            self.push_screen(
                SSLScreen(self.state),
                self._handle_ssl_result,
            )
        elif result == "dependencies":
            # HTTP selected, skip to dependencies
            self.push_screen(
                InstallScreen(self.state),
                self._handle_install_result,
            )
        elif result == "back":
            self.push_screen(
                ProtocolScreen(self.state),
                self._handle_protocol_result,
            )

    def _handle_ssl_result(self, result: str) -> None:
        """Handle result from SSL setup."""
        if result == "dependencies":
            self.push_screen(
                InstallScreen(self.state),
                self._handle_install_result,
            )
        elif result == "back":
            self.push_screen(
                DomainScreen(self.state),
                self._handle_domain_result,
            )

    def _handle_install_result(self, result: str) -> None:
        """Handle result from installation screen."""
        if result == "summary":
            self.push_screen(
                SummaryScreen(self.state),
                self._handle_summary_result,
            )

    def _handle_summary_result(self, result: str) -> None:
        """Handle result from summary screen."""
        # Summary screen only exits, so this shouldn't be called
        pass

    def _show_menu(self) -> None:
        """Show the main menu screen."""
        self.push_screen(
            MenuScreen(
                self.state,
                self.system_info.panel_installed,
                self.system_info.wings_installed,
            ),
            self._handle_menu_result,
        )

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.exit()

    def action_go_back(self) -> None:
        """Global back action (b key)."""
        # Delegate to the current screen's back handler if it exists
        if hasattr(self.screen, "back_pressed"):
            self.screen.back_pressed()

    def action_next_action(self) -> None:
        """Global next action (n key)."""
        # Delegate to the current screen's next handler if it exists
        if hasattr(self.screen, "next_pressed"):
            self.screen.next_pressed()
        elif hasattr(self.screen, "_proceed_next"):
            self.screen._proceed_next()

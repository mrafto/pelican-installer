"""Webserver selection screen."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Static

from pelican_installer.components.menu import InstallerMenu
from pelican_installer.utils.state import InstallState


class WebserverScreen(Screen[str]):
    """Screen for selecting webserver (Nginx/Apache/Caddy)."""

    CSS = """
    WebserverScreen {
        align: center middle;
    }
    """

    def __init__(self, state: InstallState) -> None:
        super().__init__()
        self.state = state

    def compose(self) -> ComposeResult:
        with Container(id="root"):
            with Container(id="card"):
                yield Static("Webserver Configuration", id="title")
                yield Static("Select your preferred webserver:", id="subtitle")
                yield InstallerMenu(id="webserver-menu")
                yield Static(
                    "Use ↑/↓, 1-3, Enter or click to select",
                    id="hint",
                )
                with Container(id="footer"):
                    yield Button("Back (b)", id="back")
                    yield Button("Close (c)", id="close")

    def on_mount(self) -> None:
        """Set up webserver options."""
        menu = self.query_one("#webserver-menu", InstallerMenu)
        menu.clear_options()
        menu.add_options(
            [
                "1) Nginx (recommended)",
                "2) Apache",
                "3) Caddy",
            ]
        )
        menu.highlighted = 0

    @on(InstallerMenu.OptionSelected)
    def handle_selection(self, event: InstallerMenu.OptionSelected) -> None:
        """Handle webserver selection."""
        if event.option_index == 0:
            self.state.webserver = "nginx"
        elif event.option_index == 1:
            self.state.webserver = "apache"
        elif event.option_index == 2:
            self.state.webserver = "caddy"

        self.dismiss("protocol")

    @on(Button.Pressed, "#back")
    def back_pressed(self) -> None:
        """Go back to main menu."""
        self.dismiss("back")

    @on(Button.Pressed, "#close")
    def close_pressed(self) -> None:
        """Handle close button."""
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.app.exit()


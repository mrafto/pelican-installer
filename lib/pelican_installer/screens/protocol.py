"""Protocol selection screen (HTTP/HTTPS)."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Static

from pelican_installer.components.menu import InstallerMenu
from pelican_installer.utils.state import InstallState


class ProtocolScreen(Screen[str]):
    """Screen for selecting HTTP or HTTPS."""

    CSS = """
    ProtocolScreen {
        align: center middle;
    }
    """

    def __init__(self, state: InstallState) -> None:
        super().__init__()
        self.state = state

    def compose(self) -> ComposeResult:
        with Container(id="root"):
            with Container(id="card"):
                yield Static("Connection Protocol", id="title")
                yield Static("Select connection protocol:", id="subtitle")
                yield InstallerMenu(id="protocol-menu")
                yield Static(
                    "Use ↑/↓, 1-2, Enter or click to select",
                    id="hint",
                )
                with Container(id="footer"):
                    yield Button("Back (b)", id="back")
                    yield Button("Close (c)", id="close")

    def on_mount(self) -> None:
        """Set up protocol options."""
        menu = self.query_one("#protocol-menu", InstallerMenu)
        menu.clear_options()
        menu.add_options(
            [
                "1) HTTPS (SSL/TLS) [RECOMMENDED]",
                "2) HTTP (development only)",
            ]
        )
        menu.highlighted = 0

    @on(InstallerMenu.OptionSelected)
    def handle_selection(self, event: InstallerMenu.OptionSelected) -> None:
        """Handle protocol selection."""
        if event.option_index == 0:
            self.state.protocol = "https"
            self.state.use_ssl = True
        else:
            self.state.protocol = "http"
            self.state.use_ssl = False

        self.dismiss("domain")

    @on(Button.Pressed, "#back")
    def back_pressed(self) -> None:
        """Go back to webserver selection."""
        self.dismiss("back")

    @on(Button.Pressed, "#close")
    def close_pressed(self) -> None:
        """Handle close button."""
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.app.exit()


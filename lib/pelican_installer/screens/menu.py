"""Main menu screen with component selection."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Static

from pelican_installer.components.menu import InstallerMenu
from pelican_installer.utils.state import InstallState


class MenuScreen(Screen[str]):
    """Main menu for selecting installation component."""

    CSS = """
    MenuScreen {
        align: center middle;
    }
    """

    def __init__(
        self,
        state: InstallState,
        panel_installed: bool = False,
        wings_installed: bool = False,
    ) -> None:
        super().__init__()
        self.state = state
        self.panel_installed = panel_installed
        self.wings_installed = wings_installed

    def compose(self) -> ComposeResult:
        with Container(id="root"):
            with Container(id="card"):
                yield Static("Pelican Panel Installer", id="title")
                yield Static(
                    f"OS: {self.state.os_name} {self.state.os_version}",
                    id="system-info",
                )
                yield InstallerMenu(id="main-menu")
                yield Static(
                    "Use ↑/↓, 1/2, Enter or click to select. Close: (c)",
                    id="hint",
                )
                with Container(id="footer"):
                    yield Button("Close (c)", id="close")

    def on_mount(self) -> None:
        """Set up menu options based on system state."""
        menu = self.query_one("#main-menu", InstallerMenu)

        # Build options based on what's installed
        options = []

        if not self.panel_installed:
            options.append("1) Install Panel")
        else:
            options.append("1) Update/Reinstall Panel")
            options.append("2) Uninstall Panel")

        if not self.wings_installed:
            idx = len(options) + 1
            options.append(f"{idx}) Install Wings")
        else:
            idx = len(options) + 1
            options.append(f"{idx}) Update/Reinstall Wings")
            options.append(f"{idx+1}) Uninstall Wings")

        menu.clear_options()
        for opt in options:
            menu.add_option(opt)

        if options:
            menu.highlighted = 0

    @on(InstallerMenu.OptionSelected)
    def handle_selection(self, event: InstallerMenu.OptionSelected) -> None:
        """Handle menu selection."""
        menu = self.query_one("#main-menu", InstallerMenu)
        selected = menu.get_option_at_index(event.option_index)
        if selected:
            text = str(selected.prompt).lower()

            # Parse selection
            if "install panel" in text and "uninstall" not in text:
                self.state.component = "panel"
                self.dismiss("webserver")
            elif "install wings" in text and "uninstall" not in text:
                self.state.component = "wings"
                self.dismiss("dependencies")
            elif "uninstall panel" in text:
                self.dismiss("uninstall_panel")
            elif "uninstall wings" in text:
                self.dismiss("uninstall_wings")
            elif "update" in text or "reinstall" in text:
                if "panel" in text:
                    self.state.component = "panel"
                    self.dismiss("webserver")
                elif "wings" in text:
                    self.state.component = "wings"
                    self.dismiss("dependencies")

    @on(Button.Pressed, "#close")
    def close_pressed(self) -> None:
        """Handle close button."""
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.app.exit()


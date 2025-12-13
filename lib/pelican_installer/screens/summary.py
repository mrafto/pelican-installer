"""Installation summary/completion screen."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from pelican_installer.utils.state import InstallState


class SummaryScreen(Screen[str]):
    """Final screen showing installation summary."""

    CSS = """
    SummaryScreen {
        align: center middle;
    }

    #summary-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding: 1;
        border: solid #777777;
        background: #2a2a2a;
    }

    .summary-item {
        margin-bottom: 0;
        color: #e9f6ff;
    }

    .summary-label {
        color: #b7dbe8;
    }

    #next-steps {
        margin-top: 1;
        margin-bottom: 1;
        color: #b7dbe8;
    }
    """

    def __init__(self, state: InstallState) -> None:
        super().__init__()
        self.state = state

    def compose(self) -> ComposeResult:
        with Container(id="root"):
            with Container(id="card"):
                yield Static("Installation Complete! ✓", id="title")

                with Vertical(id="summary-container"):
                    yield Static("INSTALLATION SUMMARY", classes="summary-label")
                    yield Static("")

                    # Component
                    component_name = (
                        "Panel" if self.state.component == "panel" else "Wings"
                    )
                    yield Static(
                        f"✓ Component: {component_name}",
                        classes="summary-item",
                    )

                    # Webserver (if panel)
                    if self.state.component == "panel":
                        yield Static(
                            f"✓ Webserver: {self.state.webserver.capitalize()}",
                            classes="summary-item",
                        )
                        yield Static(
                            f"✓ Protocol: {self.state.protocol.upper()}",
                            classes="summary-item",
                        )
                        yield Static(
                            f"✓ Domain: {self.state.domain}",
                            classes="summary-item",
                        )

                        if self.state.use_ssl:
                            yield Static(
                                f"✓ SSL Certificate: {self.state.domain}",
                                classes="summary-item",
                            )

                    yield Static("")
                    yield Static(
                        "✓ Dependencies installed",
                        classes="summary-item",
                    )
                    yield Static(
                        f"✓ {component_name} configured",
                        classes="summary-item",
                    )

                if self.state.component == "panel":
                    access_url = f"{self.state.protocol}://{self.state.domain}/installer"
                    yield Static(
                        f"Access Panel: {access_url}",
                        id="next-steps",
                    )
                else:
                    yield Static(
                        "Configure Wings through Panel dashboard",
                        id="next-steps",
                    )

                yield Static(
                    "Installation complete! Press Exit to close.",
                    id="hint",
                )

                with Container(id="footer"):
                    yield Button("Exit", id="exit")

    @on(Button.Pressed, "#exit")
    def exit_pressed(self) -> None:
        """Exit the application."""
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.app.exit()


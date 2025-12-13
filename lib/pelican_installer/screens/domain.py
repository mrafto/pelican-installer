"""Domain/IP configuration screen."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from pelican_installer.utils.state import InstallState


class DomainScreen(Screen[str]):
    """Screen for entering domain or IP address."""

    CSS = """
    DomainScreen {
        align: center middle;
    }

    #domain-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #domain-input {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    #example-text {
        color: #999;
        margin-bottom: 1;
    }
    """

    def __init__(self, state: InstallState) -> None:
        super().__init__()
        self.state = state

    def compose(self) -> ComposeResult:
        with Container(id="root"):
            with Container(id="card"):
                yield Static("Domain Configuration", id="title")

                protocol_text = (
                    "HTTPS" if self.state.protocol == "https" else "HTTP"
                )
                yield Static(
                    f"Enter your domain or IP address ({protocol_text}):",
                    id="subtitle",
                )

                with Vertical(id="domain-container"):
                    yield Input(
                        placeholder="panel.example.com",
                        id="domain-input",
                    )
                    yield Static(
                        "Example: panel.example.com or 192.168.1.100",
                        id="example-text",
                    )

                yield Static(
                    "Type domain/IP and press Next (n)",
                    id="hint",
                )

                with Container(id="footer"):
                    yield Button("Back (b)", id="back")
                    yield Button("Close (c)", id="close")
                    yield Button("Next (n)", id="next", disabled=True)

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#domain-input", Input).focus()

    @on(Input.Changed, "#domain-input")
    def validate_input(self, event: Input.Changed) -> None:
        """Enable Next button when input is valid."""
        next_btn = self.query_one("#next", Button)
        # Simple validation: not empty and no spaces
        value = event.value.strip()
        next_btn.disabled = len(value) == 0 or " " in value

    @on(Input.Submitted, "#domain-input")
    def input_submitted(self) -> None:
        """Handle Enter key in input."""
        self._proceed_next()

    @on(Button.Pressed, "#next")
    def next_pressed(self) -> None:
        """Handle Next button."""
        self._proceed_next()

    def _proceed_next(self) -> None:
        """Validate and proceed to next screen."""
        domain_input = self.query_one("#domain-input", Input)
        domain = domain_input.value.strip()

        if domain and " " not in domain:
            self.state.domain = domain

            # If HTTPS, go to SSL setup; otherwise go to dependencies
            if self.state.protocol == "https":
                self.dismiss("ssl")
            else:
                self.dismiss("dependencies")

    @on(Button.Pressed, "#back")
    def back_pressed(self) -> None:
        """Go back to protocol selection."""
        self.dismiss("back")

    @on(Button.Pressed, "#close")
    def close_pressed(self) -> None:
        """Handle close button."""
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.app.exit()


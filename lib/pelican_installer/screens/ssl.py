"""SSL certificate setup screen."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from pelican_installer.utils.state import InstallState


class SSLScreen(Screen[str]):
    """Screen for SSL certificate configuration."""

    CSS = """
    SSLScreen {
        align: center middle;
    }

    #email-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #email-input {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    #ssl-info {
        color: #b7dbe8;
        margin-bottom: 1;
    }
    """

    def __init__(self, state: InstallState) -> None:
        super().__init__()
        self.state = state

    def compose(self) -> ComposeResult:
        with Container(id="root"):
            with Container(id="card"):
                yield Static("SSL Certificate Setup", id="title")
                yield Static(
                    "Let's Encrypt will generate free SSL certificates",
                    id="subtitle",
                )

                with Vertical(id="email-container"):
                    yield Static(
                        f"Domain: {self.state.domain}",
                        id="ssl-info",
                    )
                    yield Static("Email for certificate notifications:")
                    yield Input(
                        placeholder="admin@example.com",
                        id="email-input",
                    )

                yield Static(
                    "Enter email and press Next (n)",
                    id="hint",
                )

                with Container(id="footer"):
                    yield Button("Back (b)", id="back")
                    yield Button("Close (c)", id="close")
                    yield Button("Next (n)", id="next", disabled=True)

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#email-input", Input).focus()

    @on(Input.Changed, "#email-input")
    def validate_input(self, event: Input.Changed) -> None:
        """Enable Next button when email is valid."""
        next_btn = self.query_one("#next", Button)
        # Simple email validation
        value = event.value.strip()
        next_btn.disabled = "@" not in value or "." not in value

    @on(Input.Submitted, "#email-input")
    def input_submitted(self) -> None:
        """Handle Enter key in input."""
        self._proceed_next()

    @on(Button.Pressed, "#next")
    def next_pressed(self) -> None:
        """Handle Next button."""
        self._proceed_next()

    def _proceed_next(self) -> None:
        """Validate and proceed to dependencies."""
        email_input = self.query_one("#email-input", Input)
        email = email_input.value.strip()

        if "@" in email and "." in email:
            self.state.ssl_email = email
            self.dismiss("dependencies")

    @on(Button.Pressed, "#back")
    def back_pressed(self) -> None:
        """Go back to domain configuration."""
        self.dismiss("back")

    @on(Button.Pressed, "#close")
    def close_pressed(self) -> None:
        """Handle close button."""
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        self.app.exit()


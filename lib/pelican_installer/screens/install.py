"""Dependencies installation screen with progress indicator."""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, ProgressBar, Static
from textual.worker import Worker, WorkerState

from pelican_installer.installers import (
    DependencyInstaller,
    PanelInstaller,
    WingsInstaller,
)
from pelican_installer.utils.state import InstallState


class InstallScreen(Screen[str]):
    """Screen showing dependency installation progress."""

    CSS = """
    InstallScreen {
        align: center middle;
    }

    #progress-container {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    #progress-status {
        color: #b7dbe8;
        margin-top: 1;
    }

    #error-message {
        color: #ff6b6b;
        margin-top: 1;
    }
    """

    def __init__(self, state: InstallState) -> None:
        super().__init__()
        self.state = state
        self._worker: Worker | None = None

    def compose(self) -> ComposeResult:
        component_name = "Panel" if self.state.component == "panel" else "Wings"

        with Container(id="root"):
            with Container(id="card"):
                yield Static("Installing Dependencies", id="title")
                yield Static(f"Setting up {component_name}...", id="subtitle")

                with Container(id="progress-container"):
                    yield ProgressBar(total=100, id="progress")
                    yield Static("Initializing...", id="progress-status")
                    yield Static("", id="error-message")

                yield Static(
                    "Installation in progress. Please wait...",
                    id="hint",
                )

                with Container(id="footer"):
                    yield Button("Close (c)", id="close")
                    yield Button("Next (n)", id="next", disabled=True)

    def on_mount(self) -> None:
        """Start the real installation process."""
        self._worker = self.run_installation()

    @work(exclusive=True, thread=True)
    def run_installation(self) -> None:
        """Run the actual installation in a worker thread."""
        try:
            # Phase 1: Install dependencies
            self.call_from_thread(self.update_subtitle, "Installing Dependencies...")
            dep_installer = DependencyInstaller(progress_callback=self.update_progress_thread_safe)
            dep_installer.install(self.state)

            # Phase 2: Install Panel or Wings
            if self.state.component == "panel":
                self.call_from_thread(self.update_subtitle, "Installing Panel...")
                panel_installer = PanelInstaller(progress_callback=self.update_progress_thread_safe)
                panel_installer.install(self.state)
            elif self.state.component == "wings":
                self.call_from_thread(self.update_subtitle, "Installing Wings...")
                wings_installer = WingsInstaller(progress_callback=self.update_progress_thread_safe)
                wings_installer.install()

            # Mark as complete
            self.state.dependencies_installed = True
            self.state.installation_complete = True

            # Enable next button
            self.call_from_thread(self.enable_next_button)

        except Exception as e:
            error_msg = f"Installation failed: {str(e)}"
            self.call_from_thread(self.show_error, error_msg)

    def update_progress_thread_safe(self, progress: int, message: str) -> None:
        """Update progress from worker thread (thread-safe)."""
        self.call_from_thread(self.update_progress_ui, progress, message)

    def update_progress_ui(self, progress: int, message: str) -> None:
        """Update the progress bar and status message."""
        progress_bar = self.query_one("#progress", ProgressBar)
        status = self.query_one("#progress-status", Static)

        progress_bar.update(progress=progress)
        status.update(message)

    def update_subtitle(self, text: str) -> None:
        """Update the subtitle text."""
        subtitle = self.query_one("#subtitle", Static)
        subtitle.update(text)

    def enable_next_button(self) -> None:
        """Enable and focus the Next button."""
        next_btn = self.query_one("#next", Button)
        next_btn.disabled = False
        next_btn.focus()

        status = self.query_one("#progress-status", Static)
        status.update("Installation complete!")

    def show_error(self, error_message: str) -> None:
        """Show an error message."""
        error_label = self.query_one("#error-message", Static)
        error_label.update(error_message)

        status = self.query_one("#progress-status", Static)
        status.update("Installation failed!")

        # Enable Close button focus
        close_btn = self.query_one("#close", Button)
        close_btn.focus()

    @on(Button.Pressed, "#next")
    def next_pressed(self) -> None:
        """Proceed to summary screen."""
        self.dismiss("summary")

    @on(Button.Pressed, "#close")
    def close_pressed(self) -> None:
        """Handle close button."""
        # Cancel worker if still running
        if self._worker and self._worker.state == WorkerState.RUNNING:
            self._worker.cancel()
        self.app.exit()

    def action_request_close(self) -> None:
        """Global close action (c key)."""
        if self._worker and self._worker.state == WorkerState.RUNNING:
            self._worker.cancel()
        self.app.exit()

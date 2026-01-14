"""
Format selector widget for choosing video or audio.
"""

import customtkinter as ctk
from typing import Callable, Optional

from src.domain.models import DownloadFormat


class FormatSelector(ctk.CTkFrame):
    """
    Format selector widget with segmented button.

    Provides toggle between Video and Audio formats.
    """

    def __init__(
        self,
        master,
        initial_format: DownloadFormat = DownloadFormat.VIDEO,
        on_change: Optional[Callable[[DownloadFormat], None]] = None,
        **kwargs
    ):
        """
        Initialize format selector widget.

        Args:
            master: Parent widget
            initial_format: Initial format selection
            on_change: Optional callback when format changes
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)
        self._format = initial_format
        self._on_change = on_change

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        # Label
        self._label = ctk.CTkLabel(
            self,
            text="Formato:",
            anchor="w",
        )
        self._label.pack(anchor="w", pady=(0, 5))

        # Segmented button
        self._selector = ctk.CTkSegmentedButton(
            self,
            values=["Video", "Audio"],
            command=self._on_select,
            height=40,
        )
        self._selector.pack(fill="x")

        # Set initial value
        initial_value = "Video" if self._format == DownloadFormat.VIDEO else "Audio"
        self._selector.set(initial_value)

    def _on_select(self, value: str):
        """Handle format selection."""
        self._format = DownloadFormat.VIDEO if value == "Video" else DownloadFormat.AUDIO
        if self._on_change:
            self._on_change(self._format)

    def get_format(self) -> DownloadFormat:
        """Get the currently selected format."""
        return self._format

    def set_format(self, format: DownloadFormat):
        """Set the format."""
        self._format = format
        value = "Video" if format == DownloadFormat.VIDEO else "Audio"
        self._selector.set(value)

    def set_enabled(self, enabled: bool):
        """Enable or disable the widget."""
        state = "normal" if enabled else "disabled"
        self._selector.configure(state=state)

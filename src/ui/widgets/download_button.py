"""
Download button widget that toggles between Download and Cancel.
"""

import customtkinter as ctk
from typing import Callable, Optional


class DownloadButton(ctk.CTkFrame):
    """
    Download/Cancel button widget.

    Toggles between:
    - "Descargar" state (ready to start download)
    - "Cancelar" state (download in progress)
    """

    def __init__(
        self,
        master,
        on_download: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize download button widget.

        Args:
            master: Parent widget
            on_download: Callback when download is clicked
            on_cancel: Callback when cancel is clicked
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)
        self._on_download = on_download
        self._on_cancel = on_cancel
        self._is_downloading = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        self._button = ctk.CTkButton(
            self,
            text="Descargar",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._on_click,
        )
        self._button.pack(fill="x")

    def _on_click(self):
        """Handle button click."""
        if self._is_downloading:
            if self._on_cancel:
                self._on_cancel()
        else:
            if self._on_download:
                self._on_download()

    def set_downloading(self, is_downloading: bool):
        """
        Set the button state.

        Args:
            is_downloading: True to show Cancel, False to show Download
        """
        self._is_downloading = is_downloading

        if is_downloading:
            self._button.configure(
                text="Cancelar",
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40"),
            )
        else:
            self._button.configure(
                text="Descargar",
                fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"],
            )

    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        state = "normal" if enabled else "disabled"
        self._button.configure(state=state)

    def is_downloading(self) -> bool:
        """Check if in downloading state."""
        return self._is_downloading

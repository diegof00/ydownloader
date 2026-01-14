"""
Progress bar widget with status display.
"""

import customtkinter as ctk
from typing import Optional

from src.domain.models import DownloadStatus


# Status display text mapping
STATUS_LABELS = {
    DownloadStatus.PENDING: "Listo para descargar",
    DownloadStatus.CONNECTING: "Conectando...",
    DownloadStatus.DOWNLOADING: "Descargando",
    DownloadStatus.PROCESSING: "Procesando...",
    DownloadStatus.COMPLETED: "¡Completado!",
    DownloadStatus.CANCELLED: "Cancelado",
    DownloadStatus.ERROR: "Error",
}


class ProgressBar(ctk.CTkFrame):
    """
    Progress bar widget with status label.

    Shows:
    - Progress bar (0-100%)
    - Status text
    - Content title (when available)
    """

    def __init__(self, master, **kwargs):
        """
        Initialize progress bar widget.

        Args:
            master: Parent widget
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)
        self._status = DownloadStatus.PENDING
        self._title: Optional[str] = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        # Title label
        self._title_label = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._title_label.pack(fill="x", pady=(0, 5))

        # Progress bar
        self._progress = ctk.CTkProgressBar(self, height=20)
        self._progress.pack(fill="x", pady=(0, 5))
        self._progress.set(0)

        # Status row
        self._status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._status_frame.pack(fill="x")

        # Status label (left)
        self._status_label = ctk.CTkLabel(
            self._status_frame,
            text=STATUS_LABELS[DownloadStatus.PENDING],
            anchor="w",
        )
        self._status_label.pack(side="left")

        # Percentage label (right)
        self._percent_label = ctk.CTkLabel(
            self._status_frame,
            text="",
            anchor="e",
        )
        self._percent_label.pack(side="right")

    def update_progress(
        self,
        percent: int,
        status: DownloadStatus,
        title: Optional[str] = None
    ):
        """
        Update the progress display.

        Args:
            percent: Progress percentage (0-100)
            status: Current download status
            title: Optional content title
        """
        self._status = status

        # Update progress bar
        self._progress.set(percent / 100)

        # Update status text
        status_text = STATUS_LABELS.get(status, str(status.value))
        self._status_label.configure(text=status_text)

        # Update percentage (only show during active download)
        if status in (DownloadStatus.DOWNLOADING, DownloadStatus.PROCESSING):
            self._percent_label.configure(text=f"{percent}%")
        elif status == DownloadStatus.COMPLETED:
            self._percent_label.configure(text="100%")
        else:
            self._percent_label.configure(text="")

        # Update title
        if title:
            self._title = title
            self._title_label.configure(text=title)

    def reset(self):
        """Reset to initial state."""
        self._status = DownloadStatus.PENDING
        self._title = None
        self._progress.set(0)
        self._status_label.configure(text=STATUS_LABELS[DownloadStatus.PENDING])
        self._percent_label.configure(text="")
        self._title_label.configure(text="")

    def show_error(self, message: str):
        """Show error state with message."""
        self._status = DownloadStatus.ERROR
        self._status_label.configure(text=f"Error: {message[:50]}...")
        self._percent_label.configure(text="")

    def get_status(self) -> DownloadStatus:
        """Get current status."""
        return self._status

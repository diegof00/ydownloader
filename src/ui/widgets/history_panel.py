"""
History panel widget showing recent downloads.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Callable, Optional, List
import subprocess
import platform

from src.domain.models import HistoryEntry


class HistoryPanel(ctk.CTkFrame):
    """
    Panel showing the last 5 downloads with clear functionality.
    """

    def __init__(
        self,
        master,
        on_clear: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize history panel widget.

        Args:
            master: Parent widget
            on_clear: Callback when clear button is clicked
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)
        self._on_clear = on_clear
        self._entries: List[HistoryEntry] = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="Historial reciente",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self._clear_btn = ctk.CTkButton(
            header,
            text="Limpiar",
            width=70,
            height=28,
            command=self._on_clear_click,
        )
        self._clear_btn.pack(side="right")

        # Scrollable list
        self._list_frame = ctk.CTkScrollableFrame(self, height=150)
        self._list_frame.pack(fill="both", expand=True)

        # Empty state label
        self._empty_label = ctk.CTkLabel(
            self._list_frame,
            text="No hay descargas recientes",
            text_color="gray",
        )
        self._empty_label.pack(pady=20)

    def _on_clear_click(self):
        """Handle clear button click."""
        if self._on_clear:
            self._on_clear()

    def update_entries(self, entries: List[HistoryEntry]):
        """
        Update the displayed entries.

        Args:
            entries: List of HistoryEntry objects to display
        """
        self._entries = entries

        # Clear existing items
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        if not entries:
            # Show empty state
            self._empty_label = ctk.CTkLabel(
                self._list_frame,
                text="No hay descargas recientes",
                text_color="gray",
            )
            self._empty_label.pack(pady=20)
            return

        # Create entry rows
        for entry in entries:
            self._create_entry_row(entry)

    def _create_entry_row(self, entry: HistoryEntry):
        """Create a row for a history entry."""
        row = ctk.CTkFrame(self._list_frame)
        row.pack(fill="x", pady=2)

        # Status indicator
        status_colors = {
            "completed": "#28a745",
            "cancelled": "#ffc107",
            "error": "#dc3545",
        }
        color = status_colors.get(entry.status, "gray")

        status_indicator = ctk.CTkLabel(
            row,
            text="●",
            text_color=color,
            width=20,
        )
        status_indicator.pack(side="left", padx=(5, 0))

        # Title
        title = entry.title[:40] + "..." if len(entry.title) > 40 else entry.title
        title_label = ctk.CTkLabel(
            row,
            text=title,
            anchor="w",
        )
        title_label.pack(side="left", fill="x", expand=True, padx=5)

        # Format badge
        format_text = "🎵" if entry.format == "audio" else "🎬"
        format_label = ctk.CTkLabel(
            row,
            text=format_text,
            width=30,
        )
        format_label.pack(side="right", padx=5)

        # Open folder button
        open_btn = ctk.CTkButton(
            row,
            text="📂",
            width=30,
            height=24,
            command=lambda p=entry.output_path: self._open_folder(p),
        )
        open_btn.pack(side="right", padx=2)

    def _open_folder(self, file_path: str):
        """Open the folder containing a file."""
        try:
            path = Path(file_path)
            folder = path.parent if path.exists() else Path.home()

            if platform.system() == "Windows":
                subprocess.run(["explorer", str(folder)])
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(folder)])
            else:
                subprocess.run(["xdg-open", str(folder)])
        except Exception:
            pass

    def add_entry(self, entry: HistoryEntry):
        """Add a new entry to the top of the list."""
        self._entries.insert(0, entry)
        if len(self._entries) > 5:
            self._entries = self._entries[:5]
        self.update_entries(self._entries)

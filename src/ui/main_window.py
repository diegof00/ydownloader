"""
Main application window.

Composes all widgets and manages the download workflow.
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
from typing import Optional
import queue
import threading

from src.domain.models import Download, DownloadFormat, DownloadStatus, HistoryEntry
from src.domain.download_service import DownloadService
from src.domain.validators import URLValidator
from src.infra.ytdlp_adapter import YtdlpAdapter
from src.infra.file_system import FileSystem
from src.infra.config_store import ConfigStore
from src.infra.history_store import HistoryStore

from src.ui.widgets.url_input import URLInput
from src.ui.widgets.folder_picker import FolderPicker
from src.ui.widgets.format_selector import FormatSelector
from src.ui.widgets.progress_bar import ProgressBar
from src.ui.widgets.download_button import DownloadButton
from src.ui.widgets.history_panel import HistoryPanel
from src.ui.dialogs.error_dialog import show_error
from src.ui.dialogs.about_dialog import AboutDialog, DisclaimerDialog


class MainWindow(ctk.CTk):
    """
    Main application window.

    Orchestrates all UI components and manages:
    - User input (URL, folder, format)
    - Download lifecycle
    - Progress updates (via queue polling)
    - History display
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Initialize services
        self._config_store = ConfigStore()
        self._history_store = HistoryStore()
        self._file_system = FileSystem()

        self._download_service = DownloadService(
            validator=URLValidator(),
            downloader=YtdlpAdapter(),
            file_system=self._file_system,
            history_store=self._history_store,
        )

        # Queue for thread-safe UI updates
        self._update_queue: queue.Queue = queue.Queue()
        self._current_download: Optional[Download] = None

        self._setup_window()
        self._setup_ui()
        self._load_initial_state()

        # Start queue polling
        self._poll_queue()

    def _setup_window(self):
        """Configure the main window."""
        self.title("YDownloader")
        self.geometry("600x700")
        self.minsize(500, 600)

        # Set appearance mode based on system
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Handle close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        """Set up the user interface."""
        # Main container
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="YDownloader",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

        about_btn = ctk.CTkButton(
            header,
            text="ℹ️",
            width=40,
            height=40,
            command=self._show_about,
        )
        about_btn.pack(side="right")

        # URL Input
        self._url_input = URLInput(main)
        self._url_input.pack(fill="x", pady=(0, 15))

        # Options row
        options = ctk.CTkFrame(main, fg_color="transparent")
        options.pack(fill="x", pady=(0, 15))
        options.grid_columnconfigure(0, weight=1)
        options.grid_columnconfigure(1, weight=1)

        # Folder picker
        initial_folder = self._config_store.get_last_output_folder()
        if not initial_folder:
            initial_folder = self._file_system.get_downloads_folder()

        self._folder_picker = FolderPicker(
            options,
            initial_folder=initial_folder,
            on_change=self._on_folder_change,
        )
        self._folder_picker.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Format selector
        initial_format = self._config_store.get_default_format()
        self._format_selector = FormatSelector(
            options,
            initial_format=initial_format,
        )
        self._format_selector.grid(row=0, column=1, sticky="ew")

        # Progress bar
        self._progress_bar = ProgressBar(main)
        self._progress_bar.pack(fill="x", pady=(0, 15))

        # Download button
        self._download_button = DownloadButton(
            main,
            on_download=self._start_download,
            on_cancel=self._cancel_download,
        )
        self._download_button.pack(fill="x", pady=(0, 20))

        # Separator
        ctk.CTkFrame(main, height=2, fg_color=("gray80", "gray30")).pack(
            fill="x", pady=(0, 20)
        )

        # History panel
        self._history_panel = HistoryPanel(
            main,
            on_clear=self._clear_history,
        )
        self._history_panel.pack(fill="both", expand=True)

    def _load_initial_state(self):
        """Load initial state from config and history."""
        # Load history
        entries = self._history_store.get_entries()
        self._history_panel.update_entries(entries)

        # Show disclaimer if first launch
        if self._config_store.should_show_disclaimer():
            self.after(100, self._show_disclaimer)

    def _show_disclaimer(self):
        """Show the first-launch disclaimer dialog."""
        DisclaimerDialog(
            self,
            on_accept=self._config_store.mark_disclaimer_shown,
        )

    def _show_about(self):
        """Show the about dialog."""
        AboutDialog(self)

    def _on_folder_change(self, folder: Path):
        """Handle folder selection change."""
        self._config_store.set_last_output_folder(folder)

    def _start_download(self):
        """Start a new download."""
        url = self._url_input.get_url()
        folder = self._folder_picker.get_folder()
        format = self._format_selector.get_format()

        if not url:
            show_error(self, "Por favor ingresa una URL.")
            return

        # Update UI to downloading state
        self._set_downloading_state(True)
        self._progress_bar.reset()

        # Start download
        download = self._download_service.start_download(
            url=url,
            output_folder=folder,
            format=format,
            on_progress=self._on_progress,
            on_complete=self._on_complete,
            on_error=self._on_error,
        )

        if download:
            self._current_download = download

    def _cancel_download(self):
        """Cancel the current download."""
        if self._current_download:
            self._download_service.cancel_download(self._current_download.id)

    def _on_progress(self, percent: int, status: DownloadStatus, title: Optional[str]):
        """Handle progress update from download thread."""
        # Queue update for main thread
        self._update_queue.put(("progress", percent, status, title))

    def _on_complete(self, download: Download):
        """Handle download completion."""
        self._update_queue.put(("complete", download))

    def _on_error(self, message: str):
        """Handle download error."""
        self._update_queue.put(("error", message))

    def _poll_queue(self):
        """Poll the update queue and apply updates to UI."""
        try:
            while True:
                update = self._update_queue.get_nowait()
                self._apply_update(update)
        except queue.Empty:
            pass

        # Schedule next poll
        self.after(100, self._poll_queue)

    def _apply_update(self, update):
        """Apply an update to the UI (called from main thread)."""
        update_type = update[0]

        if update_type == "progress":
            _, percent, status, title = update
            self._progress_bar.update_progress(percent, status, title)

        elif update_type == "complete":
            _, download = update
            self._set_downloading_state(False)

            if download.status == DownloadStatus.COMPLETED:
                self._progress_bar.update_progress(
                    100, DownloadStatus.COMPLETED, download.title
                )
                # Update history
                entries = self._history_store.get_entries()
                self._history_panel.update_entries(entries)

            elif download.status == DownloadStatus.CANCELLED:
                self._progress_bar.update_progress(
                    0, DownloadStatus.CANCELLED, None
                )

        elif update_type == "error":
            _, message = update
            self._set_downloading_state(False)
            self._progress_bar.show_error(message)
            show_error(self, message)

    def _set_downloading_state(self, is_downloading: bool):
        """Update UI for downloading/idle state."""
        self._download_button.set_downloading(is_downloading)
        self._url_input.set_enabled(not is_downloading)
        self._folder_picker.set_enabled(not is_downloading)
        self._format_selector.set_enabled(not is_downloading)

    def _clear_history(self):
        """Clear the download history."""
        self._history_store.clear()
        self._history_panel.update_entries([])

    def _on_close(self):
        """Handle window close event."""
        # Check if download is in progress
        if self._current_download and self._current_download.is_active:
            result = messagebox.askyesno(
                "Descarga en progreso",
                "Hay una descarga en progreso. ¿Deseas cancelarla y salir?",
            )
            if not result:
                return
            # Cancel the download
            self._cancel_download()

        self.destroy()

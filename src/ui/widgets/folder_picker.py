"""
Folder picker widget for selecting download destination.
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional


class FolderPicker(ctk.CTkFrame):
    """
    Folder picker widget with browse button.

    Provides:
    - Display of selected folder path
    - Browse button to open folder dialog
    - Path validation
    """

    def __init__(
        self,
        master,
        initial_folder: Optional[Path] = None,
        on_change: Optional[Callable[[Path], None]] = None,
        **kwargs
    ):
        """
        Initialize folder picker widget.

        Args:
            master: Parent widget
            initial_folder: Initial folder to display
            on_change: Optional callback when folder changes
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)
        self._folder = initial_folder or Path.home() / "Downloads"
        self._on_change = on_change

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        self.grid_columnconfigure(0, weight=1)

        # Label
        self._label = ctk.CTkLabel(
            self,
            text="Guardar en:",
            anchor="w",
        )
        self._label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Path display
        self._path_label = ctk.CTkLabel(
            self,
            text=self._truncate_path(self._folder),
            anchor="w",
            fg_color=("gray90", "gray20"),
            corner_radius=6,
            height=40,
        )
        self._path_label.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Browse button
        self._browse_btn = ctk.CTkButton(
            self,
            text="Cambiar",
            width=80,
            height=40,
            command=self._browse,
        )
        self._browse_btn.grid(row=1, column=1)

    def _browse(self):
        """Open folder selection dialog."""
        initial_dir = self._folder if self._folder.exists() else Path.home()

        folder = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Selecciona la carpeta de destino",
        )

        if folder:
            self.set_folder(Path(folder))

    def _truncate_path(self, path: Path, max_length: int = 40) -> str:
        """Truncate path for display."""
        path_str = str(path)
        if len(path_str) <= max_length:
            return f"  {path_str}"

        # Show beginning and end
        return f"  ...{path_str[-(max_length - 3):]}"

    def get_folder(self) -> Path:
        """Get the currently selected folder."""
        return self._folder

    def set_folder(self, folder: Path):
        """Set the folder and update display."""
        self._folder = folder
        self._path_label.configure(text=self._truncate_path(folder))
        if self._on_change:
            self._on_change(folder)

    def set_enabled(self, enabled: bool):
        """Enable or disable the widget."""
        state = "normal" if enabled else "disabled"
        self._browse_btn.configure(state=state)

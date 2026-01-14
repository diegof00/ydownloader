"""
URL input widget for pasting/typing URLs.
"""

import customtkinter as ctk
from typing import Callable, Optional


class URLInput(ctk.CTkFrame):
    """
    URL input widget with paste support.

    Provides a text entry field for URLs with:
    - Placeholder text
    - Paste button
    - Clear functionality
    """

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize URL input widget.

        Args:
            master: Parent widget
            on_change: Optional callback when URL changes
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)
        self._on_change = on_change

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        self.grid_columnconfigure(0, weight=1)

        # Label
        self._label = ctk.CTkLabel(
            self,
            text="URL del video o audio:",
            anchor="w",
        )
        self._label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Entry field
        self._entry = ctk.CTkEntry(
            self,
            placeholder_text="Pega aquí la URL (ej: https://youtube.com/watch?v=...)",
            height=40,
        )
        self._entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self._entry.bind("<KeyRelease>", self._on_key_release)

        # Paste button
        self._paste_btn = ctk.CTkButton(
            self,
            text="Pegar",
            width=80,
            height=40,
            command=self._paste_from_clipboard,
        )
        self._paste_btn.grid(row=1, column=1)

    def _on_key_release(self, event):
        """Handle key release events."""
        if self._on_change:
            self._on_change(self.get_url())

    def _paste_from_clipboard(self):
        """Paste URL from clipboard."""
        try:
            clipboard = self.clipboard_get()
            self._entry.delete(0, "end")
            self._entry.insert(0, clipboard.strip())
            if self._on_change:
                self._on_change(self.get_url())
        except Exception:
            pass  # Clipboard empty or unavailable

    def get_url(self) -> str:
        """Get the current URL."""
        return self._entry.get().strip()

    def set_url(self, url: str):
        """Set the URL."""
        self._entry.delete(0, "end")
        self._entry.insert(0, url)

    def clear(self):
        """Clear the URL field."""
        self._entry.delete(0, "end")
        if self._on_change:
            self._on_change("")

    def set_enabled(self, enabled: bool):
        """Enable or disable the widget."""
        state = "normal" if enabled else "disabled"
        self._entry.configure(state=state)
        self._paste_btn.configure(state=state)

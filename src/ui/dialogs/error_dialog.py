"""
Error dialog for displaying user-friendly error messages.
"""

import customtkinter as ctk
from typing import Callable, Optional


class ErrorDialog(ctk.CTkToplevel):
    """
    Modal dialog for displaying error messages.

    Shows a user-friendly error message with optional retry button.
    """

    def __init__(
        self,
        master,
        title: str = "Error",
        message: str = "",
        show_retry: bool = False,
        on_retry: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize error dialog.

        Args:
            master: Parent window
            title: Dialog title
            message: Error message to display
            show_retry: Whether to show retry button
            on_retry: Callback for retry button
            **kwargs: Additional CTkToplevel arguments
        """
        super().__init__(master, **kwargs)
        self._on_retry = on_retry
        self._result = None

        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)

        # Make modal
        self.transient(master)
        self.grab_set()

        self._setup_ui(message, show_retry)

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 400) // 2
        y = master.winfo_y() + (master.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self, message: str, show_retry: bool):
        """Set up the dialog UI."""
        # Icon and message
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Error icon
        icon_label = ctk.CTkLabel(
            content,
            text="⚠️",
            font=ctk.CTkFont(size=40),
        )
        icon_label.pack(pady=(0, 10))

        # Message
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            wraplength=350,
            justify="center",
        )
        msg_label.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")

        if show_retry:
            retry_btn = ctk.CTkButton(
                btn_frame,
                text="Reintentar",
                command=self._retry,
            )
            retry_btn.pack(side="left", expand=True, padx=5)

        close_btn = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            command=self._close,
            fg_color=("gray70", "gray30") if show_retry else None,
        )
        close_btn.pack(side="right" if show_retry else "left", expand=True, padx=5)

    def _retry(self):
        """Handle retry button click."""
        self._result = "retry"
        if self._on_retry:
            self._on_retry()
        self.destroy()

    def _close(self):
        """Handle close button click."""
        self._result = "close"
        self.destroy()

    def get_result(self) -> Optional[str]:
        """Get the dialog result after it's closed."""
        return self._result


def show_error(
    parent,
    message: str,
    title: str = "Error",
    show_retry: bool = False,
    on_retry: Optional[Callable[[], None]] = None,
) -> Optional[str]:
    """
    Show an error dialog and wait for user response.

    Args:
        parent: Parent window
        message: Error message to display
        title: Dialog title
        show_retry: Whether to show retry button
        on_retry: Callback for retry button

    Returns:
        "retry" if retry was clicked, "close" otherwise
    """
    dialog = ErrorDialog(
        parent,
        title=title,
        message=message,
        show_retry=show_retry,
        on_retry=on_retry,
    )
    dialog.wait_window()
    return dialog.get_result()

"""
About dialog with legal disclaimer.
"""

import customtkinter as ctk

from src import __version__, __app_name__


class AboutDialog(ctk.CTkToplevel):
    """
    About dialog showing app info and legal disclaimer.
    """

    def __init__(self, master, **kwargs):
        """
        Initialize about dialog.

        Args:
            master: Parent window
            **kwargs: Additional CTkToplevel arguments
        """
        super().__init__(master, **kwargs)

        self.title(f"Acerca de {__app_name__}")
        self.geometry("450x350")
        self.resizable(False, False)

        # Make modal
        self.transient(master)
        self.grab_set()

        self._setup_ui()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 350) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Set up the dialog UI."""
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # App name and version
        ctk.CTkLabel(
            content,
            text=__app_name__,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            content,
            text=f"Versión {__version__}",
            text_color="gray",
        ).pack(pady=(0, 20))

        # Disclaimer
        disclaimer_frame = ctk.CTkFrame(content)
        disclaimer_frame.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(
            disclaimer_frame,
            text="⚖️ Aviso Legal",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 5))

        disclaimer_text = (
            "Esta herramienta facilita la descarga de contenido multimedia. "
            "El usuario es responsable de tener los permisos necesarios "
            "para descargar y usar el contenido.\n\n"
            "Solo descarga contenido del cual tengas los derechos "
            "o que esté disponible bajo licencias que lo permitan."
        )

        ctk.CTkLabel(
            disclaimer_frame,
            text=disclaimer_text,
            wraplength=380,
            justify="center",
        ).pack(padx=15, pady=(0, 10))

        # Close button
        ctk.CTkButton(
            content,
            text="Entendido",
            command=self.destroy,
        ).pack()


class DisclaimerDialog(ctk.CTkToplevel):
    """
    First-launch disclaimer dialog.
    """

    def __init__(self, master, on_accept=None, **kwargs):
        """
        Initialize disclaimer dialog.

        Args:
            master: Parent window
            on_accept: Callback when user accepts
            **kwargs: Additional CTkToplevel arguments
        """
        super().__init__(master, **kwargs)
        self._on_accept = on_accept

        self.title("Bienvenido a YDownloader")
        self.geometry("500x400")
        self.resizable(False, False)

        # Make modal and prevent closing
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)

        self._setup_ui()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 500) // 2
        y = master.winfo_y() + (master.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Set up the dialog UI."""
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome message
        ctk.CTkLabel(
            content,
            text="👋 ¡Bienvenido!",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(0, 20))

        # Description
        desc_text = (
            "YDownloader te permite descargar videos y audio "
            "de forma fácil desde múltiples sitios web."
        )
        ctk.CTkLabel(
            content,
            text=desc_text,
            wraplength=420,
            justify="center",
        ).pack(pady=(0, 20))

        # Disclaimer box
        disclaimer_frame = ctk.CTkFrame(content)
        disclaimer_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            disclaimer_frame,
            text="⚠️ Importante",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffc107",
        ).pack(pady=(15, 10))

        disclaimer_text = (
            "Esta herramienta facilita la descarga de contenido multimedia. "
            "Al usar YDownloader, aceptas que:\n\n"
            "• Eres responsable de verificar que tienes permiso "
            "para descargar el contenido.\n"
            "• No usarás la herramienta para infringir derechos de autor.\n"
            "• Los desarrolladores no se hacen responsables del uso indebido."
        )

        ctk.CTkLabel(
            disclaimer_frame,
            text=disclaimer_text,
            wraplength=420,
            justify="left",
        ).pack(padx=20, pady=(0, 15))

        # Accept button
        ctk.CTkButton(
            content,
            text="Acepto y entiendo",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._accept,
        ).pack(fill="x")

    def _accept(self):
        """Handle accept button click."""
        if self._on_accept:
            self._on_accept()
        self.destroy()

    def _on_close_attempt(self):
        """Prevent closing without accepting."""
        pass  # Do nothing, user must click Accept

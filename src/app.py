"""
Application bootstrap and entry point.

Initializes the application and starts the main event loop.
"""

import sys
from pathlib import Path


def main():
    """
    Application entry point.

    Initializes all components and starts the GUI.
    """
    # Ensure we can import from src
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Import here to avoid circular imports
    from src.ui.main_window import MainWindow

    # Create and run the application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()

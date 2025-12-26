"""Main entry point for CAN bus monitoring application."""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from gui.main_window import MainWindow
from gui.splash_screen import SplashScreen
from config.app_config import APP_NAME, ICON_PATH_PNG, ICON_PATH_ICO, SHOW_SPLASH_SCREEN, SPLASH_DURATION


def main():
    """Main application entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("DRP1987")
    
    # Set application icon globally
    icon_path = None
    if sys.platform.startswith('win'):
        # Use ICO format on Windows
        icon_path = os.path.join(os.path.dirname(__file__), ICON_PATH_ICO)
    else:
        # Use PNG format on Linux/Mac
        icon_path = os.path.join(os.path.dirname(__file__), ICON_PATH_PNG)
    
    if icon_path and os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # Fallback to PNG if ICO doesn't exist
        icon_path_fallback = os.path.join(os.path.dirname(__file__), ICON_PATH_PNG)
        if os.path.exists(icon_path_fallback):
            app.setWindowIcon(QIcon(icon_path_fallback))

    try:
        # Show splash screen if enabled
        splash = None
        if SHOW_SPLASH_SCREEN:
            splash = SplashScreen()
            splash.show()
            # Process events to ensure splash is displayed immediately
            app.processEvents()
        
        # Create main window (in background)
        window = MainWindow()
        
        # Show main window after splash duration
        if SHOW_SPLASH_SCREEN and splash:
            # After splash duration, close splash and show main window
            QTimer.singleShot(SPLASH_DURATION, lambda: (splash.close(), window.show()))
        else:
            # No splash, show main window immediately
            window.show()

        # Run application event loop
        sys.exit(app.exec_())

    except Exception as e:
        # Show critical error dialog
        QMessageBox.critical(
            None,
            "Critical Error",
            f"An unexpected error occurred:\n{str(e)}\n\n"
            "Please ensure:\n"
            "- PCAN drivers are installed\n"
            "- configurations.json exists\n"
            "- All dependencies are installed"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

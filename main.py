"""Main entry point for CAN bus monitoring application."""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("CAN Bus Monitoring")
    app.setOrganizationName("DRP1987")

    try:
        # Create and show main window
        window = MainWindow()
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

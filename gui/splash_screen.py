"""Splash screen for application startup."""

import os
from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from config.app_config import APP_NAME, APP_VERSION, LOGO_PATH


class SplashScreen(QSplashScreen):
    """Splash screen displayed during application startup."""

    def __init__(self):
        """Initialize splash screen with logo and application info."""
        # Get logo path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(project_root, LOGO_PATH)
        
        # Load logo image or create fallback
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale logo if it's too small
            if pixmap.width() < 300 or pixmap.height() < 150:
                pixmap = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # Create a default pixmap with text if logo is missing
            pixmap = QPixmap(400, 300)
            pixmap.fill(Qt.white)
        
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        
        # Set window flags for frameless, centered splash
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.SplashScreen
        )
        
        # Add application name and version text
        self._add_text_overlay()
        
    def _add_text_overlay(self):
        """Add application name and version text overlay on splash screen."""
        # Display application name
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        
        # Show app name at bottom of splash screen
        message = f"{APP_NAME}\nVersion {APP_VERSION}\n\nLoading..."
        self.showMessage(
            message,
            Qt.AlignBottom | Qt.AlignHCenter,
            Qt.black
        )

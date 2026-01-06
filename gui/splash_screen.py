"""Splash screen for application startup."""

import os
import logging
from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont
from config.app_config import APP_NAME, APP_VERSION, LOGO_PATH, SPLASH_ANIMATION_SPEED, SPLASH_ANIMATION_ENABLED
from utils.resource_path import resource_path

# Configure logger for this module
logger = logging.getLogger(__name__)


class SplashScreen(QSplashScreen):
    """Splash screen displayed during application startup."""

    def __init__(self):
        """Initialize splash screen with logo and application info."""
        # Use resource_path for PyInstaller compatibility
        logo_path = resource_path(LOGO_PATH)
        
        # Load logo image or create fallback
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale logo if it's too small
            if pixmap.width() < 300 or pixmap.height() < 150:
                pixmap = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            logger.warning(f"Logo not found at {logo_path}")
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
        
        # Initialize loading animation
        self._dot_count = 0
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._update_loading_text)
        if SPLASH_ANIMATION_ENABLED:
            self._animation_timer.start(SPLASH_ANIMATION_SPEED)  # Update based on config
        
        # Add application name and version text
        self._add_text_overlay()
        
    def _format_loading_message(self):
        """Format the loading message with current dot count."""
        dots = "." * self._dot_count
        return f"{APP_NAME}\nVersion {APP_VERSION}\n\nLoading{dots}"
    
    def _add_text_overlay(self):
        """Add application name and version text overlay on splash screen."""
        # Display application name
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        
        # Show app name at bottom of splash screen - initial loading text
        self.showMessage(
            self._format_loading_message(),
            Qt.AlignBottom | Qt.AlignHCenter,
            Qt.black
        )
    
    def _update_loading_text(self):
        """Update the loading text with animated dots."""
        # Show message with current dot count
        self.showMessage(
            self._format_loading_message(),
            Qt.AlignBottom | Qt.AlignHCenter,
            Qt.black
        )
        # Cycle dot count: 0 -> 1 -> 2 -> 3 -> 0
        self._dot_count = (self._dot_count + 1) % 4
    
    def close(self):
        """Stop animation timer when closing splash screen."""
        if hasattr(self, '_animation_timer'):
            self._animation_timer.stop()
        super().close()

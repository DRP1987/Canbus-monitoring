"""Utility functions for GUI components."""

import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


def create_logo_widget(parent=None):
    """
    Create a QLabel widget displaying the company logo.
    
    Args:
        parent: Parent widget (optional)
        
    Returns:
        QLabel: Label widget containing the logo image, or None if logo not found
    """
    # Get the project root directory (parent of gui directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    logo_path = os.path.join(project_root, 'assets', 'logo.png')
    
    # Check if logo exists
    if not os.path.exists(logo_path):
        print(f"Warning: Logo file not found at {logo_path}")
        return None
    
    # Create label with logo
    logo_label = QLabel(parent)
    pixmap = QPixmap(logo_path)
    
    # Check if pixmap loaded successfully
    if pixmap.isNull():
        print(f"Warning: Failed to load logo from {logo_path}")
        return None
    
    # Set pixmap and configure label
    logo_label.setPixmap(pixmap)
    logo_label.setScaledContents(False)  # Keep original size
    logo_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
    
    return logo_label

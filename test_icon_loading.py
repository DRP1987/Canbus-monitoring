"""Test icon loading in PyQt5 application."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from config.app_config import APP_NAME, ICON_PATH_PNG, ICON_PATH_ICO


def test_icon_loading():
    """Test that icons can be loaded by PyQt5."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Test loading icons
    project_root_path = Path(__file__).parent
    
    # Test PNG icon
    icon_png_path = str(project_root_path / ICON_PATH_PNG)
    if os.path.exists(icon_png_path):
        icon_png = QIcon(icon_png_path)
        assert not icon_png.isNull(), "PNG icon failed to load"
        print(f"✓ PNG icon loaded successfully from {icon_png_path}")
        print(f"  Available sizes: {icon_png.availableSizes()}")
    else:
        print(f"✗ PNG icon file not found at {icon_png_path}")
        return False
    
    # Test ICO icon
    icon_ico_path = str(project_root_path / ICON_PATH_ICO)
    if os.path.exists(icon_ico_path):
        icon_ico = QIcon(icon_ico_path)
        assert not icon_ico.isNull(), "ICO icon failed to load"
        print(f"✓ ICO icon loaded successfully from {icon_ico_path}")
        print(f"  Available sizes: {icon_ico.availableSizes()}")
    else:
        print(f"✗ ICO icon file not found at {icon_ico_path}")
        return False
    
    # Test setting app icon
    app.setWindowIcon(icon_png)
    print(f"✓ Application icon set successfully")
    
    print(f"\n✓ All icon loading tests passed!")
    return True


if __name__ == '__main__':
    # Set up virtual display for headless testing (if available)
    try:
        import os
        if 'DISPLAY' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    except:
        pass
    
    success = test_icon_loading()
    sys.exit(0 if success else 1)

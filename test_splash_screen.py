"""Test splash screen functionality."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui.splash_screen import SplashScreen
from config.app_config import LOGO_PATH, APP_NAME, APP_VERSION


def test_splash_screen_creation():
    """Test that splash screen can be created."""
    app = QApplication(sys.argv)
    
    try:
        # Create splash screen
        splash = SplashScreen()
        assert splash is not None, "Splash screen creation failed"
        print(f"✓ Splash screen created successfully")
        
        # Check that splash has the correct properties
        assert splash.windowFlags() & 0x00000008, "Splash should stay on top"  # Qt.WindowStaysOnTopHint
        print(f"✓ Splash screen has correct window flags")
        
        # Show splash screen briefly
        splash.show()
        app.processEvents()
        print(f"✓ Splash screen displayed successfully")
        
        # Check logo path exists
        project_root_path = Path(__file__).parent
        logo_path = project_root_path / LOGO_PATH
        logo_exists = logo_path.exists()
        print(f"✓ Logo file {'exists' if logo_exists else 'missing (using fallback)'}: {logo_path}")
        
        # Close splash after brief display
        QTimer.singleShot(100, splash.close)
        QTimer.singleShot(200, app.quit)
        app.exec_()
        
        print(f"\n✓ All splash screen tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Splash screen test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_splash_screen_with_missing_logo():
    """Test that splash screen works even if logo is missing."""
    app = QApplication(sys.argv)
    
    try:
        # Temporarily modify LOGO_PATH to non-existent file
        from config import app_config
        original_path = app_config.LOGO_PATH
        app_config.LOGO_PATH = "assets/nonexistent_logo.png"
        
        # Create splash screen with missing logo
        splash = SplashScreen()
        assert splash is not None, "Splash screen should work with missing logo"
        print(f"✓ Splash screen created successfully with missing logo (fallback)")
        
        # Show splash screen briefly
        splash.show()
        app.processEvents()
        print(f"✓ Splash screen displayed successfully with fallback")
        
        # Restore original path
        app_config.LOGO_PATH = original_path
        
        # Close splash after brief display
        QTimer.singleShot(100, splash.close)
        QTimer.singleShot(200, app.quit)
        app.exec_()
        
        print(f"\n✓ Missing logo fallback test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Missing logo fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Set up virtual display for headless testing (if available)
    try:
        import os
        if 'DISPLAY' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    except:
        pass
    
    print("=" * 60)
    print("Testing Splash Screen Functionality")
    print("=" * 60)
    print()
    
    # Run tests
    test1_passed = test_splash_screen_creation()
    print("\n" + "-" * 60 + "\n")
    test2_passed = test_splash_screen_with_missing_logo()
    
    # Exit with appropriate code
    all_passed = test1_passed and test2_passed
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)

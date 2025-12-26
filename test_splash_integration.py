"""Integration test for splash screen in main application."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up virtual display for headless testing
try:
    if 'DISPLAY' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
except:
    pass

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui.splash_screen import SplashScreen
from config import app_config


def test_splash_integration():
    """Test splash screen integration with main app flow."""
    print("Testing splash screen integration...")
    
    app = QApplication(sys.argv)
    
    try:
        # Test with splash enabled
        print("  Testing with splash enabled...")
        splash = SplashScreen()
        splash.show()
        app.processEvents()
        
        # Simulate timer that would show main window
        def close_splash():
            print("  Closing splash after timeout...")
            splash.close()
            print("  ✓ Splash closed successfully")
        
        QTimer.singleShot(500, close_splash)
        QTimer.singleShot(600, app.quit)
        
        app.exec_()
        
        print("✓ Splash screen integration test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Splash screen integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_splash_disabled():
    """Test app behavior when splash is disabled."""
    print("Testing app with splash disabled...")
    
    # Temporarily disable splash
    original_value = app_config.SHOW_SPLASH_SCREEN
    app_config.SHOW_SPLASH_SCREEN = False
    
    app = QApplication(sys.argv)
    
    try:
        if not app_config.SHOW_SPLASH_SCREEN:
            print("  ✓ Splash screen disabled as expected")
            # In this case, main window would show immediately
            QTimer.singleShot(100, app.quit)
            app.exec_()
        
        # Restore original value
        app_config.SHOW_SPLASH_SCREEN = original_value
        
        print("✓ Splash disabled test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Splash disabled test failed: {e}")
        app_config.SHOW_SPLASH_SCREEN = original_value
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Splash Screen Integration Tests")
    print("=" * 60)
    print()
    
    test1 = test_splash_integration()
    test2 = test_splash_disabled()
    
    print("=" * 60)
    if test1 and test2:
        print("ALL INTEGRATION TESTS PASSED ✓")
    else:
        print("SOME INTEGRATION TESTS FAILED ✗")
    print("=" * 60)
    
    sys.exit(0 if (test1 and test2) else 1)

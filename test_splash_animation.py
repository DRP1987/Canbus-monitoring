"""Test splash screen animation functionality."""

import sys
import os
from pathlib import Path
import importlib

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from config import app_config


def test_animation_enabled():
    """Test that animation timer starts when enabled."""
    app = QApplication(sys.argv)
    
    try:
        # Ensure animation is enabled
        app_config.SPLASH_ANIMATION_ENABLED = True
        
        # Reload splash_screen module to pick up config changes
        if 'gui.splash_screen' in sys.modules:
            importlib.reload(sys.modules['gui.splash_screen'])
        from gui.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        assert splash is not None, "Splash screen creation failed"
        print(f"✓ Splash screen created with animation enabled")
        
        # Check that animation timer exists and is active
        assert hasattr(splash, '_animation_timer'), "Animation timer not initialized"
        assert splash._animation_timer.isActive(), "Animation timer should be active when enabled"
        print(f"✓ Animation timer is active")
        
        # Check initial dot count
        assert hasattr(splash, '_dot_count'), "Dot count not initialized"
        assert splash._dot_count == 0, "Dot count should start at 0"
        print(f"✓ Dot count initialized correctly")
        
        # Show splash screen
        splash.show()
        app.processEvents()
        
        # Close splash after brief display
        QTimer.singleShot(100, splash.close)
        QTimer.singleShot(200, app.quit)
        app.exec_()
        
        print(f"\n✓ Animation enabled test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Animation enabled test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_animation_disabled():
    """Test that animation timer doesn't start when disabled."""
    app = QApplication(sys.argv)
    
    try:
        # Disable animation
        app_config.SPLASH_ANIMATION_ENABLED = False
        
        # Reload splash_screen module to pick up config changes
        if 'gui.splash_screen' in sys.modules:
            importlib.reload(sys.modules['gui.splash_screen'])
        from gui.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        assert splash is not None, "Splash screen creation failed"
        print(f"✓ Splash screen created with animation disabled")
        
        # Check that animation timer exists but is not active
        assert hasattr(splash, '_animation_timer'), "Animation timer not initialized"
        assert not splash._animation_timer.isActive(), "Animation timer should not be active when disabled"
        print(f"✓ Animation timer is inactive as expected")
        
        # Show splash screen
        splash.show()
        app.processEvents()
        
        # Restore config
        app_config.SPLASH_ANIMATION_ENABLED = True
        
        # Close splash after brief display
        QTimer.singleShot(100, splash.close)
        QTimer.singleShot(200, app.quit)
        app.exec_()
        
        print(f"\n✓ Animation disabled test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Animation disabled test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_animation_speed_config():
    """Test that animation speed is configurable."""
    app = QApplication(sys.argv)
    
    try:
        # Set custom animation speed
        app_config.SPLASH_ANIMATION_SPEED = 250  # Faster animation
        app_config.SPLASH_ANIMATION_ENABLED = True
        
        # Reload splash_screen module to pick up config changes
        if 'gui.splash_screen' in sys.modules:
            importlib.reload(sys.modules['gui.splash_screen'])
        from gui.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        assert splash is not None, "Splash screen creation failed"
        print(f"✓ Splash screen created with custom animation speed")
        
        # Check that timer interval matches config
        assert splash._animation_timer.interval() == 250, f"Timer interval should be 250, got {splash._animation_timer.interval()}"
        print(f"✓ Animation speed set to {splash._animation_timer.interval()}ms (expected 250ms)")
        
        # Show splash screen
        splash.show()
        app.processEvents()
        
        # Restore config
        app_config.SPLASH_ANIMATION_SPEED = 500
        
        # Close splash after brief display
        QTimer.singleShot(100, splash.close)
        QTimer.singleShot(200, app.quit)
        app.exec_()
        
        print(f"\n✓ Animation speed config test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Animation speed config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dot_count_cycling():
    """Test that dot count cycles correctly (0->1->2->3->0)."""
    app = QApplication(sys.argv)
    
    try:
        # Ensure animation is enabled
        app_config.SPLASH_ANIMATION_ENABLED = True
        
        # Reload splash_screen module to pick up config changes
        if 'gui.splash_screen' in sys.modules:
            importlib.reload(sys.modules['gui.splash_screen'])
        from gui.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        splash.show()
        app.processEvents()
        
        # Initial dot count should be 0
        initial_count = splash._dot_count
        print(f"✓ Initial dot count: {initial_count}")
        
        # Manually trigger _update_loading_text several times and check cycling
        expected_sequence = [1, 2, 3, 0, 1, 2, 3, 0]
        for i, expected in enumerate(expected_sequence):
            splash._update_loading_text()
            app.processEvents()
            actual = splash._dot_count
            assert actual == expected, f"Cycle {i}: Expected {expected}, got {actual}"
            print(f"  Cycle {i+1}: dot_count = {actual} (expected {expected}) ✓")
        
        print(f"✓ Dot count cycles correctly through 0->1->2->3->0")
        
        # Close splash after brief display
        QTimer.singleShot(100, splash.close)
        QTimer.singleShot(200, app.quit)
        app.exec_()
        
        print(f"\n✓ Dot count cycling test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Dot count cycling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_timer_cleanup_on_close():
    """Test that timer is properly stopped when splash closes."""
    app = QApplication(sys.argv)
    
    try:
        # Ensure animation is enabled
        app_config.SPLASH_ANIMATION_ENABLED = True
        
        # Reload splash_screen module to pick up config changes
        if 'gui.splash_screen' in sys.modules:
            importlib.reload(sys.modules['gui.splash_screen'])
        from gui.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        splash.show()
        app.processEvents()
        
        # Timer should be active
        assert splash._animation_timer.isActive(), "Timer should be active initially"
        print(f"✓ Timer is active before close")
        
        # Close the splash screen
        splash.close()
        app.processEvents()
        
        # Timer should be stopped after close
        assert not splash._animation_timer.isActive(), "Timer should be stopped after close"
        print(f"✓ Timer is stopped after close")
        
        # Quit app
        QTimer.singleShot(100, app.quit)
        app.exec_()
        
        print(f"\n✓ Timer cleanup test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Timer cleanup test failed: {e}")
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
    print("Testing Splash Screen Animation Functionality")
    print("=" * 60)
    print()
    
    # Run tests
    test1_passed = test_animation_enabled()
    print("\n" + "-" * 60 + "\n")
    test2_passed = test_animation_disabled()
    print("\n" + "-" * 60 + "\n")
    test3_passed = test_animation_speed_config()
    print("\n" + "-" * 60 + "\n")
    test4_passed = test_dot_count_cycling()
    print("\n" + "-" * 60 + "\n")
    test5_passed = test_timer_cleanup_on_close()
    
    # Exit with appropriate code
    all_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL ANIMATION TESTS PASSED ✓")
    else:
        print("SOME ANIMATION TESTS FAILED ✗")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)

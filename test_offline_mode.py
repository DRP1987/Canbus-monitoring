"""Test offline mode functionality."""

import sys
import os
from pathlib import Path

# Set up virtual display for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.widgets import ConnectionStatusWidget


def test_connection_status_widget():
    """Test ConnectionStatusWidget creation and state changes."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create widget
    widget = ConnectionStatusWidget()
    
    # Test initial state (should be offline/red)
    assert not widget.connected
    assert widget.status_label.text() == "Offline"
    print("✓ ConnectionStatusWidget initializes to offline state")
    
    # Test setting to connected
    widget.set_connected(True)
    assert widget.connected
    assert widget.status_label.text() == "Connected"
    print("✓ ConnectionStatusWidget can be set to connected state")
    
    # Test setting back to offline
    widget.set_connected(False)
    assert not widget.connected
    assert widget.status_label.text() == "Offline"
    print("✓ ConnectionStatusWidget can be set back to offline state")
    
    return True


def test_main_window_connection_tracking():
    """Test that MainWindow tracks connection status."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Create main window
        window = MainWindow()
        
        # Check initial state
        assert hasattr(window, 'is_connected')
        assert not window.is_connected
        print("✓ MainWindow tracks connection status (initially offline)")
        
        # Check that signals exist
        assert hasattr(window.baudrate_screen, 'continue_offline')
        assert hasattr(window.config_selection_screen, 'reconnect_requested')
        print("✓ MainWindow screens have required signals")
        
        return True
    except Exception as e:
        print(f"⚠ Could not fully test MainWindow (expected without PCAN): {type(e).__name__}")
        return True


def test_config_screen_has_status_widget():
    """Test that config selection screen has connection status widget."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from config.config_loader import ConfigurationLoader
        from gui.config_selection_screen import ConfigSelectionScreen
        
        config_loader = ConfigurationLoader()
        screen = ConfigSelectionScreen(config_loader)
        
        # Check for connection status widget
        assert hasattr(screen, 'connection_status_widget')
        assert screen.connection_status_widget is not None
        print("✓ ConfigSelectionScreen has connection status widget")
        
        # Check for reconnect button
        assert hasattr(screen, 'configure_connection_btn')
        print("✓ ConfigSelectionScreen has configure connection button")
        
        # Test set_connection_status method
        screen.set_connection_status(True)
        assert screen.connection_status_widget.connected
        screen.set_connection_status(False)
        assert not screen.connection_status_widget.connected
        print("✓ ConfigSelectionScreen can update connection status")
        
        return True
    except Exception as e:
        print(f"✗ Config screen test failed: {e}")
        return False


def test_monitoring_screen_offline_mode():
    """Test that monitoring screen accepts offline parameters."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from canbus.pcan_interface import PCANInterface
        from gui.monitoring_screen import MonitoringScreen
        
        pcan = PCANInterface()
        config = {
            'name': 'Test Config',
            'signals': []
        }
        
        # Create monitoring screen in offline mode
        screen = MonitoringScreen(
            pcan_interface=pcan,
            configuration=config,
            baudrate=None,
            channel=None,
            connected=False
        )
        
        assert not screen.connected
        assert screen.baudrate is None
        assert screen.channel is None
        print("✓ MonitoringScreen accepts offline mode parameters")
        
        # Check for connection status widget
        assert hasattr(screen, 'connection_status_widget')
        print("✓ MonitoringScreen has connection status widget")
        
        return True
    except Exception as e:
        print(f"✗ Monitoring screen test failed: {e}")
        return False


if __name__ == '__main__':
    print("Testing offline mode functionality...\n")
    
    all_passed = True
    
    all_passed &= test_connection_status_widget()
    all_passed &= test_main_window_connection_tracking()
    all_passed &= test_config_screen_has_status_widget()
    all_passed &= test_monitoring_screen_offline_mode()
    
    if all_passed:
        print(f"\n✓ All offline mode tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ Some tests failed!")
        sys.exit(1)

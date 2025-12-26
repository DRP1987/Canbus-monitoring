"""Main window controller for CAN bus monitoring application."""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import pyqtSlot
from gui.baudrate_screen import BaudRateScreen
from gui.config_selection_screen import ConfigSelectionScreen
from gui.monitoring_screen import MonitoringScreen
from canbus.pcan_interface import PCANInterface
from config.config_loader import ConfigurationLoader
from config.app_config import APP_NAME


class MainWindow(QMainWindow):
    """Main application window managing screen transitions."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 600)

        # Initialize components
        self.pcan_interface = PCANInterface()
        self.config_loader = ConfigurationLoader()
        self.detected_baudrate = None
        self.selected_channel = None
        self.selected_configuration = None

        # Stacked widget for screen management
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Initialize screens
        self._init_screens()

        # Show baud rate screen first
        self.stacked_widget.setCurrentWidget(self.baudrate_screen)

    def _init_screens(self):
        """Initialize all application screens."""
        # Baud rate detection screen
        self.baudrate_screen = BaudRateScreen(self.pcan_interface)
        self.baudrate_screen.baudrate_confirmed.connect(self._on_baudrate_confirmed)
        self.stacked_widget.addWidget(self.baudrate_screen)

        # Configuration selection screen
        self.config_selection_screen = ConfigSelectionScreen(self.config_loader)
        self.config_selection_screen.configuration_selected.connect(
            self._on_configuration_selected
        )
        self.stacked_widget.addWidget(self.config_selection_screen)

    @pyqtSlot(int, str)
    def _on_baudrate_confirmed(self, baudrate: int, channel: str):
        """
        Handle baud rate confirmation.

        Args:
            baudrate: Confirmed baud rate
            channel: Selected PCAN channel
        """
        self.detected_baudrate = baudrate
        self.selected_channel = channel
        # Move to configuration selection screen
        self.stacked_widget.setCurrentWidget(self.config_selection_screen)

    @pyqtSlot(dict)
    def _on_configuration_selected(self, configuration: dict):
        """
        Handle configuration selection.

        Args:
            configuration: Selected configuration dictionary
        """
        self.selected_configuration = configuration

        # Remove any existing monitoring screens to prevent memory leaks
        for i in range(self.stacked_widget.count() - 1, 1, -1):
            widget = self.stacked_widget.widget(i)
            if isinstance(widget, MonitoringScreen):
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()

        # Create and show monitoring screen
        monitoring_screen = MonitoringScreen(
            self.pcan_interface,
            configuration,
            self.detected_baudrate,
            self.selected_channel
        )
        # Connect back signal
        monitoring_screen.back_to_config.connect(self._on_back_to_config)
        self.stacked_widget.addWidget(monitoring_screen)
        self.stacked_widget.setCurrentWidget(monitoring_screen)

    @pyqtSlot()
    def _on_back_to_config(self):
        """Handle back to configuration navigation."""
        # Remove monitoring screen
        for i in range(self.stacked_widget.count() - 1, 1, -1):
            widget = self.stacked_widget.widget(i)
            if isinstance(widget, MonitoringScreen):
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()
        
        # Show configuration selection screen
        self.stacked_widget.setCurrentWidget(self.config_selection_screen)

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Ensure PCAN interface is disconnected
        if self.pcan_interface:
            self.pcan_interface.disconnect()
        event.accept()

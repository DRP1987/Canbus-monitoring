"""Signal monitoring screen with tabs for CAN bus monitoring application."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTextEdit,
                             QScrollArea, QPushButton, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor
from datetime import datetime
from typing import Dict, Any, List
from gui.widgets import SignalStatusWidget
from canbus.pcan_interface import PCANInterface
from canbus.signal_matcher import SignalMatcher


class MonitoringScreen(QWidget):
    """Main monitoring screen with signal status and logging tabs."""

    def __init__(self, pcan_interface: PCANInterface, configuration: Dict[str, Any], 
                 baudrate: int, parent=None):
        """
        Initialize monitoring screen.

        Args:
            pcan_interface: PCAN interface instance
            configuration: Selected configuration dictionary
            baudrate: CAN bus baud rate
            parent: Parent widget
        """
        super().__init__(parent)
        self.pcan_interface = pcan_interface
        self.configuration = configuration
        self.baudrate = baudrate
        self.signal_widgets: Dict[str, SignalStatusWidget] = {}
        self.signal_matchers: Dict[str, Dict[str, Any]] = {}

        self._init_ui()
        self._setup_signals()
        self._connect_to_can()

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("CAN Bus Monitoring")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Header with configuration info
        header_layout = QHBoxLayout()
        config_name = self.configuration.get('name', 'Unknown')
        header_label = QLabel(f"Configuration: {config_name} | Baud Rate: {self.baudrate} bps")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Tab 1: Signal Status
        self.signal_tab = self._create_signal_tab()
        self.tab_widget.addTab(self.signal_tab, "Signal Status")

        # Tab 2: Logging
        self.log_tab = self._create_log_tab()
        self.tab_widget.addTab(self.log_tab, "CAN Bus Log")

        layout.addWidget(self.tab_widget)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.clear_log_button = QPushButton("Clear Log")
        self.clear_log_button.clicked.connect(self._clear_log)
        button_layout.addWidget(self.clear_log_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_signal_tab(self) -> QWidget:
        """
        Create signal status tab.

        Returns:
            Signal status tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Scroll area for signals
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Container for signal widgets
        signals_container = QWidget()
        signals_layout = QVBoxLayout()
        signals_layout.setAlignment(Qt.AlignTop)

        # Create signal widgets from configuration
        signals = self.configuration.get('signals', [])
        for signal_config in signals:
            signal_name = signal_config.get('name', 'Unknown')
            signal_widget = SignalStatusWidget(signal_name)
            signals_layout.addWidget(signal_widget)

            # Store widget and config for later matching
            self.signal_widgets[signal_name] = signal_widget
            self.signal_matchers[signal_name] = signal_config

        signals_container.setLayout(signals_layout)
        scroll_area.setWidget(signals_container)
        layout.addWidget(scroll_area)

        tab.setLayout(layout)
        return tab

    def _create_log_tab(self) -> QWidget:
        """
        Create logging tab.

        Returns:
            Logging tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Text edit for log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        layout.addWidget(self.log_text)

        tab.setLayout(layout)
        return tab

    def _setup_signals(self):
        """Setup Qt signal connections."""
        self.pcan_interface.message_received.connect(self._on_message_received)
        self.pcan_interface.error_occurred.connect(self._on_error)

    def _connect_to_can(self):
        """Connect to CAN bus and start receiving."""
        if self.pcan_interface.connect(baudrate=self.baudrate):
            self.pcan_interface.start_receiving()
            self._log_message("Connected to CAN bus successfully")
        else:
            self._log_message("ERROR: Failed to connect to CAN bus")

    @pyqtSlot(object)
    def _on_message_received(self, message):
        """
        Handle received CAN message.

        Args:
            message: CAN message object
        """
        # Log the message
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        can_id_str = f"0x{message.arbitration_id:03X}"
        data_str = " ".join(f"{b:02X}" for b in message.data)
        log_entry = f"{timestamp} | {can_id_str:8s} | {data_str}"
        self._log_message(log_entry)

        # Check signal matches
        for signal_name, signal_config in self.signal_matchers.items():
            is_match = SignalMatcher.match_signal(
                signal_config,
                message.arbitration_id,
                list(message.data)
            )

            # Update signal widget
            if signal_name in self.signal_widgets:
                self.signal_widgets[signal_name].update_status(is_match)

    @pyqtSlot(str)
    def _on_error(self, error_message: str):
        """
        Handle error from PCAN interface.

        Args:
            error_message: Error message
        """
        self._log_message(f"ERROR: {error_message}")

    def _log_message(self, message: str):
        """
        Add message to log.

        Args:
            message: Message to log
        """
        self.log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def _clear_log(self):
        """Clear the log display."""
        self.log_text.clear()

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Disconnect from CAN bus
        self.pcan_interface.disconnect()
        event.accept()

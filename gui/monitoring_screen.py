"""Signal monitoring screen with tabs for CAN bus monitoring application."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTextEdit,
                             QScrollArea, QPushButton, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor
from datetime import datetime
from typing import Dict, Any, List
import csv
from gui.widgets import SignalStatusWidget
from canbus.pcan_interface import PCANInterface
from canbus.signal_matcher import SignalMatcher


class MonitoringScreen(QWidget):
    """Main monitoring screen with signal status and logging tabs."""

    # Signal to navigate back to configuration selection
    back_to_config = pyqtSignal()

    def __init__(self, pcan_interface: PCANInterface, configuration: Dict[str, Any], 
                 baudrate: int, channel: str, parent=None):
        """
        Initialize monitoring screen.

        Args:
            pcan_interface: PCAN interface instance
            configuration: Selected configuration dictionary
            baudrate: CAN bus baud rate
            channel: PCAN channel name
            parent: Parent widget
        """
        super().__init__(parent)
        self.pcan_interface = pcan_interface
        self.configuration = configuration
        self.baudrate = baudrate
        self.channel = channel
        self.signal_widgets: Dict[str, SignalStatusWidget] = {}
        self.signal_matchers: Dict[str, Dict[str, Any]] = {}
        
        # Store CAN message data for override mode and CSV export
        # Key: CAN ID, Value: {'timestamp': datetime, 'data': bytes, 'last_time': datetime}
        self.can_messages: Dict[int, Dict[str, Any]] = {}

        # Timer for throttling GUI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_log_table)
        self.update_timer.setInterval(100)  # Update every 100ms (10 times per second)
        self.pending_update = False  # Flag to track if update is needed

        self._init_ui()
        self._setup_signals()
        self._connect_to_can()

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("CAN Bus Monitoring")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Header with configuration info and back button
        header_layout = QHBoxLayout()
        
        # Back button
        self.back_button = QPushButton("← Back to Configuration")
        self.back_button.setMaximumWidth(200)
        self.back_button.clicked.connect(self._on_back_clicked)
        header_layout.addWidget(self.back_button)
        
        # Configuration info
        config_name = self.configuration.get('name', 'Unknown')
        header_label = QLabel(f"Configuration: {config_name} | Channel: {self.channel} | Baud Rate: {self.baudrate} bps")
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

        self.save_log_button = QPushButton("Save Log to CSV")
        self.save_log_button.clicked.connect(self._save_log_to_csv)
        button_layout.addWidget(self.save_log_button)

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
        Create logging tab with table display (override mode).

        Returns:
            Logging tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Table widget for log display
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(['CAN ID', 'Data', 'Timestamp', 'Cycle Time (ms)'])
        
        # Configure table appearance
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setStyleSheet("font-family: monospace; font-size: 10px;")
        
        # Set column widths
        header = self.log_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # CAN ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Data
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Timestamp
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Cycle Time
        
        layout.addWidget(self.log_table)

        tab.setLayout(layout)
        return tab

    def _setup_signals(self):
        """Setup Qt signal connections."""
        self.pcan_interface.message_received.connect(self._on_message_received)
        self.pcan_interface.error_occurred.connect(self._on_error)

    def _connect_to_can(self):
        """Connect to CAN bus and start receiving."""
        if self.pcan_interface.connect(channel=self.channel, baudrate=self.baudrate):
            self.pcan_interface.start_receiving()
            print(f"Connected to CAN bus on {self.channel} at {self.baudrate} bps")
        else:
            print(f"ERROR: Failed to connect to CAN bus on {self.channel}")

    @pyqtSlot(object)
    def _on_message_received(self, message):
        """
        Handle received CAN message.

        Args:
            message: CAN message object
        """
        can_id = message.arbitration_id
        current_time = datetime.now()
        
        # Calculate cycle time
        cycle_time = None
        if can_id in self.can_messages:
            last_time = self.can_messages[can_id]['last_time']
            cycle_time = (current_time - last_time).total_seconds() * 1000  # in milliseconds
        
        # Update message storage
        self.can_messages[can_id] = {
            'timestamp': current_time,
            'data': message.data,
            'last_time': current_time,
            'cycle_time': cycle_time
        }
        
        # Mark that we have pending updates, don't update immediately
        self.pending_update = True

        # Start timer if not already running (timer will batch updates)
        if not self.update_timer.isActive():
            self.update_timer.start()

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
        # Display error in status bar or as a popup
        print(f"ERROR: {error_message}")

    def _update_log_table(self):
        """Update the log table with current CAN messages (override mode)."""
        # Only update if there are pending changes
        if not self.pending_update:
            return
        
        self.pending_update = False
        
        # Sort CAN IDs for consistent display
        sorted_ids = sorted(self.can_messages.keys())
        
        # Update table row count
        self.log_table.setRowCount(len(sorted_ids))
        
        # Populate table
        for row, can_id in enumerate(sorted_ids):
            msg_data = self.can_messages[can_id]
            
            # CAN ID
            can_id_item = QTableWidgetItem(f"0x{can_id:03X}")
            self.log_table.setItem(row, 0, can_id_item)
            
            # Data
            data_str = " ".join(f"{b:02X}" for b in msg_data['data'])
            data_item = QTableWidgetItem(data_str)
            self.log_table.setItem(row, 1, data_item)
            
            # Timestamp
            timestamp_str = msg_data['timestamp'].strftime("%H:%M:%S.%f")[:-3]
            timestamp_item = QTableWidgetItem(timestamp_str)
            self.log_table.setItem(row, 2, timestamp_item)
            
            # Cycle Time
            cycle_time = msg_data.get('cycle_time')
            cycle_time_str = f"{cycle_time:.1f}" if cycle_time is not None else ""
            cycle_time_item = QTableWidgetItem(cycle_time_str if cycle_time_str else "-")
            self.log_table.setItem(row, 3, cycle_time_item)

    def _clear_log(self):
        """Clear the log display."""
        self.can_messages.clear()
        self.log_table.setRowCount(0)
        self.pending_update = False
        # Stop timer when there's no data to display
        if self.update_timer.isActive():
            self.update_timer.stop()
    
    def _save_log_to_csv(self):
        """Save current log data to CSV file."""
        from PyQt5.QtWidgets import QMessageBox
        
        if not self.can_messages:
            QMessageBox.information(self, "No Data", "No CAN messages to save.")
            return
        
        # Open file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save CAN Bus Log",
            "can_bus_log.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['CAN ID', 'Data', 'Timestamp', 'Cycle Time (ms)'])
                
                # Write data (sorted by CAN ID)
                sorted_ids = sorted(self.can_messages.keys())
                for can_id in sorted_ids:
                    msg_data = self.can_messages[can_id]
                    
                    can_id_str = f"0x{can_id:03X}"
                    data_str = " ".join(f"{b:02X}" for b in msg_data['data'])
                    timestamp_str = msg_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    cycle_time = msg_data.get('cycle_time')
                    cycle_time_str = f"{cycle_time:.1f}" if cycle_time is not None else ""
                    
                    writer.writerow([can_id_str, data_str, timestamp_str, cycle_time_str])
            
            QMessageBox.information(self, "Success", f"Log saved to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log:\n{str(e)}")
    
    def _on_back_clicked(self):
        """Handle back button click."""
        # Stop update timer
        if self.update_timer.isActive():
            self.update_timer.stop()
        # Disconnect from CAN bus before going back
        self.pcan_interface.disconnect()
        # Emit signal to navigate back
        self.back_to_config.emit()

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Stop update timer
        if self.update_timer.isActive():
            self.update_timer.stop()
        # Disconnect from CAN bus
        self.pcan_interface.disconnect()
        event.accept()

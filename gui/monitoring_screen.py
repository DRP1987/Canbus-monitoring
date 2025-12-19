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
        
        # Real-time display buffer (limited size, for viewing)
        self.display_messages: List[Dict[str, Any]] = []
        self.max_display_messages = 1000  # Keep last 1000 messages visible

        # Logging buffer (unlimited, for CSV export)
        self.log_buffer: List[Dict[str, Any]] = []
        self.is_logging = False

        # Display pause state
        self.display_paused = False

        # Track last message time per CAN ID for cycle time calculation
        self.last_message_time: Dict[int, datetime] = {}

        # Pending messages queue for batched GUI updates
        self.pending_display_messages: List[Dict[str, Any]] = []
        self.max_pending_messages = 100  # Threshold to force immediate processing

        # Timer for batched GUI updates (60 FPS = smooth, no latency)
        self.display_update_timer = QTimer()
        self.display_update_timer.timeout.connect(self._batch_update_table)
        self.display_update_timer.setInterval(16)  # 16ms = ~60 FPS
        self.display_update_timer.start()

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

        # Logging status indicator
        self.log_status_label = QLabel("Logging: Inactive")
        self.log_status_label.setStyleSheet("padding: 5px;")
        button_layout.addWidget(self.log_status_label)

        button_layout.addStretch()

        # Start Log button (NO BACKGROUND COLOR)
        self.start_log_button = QPushButton("Start Log")
        self.start_log_button.clicked.connect(self._start_logging)
        button_layout.addWidget(self.start_log_button)

        # Stop Log button (NO BACKGROUND COLOR)
        self.stop_log_button = QPushButton("Stop Log")
        self.stop_log_button.clicked.connect(self._stop_logging)
        self.stop_log_button.setEnabled(False)
        button_layout.addWidget(self.stop_log_button)

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
        Create logging tab with table display (append/scrolling mode).

        Returns:
            Logging tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Pause/Resume button layout
        display_control_layout = QHBoxLayout()
        display_control_layout.addStretch()
        
        # Pause Display button
        self.pause_display_button = QPushButton("⏸ Pause Display")
        self.pause_display_button.clicked.connect(self._pause_display)
        display_control_layout.addWidget(self.pause_display_button)
        
        # Resume Display button
        self.resume_display_button = QPushButton("▶ Resume Display")
        self.resume_display_button.clicked.connect(self._resume_display)
        self.resume_display_button.setEnabled(False)
        display_control_layout.addWidget(self.resume_display_button)
        
        layout.addLayout(display_control_layout)

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
        if can_id in self.last_message_time:
            last_time = self.last_message_time[can_id]
            cycle_time = (current_time - last_time).total_seconds() * 1000  # milliseconds
        
        # Update last message time for this CAN ID
        self.last_message_time[can_id] = current_time
        
        # Create message data dictionary
        msg_data = {
            'timestamp': current_time,
            'can_id': can_id,
            'data': bytes(message.data),
            'cycle_time': cycle_time
        }
        
        # Add to logging buffer if active
        if self.is_logging:
            self.log_buffer.append(msg_data)
        
        # Add to pending display queue (will be processed by timer)
        self.pending_display_messages.append(msg_data)
        
        # Limit pending queue size to prevent memory issues
        if len(self.pending_display_messages) > self.max_pending_messages:
            # If threshold exceeded, process immediately to prevent backup
            self._batch_update_table()
        
        # Check signal matches (lightweight operation, can stay here)
        for signal_name, signal_config in self.signal_matchers.items():
            is_match = SignalMatcher.match_signal(
                signal_config,
                message.arbitration_id,
                list(message.data)
            )
            
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

    def _batch_update_table(self):
        """
        Batch update table with pending messages.
        Called by timer at 60 FPS for smooth, efficient updates.
        """
        # If display is paused, don't update table (messages stay in queue)
        if self.display_paused:
            return
        
        # If no pending messages, nothing to do
        if not self.pending_display_messages:
            return
        
        # Get all pending messages and clear queue
        messages_to_add = self.pending_display_messages.copy()
        self.pending_display_messages.clear()
        
        # Add to display buffer
        self.display_messages.extend(messages_to_add)
        
        # Trim display buffer to max size
        if len(self.display_messages) > self.max_display_messages:
            overflow = len(self.display_messages) - self.max_display_messages
            self.display_messages = self.display_messages[overflow:]
            
            # If we removed messages from buffer, rebuild entire table
            self._rebuild_table()
            return
        
        # Block signals during batch update for performance
        self.log_table.blockSignals(True)
        
        try:
            # Batch insert rows at the end
            current_row_count = self.log_table.rowCount()
            
            for msg_data in messages_to_add:
                row = current_row_count
                current_row_count += 1
                
                self.log_table.insertRow(row)
                
                # CAN ID
                can_id = msg_data['can_id']
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
                if cycle_time is not None:
                    cycle_time_str = f"{cycle_time:.1f}"
                else:
                    cycle_time_str = "-"
                cycle_time_item = QTableWidgetItem(cycle_time_str)
                self.log_table.setItem(row, 3, cycle_time_item)
        
        finally:
            # Re-enable signals
            self.log_table.blockSignals(False)
        
        # Auto-scroll to bottom (smooth, once per batch)
        self.log_table.scrollToBottom()

    def _rebuild_table(self):
        """
        Rebuild entire table from display buffer.
        Called when buffer is trimmed or cleared.
        """
        # Block signals for performance
        self.log_table.blockSignals(True)
        
        try:
            # Clear table
            self.log_table.setRowCount(0)
            
            # Repopulate from display buffer
            for msg_data in self.display_messages:
                row = self.log_table.rowCount()
                self.log_table.insertRow(row)
                
                # CAN ID
                can_id = msg_data['can_id']
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
                if cycle_time is not None:
                    cycle_time_str = f"{cycle_time:.1f}"
                else:
                    cycle_time_str = "-"
                cycle_time_item = QTableWidgetItem(cycle_time_str)
                self.log_table.setItem(row, 3, cycle_time_item)
        
        finally:
            self.log_table.blockSignals(False)
        
        self.log_table.scrollToBottom()

    def _start_logging(self):
        """Start logging CAN messages to buffer."""
        self.is_logging = True
        self.log_buffer.clear()
        
        # Update UI (no colors)
        self.start_log_button.setEnabled(False)
        self.stop_log_button.setEnabled(True)
        self.log_status_label.setText("Logging: ACTIVE")
        self.log_status_label.setStyleSheet("padding: 5px; color: red; font-weight: bold;")
        
        print("Started logging CAN messages")

    def _stop_logging(self):
        """Stop logging and save to CSV."""
        self.is_logging = False
        
        # Update UI
        self.start_log_button.setEnabled(True)
        self.stop_log_button.setEnabled(False)
        self.log_status_label.setText("Logging: Inactive")
        self.log_status_label.setStyleSheet("padding: 5px;")
        
        print(f"Stopped logging. Captured {len(self.log_buffer)} messages")
        
        # Open save dialog immediately
        self._save_log_to_csv()
    
    def _save_log_to_csv(self):
        """Save logged messages to CSV file."""
        from PyQt5.QtWidgets import QMessageBox
        
        if not self.log_buffer:
            QMessageBox.information(self, "No Data", "No logged messages to save.")
            return
        
        # Open file dialog with timestamp in default filename
        default_filename = f"can_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save CAN Bus Log",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header with Date and Time as separate columns
                writer.writerow(['Date', 'Time', 'CAN ID', 'Data', 'Cycle Time (ms)'])
                
                # Write all logged messages in chronological order
                for msg_data in self.log_buffer:
                    # Split timestamp into date and time
                    date_str = msg_data['timestamp'].strftime("%Y-%m-%d")
                    time_str = msg_data['timestamp'].strftime("%H:%M:%S.%f")[:-3]
                    can_id_str = f"0x{msg_data['can_id']:03X}"
                    data_str = " ".join(f"{b:02X}" for b in msg_data['data'])
                    
                    cycle_time = msg_data.get('cycle_time')
                    cycle_time_str = f"{cycle_time:.1f}" if cycle_time is not None else ""
                    
                    writer.writerow([date_str, time_str, can_id_str, data_str, cycle_time_str])
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Saved {len(self.log_buffer)} messages to:\n{filename}"
            )
            
            # Clear log buffer after successful save
            self.log_buffer.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log:\n{str(e)}")
    
    def _pause_display(self):
        """Pause display updates (messages still captured in background)."""
        self.display_paused = True
        self.pause_display_button.setEnabled(False)
        self.resume_display_button.setEnabled(True)
        print("Display paused - messages still being captured")
    
    def _resume_display(self):
        """Resume display updates and catch up with pending messages."""
        self.display_paused = False
        self.pause_display_button.setEnabled(True)
        self.resume_display_button.setEnabled(False)
        print(f"Display resumed - catching up with {len(self.pending_display_messages)} pending messages")
    
    def _on_back_clicked(self):
        """Handle back button click."""
        # Stop display timer
        if self.display_update_timer.isActive():
            self.display_update_timer.stop()
        # Stop logging if active
        if self.is_logging:
            self.is_logging = False
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
        # Stop display timer
        if self.display_update_timer.isActive():
            self.display_update_timer.stop()
        # Stop logging if active
        if self.is_logging:
            self.is_logging = False
        # Disconnect from CAN bus
        self.pcan_interface.disconnect()
        event.accept()

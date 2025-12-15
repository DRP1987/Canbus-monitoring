"""Baud rate detection screen for CAN bus monitoring application."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from canbus.pcan_interface import PCANInterface


class BaudRateDetectionThread(QThread):
    """Thread for detecting baud rate without blocking GUI."""

    baudrate_detected = pyqtSignal(int)
    detection_failed = pyqtSignal()
    progress_update = pyqtSignal(int)

    def __init__(self, pcan_interface: PCANInterface, channel: str = 'PCAN_USBBUS1'):
        """
        Initialize detection thread.

        Args:
            pcan_interface: PCAN interface instance
            channel: PCAN channel name
        """
        super().__init__()
        self.pcan_interface = pcan_interface
        self.channel = channel

    def run(self):
        """Run baud rate detection."""
        result = self.pcan_interface.detect_baudrate(
            self.channel,
            callback=self.progress_update.emit
        )

        if result:
            self.baudrate_detected.emit(result)
        else:
            self.detection_failed.emit()


class BaudRateScreen(QWidget):
    """Screen for automatic baud rate detection."""

    baudrate_confirmed = pyqtSignal(int)

    def __init__(self, pcan_interface: PCANInterface, parent=None):
        """
        Initialize baud rate detection screen.

        Args:
            pcan_interface: PCAN interface instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.pcan_interface = pcan_interface
        self.detected_baudrate = None
        self.detection_thread = None

        self._init_ui()

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Baud Rate Detection")
        self.setMinimumSize(400, 300)

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("CAN Bus Baud Rate Detection")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Click the button below to automatically detect the CAN bus baud rate.\n"
            "This process will try common baud rates: 125k, 250k, 500k, 1000k."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("margin: 10px; font-size: 12px;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        # Detected baud rate label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.result_label)

        # Button layout
        button_layout = QHBoxLayout()

        # Detect button
        self.detect_button = QPushButton("Detect Baud Rate")
        self.detect_button.setMinimumSize(150, 40)
        self.detect_button.clicked.connect(self._start_detection)
        button_layout.addWidget(self.detect_button)

        # Confirm button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setMinimumSize(150, 40)
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self._confirm_baudrate)
        button_layout.addWidget(self.confirm_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _start_detection(self):
        """Start baud rate detection process."""
        self.detect_button.setEnabled(False)
        self.confirm_button.setEnabled(False)
        self.result_label.setText("")
        self.status_label.setText("Detecting baud rate...")
        self.progress_bar.setVisible(True)

        # Create and start detection thread
        self.detection_thread = BaudRateDetectionThread(self.pcan_interface)
        self.detection_thread.baudrate_detected.connect(self._on_detection_success)
        self.detection_thread.detection_failed.connect(self._on_detection_failed)
        self.detection_thread.progress_update.connect(self._on_progress_update)
        self.detection_thread.finished.connect(self._on_detection_finished)
        self.detection_thread.start()

    def _on_progress_update(self, baudrate: int):
        """
        Handle progress update.

        Args:
            baudrate: Currently testing baud rate
        """
        self.status_label.setText(f"Testing baud rate: {baudrate} bps...")

    def _on_detection_success(self, baudrate: int):
        """
        Handle successful detection.

        Args:
            baudrate: Detected baud rate
        """
        self.detected_baudrate = baudrate
        self.result_label.setText(f"Detected Baud Rate: {baudrate} bps")
        self.result_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin: 10px; color: green;"
        )
        self.status_label.setText("Detection successful!")
        self.confirm_button.setEnabled(True)

    def _on_detection_failed(self):
        """Handle failed detection."""
        self.result_label.setText("Detection Failed")
        self.result_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin: 10px; color: red;"
        )
        self.status_label.setText("No CAN bus activity detected. Please check your connection.")

        QMessageBox.warning(
            self,
            "Detection Failed",
            "Failed to detect baud rate. Please ensure:\n"
            "- PCAN device is connected\n"
            "- CAN bus has active traffic\n"
            "- Proper termination is in place"
        )

    def _on_detection_finished(self):
        """Handle detection thread finished."""
        self.progress_bar.setVisible(False)
        self.detect_button.setEnabled(True)

    def _confirm_baudrate(self):
        """Confirm detected baud rate and proceed."""
        if self.detected_baudrate:
            self.baudrate_confirmed.emit(self.detected_baudrate)

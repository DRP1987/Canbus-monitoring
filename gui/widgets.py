"""Custom widgets for CAN bus monitoring GUI."""

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush


class LEDIndicator(QWidget):
    """LED indicator widget showing match status."""

    def __init__(self, parent=None):
        """
        Initialize LED indicator.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.status = False  # False = red, True = green
        self.setFixedSize(20, 20)

    def set_status(self, status: bool):
        """
        Set LED status.

        Args:
            status: True for green (match), False for red (no match)
        """
        self.status = status
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """
        Paint the LED indicator.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Choose color based on status
        if self.status:
            color = QColor(0, 255, 0)  # Green
        else:
            color = QColor(255, 0, 0)  # Red

        # Draw filled circle
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 16, 16)


class SignalStatusWidget(QWidget):
    """Widget displaying signal name with LED indicator."""

    def __init__(self, signal_name: str, parent=None):
        """
        Initialize signal status widget.

        Args:
            signal_name: Name of the signal
            parent: Parent widget
        """
        super().__init__(parent)
        self.signal_name = signal_name

        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Create LED indicator
        self.led = LEDIndicator()
        layout.addWidget(self.led)

        # Create label
        self.label = QLabel(signal_name)
        layout.addWidget(self.label)

        # Add stretch to left-align
        layout.addStretch()

        self.setLayout(layout)

    def update_status(self, status: bool):
        """
        Update signal status.

        Args:
            status: True for match (green), False for no match (red)
        """
        self.led.set_status(status)

    def get_signal_name(self) -> str:
        """
        Get signal name.

        Returns:
            Signal name
        """
        return self.signal_name

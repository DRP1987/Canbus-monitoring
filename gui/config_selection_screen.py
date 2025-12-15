"""Configuration selection screen for CAN bus monitoring application."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from config.config_loader import ConfigurationLoader


class ConfigSelectionScreen(QWidget):
    """Screen for selecting monitoring configuration."""

    configuration_selected = pyqtSignal(dict)

    def __init__(self, config_loader: ConfigurationLoader, parent=None):
        """
        Initialize configuration selection screen.

        Args:
            config_loader: Configuration loader instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_loader = config_loader
        self.configurations = []

        self._init_ui()
        self._load_configurations()

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Configuration Selection")
        self.setMinimumSize(500, 400)

        # Main layout
        layout = QVBoxLayout()

        # Title
        title = QLabel("Select Monitoring Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Select a configuration from the list below and click 'Load Configuration'."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Configuration list
        list_label = QLabel("Available Configurations:")
        list_label.setStyleSheet("margin-top: 20px; font-weight: bold;")
        layout.addWidget(list_label)

        self.config_list = QListWidget()
        self.config_list.itemDoubleClicked.connect(self._load_selected_config)
        layout.addWidget(self.config_list)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("margin: 10px; color: red;")
        layout.addWidget(self.status_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Load button
        self.load_button = QPushButton("Load Configuration")
        self.load_button.setMinimumSize(150, 40)
        self.load_button.clicked.connect(self._load_selected_config)
        button_layout.addWidget(self.load_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_configurations(self):
        """Load configurations from file."""
        try:
            self.configurations = self.config_loader.load_configurations()

            if not self.configurations:
                self.status_label.setText("No configurations found in file.")
                self.load_button.setEnabled(False)
                return

            # Populate list
            for config in self.configurations:
                config_name = config.get('name', 'Unnamed')
                signal_count = len(config.get('signals', []))
                self.config_list.addItem(f"{config_name} ({signal_count} signals)")

            # Select first item by default
            if self.config_list.count() > 0:
                self.config_list.setCurrentRow(0)

        except FileNotFoundError:
            self.status_label.setText("Configuration file not found!")
            self.load_button.setEnabled(False)
            QMessageBox.critical(
                self,
                "Error",
                "Configuration file 'configurations.json' not found.\n"
                "Please ensure the file exists in the application directory."
            )
        except Exception as e:
            self.status_label.setText(f"Error loading configurations: {str(e)}")
            self.load_button.setEnabled(False)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load configurations:\n{str(e)}"
            )

    def _load_selected_config(self):
        """Load selected configuration and emit signal."""
        current_item = self.config_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a configuration from the list."
            )
            return

        current_row = self.config_list.currentRow()
        if current_row >= 0 and current_row < len(self.configurations):
            selected_config = self.configurations[current_row]

            # Validate configuration
            if not self.config_loader.validate_configuration(selected_config):
                QMessageBox.critical(
                    self,
                    "Invalid Configuration",
                    "The selected configuration is invalid. Please check the JSON file."
                )
                return

            self.configuration_selected.emit(selected_config)

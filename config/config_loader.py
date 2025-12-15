"""Configuration loader for CAN bus monitoring configurations."""

import json
import os
from typing import List, Dict, Any


class ConfigurationLoader:
    """Loads and manages CAN bus monitoring configurations from JSON files."""

    def __init__(self, config_file: str = "configurations.json"):
        """
        Initialize the configuration loader.

        Args:
            config_file: Path to the JSON configuration file
        """
        self.config_file = config_file
        self.configurations = []

    def load_configurations(self) -> List[Dict[str, Any]]:
        """
        Load configurations from JSON file.

        Returns:
            List of configuration dictionaries

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            data = json.load(f)

        self.configurations = data.get('configurations', [])
        return self.configurations

    def get_configuration_names(self) -> List[str]:
        """
        Get list of configuration names.

        Returns:
            List of configuration names
        """
        return [config.get('name', 'Unnamed') for config in self.configurations]

    def get_configuration_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            name: Configuration name

        Returns:
            Configuration dictionary or None if not found
        """
        for config in self.configurations:
            if config.get('name') == name:
                return config
        return None

    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(config, dict):
            return False

        if 'name' not in config or 'signals' not in config:
            return False

        if not isinstance(config['signals'], list):
            return False

        for signal in config['signals']:
            if not self._validate_signal(signal):
                return False

        return True

    def _validate_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Validate individual signal configuration.

        Args:
            signal: Signal dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['name', 'can_id', 'match_type']
        for field in required_fields:
            if field not in signal:
                return False

        match_type = signal['match_type']
        if match_type == 'exact':
            if 'data' not in signal or not isinstance(signal['data'], list):
                return False
        elif match_type == 'range':
            required_range_fields = ['data_byte_index', 'min_value', 'max_value']
            for field in required_range_fields:
                if field not in signal:
                    return False
        else:
            return False

        return True

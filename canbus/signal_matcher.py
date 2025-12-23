"""Signal matching logic for CAN bus messages."""

from typing import Dict, Any, List


class SignalMatcher:
    """Matches received CAN messages against configured signal definitions."""

    @staticmethod
    def match_signal(signal_config: Dict[str, Any], can_id: int, data: List[int]) -> bool:
        """
        Check if a received CAN message matches the signal configuration.

        Args:
            signal_config: Signal configuration dictionary (with parsed integer values)
            can_id: Received CAN message ID
            data: Received CAN message data bytes

        Returns:
            True if message matches signal configuration, False otherwise
        """
        # Get config CAN ID (already parsed to int by ConfigurationLoader)
        config_can_id = signal_config.get('can_id')
        
        # Check if CAN IDs match
        if can_id != config_can_id:
            return False

        # Check match type
        match_type = signal_config.get('match_type', 'exact')

        if match_type == 'exact':
            return SignalMatcher._match_exact(signal_config, data)
        elif match_type == 'range':
            return SignalMatcher._match_range(signal_config, data)
        else:
            return False

    @staticmethod
    def _match_exact(signal_config: Dict[str, Any], data: List[int]) -> bool:
        """
        Check for exact data match.

        Args:
            signal_config: Signal configuration dictionary
            data: Received CAN message data bytes

        Returns:
            True if data matches exactly, False otherwise
        """
        expected_data = signal_config.get('data', [])

        # Check if data matches exactly (Python handles element-wise comparison)
        return data == expected_data

    @staticmethod
    def _match_range(signal_config: Dict[str, Any], data: List[int]) -> bool:
        """
        Check if specific byte is within configured range.

        Args:
            signal_config: Signal configuration dictionary
            data: Received CAN message data bytes

        Returns:
            True if byte value is within range, False otherwise
        """
        byte_index = signal_config.get('data_byte_index', 0)
        min_value = signal_config.get('min_value', 0)
        max_value = signal_config.get('max_value', 255)

        # Check if byte index is valid
        if byte_index >= len(data):
            return False

        # Check if value is within range
        byte_value = data[byte_index]
        return min_value <= byte_value <= max_value

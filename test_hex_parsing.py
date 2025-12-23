"""Test hex parsing functionality for configuration loader."""

import json
import os
import tempfile
from config.config_loader import ConfigurationLoader


def test_parse_value():
    """Test the _parse_value helper method."""
    loader = ConfigurationLoader()
    
    # Test hex strings
    assert loader._parse_value("0x123") == 291
    assert loader._parse_value("0xFF") == 255
    assert loader._parse_value("0xAA") == 170
    assert loader._parse_value("0x00") == 0
    
    # Test decimal integers
    assert loader._parse_value(291) == 291
    assert loader._parse_value(255) == 255
    assert loader._parse_value(0) == 0
    
    # Test decimal strings
    assert loader._parse_value("291") == 291
    assert loader._parse_value("255") == 255
    
    # Test case insensitivity
    assert loader._parse_value("0XFF") == 255
    assert loader._parse_value("0Xff") == 255
    
    print("✓ All _parse_value tests passed")


def test_load_configurations_with_hex():
    """Test loading configurations with hex values."""
    # Create a temporary config file
    config_data = {
        "configurations": [
            {
                "name": "Test Config",
                "signals": [
                    {
                        "name": "Signal 1",
                        "can_id": "0x123",
                        "match_type": "exact",
                        "data": ["0xAA", "0x02", 3, "0x04", 5, 6, 7, 8]
                    },
                    {
                        "name": "Signal 2",
                        "can_id": "0x456",
                        "match_type": "range",
                        "data_byte_index": 0,
                        "min_value": "0x0A",
                        "max_value": "0x32"
                    },
                    {
                        "name": "Signal 3",
                        "can_id": 789,
                        "match_type": "exact",
                        "data": [1, 2, 3, 4, 5, 6, 7, 8]
                    }
                ]
            }
        ]
    }
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    
    try:
        # Load configuration
        loader = ConfigurationLoader(temp_file)
        configs = loader.load_configurations()
        
        # Verify parsing
        assert len(configs) == 1
        assert configs[0]['name'] == "Test Config"
        
        signals = configs[0]['signals']
        assert len(signals) == 3
        
        # Signal 1: Mixed hex and decimal in data array
        signal1 = signals[0]
        assert signal1['can_id'] == 291  # 0x123
        assert signal1['data'] == [170, 2, 3, 4, 5, 6, 7, 8]  # Mixed hex/decimal
        
        # Signal 2: Range with hex min/max
        signal2 = signals[1]
        assert signal2['can_id'] == 1110  # 0x456
        assert signal2['min_value'] == 10  # 0x0A
        assert signal2['max_value'] == 50  # 0x32
        
        # Signal 3: All decimal (backward compatibility)
        signal3 = signals[2]
        assert signal3['can_id'] == 789
        assert signal3['data'] == [1, 2, 3, 4, 5, 6, 7, 8]
        
        print("✓ All configuration loading tests passed")
        
    finally:
        # Clean up temp file
        os.unlink(temp_file)


def test_backward_compatibility():
    """Test that old decimal-only configs still work."""
    config_data = {
        "configurations": [
            {
                "name": "Decimal Config",
                "signals": [
                    {
                        "name": "Old Signal",
                        "can_id": 291,
                        "match_type": "exact",
                        "data": [1, 2, 3, 4, 5, 6, 7, 8]
                    },
                    {
                        "name": "Old Range",
                        "can_id": 512,
                        "match_type": "range",
                        "data_byte_index": 1,
                        "min_value": 100,
                        "max_value": 200
                    }
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    
    try:
        loader = ConfigurationLoader(temp_file)
        configs = loader.load_configurations()
        
        signals = configs[0]['signals']
        
        # Verify decimal values still work
        assert signals[0]['can_id'] == 291
        assert signals[0]['data'] == [1, 2, 3, 4, 5, 6, 7, 8]
        
        assert signals[1]['can_id'] == 512
        assert signals[1]['min_value'] == 100
        assert signals[1]['max_value'] == 200
        
        print("✓ Backward compatibility tests passed")
        
    finally:
        os.unlink(temp_file)


def test_edge_cases():
    """Test edge cases and potential errors."""
    loader = ConfigurationLoader()
    
    # Test with various hex formats
    assert loader._parse_value("0x0") == 0
    assert loader._parse_value("0x1") == 1
    assert loader._parse_value("0xFFFF") == 65535
    
    # Test error handling for invalid types
    try:
        loader._parse_value(None)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid value type" in str(e)
    
    try:
        loader._parse_value([1, 2, 3])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid value type" in str(e)
    
    print("✓ Edge case tests passed")


if __name__ == "__main__":
    print("Running hex parsing tests...\n")
    
    test_parse_value()
    test_load_configurations_with_hex()
    test_backward_compatibility()
    test_edge_cases()
    
    print("\n✅ All tests passed successfully!")

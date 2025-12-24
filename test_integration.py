"""
Integration test for bit-level monitoring scenario.

This test demonstrates the complete bit-level monitoring workflow
as specified in the requirements:
- CAN ID 0x119
- Byte 3
- Bit 0 (LSB)
- LED turns green when bit 0 = 1
"""

import sys
import traceback
from canbus.signal_matcher import SignalMatcher
from config.config_loader import ConfigurationLoader


def run_integration_test():
    """Run integration test for bit-level monitoring."""
    print("=" * 70)
    print("BIT-LEVEL MONITORING - INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Load configuration from configurations.json
    print("\n[STEP 1] Load Configuration 1 from configurations.json")
    print("-" * 70)
    
    loader = ConfigurationLoader("configurations.json")
    configs = loader.load_configurations()
    
    config1 = next((config for config in configs if config.get('name') == 'Configuration 1'), None)
    
    assert config1 is not None, "Configuration 1 not found"
    print("✓ Configuration 1 loaded successfully")
    
    # Test 2: Verify Signal 1 configuration
    print("\n[STEP 2] Verify Signal 1 configuration")
    print("-" * 70)
    
    signal1 = config1['signals'][0]
    print(f"  Signal Name: {signal1['name']}")
    print(f"  CAN ID: 0x{signal1['can_id']:03X}")
    print(f"  Match Type: {signal1['match_type']}")
    print(f"  Byte Index: {signal1['byte_index']}")
    print(f"  Bit Index: {signal1['bit_index']}")
    print(f"  Bit Value: {signal1['bit_value']}")
    
    assert signal1['name'] == 'Signal 1', "Signal name incorrect"
    assert signal1['can_id'] == 0x119, "CAN ID should be 0x119"
    assert signal1['match_type'] == 'bit', "Match type should be 'bit'"
    assert signal1['byte_index'] == 3, "Byte index should be 3"
    assert signal1['bit_index'] == 0, "Bit index should be 0 (LSB)"
    assert signal1['bit_value'] == 1, "Bit value should be 1"
    print("✓ Signal 1 configuration is correct")
    
    # Test 3: Simulate CAN messages and verify LED behavior
    print("\n[STEP 3] Simulate CAN messages and verify LED behavior")
    print("-" * 70)
    
    test_cases = [
        {
            'description': 'Byte 3 = 0x01 (bit 0 = 1)',
            'can_id': 0x119,
            'data': [0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'Byte 3 = 0x00 (bit 0 = 0)',
            'can_id': 0x119,
            'data': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'expected': False,
            'led_color': 'RED'
        },
        {
            'description': 'Byte 3 = 0x29 (binary: 00101001, bit 0 = 1)',
            'can_id': 0x119,
            'data': [0x00, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'Byte 3 = 0x28 (binary: 00101000, bit 0 = 0)',
            'can_id': 0x119,
            'data': [0x00, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x00],
            'expected': False,
            'led_color': 'RED'
        },
        {
            'description': 'Byte 3 = 0xFF (all bits set, bit 0 = 1)',
            'can_id': 0x119,
            'data': [0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'Byte 3 = 0xFE (binary: 11111110, bit 0 = 0)',
            'can_id': 0x119,
            'data': [0x00, 0x00, 0x00, 0xFE, 0x00, 0x00, 0x00, 0x00],
            'expected': False,
            'led_color': 'RED'
        },
        {
            'description': 'Wrong CAN ID (0x123), bit 0 = 1',
            'can_id': 0x123,
            'data': [0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00],
            'expected': False,
            'led_color': 'RED (no CAN ID match)'
        },
        {
            'description': 'Other bytes vary, byte 3 = 0x03 (bit 0 = 1)',
            'can_id': 0x119,
            'data': [0xAA, 0xBB, 0xCC, 0x03, 0xDD, 0xEE, 0xFF, 0x11],
            'expected': True,
            'led_color': 'GREEN'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = SignalMatcher.match_signal(
            signal1,
            test['can_id'],
            test['data']
        )
        
        status = "✓" if result == test['expected'] else "✗"
        print(f"{status} Test {i}: {test['description']}")
        print(f"     Expected: LED {test['led_color']}, Got: {'MATCH' if result else 'NO MATCH'}")
        
        assert result == test['expected'], f"Test {i} failed: {test['description']}"
    
    print("✓ All CAN message simulations passed")
    
    # Test 4: Verify integration with validation
    print("\n[STEP 4] Verify configuration validation")
    print("-" * 70)
    
    assert loader.validate_configuration(config1), "Configuration should be valid"
    print("✓ Configuration validates successfully")
    
    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST PASSED ✓")
    print("=" * 70)
    print("\nBit-level monitoring is fully functional:")
    print("  ✓ Configuration loads correctly from JSON")
    print("  ✓ Bit match type is properly configured")
    print("  ✓ CAN ID 0x119 is monitored")
    print("  ✓ Byte 3, bit 0 (LSB) is checked")
    print("  ✓ LED turns green when bit 0 = 1")
    print("  ✓ LED turns red when bit 0 = 0")
    print("  ✓ Configuration validation works correctly")
    print("\nThe implementation meets all requirements!")


if __name__ == "__main__":
    try:
        run_integration_test()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

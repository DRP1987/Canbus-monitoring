"""
Integration test for J1939 PGN matching with Configuration 2.

This test demonstrates the complete J1939 PGN matching workflow
as specified in the feature requirements:
- Load J1939 configuration from configurations.json
- Verify PGN extraction and matching
- Test range matching with byte_index parameter
"""

import sys
import traceback
from canbus.signal_matcher import SignalMatcher
from config.config_loader import ConfigurationLoader


def run_integration_test():
    """Run integration test for J1939 PGN matching."""
    print("=" * 70)
    print("J1939 PGN MATCHING - INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Load Configuration 2 from configurations.json
    print("\n[STEP 1] Load Configuration 2 from configurations.json")
    print("-" * 70)
    
    loader = ConfigurationLoader("configurations.json")
    configs = loader.load_configurations()
    
    config2 = next((config for config in configs if config.get('name') == 'Configuration 2'), None)
    
    assert config2 is not None, "Configuration 2 not found"
    print("✓ Configuration 2 loaded successfully")
    
    # Test 2: Verify J1939 signal configuration
    print("\n[STEP 2] Verify J1939 Signal configuration")
    print("-" * 70)
    
    signal = config2['signals'][0]
    print(f"  Signal Name: {signal['name']}")
    print(f"  CAN ID: 0x{signal['can_id']:08X}")
    print(f"  Protocol: {signal.get('protocol', 'standard')}")
    print(f"  Match Type: {signal['match_type']}")
    print(f"  Byte Index: {signal.get('byte_index')}")
    print(f"  Min Value: 0x{signal.get('min_value'):02X}")
    print(f"  Max Value: 0x{signal.get('max_value'):02X}")
    
    assert signal['name'] == 'J1939 PGN F004', "Signal name incorrect"
    assert signal['can_id'] == 0x18F00401, "CAN ID should be 0x18F00401"
    assert signal.get('protocol') == 'j1939', "Protocol should be 'j1939'"
    assert signal['match_type'] == 'range', "Match type should be 'range'"
    assert signal['byte_index'] == 3, "Byte index should be 3"
    assert signal['min_value'] == 0x06, "Min value should be 0x06"
    assert signal['max_value'] == 0xFF, "Max value should be 0xFF"
    print("✓ J1939 signal configuration is correct")
    
    # Test 3: Verify PGN extraction
    print("\n[STEP 3] Verify PGN extraction from CAN ID")
    print("-" * 70)
    
    can_id = 0x18F00401
    pgn = SignalMatcher._extract_pgn(can_id)
    expected_pgn = 0xF004
    
    print(f"  CAN ID: 0x{can_id:08X}")
    print(f"  Binary: {can_id:029b}")
    print(f"  Extracted PGN: 0x{pgn:04X}")
    print(f"  Expected PGN: 0x{expected_pgn:04X}")
    
    assert pgn == expected_pgn, f"PGN extraction failed: got 0x{pgn:04X}, expected 0x{expected_pgn:04X}"
    print("✓ PGN correctly extracted from CAN ID")
    
    # Test 4: Simulate J1939 messages with different source addresses
    print("\n[STEP 4] Simulate J1939 messages with PGN 0xF004")
    print("-" * 70)
    
    test_cases = [
        {
            'description': 'CAN ID 0x18F00401 (Source 0x01), Byte 3 = 0x10',
            'can_id': 0x18F00401,
            'data': [0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'CAN ID 0x18F00402 (Source 0x02), Byte 3 = 0x50',
            'can_id': 0x18F00402,
            'data': [0x00, 0x00, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'CAN ID 0x18F004FF (Source 0xFF), Byte 3 = 0xFF',
            'can_id': 0x18F004FF,
            'data': [0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'CAN ID 0x1CF00410 (Different Priority 0x07), Byte 3 = 0x06',
            'can_id': 0x1CF00410,
            'data': [0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00],
            'expected': True,
            'led_color': 'GREEN'
        },
        {
            'description': 'CAN ID 0x18F00401 (Source 0x01), Byte 3 = 0x05 (below min)',
            'can_id': 0x18F00401,
            'data': [0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00],
            'expected': False,
            'led_color': 'RED'
        },
        {
            'description': 'CAN ID 0x18F00501 (Different PGN 0xF005), Byte 3 = 0x10',
            'can_id': 0x18F00501,
            'data': [0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00],
            'expected': False,
            'led_color': 'RED'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = SignalMatcher.match_signal(
            signal,
            test['can_id'],
            test['data']
        )
        
        status = "✓" if result == test['expected'] else "✗"
        print(f"{status} Test {i}: {test['description']}")
        print(f"     Expected: LED {test['led_color']}, Got: {'MATCH' if result else 'NO MATCH'}")
        
        assert result == test['expected'], f"Test {i} failed: {test['description']}"
    
    print("✓ All J1939 message simulations passed")
    
    # Test 5: Verify configuration validation
    print("\n[STEP 5] Verify configuration validation")
    print("-" * 70)
    
    assert loader.validate_configuration(config2), "Configuration should be valid"
    print("✓ Configuration validates successfully")
    
    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST PASSED ✓")
    print("=" * 70)
    print("\nJ1939 PGN matching is fully functional:")
    print("  ✓ Configuration loads correctly from JSON")
    print("  ✓ J1939 protocol type is properly configured")
    print("  ✓ PGN extraction works correctly (bits 8-25)")
    print("  ✓ Messages match by PGN (ignoring priority and source address)")
    print("  ✓ Range matching works with byte_index parameter")
    print("  ✓ Byte 3 range check (0x06 to 0xFF) works correctly")
    print("  ✓ Configuration validation works correctly")
    print("\nThe implementation meets all J1939 requirements!")


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

"""
Unit tests for J1939 PGN matching.

This test validates that the J1939 protocol support works correctly
for matching messages by PGN (Parameter Group Number) instead of full CAN ID.
"""

import sys
import traceback
from canbus.signal_matcher import SignalMatcher


class TestJ1939PGN:
    """Test J1939 PGN matching."""
    
    def __init__(self):
        """Initialize test harness."""
        self.test_count = 0
        self.passed_count = 0
    
    def test(self, name, condition, expected=True):
        """Run a test and track results."""
        self.test_count += 1
        if condition == expected:
            self.passed_count += 1
            print(f"  ✓ {name}")
            return True
        else:
            print(f"  ✗ {name} - Expected {expected}, got {condition}")
            return False


def run_tests():
    """Run all J1939 PGN matching tests."""
    print("=" * 70)
    print("J1939 PGN MATCHING TESTS")
    print("=" * 70)
    
    test = TestJ1939PGN()
    
    # Test 1: PGN extraction from CAN ID
    print("\n[TEST 1] PGN Extraction")
    print("-" * 70)
    
    # CAN ID 0x18F00401:
    # Binary: 0001 1000 1111 0000 0000 0100 0000 0001
    # Priority (bits 26-28): 0x06 (binary: 110)
    # PGN (bits 8-25): 0xF004 (binary: 1111 0000 0000 0100)
    # Source Address (bits 0-7): 0x01 (binary: 0000 0001)
    can_id = 0x18F00401
    pgn = SignalMatcher._extract_pgn(can_id)
    expected_pgn = 0xF004
    test.test(f"Extract PGN from 0x{can_id:08X} should be 0x{expected_pgn:04X}", 
              pgn == expected_pgn, True)
    
    # Test with different source address - same PGN
    can_id = 0x18F00402  # Source address 0x02
    pgn = SignalMatcher._extract_pgn(can_id)
    test.test(f"Extract PGN from 0x{can_id:08X} should be 0x{expected_pgn:04X}", 
              pgn == expected_pgn, True)
    
    # Test with different priority - same PGN
    can_id = 0x1CF00401  # Priority 0x07 (different from 0x06)
    pgn = SignalMatcher._extract_pgn(can_id)
    test.test(f"Extract PGN from 0x{can_id:08X} should be 0x{expected_pgn:04X}", 
              pgn == expected_pgn, True)
    
    # Test 2: J1939 PGN matching - same PGN, different source addresses
    print("\n[TEST 2] J1939 PGN Matching - Different Source Addresses")
    print("-" * 70)
    
    signal_config = {
        'can_id': 0x18F00401,  # PGN 0xF004, Source 0x01
        'match_type': 'range',
        'protocol': 'j1939',
        'byte_index': 3,
        'min_value': 0x06,
        'max_value': 0xFF
    }
    
    # Message with same PGN but different source address
    data = [0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]
    can_id_source_02 = 0x18F00402  # PGN 0xF004, Source 0x02
    result = SignalMatcher.match_signal(signal_config, can_id_source_02, data)
    test.test("Same PGN (0xF004), different source address (0x02) should match", 
              result, True)
    
    # Message with same PGN but different priority and source address
    can_id_source_ff = 0x1CF004FF  # PGN 0xF004, Source 0xFF, Priority 0x07
    result = SignalMatcher.match_signal(signal_config, can_id_source_ff, data)
    test.test("Same PGN (0xF004), different priority and source (0xFF) should match", 
              result, True)
    
    # Test 3: J1939 PGN matching - different PGN
    print("\n[TEST 3] J1939 PGN Matching - Different PGN")
    print("-" * 70)
    
    # Message with different PGN
    can_id_diff_pgn = 0x18F00501  # PGN 0xF005, Source 0x01
    result = SignalMatcher.match_signal(signal_config, can_id_diff_pgn, data)
    test.test("Different PGN (0xF005) should not match", result, False)
    
    # Test 4: J1939 range matching with byte_index
    print("\n[TEST 4] J1939 Range Matching with byte_index")
    print("-" * 70)
    
    signal_config = {
        'can_id': 0x18F00401,
        'match_type': 'range',
        'protocol': 'j1939',
        'byte_index': 3,
        'min_value': 0x06,
        'max_value': 0xFF
    }
    
    # Byte 3 = 0x06 (at minimum)
    data = [0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x18F00401, data)
    test.test("Byte 3 = 0x06 (at minimum) should match", result, True)
    
    # Byte 3 = 0xFF (at maximum)
    data = [0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x18F00401, data)
    test.test("Byte 3 = 0xFF (at maximum) should match", result, True)
    
    # Byte 3 = 0x50 (in range)
    data = [0x00, 0x00, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x18F00401, data)
    test.test("Byte 3 = 0x50 (in range) should match", result, True)
    
    # Byte 3 = 0x05 (below minimum)
    data = [0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x18F00401, data)
    test.test("Byte 3 = 0x05 (below minimum) should not match", result, False)
    
    # Test 5: Standard CAN matching still works (no protocol specified)
    print("\n[TEST 5] Standard CAN Matching (no protocol)")
    print("-" * 70)
    
    signal_config = {
        'can_id': 0x123,
        'match_type': 'range',
        'byte_index': 0,
        'min_value': 0x10,
        'max_value': 0x20
    }
    
    # Exact CAN ID match
    data = [0x15, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x123, data)
    test.test("Standard CAN: Exact CAN ID (0x123) should match", result, True)
    
    # Different CAN ID (no match)
    result = SignalMatcher.match_signal(signal_config, 0x124, data)
    test.test("Standard CAN: Different CAN ID (0x124) should not match", result, False)
    
    # Test 6: J1939 with different match types
    print("\n[TEST 6] J1939 with Exact Match Type")
    print("-" * 70)
    
    signal_config = {
        'can_id': 0x18F00401,
        'match_type': 'exact',
        'protocol': 'j1939',
        'data': [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    }
    
    # Same PGN, different source address, matching data
    data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    result = SignalMatcher.match_signal(signal_config, 0x18F00402, data)
    test.test("J1939 exact match: Same PGN, different source should match with exact data", 
              result, True)
    
    # Same PGN, different data
    data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x09]
    result = SignalMatcher.match_signal(signal_config, 0x18F00402, data)
    test.test("J1939 exact match: Same PGN, different data should not match", 
              result, False)
    
    # Test 7: J1939 with Bit Match Type
    print("\n[TEST 7] J1939 with Bit Match Type")
    print("-" * 70)
    
    signal_config = {
        'can_id': 0x18F00401,
        'match_type': 'bit',
        'protocol': 'j1939',
        'byte_index': 2,
        'bit_index': 0,
        'bit_value': 1
    }
    
    # Same PGN, different source, bit 0 of byte 2 is 1
    data = [0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x18F00402, data)
    test.test("J1939 bit match: Same PGN, bit 0 = 1 should match", result, True)
    
    # Same PGN, different source, bit 0 of byte 2 is 0
    data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x18F00402, data)
    test.test("J1939 bit match: Same PGN, bit 0 = 0 should not match", result, False)
    
    # Test 8: Backwards compatibility - data_byte_index still works
    print("\n[TEST 8] Backwards Compatibility - data_byte_index")
    print("-" * 70)
    
    signal_config = {
        'can_id': 0x200,
        'match_type': 'range',
        'data_byte_index': 1,
        'min_value': 0x10,
        'max_value': 0x20
    }
    
    data = [0x00, 0x15, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    result = SignalMatcher.match_signal(signal_config, 0x200, data)
    test.test("data_byte_index (old parameter) should still work", result, True)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"TESTS COMPLETED: {test.passed_count}/{test.test_count} PASSED")
    print("=" * 70)
    
    if test.passed_count == test.test_count:
        print("\n✓ All J1939 PGN matching tests passed!")
        print("\nThe J1939 PGN matching logic is working correctly:")
        print("  ✓ Correctly extracts PGN from 29-bit CAN IDs")
        print("  ✓ Matches messages by PGN (ignoring priority and source address)")
        print("  ✓ Works with all match types (exact, range, bit)")
        print("  ✓ Supports byte_index parameter for range matching")
        print("  ✓ Maintains backwards compatibility with standard CAN")
        print("  ✓ Maintains backwards compatibility with data_byte_index")
        return True
    else:
        print(f"\n✗ {test.test_count - test.passed_count} test(s) failed")
        return False


if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

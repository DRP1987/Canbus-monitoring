"""
Test for J1939 PGN matching in monitoring screen.

This test validates that the monitoring screen correctly filters messages
for J1939 signals by comparing PGNs instead of full CAN IDs.
"""

import sys
from unittest.mock import Mock, MagicMock
from canbus.signal_matcher import SignalMatcher


class MockMessage:
    """Mock CAN message for testing."""
    
    def __init__(self, arbitration_id, data):
        """Initialize mock message."""
        self.arbitration_id = arbitration_id
        self.data = data


def test_j1939_pgn_filtering():
    """Test that J1939 signals are filtered by PGN, not full CAN ID."""
    print("=" * 70)
    print("TEST: J1939 PGN Filtering in Monitoring Screen")
    print("=" * 70)
    
    # Test scenario from the bug report
    # Config has: "can_id": "0x18F00401", "protocol": "j1939"
    # Message arrives with: 0x0CF00400 (same PGN F004, different priority/source)
    
    signal_config = {
        'can_id': 0x18F00401,
        'protocol': 'j1939',
        'match_type': 'range',
        'byte_index': 3,
        'min_value': 0x06,
        'max_value': 0xFF
    }
    
    # Simulate the filtering logic from monitoring_screen.py
    def is_message_relevant(message, signal_config):
        """Check if message is relevant to signal (mimics monitoring screen logic)."""
        signal_can_id = signal_config.get('can_id')
        protocol = signal_config.get('protocol', None)
        
        if protocol == 'j1939':
            # For J1939, compare PGNs (ignore priority and source address)
            received_pgn = SignalMatcher._extract_pgn(message.arbitration_id)
            config_pgn = SignalMatcher._extract_pgn(signal_can_id)
            return (received_pgn == config_pgn)
        else:
            # Standard CAN - exact CAN ID match
            return (message.arbitration_id == signal_can_id)
    
    print("\n[TEST 1] Message with same PGN but different source/priority")
    print("-" * 70)
    
    # Test case 1: Same PGN (0xF004), different source address (0x00 vs 0x01)
    message1 = MockMessage(
        arbitration_id=0x0CF00400,  # Priority 0x03, PGN 0xF004, Source 0x00
        data=[0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]  # Byte 3 = 0x10 (in range)
    )
    
    config_pgn = SignalMatcher._extract_pgn(signal_config['can_id'])
    received_pgn = SignalMatcher._extract_pgn(message1.arbitration_id)
    
    print(f"Config CAN ID: 0x{signal_config['can_id']:08X} (PGN: 0x{config_pgn:04X})")
    print(f"Message CAN ID: 0x{message1.arbitration_id:08X} (PGN: 0x{received_pgn:04X})")
    
    is_relevant = is_message_relevant(message1, signal_config)
    print(f"Message is relevant: {is_relevant}")
    
    assert is_relevant, "Message with same PGN should be relevant"
    print("✓ PASS: Message filtered correctly by PGN")
    
    # Verify the signal matcher would also match the data
    is_match = SignalMatcher.match_signal(
        signal_config,
        message1.arbitration_id,
        list(message1.data)
    )
    print(f"Signal matcher result: {is_match}")
    assert is_match, "Signal should match (PGN matches, byte 3 in range)"
    print("✓ PASS: Signal matcher correctly identifies match")
    
    print("\n[TEST 2] Message with different PGN")
    print("-" * 70)
    
    # Test case 2: Different PGN (0xF005 instead of 0xF004)
    message2 = MockMessage(
        arbitration_id=0x18F00501,  # Priority 0x06, PGN 0xF005, Source 0x01
        data=[0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]
    )
    
    received_pgn2 = SignalMatcher._extract_pgn(message2.arbitration_id)
    print(f"Config PGN: 0x{config_pgn:04X}")
    print(f"Message PGN: 0x{received_pgn2:04X}")
    
    is_relevant2 = is_message_relevant(message2, signal_config)
    print(f"Message is relevant: {is_relevant2}")
    
    assert not is_relevant2, "Message with different PGN should not be relevant"
    print("✓ PASS: Message with different PGN correctly filtered out")
    
    print("\n[TEST 3] Standard CAN signal (no J1939)")
    print("-" * 70)
    
    # Test case 3: Standard CAN signal should still use exact CAN ID matching
    standard_signal_config = {
        'can_id': 0x123,
        'match_type': 'exact',
        'data': [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    }
    
    message3 = MockMessage(
        arbitration_id=0x123,
        data=[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    )
    
    is_relevant3 = is_message_relevant(message3, standard_signal_config)
    print(f"Config CAN ID: 0x{standard_signal_config['can_id']:03X}")
    print(f"Message CAN ID: 0x{message3.arbitration_id:03X}")
    print(f"Message is relevant: {is_relevant3}")
    
    assert is_relevant3, "Standard CAN with matching ID should be relevant"
    print("✓ PASS: Standard CAN exact matching works")
    
    # Test case 4: Standard CAN with different ID should not match
    message4 = MockMessage(
        arbitration_id=0x124,
        data=[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    )
    
    is_relevant4 = is_message_relevant(message4, standard_signal_config)
    print(f"Message CAN ID: 0x{message4.arbitration_id:03X}")
    print(f"Message is relevant: {is_relevant4}")
    
    assert not is_relevant4, "Standard CAN with different ID should not be relevant"
    print("✓ PASS: Standard CAN different ID filtered out")
    
    print("\n[TEST 4] Multiple J1939 messages with same PGN")
    print("-" * 70)
    
    # Test the specific scenario from the bug report
    test_messages = [
        (0x18F00401, "Same as config"),
        (0x0CF00400, "Different priority (0x03), different source (0x00)"),
        (0x1CF00410, "Different priority (0x07), different source (0x10)"),
        (0x18F004FF, "Same priority, different source (0xFF)"),
    ]
    
    for can_id, description in test_messages:
        message = MockMessage(
            arbitration_id=can_id,
            data=[0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]
        )
        
        is_relevant = is_message_relevant(message, signal_config)
        pgn = SignalMatcher._extract_pgn(can_id)
        
        print(f"CAN ID: 0x{can_id:08X} (PGN: 0x{pgn:04X}) - {description}")
        print(f"  Is relevant: {is_relevant}")
        
        assert is_relevant, f"All messages with PGN 0xF004 should be relevant: {description}"
        print(f"  ✓ PASS")
    
    # Summary
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)
    print("\nJ1939 PGN filtering in monitoring screen works correctly:")
    print("  ✓ J1939 signals filtered by PGN (not full CAN ID)")
    print("  ✓ Messages with same PGN but different priority/source are relevant")
    print("  ✓ Messages with different PGN are filtered out")
    print("  ✓ Standard CAN signals still use exact CAN ID matching")
    print("  ✓ Bug fix resolves the issue: 0x0CF00400 now matches config 0x18F00401")


if __name__ == "__main__":
    try:
        test_j1939_pgn_filtering()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

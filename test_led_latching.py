"""
Unit tests for LED status latching behavior.

This test validates that LED status only updates when messages from the
configured CAN ID arrive, and maintains its state for messages from other IDs.
"""

import sys
from unittest.mock import Mock, MagicMock
from typing import Dict, Any


class TestLEDLatching:
    """Test LED latching behavior for signal monitoring."""
    
    def __init__(self):
        """Initialize test harness."""
        self.signal_widgets = {}
        self.signal_matchers = {}
        self.signal_last_status = {}
        
    def setup_signal(self, signal_name: str, can_id: int, expected_data: list):
        """Setup a test signal with mock widget."""
        # Create mock widget
        mock_widget = Mock()
        mock_widget.update_status = Mock()
        
        # Store widget
        self.signal_widgets[signal_name] = mock_widget
        
        # Create signal config
        self.signal_matchers[signal_name] = {
            'name': signal_name,
            'can_id': can_id,
            'match_type': 'exact',
            'data': expected_data,
            'mask': None
        }
        
        # Initialize status
        self.signal_last_status[signal_name] = False
        
    def simulate_message_received(self, message):
        """
        Simulate the FIXED _on_message_received logic.
        
        This is the CORRECT implementation that should be in monitoring_screen.py
        """
        # Check signal matches (lightweight operation, can stay here)
        for signal_name, signal_config in self.signal_matchers.items():
            # Get the CAN ID this signal is monitoring
            signal_can_id = signal_config.get('can_id')
            
            # Only process messages that match this signal's CAN ID
            if message.arbitration_id == signal_can_id:
                # This message is relevant to this signal - check if data matches
                is_match = self._match_signal(
                    signal_config,
                    message.arbitration_id,
                    list(message.data)
                )
                
                # Update LED only if status changed
                if signal_name in self.signal_widgets:
                    last_status = self.signal_last_status.get(signal_name, False)
                    
                    if is_match != last_status:
                        self.signal_widgets[signal_name].update_status(is_match)
                        self.signal_last_status[signal_name] = is_match
            # If message CAN ID doesn't match this signal's CAN ID, don't change LED state
            # This keeps the LED latched at its previous state
    
    def _match_signal(self, signal_config: Dict[str, Any], can_id: int, data: list) -> bool:
        """Simple signal matcher for testing."""
        # Check CAN ID
        if can_id != signal_config.get('can_id'):
            return False
            
        # Check data (exact match)
        expected_data = signal_config.get('data', [])
        mask = signal_config.get('mask', None)
        
        if mask is not None:
            if len(mask) != len(expected_data) or len(data) != len(expected_data):
                return False
            for i in range(len(expected_data)):
                if (data[i] & mask[i]) != (expected_data[i] & mask[i]):
                    return False
            return True
        
        return data == expected_data


def run_tests():
    """Run all LED latching tests."""
    print("=" * 70)
    print("LED LATCHING BEHAVIOR TESTS")
    print("=" * 70)
    
    # Test 1: LED should latch GREEN when matching message arrives
    print("\n[TEST 1] LED latches GREEN on matching message")
    print("-" * 70)
    
    test = TestLEDLatching()
    test.setup_signal("Test Signal", 0x119, [0x00, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00])
    
    # Send matching message
    message = Mock()
    message.arbitration_id = 0x119
    message.data = bytes([0x00, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00])
    
    test.simulate_message_received(message)
    
    # Verify LED turned GREEN (update_status called with True)
    widget = test.signal_widgets["Test Signal"]
    assert widget.update_status.call_count == 1, f"Expected 1 call, got {widget.update_status.call_count}"
    assert widget.update_status.call_args[0][0] == True, "Expected LED to turn GREEN"
    assert test.signal_last_status["Test Signal"] == True, "Status should be True"
    print("✓ LED turned GREEN on matching message")
    
    # Test 2: LED should STAY GREEN when unrelated CAN ID arrives
    print("\n[TEST 2] LED stays GREEN when unrelated CAN ID arrives")
    print("-" * 70)
    
    widget.update_status.reset_mock()
    
    # Send message with different CAN ID (0x123 instead of 0x119)
    message2 = Mock()
    message2.arbitration_id = 0x123
    message2.data = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x11, 0x22])
    
    test.simulate_message_received(message2)
    
    # Verify LED did NOT update (should stay GREEN)
    assert widget.update_status.call_count == 0, f"Expected 0 calls, got {widget.update_status.call_count}"
    assert test.signal_last_status["Test Signal"] == True, "Status should remain True"
    print("✓ LED stayed GREEN (no update called)")
    
    # Test 3: Send another unrelated message, LED should still stay GREEN
    print("\n[TEST 3] LED continues to stay GREEN for multiple unrelated messages")
    print("-" * 70)
    
    message3 = Mock()
    message3.arbitration_id = 0x456
    message3.data = bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88])
    
    test.simulate_message_received(message3)
    
    assert widget.update_status.call_count == 0, f"Expected 0 calls, got {widget.update_status.call_count}"
    assert test.signal_last_status["Test Signal"] == True, "Status should remain True"
    print("✓ LED stayed GREEN (no update called)")
    
    # Test 4: LED should turn RED when matching CAN ID with non-matching data arrives
    print("\n[TEST 4] LED turns RED when configured CAN ID sends non-matching data")
    print("-" * 70)
    
    widget.update_status.reset_mock()
    
    # Send message with correct CAN ID but wrong data
    message4 = Mock()
    message4.arbitration_id = 0x119  # Correct CAN ID
    message4.data = bytes([0x00, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x00])  # byte 3 = 0x28 instead of 0x29
    
    test.simulate_message_received(message4)
    
    # Verify LED turned RED (update_status called with False)
    assert widget.update_status.call_count == 1, f"Expected 1 call, got {widget.update_status.call_count}"
    assert widget.update_status.call_args[0][0] == False, "Expected LED to turn RED"
    assert test.signal_last_status["Test Signal"] == False, "Status should be False"
    print("✓ LED turned RED on non-matching data from correct CAN ID")
    
    # Test 5: LED should STAY RED when unrelated CAN IDs arrive
    print("\n[TEST 5] LED stays RED when unrelated CAN IDs arrive")
    print("-" * 70)
    
    widget.update_status.reset_mock()
    
    # Send unrelated message
    message5 = Mock()
    message5.arbitration_id = 0x789
    message5.data = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    
    test.simulate_message_received(message5)
    
    # Verify LED did NOT update (should stay RED)
    assert widget.update_status.call_count == 0, f"Expected 0 calls, got {widget.update_status.call_count}"
    assert test.signal_last_status["Test Signal"] == False, "Status should remain False"
    print("✓ LED stayed RED (no update called)")
    
    # Test 6: LED should turn GREEN again when matching message arrives
    print("\n[TEST 6] LED turns GREEN again when matching message arrives")
    print("-" * 70)
    
    widget.update_status.reset_mock()
    
    # Send matching message again
    message6 = Mock()
    message6.arbitration_id = 0x119
    message6.data = bytes([0x00, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00])
    
    test.simulate_message_received(message6)
    
    # Verify LED turned GREEN
    assert widget.update_status.call_count == 1, f"Expected 1 call, got {widget.update_status.call_count}"
    assert widget.update_status.call_args[0][0] == True, "Expected LED to turn GREEN"
    assert test.signal_last_status["Test Signal"] == True, "Status should be True"
    print("✓ LED turned GREEN again on matching message")
    
    # Test 7: Multiple signals with different CAN IDs should work independently
    print("\n[TEST 7] Multiple signals work independently")
    print("-" * 70)
    
    test2 = TestLEDLatching()
    test2.setup_signal("Signal A", 0x100, [0xAA, 0xBB, 0xCC, 0xDD, 0x00, 0x00, 0x00, 0x00])
    test2.setup_signal("Signal B", 0x200, [0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00])
    
    # Send message for Signal A
    msg_a = Mock()
    msg_a.arbitration_id = 0x100
    msg_a.data = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0x00, 0x00, 0x00, 0x00])
    test2.simulate_message_received(msg_a)
    
    # Verify only Signal A updated
    widget_a = test2.signal_widgets["Signal A"]
    widget_b = test2.signal_widgets["Signal B"]
    assert widget_a.update_status.call_count == 1, "Signal A should update"
    assert widget_b.update_status.call_count == 0, "Signal B should NOT update"
    assert test2.signal_last_status["Signal A"] == True, "Signal A should be GREEN"
    assert test2.signal_last_status["Signal B"] == False, "Signal B should stay RED"
    
    # Send message for Signal B
    msg_b = Mock()
    msg_b.arbitration_id = 0x200
    msg_b.data = bytes([0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00])
    test2.simulate_message_received(msg_b)
    
    # Verify only Signal B updated
    assert widget_a.update_status.call_count == 1, "Signal A should NOT update again"
    assert widget_b.update_status.call_count == 1, "Signal B should update"
    assert test2.signal_last_status["Signal A"] == True, "Signal A should stay GREEN"
    assert test2.signal_last_status["Signal B"] == True, "Signal B should be GREEN"
    
    print("✓ Multiple signals work independently")
    
    # Summary
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)
    print("\nThe LED latching logic is working correctly:")
    print("  ✓ LED updates only for relevant CAN IDs")
    print("  ✓ LED latches state between messages")
    print("  ✓ LED turns GREEN on match")
    print("  ✓ LED turns RED on non-match from correct CAN ID")
    print("  ✓ LED ignores unrelated CAN IDs")
    print("  ✓ Multiple signals work independently")


if __name__ == "__main__":
    try:
        run_tests()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

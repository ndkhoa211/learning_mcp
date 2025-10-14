#!/usr/bin/env python3
"""Test script to verify input validation in server.py"""

from server import sanitize_topic_name

def test_sanitize_topic_name():
    """Test the topic name sanitization function"""

    test_cases = [
        # (input, expected_output)
        ("Apple and Tesla Stock Analysis", "Apple_and_Tesla_Stock_Analysis"),
        ("Simple", "Simple"),
        ("with   spaces", "with_spaces"),
        ("special!@#$%chars", "special_chars"),
        ("multiple___underscores", "multiple_underscores"),
        ("_leading_trailing_", "leading_trailing"),
        ("a" * 150, "a" * 100),  # Test length limit
        ("", "default"),  # Empty string
        ("123-numbers_ok.here", "123-numbers_ok.here"),
    ]

    print("Testing sanitize_topic_name():")
    print("-" * 70)

    for input_val, expected in test_cases:
        result = sanitize_topic_name(input_val)
        status = "[PASS]" if result == expected else "[FAIL]"

        # Truncate long strings for display
        display_input = input_val if len(input_val) <= 40 else input_val[:37] + "..."
        display_result = result if len(result) <= 40 else result[:37] + "..."

        print(f"{status} Input: '{display_input}'")
        print(f"  Result: '{display_result}'")
        if result != expected:
            print(f"  Expected: '{expected}'")
        print()

if __name__ == "__main__":
    test_sanitize_topic_name()
    print("\nValidation features added:")
    print("1. Topic name sanitization (spaces → underscores)")
    print("2. Content type validation (must be List[str])")
    print("3. Empty content detection")
    print("4. Individual string validation")
    print("5. Length limits (max 50,000 chars per item)")
    print("6. Detailed error messages with type information")

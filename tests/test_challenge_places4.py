"""
Test for Challenge 4: Parse the Response

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
    python tests/test_challenge_places4.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SAMPLE_RESPONSE = {
    "places": [
        {
            "displayName": {"text": "Aria Restaurant"},
            "formattedAddress": "1 Macquarie St, Sydney NSW 2000",
            "rating": 4.7,
            "priceLevel": "PRICE_LEVEL_VERY_EXPENSIVE",
            "currentOpeningHours": {"openNow": True},
            "types": ["restaurant", "food", "establishment", "point_of_interest"]
        },
        {
            "displayName": {"text": "Cafe Sydney"},
            "formattedAddress": "31 Alfred St, Sydney NSW 2000",
            "rating": 4.2,
            "priceLevel": "PRICE_LEVEL_MODERATE",
            "currentOpeningHours": {"openNow": False},
            "types": ["cafe", "food"]
        }
    ]
}


def test_empty_response():
    """Test 1: No places found"""
    from tools.google_places import format_places_response

    result = format_places_response({"places": []}, "unicorns in the moon")
    assert "No places found" in result, f"Expected 'No places found', got: {result}"
    print("✅ Test 1 passed: Empty response handled")


def test_place_name_included():
    """Test 2: Place name appears in output"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "Aria Restaurant" in result, f"Name missing from: {result}"
    assert "Cafe Sydney" in result, f"Second name missing from: {result}"
    print("✅ Test 2 passed: Place names included")


def test_address_included():
    """Test 3: Address appears in output"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "1 Macquarie St" in result, f"Address missing from: {result}"
    print("✅ Test 3 passed: Address included")


def test_rating_included():
    """Test 4: Rating appears in output"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "4.7" in result, f"Rating missing from: {result}"
    print("✅ Test 4 passed: Rating included")


def test_price_level_converted():
    """Test 5: Price level converted to $ symbols"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "$$$$" in result, f"$$$ missing from: {result}"
    assert "$$" in result, f"$$ missing from: {result}"
    print("✅ Test 5 passed: Price level converted to $ symbols")


def test_open_status_included():
    """Test 6: Open/closed status shown"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "Open" in result or "open" in result, f"Open status missing from: {result}"
    assert "Closed" in result or "closed" in result, f"Closed status missing from: {result}"
    print("✅ Test 6 passed: Open/closed status included")


def test_types_included():
    """Test 7: Place types included in output"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "restaurant" in result.lower(), f"Types missing from: {result}"
    print("✅ Test 7 passed: Types included")


def test_result_count_shown():
    """Test 8: Shows number of results found"""
    from tools.google_places import format_places_response

    result = format_places_response(SAMPLE_RESPONSE, "restaurants")
    assert "2" in result, f"Count missing from: {result}"
    print("✅ Test 8 passed: Result count shown")


def test_missing_fields_handled_gracefully():
    """Test 9: Missing fields don't crash"""
    from tools.google_places import format_places_response

    minimal_response = {
        "places": [
            {
                "displayName": {"text": "Mystery Place"}
                # Missing: formattedAddress, rating, priceLevel, currentOpeningHours, types
            }
        ]
    }

    try:
        result = format_places_response(minimal_response, "test")
        assert "Mystery Place" in result, "Name should still appear"
        print("✅ Test 9 passed: Missing fields handled gracefully")
    except Exception as e:
        print(f"❌ Test 9 failed: Crashed with missing fields: {e}")
        raise


if __name__ == "__main__":
    print("🗺️  Running Challenge 4 Tests: Parse the Response\n")

    try:
        test_empty_response()
        test_place_name_included()
        test_address_included()
        test_rating_included()
        test_price_level_converted()
        test_open_status_included()
        test_types_included()
        test_result_count_shown()
        test_missing_fields_handled_gracefully()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Challenge 4 Complete!")
        print("=" * 50)
        print("\nYou've learned:")
        print("  ✓ Parsing nested JSON responses")
        print("  ✓ Handling missing/None fields safely with .get()")
        print("  ✓ Formatting output for LLM consumption")
        print("  ✓ Mapping values (price level → $ symbols)")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("👉 Add format_places_response() to: tools/google_places.py")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        traceback.print_exc()

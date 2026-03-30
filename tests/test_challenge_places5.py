"""
Test for Challenge 5: Full Tool Integration

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
    python tests/test_challenge_places5.py
"""

import sys
import os
import json
import unittest.mock as mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


MOCK_API_RESPONSE = {
    "places": [
        {
            "displayName": {"text": "Test Cafe"},
            "formattedAddress": "123 Test St, Melbourne VIC 3000",
            "rating": 4.5,
            "priceLevel": "PRICE_LEVEL_MODERATE",
            "currentOpeningHours": {"openNow": True},
            "types": ["cafe", "food", "establishment"]
        }
    ]
}


def get_mock_response():
    mock_response = mock.Mock()
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status.return_value = None
    return mock_response


def test_tool_registered():
    """Test 1: Tool is registered in global registry"""
    from tools.tools import registry

    assert "google_places_search" in registry.tool_spec, "Tool not in tool_spec!"
    assert "google_places_search" in registry.tool_function, "Tool not in tool_function!"
    print("✅ Test 1 passed: Tool registered in registry")


def test_tool_spec_structure():
    """Test 2: Tool spec has correct structure"""
    from tools.tools import registry

    spec = registry.tool_spec["google_places_search"]
    assert spec["type"] == "function"
    assert spec["name"] == "google_places_search"
    assert "query" in spec["parameters"]["properties"]
    assert "max_results" in spec["parameters"]["properties"]
    print("✅ Test 2 passed: Tool spec structure is correct")
    print(f"   Spec: {json.dumps(spec, indent=2)}")


def test_full_execution_via_registry():
    """Test 3: Tool executes correctly via registry"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"
    from tools.tools import registry

    with mock.patch("requests.post", return_value=get_mock_response()):
        result = registry.execute(
            "google_places_search",
            json.dumps({"query": "cafes in Melbourne", "max_results": 3})
        )

    assert "Test Cafe" in result, f"Place name missing: {result}"
    assert "123 Test St" in result, f"Address missing: {result}"
    print("✅ Test 3 passed: Full execution via registry works")
    print(f"\nTool output:\n{result}")


def test_max_results_clamped_to_20():
    """Test 4: max_results > 20 is clamped to 20"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

    with mock.patch("requests.post", return_value=get_mock_response()) as mock_post:
        from importlib import reload
        import tools.google_places as gp
        reload(gp)
        gp.google_places_search(query="coffee", max_results=100)  # Too big!

        body = mock_post.call_args[1]["json"]
        assert body["maxResultCount"] <= 20, f"Not clamped: {body['maxResultCount']}"
        print(f"✅ Test 4 passed: max_results clamped to 20 (sent: {body['maxResultCount']})")


def test_max_results_clamped_to_1():
    """Test 5: max_results < 1 is clamped to 1"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

    with mock.patch("requests.post", return_value=get_mock_response()) as mock_post:
        from importlib import reload
        import tools.google_places as gp
        reload(gp)
        gp.google_places_search(query="coffee", max_results=0)  # Too small!

        body = mock_post.call_args[1]["json"]
        assert body["maxResultCount"] >= 1, f"Not clamped: {body['maxResultCount']}"
        print(f"✅ Test 5 passed: max_results clamped to 1 (sent: {body['maxResultCount']})")


def test_no_api_key_returns_error_string():
    """Test 6: Missing API key returns error string (doesn't crash)"""
    os.environ.pop("GOOGLE_PLACES_API_KEY", None)

    from importlib import reload
    import tools.google_places as gp
    reload(gp)

    result = gp.google_places_search(query="coffee", max_results=5)

    assert isinstance(result, str), "Should return a string"
    assert "error" in result.lower() or "key" in result.lower(), f"Should mention error: {result}"
    print(f"✅ Test 6 passed: Missing API key returns error string: '{result[:80]}'")


def test_api_error_returns_error_string():
    """Test 7: API errors return friendly error string"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

    import requests
    error_response = mock.Mock()
    error_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")

    with mock.patch("requests.post", return_value=error_response):
        from importlib import reload
        import tools.google_places as gp
        reload(gp)

        result = gp.google_places_search(query="coffee", max_results=5)

        assert isinstance(result, str), "Should return a string"
        assert "error" in result.lower(), f"Should mention error: {result}"
        print(f"✅ Test 7 passed: API error returns error string: '{result[:80]}'")


if __name__ == "__main__":
    print("🗺️  Running Challenge 5 Tests: Full Tool Integration\n")

    try:
        test_tool_registered()
        test_tool_spec_structure()
        test_full_execution_via_registry()
        test_max_results_clamped_to_20()
        test_max_results_clamped_to_1()
        test_no_api_key_returns_error_string()
        test_api_error_returns_error_string()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Challenge 5 Complete!")
        print("🗺️  You built a real Google Places tool!")
        print("=" * 50)
        print("\nYou've mastered:")
        print("  ✓ Full tool integration with @tool decorator")
        print("  ✓ Input validation (clamping max_results)")
        print("  ✓ Graceful error handling")
        print("  ✓ Real HTTP API integration")
        print("\n🚀 Next: Add GOOGLE_PLACES_API_KEY to .env and test with a real query!")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("👉 Make sure tools/google_places.py is complete")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        traceback.print_exc()

"""
Test for Challenge 3: Make the HTTP Request

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
    python tests/test_challenge_places3.py
"""

import sys
import os
import json
import unittest.mock as mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_raises_when_no_api_key():
    """Test 1: Raises ValueError when API key not in environment"""
    os.environ.pop("GOOGLE_PLACES_API_KEY", None)

    from tools.google_places import call_places_api

    try:
        call_places_api("coffee", 5)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "GOOGLE_PLACES_API_KEY" in str(e) or "key" in str(e).lower(), f"Error message: {e}"
        print("✅ Test 1 passed: ValueError raised when no API key")


def test_correct_url_used():
    """Test 2: POST request goes to the right URL"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key-123"

    mock_response = mock.Mock()
    mock_response.json.return_value = {"places": []}
    mock_response.raise_for_status.return_value = None

    with mock.patch("requests.post", return_value=mock_response) as mock_post:
        from importlib import reload
        import tools.google_places as gp
        reload(gp)
        gp.call_places_api("coffee", 5)

        call_args = mock_post.call_args
        url = call_args[0][0]
        assert "places.googleapis.com" in url, f"Wrong URL: {url}"
        assert "searchText" in url, f"Wrong endpoint: {url}"
        print(f"✅ Test 2 passed: Correct URL used: {url}")


def test_correct_headers_sent():
    """Test 3: Headers include API key and field mask"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "my-api-key"

    mock_response = mock.Mock()
    mock_response.json.return_value = {"places": []}
    mock_response.raise_for_status.return_value = None

    with mock.patch("requests.post", return_value=mock_response) as mock_post:
        from importlib import reload
        import tools.google_places as gp
        reload(gp)
        gp.call_places_api("coffee", 5)

        headers = mock_post.call_args[1]["headers"]
        assert headers.get("X-Goog-Api-Key") == "my-api-key", f"API key header wrong: {headers}"
        assert "X-Goog-FieldMask" in headers, f"Missing FieldMask header: {headers}"
        assert "displayName" in headers["X-Goog-FieldMask"], "displayName not in FieldMask"
        print("✅ Test 3 passed: Correct headers sent")


def test_correct_body_sent():
    """Test 4: Request body has textQuery and maxResultCount"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

    mock_response = mock.Mock()
    mock_response.json.return_value = {"places": []}
    mock_response.raise_for_status.return_value = None

    with mock.patch("requests.post", return_value=mock_response) as mock_post:
        from importlib import reload
        import tools.google_places as gp
        reload(gp)
        gp.call_places_api("sushi restaurants", 8)

        body = mock_post.call_args[1]["json"]
        assert body.get("textQuery") == "sushi restaurants", f"Wrong textQuery: {body}"
        assert body.get("maxResultCount") == 8, f"Wrong maxResultCount: {body}"
        print("✅ Test 4 passed: Correct request body sent")


def test_returns_parsed_json():
    """Test 5: Returns parsed JSON dict"""
    os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

    expected = {"places": [{"displayName": {"text": "Cafe Uno"}}]}

    mock_response = mock.Mock()
    mock_response.json.return_value = expected
    mock_response.raise_for_status.return_value = None

    with mock.patch("requests.post", return_value=mock_response):
        from importlib import reload
        import tools.google_places as gp
        reload(gp)
        result = gp.call_places_api("cafe", 1)

        assert result == expected, f"Expected {expected}, got {result}"
        print("✅ Test 5 passed: Returns parsed JSON dict")


if __name__ == "__main__":
    print("🗺️  Running Challenge 3 Tests: Make the HTTP Request\n")

    try:
        test_raises_when_no_api_key()
        test_correct_url_used()
        test_correct_headers_sent()
        test_correct_body_sent()
        test_returns_parsed_json()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Challenge 3 Complete!")
        print("=" * 50)
        print("\nYou've learned:")
        print("  ✓ Making HTTP POST requests with requests library")
        print("  ✓ Environment variables for API keys")
        print("  ✓ Setting headers and request body")
        print("  ✓ Error handling for missing config")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("👉 Add call_places_api() to: tools/google_places.py")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        traceback.print_exc()

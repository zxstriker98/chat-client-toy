"""
Test for Challenge 2: Build the Params Model

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
    python tests/test_challenge_places2.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_params_required_field():
    """Test 1: query is required"""
    from tools.google_places import GooglePlacesParams

    params = GooglePlacesParams(query="coffee shops in Melbourne")
    assert params.query == "coffee shops in Melbourne"
    print("✅ Test 1 passed: query field works")


def test_params_default_max_results():
    """Test 2: max_results defaults to 5"""
    from tools.google_places import GooglePlacesParams

    params = GooglePlacesParams(query="restaurants")
    assert params.max_results == 5, f"Expected 5, got: {params.max_results}"
    print("✅ Test 2 passed: max_results defaults to 5")


def test_params_custom_max_results():
    """Test 3: max_results can be overridden"""
    from tools.google_places import GooglePlacesParams

    params = GooglePlacesParams(query="restaurants", max_results=10)
    assert params.max_results == 10, f"Expected 10, got: {params.max_results}"
    print("✅ Test 3 passed: max_results can be set to 10")


def test_params_schema_has_required_fields():
    """Test 4: Schema has both fields"""
    from tools.google_places import GooglePlacesParams

    schema = GooglePlacesParams.model_json_schema()
    props = schema.get("properties", {})

    assert "query" in props, f"'query' missing from schema: {props.keys()}"
    assert "max_results" in props, f"'max_results' missing from schema: {props.keys()}"
    print("✅ Test 4 passed: Schema has both fields")
    print(f"   Schema: {schema}")


def test_params_schema_has_descriptions():
    """Test 5: Fields have descriptions"""
    from tools.google_places import GooglePlacesParams

    schema = GooglePlacesParams.model_json_schema()
    props = schema["properties"]

    query_desc = props["query"].get("description", "")
    assert len(query_desc) > 5, f"query description too short: '{query_desc}'"
    print(f"✅ Test 5 passed: query description: '{query_desc}'")


def test_tool_registered():
    """Test 6: Tool is registered in global registry"""
    from tools.tools import registry

    assert "google_places_search" in registry.tool_spec, "Tool not registered!"
    spec = registry.tool_spec["google_places_search"]
    assert spec["type"] == "function"
    assert spec["name"] == "google_places_search"
    print("✅ Test 6 passed: Tool registered in registry")


if __name__ == "__main__":
    print("🗺️  Running Challenge 2 Tests: Build the Params Model\n")

    try:
        test_params_required_field()
        test_params_default_max_results()
        test_params_custom_max_results()
        test_params_schema_has_required_fields()
        test_params_schema_has_descriptions()
        test_tool_registered()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Challenge 2 Complete!")
        print("=" * 50)
        print("\nYou've learned:")
        print("  ✓ Pydantic BaseModel with required fields")
        print("  ✓ Field() with default values and descriptions")
        print("  ✓ model_json_schema() generates the tool spec")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("👉 Create your solution in: tools/google_places.py")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        traceback.print_exc()

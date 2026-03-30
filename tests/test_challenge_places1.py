"""
Test for Challenge 1: Copy the Pattern (Greet Place Tool)

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
    python tests/test_challenge_places1.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_greet_place_returns_correct_string():
    """Test 1: Function returns correct greeting"""
    from tools.greet_place import greet_place

    result = greet_place("Sydney")
    assert result == "Hello from Sydney! 👋", f"Got: {result}"
    print("✅ Test 1 passed: greet_place('Sydney') works")


def test_greet_place_different_city():
    """Test 2: Works with different city names"""
    from tools.greet_place import greet_place

    result = greet_place("Tokyo")
    assert result == "Hello from Tokyo! 👋", f"Got: {result}"
    print("✅ Test 2 passed: greet_place('Tokyo') works")


def test_tool_registered_in_registry():
    """Test 3: Tool is registered in the global registry"""
    from tools.tools import registry

    assert "greet_place" in registry.tool_spec, "Tool not registered in tool_spec"
    assert "greet_place" in registry.tool_function, "Tool not registered in tool_function"
    print("✅ Test 3 passed: Tool registered in registry")


def test_tool_spec_structure():
    """Test 4: Tool spec has correct structure"""
    from tools.tools import registry

    spec = registry.tool_spec["greet_place"]

    assert spec["type"] == "function", f"Expected 'function', got: {spec['type']}"
    assert spec["name"] == "greet_place", f"Wrong name: {spec['name']}"
    assert "place_name" in spec["parameters"]["properties"], "Missing place_name parameter"
    print("✅ Test 4 passed: Tool spec is correctly structured")


def test_tool_execution_via_registry():
    """Test 5: Tool executes correctly via registry.execute()"""
    import json
    from tools.tools import registry

    result = registry.execute("greet_place", json.dumps({"place_name": "Paris"}))
    assert result == "Hello from Paris! 👋", f"Got: {result}"
    print("✅ Test 5 passed: Tool executes via registry correctly")


if __name__ == "__main__":
    print("🗺️  Running Challenge 1 Tests: Copy the Pattern\n")

    try:
        test_greet_place_returns_correct_string()
        test_greet_place_different_city()
        test_tool_registered_in_registry()
        test_tool_spec_structure()
        test_tool_execution_via_registry()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Challenge 1 Complete!")
        print("=" * 50)
        print("\nYou've learned:")
        print("  ✓ The @tool decorator pattern")
        print("  ✓ How Pydantic params work")
        print("  ✓ How the registry stores and executes tools")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("👉 Create your solution in: tools/greet_place.py")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        traceback.print_exc()

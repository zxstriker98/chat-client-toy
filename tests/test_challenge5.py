"""
Test file for Challenge 5: Mode System

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy/tests
    python test_challenge5.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from challenge5_solution import PromptMode, ModeController


def test_full_mode_includes_all():
    """Test 1: FULL mode includes all sections"""
    controller = ModeController(PromptMode.FULL)

    assert controller.should_include("identity")  == True
    assert controller.should_include("datetime")  == True
    assert controller.should_include("tools")     == True
    assert controller.should_include("memory")    == True
    assert controller.should_include("bootstrap") == True
    assert controller.should_include("workspace") == True
    print("✅ Test 1 passed: FULL mode includes all sections")


def test_minimal_mode_includes_only_core():
    """Test 2: MINIMAL mode includes only identity, datetime, tools"""
    controller = ModeController(PromptMode.MINIMAL)

    assert controller.should_include("identity") == True
    assert controller.should_include("datetime") == True
    assert controller.should_include("tools")    == True

    assert controller.should_include("memory")    == False
    assert controller.should_include("bootstrap") == False
    assert controller.should_include("workspace") == False
    print("✅ Test 2 passed: MINIMAL mode includes only core sections")


def test_none_mode_excludes_all():
    """Test 3: NONE mode excludes everything"""
    controller = ModeController(PromptMode.NONE)

    assert controller.should_include("identity")  == False
    assert controller.should_include("datetime")  == False
    assert controller.should_include("tools")     == False
    assert controller.should_include("memory")    == False
    assert controller.should_include("bootstrap") == False
    print("✅ Test 3 passed: NONE mode excludes all sections")


def test_filter_sections_full():
    """Test 4: filter_sections keeps all in FULL mode"""
    controller = ModeController(PromptMode.FULL)

    sections = {
        "identity":  "I am AI",
        "datetime":  "Friday",
        "tools":     "Tools list",
        "memory":    "RAG results",
        "bootstrap": "Workspace rules",
    }

    filtered = controller.filter_sections(sections)

    assert len(filtered) == 5, f"Expected 5 sections, got {len(filtered)}"
    assert "memory" in filtered
    assert "bootstrap" in filtered
    print("✅ Test 4 passed: filter_sections keeps all in FULL mode")


def test_filter_sections_minimal():
    """Test 5: filter_sections removes non-core in MINIMAL mode"""
    controller = ModeController(PromptMode.MINIMAL)

    sections = {
        "identity":  "I am AI",
        "datetime":  "Friday",
        "tools":     "Tools list",
        "memory":    "RAG results",
        "bootstrap": "Workspace rules",
    }

    filtered = controller.filter_sections(sections)

    assert "identity" in filtered,  "identity should be kept"
    assert "datetime" in filtered,  "datetime should be kept"
    assert "tools" in filtered,     "tools should be kept"
    assert "memory" not in filtered,    "memory should be removed"
    assert "bootstrap" not in filtered, "bootstrap should be removed"
    assert len(filtered) == 3, f"Expected 3 sections, got {len(filtered)}"
    print("✅ Test 5 passed: filter_sections removes non-core in MINIMAL mode")


def test_filter_sections_none():
    """Test 6: filter_sections returns empty dict in NONE mode"""
    controller = ModeController(PromptMode.NONE)

    sections = {
        "identity": "I am AI",
        "tools":    "Tools list",
        "memory":   "RAG results",
    }

    filtered = controller.filter_sections(sections)

    assert filtered == {}, f"Expected empty dict, got: {filtered}"
    print("✅ Test 6 passed: filter_sections returns empty in NONE mode")


def test_unknown_section_excluded():
    """Test 7: Unknown sections are always excluded"""
    controller = ModeController(PromptMode.FULL)

    assert controller.should_include("unknown_section") == False
    assert controller.should_include("random_stuff")    == False
    print("✅ Test 7 passed: Unknown sections excluded even in FULL mode")


def test_enum_values():
    """Test 8: Enum values are correct strings"""
    assert PromptMode.FULL.value    == "full"
    assert PromptMode.MINIMAL.value == "minimal"
    assert PromptMode.NONE.value    == "none"
    print("✅ Test 8 passed: Enum values are correct")


if __name__ == "__main__":
    print("Running Challenge 5 Tests...\n")

    try:
        test_full_mode_includes_all()
        test_minimal_mode_includes_only_core()
        test_none_mode_excludes_all()
        test_filter_sections_full()
        test_filter_sections_minimal()
        test_filter_sections_none()
        test_unknown_section_excluded()
        test_enum_values()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Challenge 5 Complete!")
        print("=" * 50)
        print("\nYou've mastered:")
        print("  ✓ Enum for type safety")
        print("  ✓ Set operations (in operator)")
        print("  ✓ Dictionary comprehension")
        print("  ✓ Mode-based configuration")

    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

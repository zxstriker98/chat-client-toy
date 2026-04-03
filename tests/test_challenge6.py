"""
Test file for Challenge 6: Full PromptBuilder Integration

Run with:
    cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
    python tests/test_challenge6.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_init():
    """Test 1: PromptBuilder initializes correctly"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder(mode="full", max_chars=32000)
    assert builder.mode == "full"
    assert builder.max_chars == 32000
    assert builder.sections == {}
    print("✅ Test 1 passed: __init__ works")


def test_add_identity_yaml():
    """Test 2: add_identity loads YAML config"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder()
    builder.add_identity("tests/test_identity.yaml")

    assert "identity" in builder.sections
    assert "Rovo Dev" in builder.sections["identity"]
    assert "code analysis" in builder.sections["identity"]
    print("✅ Test 2 passed: add_identity loads YAML")


def test_add_identity_returns_self():
    """Test 3: add_identity returns self for chaining"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder()
    result = builder.add_identity("tests/test_identity.yaml")
    assert result is builder, "Should return self for chaining"
    print("✅ Test 3 passed: Method chaining works")


def test_add_datetime():
    """Test 4: add_datetime adds current date/time"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder()
    builder.add_datetime()

    assert "datetime" in builder.sections
    assert "2026" in builder.sections["datetime"]
    assert "Current date" in builder.sections["datetime"]
    print("✅ Test 4 passed: add_datetime works")


def test_add_tools():
    """Test 5: add_tools formats tool registry"""
    from services.PromptBuilder import PromptBuilder
    from tools.tools import registry

    builder = PromptBuilder()
    builder.add_tools(registry)

    assert "tools" in builder.sections
    assert "read_file" in builder.sections["tools"]
    print("✅ Test 5 passed: add_tools works")


def test_add_memory():
    """Test 6: add_memory formats RAG results"""
    from services.PromptBuilder import PromptBuilder

    rag_results = [
        {
            "file_path": "data/menu.pdf",
            "chunk_text": "Our butter chicken is made with...",
            "page_num": 3,
            "score": 0.92
        }
    ]

    builder = PromptBuilder()
    builder.add_memory(rag_results)

    assert "memory" in builder.sections
    assert "menu.pdf" in builder.sections["memory"]
    assert "butter chicken" in builder.sections["memory"]
    print("✅ Test 6 passed: add_memory works")


def test_add_memory_empty_skipped():
    """Test 7: add_memory skips empty results"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder()
    builder.add_memory([])

    assert "memory" not in builder.sections
    print("✅ Test 7 passed: Empty memory skipped")


def test_build_full_mode():
    """Test 8: build() assembles all sections in FULL mode"""
    from services.PromptBuilder import PromptBuilder
    from tools.tools import registry

    builder = PromptBuilder(mode="full")
    builder.add_identity("tests/test_identity.yaml")
    builder.add_datetime()
    builder.add_tools(registry)

    prompt = builder.build()

    assert "## IDENTITY" in prompt
    assert "## DATETIME" in prompt
    assert "## TOOLS" in prompt
    assert "Rovo Dev" in prompt
    assert "2026" in prompt
    print("✅ Test 8 passed: build() assembles all sections")


def test_build_minimal_mode():
    """Test 9: build() only includes core sections in MINIMAL mode"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder(mode="minimal")
    builder.add_identity("tests/test_identity.yaml")
    builder.add_datetime()
    builder.add_memory([{"file_path": "f", "chunk_text": "Should NOT appear", "page_num": 1, "score": 0.9}])

    prompt = builder.build()

    assert "Rovo Dev" in prompt
    assert "Should NOT appear" not in prompt
    print("✅ Test 9 passed: MINIMAL mode excludes memory")


def test_build_none_mode():
    """Test 10: build() returns empty string in NONE mode"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder(mode="none")
    builder.add_identity("tests/test_identity.yaml")
    builder.add_datetime()

    prompt = builder.build()

    assert prompt == ""
    print("✅ Test 10 passed: NONE mode returns empty string")


def test_build_respects_max_chars():
    """Test 11: build() truncates when over max_chars"""
    from services.PromptBuilder import PromptBuilder

    builder = PromptBuilder(mode="full", max_chars=200)
    builder.add_identity("tests/test_identity.yaml")
    builder.add_memory([{
        "file_path": "data/big.pdf",
        "chunk_text": "X" * 5000,   # Very long!
        "page_num": 1,
        "score": 0.9
    }])

    prompt = builder.build()

    assert len(prompt) <= 200 or "truncated" in prompt.lower()
    print("✅ Test 11 passed: max_chars truncation works")


def test_method_chaining():
    """Test 12: All methods chain together"""
    from services.PromptBuilder import PromptBuilder
    from tools.tools import registry

    prompt = (
        PromptBuilder(mode="full")
        .add_identity("tests/test_identity.yaml")
        .add_datetime()
        .add_tools(registry)
        .build()
    )

    assert isinstance(prompt, str)
    assert len(prompt) > 0
    print("✅ Test 12 passed: Method chaining works end-to-end")


if __name__ == "__main__":
    print("🏆 Running Challenge 6 Tests: Full PromptBuilder\n")

    try:
        test_init()
        test_add_identity_yaml()
        test_add_identity_returns_self()
        test_add_datetime()
        test_add_tools()
        test_add_memory()
        test_add_memory_empty_skipped()
        test_build_full_mode()
        test_build_minimal_mode()
        test_build_none_mode()
        test_build_respects_max_chars()
        test_method_chaining()

        print("\n" + "=" * 55)
        print("🎉 ALL TESTS PASSED! Challenge 6 Complete!")
        print("🏆 You've completed the full KAN-8 challenge series!")
        print("=" * 55)
        print("\nYou've mastered:")
        print("  ✓ Builder pattern with method chaining")
        print("  ✓ File I/O and config loading")
        print("  ✓ Tool spec formatting")
        print("  ✓ RAG result injection")
        print("  ✓ Smart truncation")
        print("  ✓ Mode-based section filtering")
        print("  ✓ Full system integration")

    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

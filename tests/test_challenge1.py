"""
Test file for Challenge 1: String Section Builder

Run with: python -m pytest tests/test_challenge1.py -v
Or simply: python tests/test_challenge1.py
"""

def test_single_section():
    """Test 1: Single section"""
    from challenge1_solution import SectionBuilder
    
    builder = SectionBuilder()
    builder.add_section("test", "content")
    result = builder.build()
    
    expected = "## TEST\ncontent\n\n"
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"
    print("✅ Test 1 passed: Single section")


def test_multiple_sections_with_chaining():
    """Test 2: Multiple sections + method chaining"""
    from challenge1_solution import SectionBuilder
    
    builder = SectionBuilder()
    result = builder.add_section("first", "A").add_section("second", "B").build()
    
    expected = "## FIRST\nA\n\n## SECOND\nB\n\n"
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"
    print("✅ Test 2 passed: Multiple sections with chaining")


def test_empty_builder():
    """Test 3: Empty builder"""
    from challenge1_solution import SectionBuilder
    
    builder = SectionBuilder()
    result = builder.build()
    
    assert result == "", f"Expected empty string, got: {result}"
    print("✅ Test 3 passed: Empty builder")


def test_section_order_preserved():
    """Test 4: Section order is preserved"""
    from challenge1_solution import SectionBuilder
    
    builder = SectionBuilder()
    builder.add_section("third", "3")
    builder.add_section("first", "1")
    builder.add_section("second", "2")
    
    result = builder.build()
    
    # Check that "third" appears before "first"
    third_pos = result.find("## THIRD")
    first_pos = result.find("## FIRST")
    second_pos = result.find("## SECOND")
    
    assert third_pos < first_pos < second_pos, "Section order not preserved"
    print("✅ Test 4 passed: Section order preserved")


if __name__ == "__main__":
    print("Running Challenge 1 Tests...\n")
    
    try:
        test_single_section()
        test_multiple_sections_with_chaining()
        test_empty_builder()
        test_section_order_preserved()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! Challenge 1 Complete!")
        print("="*50)
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\nCreate your solution in: tests/challenge1_solution.py")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

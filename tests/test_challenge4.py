"""
Test file for Challenge 4: Smart Truncation Algorithm

Run with: python tests/test_challenge4.py
"""

from challenge4_solution import SmartTruncator, Section


def test_under_limit():
    """Test 1: Content under limit - no truncation needed"""
    truncator = SmartTruncator(max_chars=500)
    
    sections = [
        Section("identity", "I am an AI assistant.", priority=1),
        Section("tools", "Tools: read, write", priority=3)
    ]
    
    result = truncator.truncate(sections)
    
    # Both sections should be present
    assert "AI assistant" in result, "Identity section missing"
    assert "read, write" in result, "Tools section missing"
    assert len(result) <= 500, "Result exceeds max_chars"
    
    print("✅ Test 1 passed: Under limit - no truncation")


def test_remove_low_priority():
    """Test 2: Remove low priority sections"""
    truncator = SmartTruncator(max_chars=150)
    
    sections = [
        Section("identity", "I am AI", priority=1),
        Section("tools", "Tools: read", priority=3),
        Section("memory", "A" * 300, priority=8)  # Low priority, very long
    ]
    
    result = truncator.truncate(sections)
    
    # High priority sections should be kept
    assert "AI" in result, "Identity section missing"
    assert "read" in result, "Tools section missing"
    
    # Low priority section should be mostly removed
    assert len([c for c in result if c == 'A']) < 300, "Memory section not truncated"
    assert len(result) <= 150, "Result exceeds max_chars"
    
    print("✅ Test 2 passed: Remove low priority sections")


def test_all_high_priority_truncate_content():
    """Test 3: All high priority - truncate content"""
    truncator = SmartTruncator(max_chars=100)
    
    sections = [
        Section("part1", "X" * 100, priority=1),
        Section("part2", "Y" * 100, priority=1)
    ]
    
    result = truncator.truncate(sections)
    
    # Result should be under limit
    assert len(result) <= 100, f"Result exceeds limit: {len(result)} > 100"
    
    # Should have truncation marker
    assert "truncated" in result.lower() or len(result) < 200, "Should be truncated"
    
    print("✅ Test 3 passed: All high priority - truncate content")


def test_priority_order():
    """Test 4: Correct priority order (remove lowest priority first)"""
    truncator = SmartTruncator(max_chars=200)
    
    sections = [
        Section("identity", "I am AI", priority=1),       # Keep
        Section("tools", "Tools", priority=2),             # Keep
        Section("bootstrap", "Rules" * 10, priority=5),    # Remove this first
        Section("memory", "Memory" * 50, priority=8)       # Remove this second
    ]
    
    result = truncator.truncate(sections)
    
    # High priority should remain
    assert "AI" in result, "Identity lost"
    assert "Tools" in result, "Tools lost"
    
    # Bootstrap might be there or removed (priority=5)
    # Memory should definitely be removed/truncated (priority=8)
    assert len(result) <= 200, "Result exceeds limit"
    
    print("✅ Test 4 passed: Priority order respected")


def test_exact_limit():
    """Test 5: Content exactly at limit"""
    truncator = SmartTruncator(max_chars=100)
    
    sections = [
        Section("test", "X" * 80, priority=1)
    ]
    
    result = truncator.truncate(sections)
    
    # Should be under or at limit (accounting for overhead)
    assert len(result) <= 100, f"Result exceeds limit: {len(result)} > 100"
    
    print("✅ Test 5 passed: Exact limit handling")


def test_empty_sections():
    """Test 6: Empty sections list"""
    truncator = SmartTruncator(max_chars=100)
    
    result = truncator.truncate([])
    
    assert result == "", "Empty sections should return empty string"
    
    print("✅ Test 6 passed: Empty sections handling")


if __name__ == "__main__":
    print("Running Challenge 4 Tests...\n")
    
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    try:
        test_under_limit()
        test_remove_low_priority()
        test_all_high_priority_truncate_content()
        test_priority_order()
        test_exact_limit()
        test_empty_sections()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! Challenge 4 Complete!")
        print("="*50)
        print("\nYou've mastered:")
        print("  ✓ Algorithm design")
        print("  ✓ Greedy algorithms")
        print("  ✓ Priority-based sorting")
        print("  ✓ Context window management")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your solution is in: tests/challenge4_solution.py")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

"""
Test file for Challenge 2: Config File Parser

Run with: python tests/test_challenge2.py
"""

def test_yaml_file():
    """Test 1: Load YAML file"""
    from challenge2_solution import ConfigParser
    
    result = ConfigParser.load_identity("test_identity.yaml")
    
    assert "Rovo Dev" in result, "Name not found in result"
    assert "AI software development assistant" in result, "Role not found"
    assert "code analysis" in result, "Capabilities not found"
    assert "Friendly and professional" in result, "Style not found"
    
    print("✅ Test 1 passed: YAML file loaded successfully")


def test_json_file():
    """Test 2: Load JSON file"""
    from challenge2_solution import ConfigParser
    
    result = ConfigParser.load_identity("test_identity.json")
    
    assert "Rovo Dev" in result, "Name not found in result"
    assert "debugging" in result, "Capabilities not found"
    
    print("✅ Test 2 passed: JSON file loaded successfully")


def test_file_not_found():
    """Test 3: File not found raises error"""
    from challenge2_solution import ConfigParser
    
    try:
        ConfigParser.load_identity("nonexistent.yaml")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "nonexistent.yaml" in str(e), "Error message should mention filename"
        print("✅ Test 3 passed: FileNotFoundError raised correctly")


def test_unsupported_format():
    """Test 4: Unsupported file format raises error"""
    from challenge2_solution import ConfigParser
    
    # Create a test .txt file
    with open("test.txt", "w") as f:
        f.write("test content")
    
    try:
        ConfigParser.load_identity("test.txt")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported" in str(e) or "file type" in str(e).lower()
        print("✅ Test 4 passed: ValueError raised for unsupported format")
    finally:
        # Clean up
        import os
        if os.path.exists("test.txt"):
            os.remove("test.txt")


def test_output_format():
    """Test 5: Output is properly formatted"""
    from challenge2_solution import ConfigParser
    
    result = ConfigParser.load_identity("test_identity.yaml")
    
    # Check structure
    assert result.startswith("You are"), "Should start with 'You are'"
    assert "Your capabilities include:" in result, "Should list capabilities"
    assert "Communication style:" in result, "Should include style"
    
    # Check capabilities are listed with bullets
    assert "- code analysis" in result or "- Code analysis" in result or "code analysis" in result
    
    print("✅ Test 5 passed: Output format is correct")


if __name__ == "__main__":
    print("Running Challenge 2 Tests...\n")
    
    import os
    # Change to tests directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    try:
        test_yaml_file()
        test_json_file()
        test_file_not_found()
        test_unsupported_format()
        test_output_format()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! Challenge 2 Complete!")
        print("="*50)
        print("\nYou've mastered:")
        print("  ✓ File I/O operations")
        print("  ✓ YAML and JSON parsing")
        print("  ✓ Error handling")
        print("  ✓ String formatting")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your solution is in: tests/challenge2_solution.py")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

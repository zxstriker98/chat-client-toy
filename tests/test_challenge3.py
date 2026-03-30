"""
Test file for Challenge 3: Tool Registry Formatter

Run with: python tests/test_challenge3.py
"""

def test_single_tool():
    """Test 1: Format a single tool"""
    from challenge3_solution import ToolFormatter
    
    # This matches what Pydantic generates from your actual tools
    tool_spec = {
        "read_file": {
            "type": "function",
            "name": "read_file",
            "description": "Read the contents of a file at the given path (large files are truncated)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read",
                        "title": "Path"
                    }
                },
                "required": ["path"],
                "title": "ReadFileParams"
            }
        }
    }
    
    result = ToolFormatter.format_tools(tool_spec)
    
    assert "read_file" in result, "Tool name missing"
    assert "Read the contents of a file" in result, "Description missing"
    assert "file path to read" in result.lower(), "Parameter description missing"
    assert "required" in result.lower(), "Required marker missing"
    
    print("✅ Test 1 passed: Single tool formatted correctly")


def test_multiple_tools():
    """Test 2: Format multiple tools"""
    from challenge3_solution import ToolFormatter
    
    # Realistic tool specs from your actual chat-client-toy project
    tool_spec = {
        "read_file": {
            "type": "function",
            "name": "read_file",
            "description": "Read the contents of a file at the given path (large files are truncated)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read"
                    }
                },
                "required": ["path"]
            }
        },
        "run_bash": {
            "type": "function",
            "name": "run_bash",
            "description": "Execute a bash command and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    }
    
    result = ToolFormatter.format_tools(tool_spec)
    
    assert "read_file" in result, "First tool missing"
    assert "run_bash" in result, "Second tool missing"
    assert "bash command to execute" in result.lower(), "Second tool parameter missing"
    
    print("✅ Test 2 passed: Multiple tools formatted correctly")


def test_empty_registry():
    """Test 3: Handle empty tool registry"""
    from challenge3_solution import ToolFormatter
    
    result = ToolFormatter.format_tools({})
    
    assert result == "" or result.strip() == "", "Empty registry should return empty string"
    
    print("✅ Test 3 passed: Empty registry handled correctly")


def test_optional_vs_required_parameters():
    """Test 4: Distinguish required vs optional parameters"""
    from challenge3_solution import ToolFormatter
    
    tool_spec = {
        "api_call": {
            "name": "api_call",
            "description": "Make API call",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "API endpoint"},
                    "method": {"type": "string", "description": "HTTP method"},
                    "headers": {"type": "object", "description": "Optional headers"}
                },
                "required": ["url", "method"]
            }
        }
    }
    
    result = ToolFormatter.format_tools(tool_spec)
    
    # Check that url and method are marked as required
    lines = result.split('\n')
    url_line = [l for l in lines if 'url' in l.lower()]
    method_line = [l for l in lines if 'method' in l.lower()]
    headers_line = [l for l in lines if 'headers' in l.lower()]
    
    assert len(url_line) > 0, "URL parameter missing"
    assert len(method_line) > 0, "Method parameter missing"
    assert len(headers_line) > 0, "Headers parameter missing"
    
    # url and method should have 'required', headers should not
    assert any('required' in l for l in url_line), "URL should be marked required"
    assert any('required' in l for l in method_line), "Method should be marked required"
    
    print("✅ Test 4 passed: Required vs optional parameters distinguished")


def test_output_format_structure():
    """Test 5: Check output structure"""
    from challenge3_solution import ToolFormatter
    
    tool_spec = {
        "test_tool": {
            "name": "test_tool",
            "description": "A test tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "First param"}
                },
                "required": ["param1"]
            }
        }
    }
    
    result = ToolFormatter.format_tools(tool_spec)
    
    # Should start with header
    assert result.startswith("## Available Tools"), "Should start with header"
    
    # Should have tool name in bold
    assert "**test_tool**" in result, "Tool name should be in bold"
    
    # Should have Parameters section
    assert "Parameters:" in result, "Should have Parameters section"
    
    # Should have parameter formatted with dash
    assert "- param1" in result, "Parameter should start with dash"
    
    print("✅ Test 5 passed: Output format structure is correct")


if __name__ == "__main__":
    print("Running Challenge 3 Tests...\n")
    
    import os
    # Change to tests directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    try:
        test_single_tool()
        test_multiple_tools()
        test_empty_registry()
        test_optional_vs_required_parameters()
        test_output_format_structure()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! Challenge 3 Complete!")
        print("="*50)
        print("\nYou've mastered:")
        print("  ✓ Dictionary traversal")
        print("  ✓ Nested data structures")
        print("  ✓ Schema parsing")
        print("  ✓ Conditional formatting")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your solution is in: tests/challenge3_solution.py")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

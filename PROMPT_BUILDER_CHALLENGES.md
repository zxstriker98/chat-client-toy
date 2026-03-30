# 🎯 PromptBuilder LeetCode-Style Challenges

Welcome to the KAN-8 learning path! Complete these challenges in order to build your `PromptBuilder` class step by step.

---

## 🏆 Challenge 1: String Section Builder (Easy)

**Difficulty**: Easy  
**Time**: 15-20 minutes  
**Concepts**: Builder pattern, dictionaries, string formatting

### Problem Statement
Create a `SectionBuilder` class that can collect named text sections and combine them with headers.

### Requirements
```python
class SectionBuilder:
    """
    A builder that collects named sections and formats them with headers.
    
    Example:
        builder = SectionBuilder()
        builder.add_section("greeting", "Hello, World!")
        builder.add_section("info", "This is a test.")
        result = builder.build()
        
        # Output:
        # ## GREETING
        # Hello, World!
        # 
        # ## INFO
        # This is a test.
    """
    
    def __init__(self):
        # TODO: Initialize storage for sections
        pass
    
    def add_section(self, name: str, content: str) -> "SectionBuilder":
        # TODO: Store the section
        # Return self for method chaining
        pass
    
    def build(self) -> str:
        # TODO: Combine all sections with headers
        # Format: ## SECTION_NAME\n{content}\n\n
        pass
```

### Test Cases
```python
# Test 1: Single section
builder = SectionBuilder()
builder.add_section("test", "content")
assert builder.build() == "## TEST\ncontent\n\n"

# Test 2: Multiple sections + chaining
builder = SectionBuilder()
result = builder.add_section("first", "A").add_section("second", "B").build()
assert "## FIRST\nA\n\n## SECOND\nB\n\n" == result

# Test 3: Empty builder
builder = SectionBuilder()
assert builder.build() == ""
```

### Hints
- Use a dictionary to store sections: `{name: content}`
- Return `self` to enable method chaining
- Use `.upper()` for section names
- Join sections with `\n\n`

### Learning Goals
✅ Understand the Builder pattern  
✅ Practice method chaining  
✅ String formatting and joining

---

## 🏆 Challenge 2: Config File Parser (Medium)

**Difficulty**: Medium  
**Time**: 20-30 minutes  
**Concepts**: File I/O, YAML/JSON parsing, error handling

### Problem Statement
Create a `ConfigParser` class that can load identity configuration from YAML or JSON files and format it as a prompt section.

### Requirements
```python
import yaml
import json
from pathlib import Path
from typing import Dict, Any

class ConfigParser:
    """
    Parse identity configuration from YAML or JSON files.
    
    Expected config structure:
    {
        "name": "Assistant Name",
        "role": "Description of role",
        "capabilities": ["skill1", "skill2"],
        "style": "Communication style"
    }
    """
    
    @staticmethod
    def load_identity(config_path: str) -> str:
        """
        Load config file and format as identity section.
        
        Args:
            config_path: Path to .yaml or .json file
            
        Returns:
            Formatted identity text
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If unsupported file type
        """
        # TODO: Implement this
        pass
```

### Expected Output Format
```
You are {name}, a {role}.

Your capabilities include:
- {capability1}
- {capability2}

Communication style: {style}
```

### Test Cases

**Create test config files first:**

`test_identity.yaml`:
```yaml
name: "Rovo Dev"
role: "AI software development assistant"
capabilities:
  - code analysis
  - debugging
  - documentation
style: "Friendly and professional"
```

`test_identity.json`:
```json
{
  "name": "Rovo Dev",
  "role": "AI software development assistant",
  "capabilities": ["code analysis", "debugging", "documentation"],
  "style": "Friendly and professional"
}
```

**Test code:**
```python
# Test 1: YAML file
result = ConfigParser.load_identity("test_identity.yaml")
assert "Rovo Dev" in result
assert "code analysis" in result

# Test 2: JSON file
result = ConfigParser.load_identity("test_identity.json")
assert "AI software development assistant" in result

# Test 3: File not found
try:
    ConfigParser.load_identity("nonexistent.yaml")
    assert False, "Should raise FileNotFoundError"
except FileNotFoundError:
    pass

# Test 4: Unsupported format
try:
    ConfigParser.load_identity("test.txt")
    assert False, "Should raise ValueError"
except ValueError:
    pass
```

### Hints
- Use `Path(config_path).suffix` to check file extension
- Use `yaml.safe_load()` for YAML files
- Use `json.load()` for JSON files
- Handle missing keys gracefully (use `.get()` with defaults)

### Learning Goals
✅ File I/O operations  
✅ YAML and JSON parsing  
✅ Error handling and validation  
✅ String formatting with dynamic data

---

## 🏆 Challenge 3: Tool Registry Formatter (Medium)

**Difficulty**: Medium  
**Time**: 25-35 minutes  
**Concepts**: Dictionary iteration, schema parsing, formatting

### Problem Statement
Create a `ToolFormatter` that converts a `ToolRegistry` into a human-readable prompt section.

### Context
The `ToolRegistry` in your project stores tools like this:
```python
registry.tool_spec = {
    "read_file": {
        "name": "read_file",
        "description": "Read contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path to read"
                }
            },
            "required": ["path"]
        }
    }
}
```

### Requirements
```python
from typing import Dict, Any

class ToolFormatter:
    """Format tool specifications as readable text."""
    
    @staticmethod
    def format_tools(tool_spec: Dict[str, Dict[str, Any]]) -> str:
        """
        Convert tool specs to formatted text.
        
        Expected output format:
        ## Available Tools
        
        **tool_name**: Description
          Parameters:
          - param_name (type): description
          - param_name (type, required): description
        
        Args:
            tool_spec: Dictionary of tool specifications
            
        Returns:
            Formatted tool documentation
        """
        # TODO: Implement this
        pass
```

### Test Cases
```python
# Test 1: Single tool
tool_spec = {
    "read_file": {
        "name": "read_file",
        "description": "Read file contents",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"}
            },
            "required": ["path"]
        }
    }
}

result = ToolFormatter.format_tools(tool_spec)
assert "read_file" in result
assert "File path" in result
assert "required" in result.lower()

# Test 2: Multiple tools
tool_spec = {
    "read_file": {...},
    "run_bash": {
        "name": "run_bash",
        "description": "Execute bash command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds"}
            },
            "required": ["command"]
        }
    }
}

result = ToolFormatter.format_tools(tool_spec)
assert "read_file" in result
assert "run_bash" in result

# Test 3: Empty registry
result = ToolFormatter.format_tools({})
assert result == "" or "No tools" in result
```

### Hints
- Iterate over `tool_spec.items()`
- Check if param is in `required` list to mark it
- Use proper indentation for readability
- Consider using f-strings for formatting

### Learning Goals
✅ Dictionary traversal  
✅ Schema parsing  
✅ Text formatting and indentation  
✅ Conditional formatting (required vs optional)

---

## 🏆 Challenge 4: Smart Truncation Algorithm (Hard)

**Difficulty**: Hard  
**Time**: 30-45 minutes  
**Concepts**: Algorithms, priority queues, text manipulation

### Problem Statement
Implement an intelligent truncation algorithm that keeps the most important sections when the total prompt exceeds a character limit.

### Requirements
```python
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class Section:
    name: str
    content: str
    priority: int  # Lower number = higher priority (1 is most important)

class SmartTruncator:
    """
    Intelligently truncate a prompt to fit within character limits
    while preserving the most important sections.
    """
    
    def __init__(self, max_chars: int):
        self.max_chars = max_chars
    
    def truncate(self, sections: List[Section]) -> str:
        """
        Truncate sections to fit within max_chars.
        
        Strategy:
        1. Always keep priority 1 sections (identity, datetime)
        2. Remove lower-priority sections first
        3. If still too long, truncate individual sections from lowest priority
        
        Args:
            sections: List of Section objects
            
        Returns:
            Combined text that fits within max_chars
        """
        # TODO: Implement this algorithm
        pass
    
    def _calculate_total_length(self, sections: List[Section]) -> int:
        """Helper: Calculate total character count."""
        # TODO: Implement
        pass
    
    def _truncate_section(self, section: Section, max_len: int) -> Section:
        """Helper: Truncate a single section to max_len characters."""
        # TODO: Implement
        pass
```

### Test Cases
```python
# Test 1: Under limit - no truncation needed
sections = [
    Section("identity", "I am an AI assistant.", priority=1),
    Section("tools", "Tools: read, write", priority=2)
]
truncator = SmartTruncator(max_chars=100)
result = truncator.truncate(sections)
assert len(result) <= 100
assert "AI assistant" in result
assert "Tools" in result

# Test 2: Over limit - remove low priority
sections = [
    Section("identity", "I am an AI.", priority=1),
    Section("memory", "A" * 500, priority=3),  # Low priority, long
    Section("tools", "Tools: X", priority=2)
]
truncator = SmartTruncator(max_chars=100)
result = truncator.truncate(sections)
assert len(result) <= 100
assert "AI" in result  # Priority 1 kept
assert len([c for c in result if c == 'A']) < 500  # Memory truncated/removed

# Test 3: All high priority - truncate content
sections = [
    Section("part1", "X" * 1000, priority=1),
    Section("part2", "Y" * 1000, priority=1)
]
truncator = SmartTruncator(max_chars=500)
result = truncator.truncate(sections)
assert len(result) <= 500
```

### Hints
- Sort sections by priority first
- Use a greedy algorithm: keep highest priority sections first
- Consider adding "...[truncated]" markers
- Calculate total length including section headers

### Learning Goals
✅ Algorithm design  
✅ Priority-based decision making  
✅ Text manipulation  
✅ Greedy algorithms

---

## 🏆 Challenge 5: Mode System (Medium)

**Difficulty**: Medium  
**Time**: 20-30 minutes  
**Concepts**: Enums, conditional logic, configuration

### Problem Statement
Implement a mode system that controls which sections are included in the final prompt.

### Requirements
```python
from enum import Enum
from typing import Set

class PromptMode(Enum):
    """Different prompt construction modes."""
    FULL = "full"        # All sections
    MINIMAL = "minimal"  # Only identity, datetime, tools
    NONE = "none"        # Empty prompt

class ModeController:
    """Controls which sections to include based on mode."""
    
    # Define which sections are allowed in each mode
    MODE_SECTIONS = {
        PromptMode.FULL: {"identity", "datetime", "tools", "memory", "bootstrap", "workspace"},
        PromptMode.MINIMAL: {"identity", "datetime", "tools"},
        PromptMode.NONE: set()
    }
    
    def __init__(self, mode: PromptMode):
        self.mode = mode
    
    def should_include(self, section_name: str) -> bool:
        """Check if a section should be included in current mode."""
        # TODO: Implement
        pass
    
    def filter_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Filter sections dict based on current mode."""
        # TODO: Implement
        pass
```

### Test Cases
```python
# Test 1: FULL mode includes everything
controller = ModeController(PromptMode.FULL)
assert controller.should_include("identity") == True
assert controller.should_include("memory") == True
assert controller.should_include("bootstrap") == True

# Test 2: MINIMAL mode excludes some
controller = ModeController(PromptMode.MINIMAL)
assert controller.should_include("identity") == True
assert controller.should_include("tools") == True
assert controller.should_include("memory") == False
assert controller.should_include("bootstrap") == False

# Test 3: NONE mode excludes all
controller = ModeController(PromptMode.NONE)
assert controller.should_include("identity") == False

# Test 4: Filter sections dict
controller = ModeController(PromptMode.MINIMAL)
sections = {
    "identity": "I am AI",
    "tools": "Tools: X",
    "memory": "Some memories",
    "bootstrap": "Workspace rules"
}
filtered = controller.filter_sections(sections)
assert "identity" in filtered
assert "tools" in filtered
assert "memory" not in filtered
assert "bootstrap" not in filtered
```

### Hints
- Use Enum for type safety
- Use sets for efficient lookups
- Dictionary comprehension for filtering

### Learning Goals
✅ Enum usage  
✅ Configuration patterns  
✅ Set operations  
✅ Dictionary filtering

---

## 🏆 Challenge 6: Full PromptBuilder (Hard)

**Difficulty**: Hard  
**Time**: 60-90 minutes  
**Concepts**: Integration, class design, all previous concepts

### Problem Statement
Now combine everything! Create the complete `PromptBuilder` class using all the components you've built.

### Requirements
```python
"""
File: services/PromptBuilder.py

Combine all previous challenges into a complete PromptBuilder.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json

class PromptBuilder:
    """
    Dynamically build system prompts from multiple sections.
    
    Usage:
        builder = PromptBuilder(mode="full", max_chars=32000)
        builder.add_identity("config.yaml")
        builder.add_tools(tool_registry)
        builder.add_datetime()
        builder.add_memory(rag_results)
        prompt = builder.build()
    """
    
    def __init__(self, mode: str = "full", max_chars: int = 32000):
        """
        Initialize the prompt builder.
        
        Args:
            mode: "full", "minimal", or "none"
            max_chars: Maximum characters in final prompt
        """
        # TODO: Use your previous solutions here
        pass
    
    def add_identity(self, config_path: str) -> "PromptBuilder":
        """Load identity from config file (Challenge 2)."""
        # TODO: Use ConfigParser from Challenge 2
        pass
    
    def add_tools(self, tool_registry) -> "PromptBuilder":
        """Format tools from registry (Challenge 3)."""
        # TODO: Use ToolFormatter from Challenge 3
        pass
    
    def add_datetime(self) -> "PromptBuilder":
        """Add current date/time section."""
        # TODO: Format like "Current time: Friday, 2026-03-27 09:38:53"
        pass
    
    def add_memory(self, rag_results: List[Dict[str, Any]]) -> "PromptBuilder":
        """
        Add RAG results as memory section.
        
        rag_results format:
        [
            {
                "file_path": "data/doc.pdf",
                "chunk_text": "Content here...",
                "page_num": 5,
                "score": 0.85
            }
        ]
        """
        # TODO: Format RAG results nicely
        pass
    
    def add_bootstrap(self, workspace_dir: str) -> "PromptBuilder":
        """
        Load workspace rules from AGENTS.md and config files.
        
        Look for:
        - AGENTS.md
        - AGENTS.local.md
        - .workspace-config.yaml
        """
        # TODO: Scan directory and load files
        pass
    
    def build(self) -> str:
        """
        Build the final prompt.
        
        Steps:
        1. Filter sections by mode (Challenge 5)
        2. Combine sections (Challenge 1)
        3. Truncate if needed (Challenge 4)
        """
        # TODO: Combine all challenges
        pass
```

### Test Cases
Create a full integration test:

```python
def test_full_integration():
    """Test the complete PromptBuilder."""
    
    # Setup
    builder = PromptBuilder(mode="full", max_chars=10000)
    
    # Add all sections
    builder.add_identity("test_identity.yaml")
    builder.add_datetime()
    
    # Mock tool registry
    from tools.tools import ToolRegistry
    registry = ToolRegistry()
    builder.add_tools(registry)
    
    # Mock RAG results
    rag_results = [
        {
            "file_path": "data/test.pdf",
            "chunk_text": "Important context here",
            "page_num": 1,
            "score": 0.9
        }
    ]
    builder.add_memory(rag_results)
    
    # Build
    prompt = builder.build()
    
    # Assertions
    assert len(prompt) <= 10000
    assert "Rovo Dev" in prompt  # From identity
    assert "2026" in prompt  # From datetime
    assert "Important context" in prompt  # From memory
    
    print("✅ Full integration test passed!")

def test_minimal_mode():
    """Test that minimal mode excludes memory."""
    builder = PromptBuilder(mode="minimal")
    builder.add_identity("test_identity.yaml")
    builder.add_datetime()
    builder.add_memory([{"chunk_text": "Should not appear"}])
    
    prompt = builder.build()
    assert "Should not appear" not in prompt
    print("✅ Minimal mode test passed!")
```

### Hints
- Import all your previous challenge solutions
- Keep section priorities in mind
- Test each method individually first
- Use method chaining for clean API

### Learning Goals
✅ Class design and composition  
✅ Integration of multiple components  
✅ Builder pattern implementation  
✅ Real-world prompt engineering

---

## 🎯 Bonus Challenges (Stretch Goals)

### Bonus 1: Token Counting
Use `tiktoken` to count tokens instead of characters:

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

### Bonus 2: Visualization
Create a visual representation of section sizes:

```python
def visualize_sections(self) -> None:
    """Print a bar chart of section token counts."""
    # Example output:
    # PROMPT COMPOSITION:
    # ├─ Identity (245 tokens)  ████████░░░░░░░░░░
    # ├─ Tools (1,203 tokens)   ██████████████░░░░
    # └─ Memory (3,421 tokens)  ████████████████████
    # Total: 4,869 / 8,000 tokens (61%)
```

### Bonus 3: Conditional Sections
Only add sections if they have content:

```python
def add_memory(self, rag_results: List[Dict]) -> "PromptBuilder":
    """Only add memory section if results are non-empty."""
    if not rag_results:
        return self
    # ... rest of implementation
```

---

## 📝 Submission Checklist

When you complete the challenges:

- [ ] All Challenge 1 tests pass
- [ ] All Challenge 2 tests pass
- [ ] All Challenge 3 tests pass
- [ ] All Challenge 4 tests pass
- [ ] All Challenge 5 tests pass
- [ ] Challenge 6 integration tests pass
- [ ] Code is documented with docstrings
- [ ] Manual testing in main.py works
- [ ] Manual testing in server.py works

---

## 🎓 What You'll Learn

By completing these challenges, you'll master:

1. **Builder Pattern**: Fluent API design for complex object construction
2. **Template Composition**: Assembling outputs from modular parts
3. **Context Window Management**: Smart truncation and prioritization
4. **File I/O**: Loading YAML/JSON configuration files
5. **Algorithm Design**: Priority-based truncation algorithms
6. **Mode Systems**: Conditional feature toggling
7. **Integration**: Combining components into a cohesive system

---

## 🚀 Ready to Start?

Begin with **Challenge 1** and work your way through! Each challenge builds on the previous one.

**Create test files in**: `/Users/rgupta6/Desktop/chat-client-toy/chat-client-toy/tests/`

**Create solution files in**: `/Users/rgupta6/Desktop/chat-client-toy/chat-client-toy/services/`

Good luck! 🎯

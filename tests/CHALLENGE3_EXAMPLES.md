# Challenge 3: Input/Output Examples

## Example 1: Single Tool with One Parameter

### INPUT:
```python
tool_spec = {
    "read_file": {
        "type": "function",
        "name": "read_file",
        "description": "Read the contents of a file at the given path",
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
    }
}
```

### OUTPUT (what your function should return):
```
## Available Tools

**read_file**: Read the contents of a file at the given path
  Parameters:
  - path (string, required): The file path to read

```

---

## Example 2: Two Tools (Your Actual Tools!)

### INPUT:
```python
tool_spec = {
    "read_file": {
        "type": "function",
        "name": "read_file",
        "description": "Read file contents",
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
    },
    "run_bash": {
        "type": "function",
        "name": "run_bash",
        "description": "Execute a bash command",
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
```

### OUTPUT:
```
## Available Tools

**read_file**: Read file contents
  Parameters:
  - path (string, required): File path to read

**run_bash**: Execute a bash command
  Parameters:
  - command (string, required): The bash command to execute

```

---

## Example 3: Tool with Optional Parameters

### INPUT:
```python
tool_spec = {
    "api_call": {
        "type": "function",
        "name": "api_call",
        "description": "Make an API call",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "API endpoint URL"
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method (GET, POST, etc)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds"
                }
            },
            "required": ["url", "method"]
        }
    }
}
```

### OUTPUT:
```
## Available Tools

**api_call**: Make an API call
  Parameters:
  - url (string, required): API endpoint URL
  - method (string, required): HTTP method (GET, POST, etc)
  - timeout (integer): Request timeout in seconds

```

**NOTICE:** `timeout` is NOT marked as required because it's not in the `required` list!

---

## Example 4: Empty Tool Spec

### INPUT:
```python
tool_spec = {}
```

### OUTPUT:
```python
""  # Just an empty string
```

---

## Example 5: Tool with No Parameters

### INPUT:
```python
tool_spec = {
    "get_time": {
        "type": "function",
        "name": "get_time",
        "description": "Get the current time",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
```

### OUTPUT:
```
## Available Tools

**get_time**: Get the current time

```

**NOTICE:** No "Parameters:" section because there are no properties!

---

## Step-by-Step Walkthrough: Building Example 1

```
STEP 1: Check if empty
  tool_spec is NOT empty, so continue

STEP 2: Start result
  result = "## Available Tools\n\n"

STEP 3: Loop through tools
  tool_name = "read_file"
  tool_info = {
    "type": "function",
    "name": "read_file",
    "description": "Read the contents of a file at the given path",
    "parameters": {...}
  }

STEP 4: Get description
  description = "Read the contents of a file at the given path"
  result += "**read_file**: Read the contents of a file at the given path\n"
  
  Now result = "## Available Tools\n\n**read_file**: Read the contents of a file at the given path\n"

STEP 5: Get parameters
  parameters = {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "The file path to read"}
    },
    "required": ["path"]
  }
  
  properties = {"path": {"type": "string", "description": "The file path to read"}}
  required = ["path"]

STEP 6: Check if there are properties
  properties is NOT empty, so add Parameters section
  result += "  Parameters:\n"
  
  Now result = "## Available Tools\n\n**read_file**: Read the contents of a file at the given path\n  Parameters:\n"

STEP 7: Loop through each parameter
  param_name = "path"
  param_info = {"type": "string", "description": "The file path to read"}
  
  param_type = "string"
  param_desc = "The file path to read"
  
  Check if "path" is in required list: YES IT IS!
  result += "  - path (string, required): The file path to read\n"
  
  Now result = "## Available Tools\n\n**read_file**: Read the contents of a file at the given path\n  Parameters:\n  - path (string, required): The file path to read\n"

STEP 8: Add blank line between tools
  result += "\n"
  
  Final result = "## Available Tools\n\n**read_file**: Read the contents of a file at the given path\n  Parameters:\n  - path (string, required): The file path to read\n\n"

STEP 9: Return
  return result
```

---

## Visual Data Flow

```
INPUT DICTIONARY:
{
  "read_file": {
    "description": "Read file contents",
    "parameters": {
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

        ↓ YOUR CODE PROCESSES IT ↓

OUTPUT STRING:
"## Available Tools\n\n**read_file**: Read file contents\n  Parameters:\n  - path (string, required): File path to read\n\n"

        ↓ WHEN PRINTED ↓

## Available Tools

**read_file**: Read file contents
  Parameters:
  - path (string, required): File path to read

```

---

## Key Code Patterns You Need

### Pattern 1: Looping Through Tools
```python
for tool_name, tool_info in tool_spec.items():
    # tool_name = "read_file"
    # tool_info = {...all the tool data...}
```

### Pattern 2: Safe Dictionary Access
```python
description = tool_info.get('description', 'No description')
# If 'description' exists, use it
# If not, use 'No description'
```

### Pattern 3: Nested Dictionary Access
```python
parameters = tool_info.get('parameters', {})
properties = parameters.get('properties', {})
required = parameters.get('required', [])
```

### Pattern 4: Checking Required Parameters
```python
if param_name in required:
    # It's required!
    result += f"  - {param_name} ({param_type}, required): {param_desc}\n"
else:
    # It's optional
    result += f"  - {param_name} ({param_type}): {param_desc}\n"
```

---

## Quick Reference Table

| What | Where to Find It | Example |
|------|------------------|---------|
| Tool name | Loop key | `"read_file"` |
| Tool description | `tool_info['description']` | `"Read file contents"` |
| Parameters object | `tool_info['parameters']` | `{...}` |
| Properties | `parameters['properties']` | `{"path": {...}}` |
| Required list | `parameters['required']` | `["path"]` |
| Param type | `param_info['type']` | `"string"` |
| Param description | `param_info['description']` | `"File path to read"` |

---

## Now You're Ready! 🚀

Use these examples to implement your `format_tools()` function.

Remember:
1. Handle empty case first
2. Start with header
3. Loop through tools
4. Format each tool's description and parameters
5. Add blank lines between tools

Good luck! 💪

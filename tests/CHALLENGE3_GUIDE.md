# Challenge 3: Tool Registry Formatter - Quick Guide

## What You're Working With

Your `chat-client-toy` project has a `ToolRegistry` that stores tools like this:

```python
registry.tool_spec = {
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
```

## Your Task

Transform this into:

```
## Available Tools

**read_file**: Read the contents of a file at the given path (large files are truncated)
  Parameters:
  - path (string, required): The file path to read

**run_bash**: Execute a bash command and return the output
  Parameters:
  - command (string, required): The bash command to execute

```

## Key Points

1. **Ignore extra fields**: The spec has `"type": "function"`, `"title"` fields - you can ignore these
2. **Focus on**: `name`, `description`, `parameters`
3. **Parameters structure**: `parameters` → `properties` → param details
4. **Required list**: Check `parameters` → `required` list

## Quick Implementation Guide

```python
@staticmethod
def format_tools(tool_spec: Dict[str, Dict[str, Any]]) -> str:
    if not tool_spec:
        return ""
    
    result = "## Available Tools\n\n"
    
    for tool_name, tool_info in tool_spec.items():
        # Get description
        description = tool_info.get('description', 'No description')
        result += f"**{tool_name}**: {description}\n"
        
        # Get parameters
        parameters = tool_info.get('parameters', {})
        properties = parameters.get('properties', {})
        required = parameters.get('required', [])
        
        # Format parameters
        if properties:
            result += "  Parameters:\n"
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'any')
                param_desc = param_info.get('description', '')
                
                if param_name in required:
                    result += f"  - {param_name} ({param_type}, required): {param_desc}\n"
                else:
                    result += f"  - {param_name} ({param_type}): {param_desc}\n"
        
        result += "\n"
    
    return result
```

Good luck! 🚀

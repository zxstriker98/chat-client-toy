"""
Challenge 3: Tool Registry Formatter

Your task: Transform tool specifications (nested dictionaries) into 
human-readable documentation format.

Requirements:
1. Iterate over tool specifications
2. Extract tool name, description, and parameters
3. Mark required vs optional parameters
4. Format with proper indentation
"""

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
        if not tool_spec:
            return ""

        result = "## Available Tools\n\n"
        for tool_name, tool_info in tool_spec.items():
            description = tool_info.get("description", "No description")
            result += f"**{tool_name}**: {description}\n"
            
            parameters = tool_info.get("parameters", {})
            properties = parameters.get("properties", {})
            required = parameters.get("required", [])
            
            if properties:
                result += "  Parameters:\n"
                for param_name, param_info in properties.items():
                    param_type = param_info.get("type", "any")
                    param_desc = param_info.get("description", "")
                    
                    if param_name in required:
                        result += f"  - {param_name} ({param_type}, required): {param_desc}\n"
                    else:
                        result += f"  - {param_name} ({param_type}): {param_desc}\n"
            result += "\n"
        return result


# ============================================
# HINTS & GUIDANCE
# ============================================

"""
HINT 1: Understanding the Tool Spec Structure
----------------------------------------------
tool_spec = {
    "read_file": {                          # Tool name
        "name": "read_file",
        "description": "Read file contents",  # Tool description
        "parameters": {
            "type": "object",
            "properties": {                 # Parameter definitions
                "path": {
                    "type": "string",       # Parameter type
                    "description": "File path to read"  # Parameter description
                }
            },
            "required": ["path"]            # List of required parameters
        }
    }
}


HINT 2: Checking if Empty
--------------------------
if not tool_spec:
    return ""


HINT 3: Iterating Over Tools
-----------------------------
result = "## Available Tools\n\n"

for tool_name, tool_info in tool_spec.items():
    # tool_name = "read_file"
    # tool_info = {...the whole tool definition...}
    pass


HINT 4: Getting Nested Values Safely
-------------------------------------
description = tool_info.get('description', 'No description')
parameters = tool_info.get('parameters', {})
properties = parameters.get('properties', {})
required = parameters.get('required', [])


HINT 5: Iterating Over Parameters
----------------------------------
for param_name, param_info in properties.items():
    param_type = param_info.get('type', 'any')
    param_desc = param_info.get('description', '')
    
    # Check if required
    if param_name in required:
        result += f"  - {param_name} ({param_type}, required): {param_desc}\n"
    else:
        result += f"  - {param_name} ({param_type}): {param_desc}\n"


HINT 6: Complete Structure
---------------------------
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
        
        # If there are parameters, format them
        if properties:
            result += "  Parameters:\n"
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'any')
                param_desc = param_info.get('description', '')
                
                if param_name in required:
                    result += f"  - {param_name} ({param_type}, required): {param_desc}\n"
                else:
                    result += f"  - {param_name} ({param_type}): {param_desc}\n"
        
        result += "\n"  # Blank line between tools
    
    return result


HINT 7: Example Input & Output
-------------------------------
INPUT:
{
    "read_file": {
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
    }
}

OUTPUT:
## Available Tools

**read_file**: Read file contents
  Parameters:
  - path (string, required): File path to read

"""

# ============================================
# TRY IT YOURSELF FIRST!
# ============================================
# Don't scroll down yet - try implementing it yourself!
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# ============================================
# SOLUTION (Try not to peek!)
# ============================================

# Uncomment below if you want to see the solution:

# class ToolFormatter:
#     @staticmethod
#     def format_tools(tool_spec: Dict[str, Dict[str, Any]]) -> str:
#         if not tool_spec:
#             return ""
#         
#         result = "## Available Tools\n\n"
#         
#         for tool_name, tool_info in tool_spec.items():
#             description = tool_info.get('description', 'No description')
#             result += f"**{tool_name}**: {description}\n"
#             
#             parameters = tool_info.get('parameters', {})
#             properties = parameters.get('properties', {})
#             required = parameters.get('required', [])
#             
#             if properties:
#                 result += "  Parameters:\n"
#                 for param_name, param_info in properties.items():
#                     param_type = param_info.get('type', 'any')
#                     param_desc = param_info.get('description', '')
#                     
#                     if param_name in required:
#                         result += f"  - {param_name} ({param_type}, required): {param_desc}\n"
#                     else:
#                         result += f"  - {param_name} ({param_type}): {param_desc}\n"
#             
#             result += "\n"
#         
#         return result

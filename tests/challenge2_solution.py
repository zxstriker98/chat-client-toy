"""
Challenge 2: Config File Parser

Your task: Implement the ConfigParser class to load identity configurations
from YAML or JSON files and format them as prompt sections.

Requirements:
1. Support both YAML and JSON file formats
2. Handle file not found errors
3. Handle unsupported file types
4. Format the config into a readable identity section
"""

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
        file_path = Path(config_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        if file_path.suffix not in [".yaml", ".yml", ".json"]:
            raise ValueError("Unsupported file format")
        
        config = dict()
        with open(file_path, "r") as f:
            if file_path.suffix in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            else:
                config = json.load(f)

        name = config.get("name")
        role = config.get("role")
        capabilities = config.get("capabilities")
        style = config.get("style")
        caps = "\n".join([f"- {capability}" for capability in capabilities])
        result = f"You are {name}, a {role}.\n\n"
        result += f"Your capabilities include:\n{caps}\n\n"
        result += f"Communication style: {style}"
        return result


# ============================================
# HINTS & GUIDANCE
# ============================================

"""
HINT 1: File Existence Check
-----------------------------
from pathlib import Path

path = Path(config_path)
if not path.exists():
    raise FileNotFoundError(f"Config file not found: {config_path}")


HINT 2: File Extension Check
-----------------------------
suffix = Path(config_path).suffix  # Returns '.yaml', '.json', etc.

if suffix not in ['.yaml', '.yml', '.json']:
    raise ValueError(f"Unsupported file type: {suffix}")


HINT 3: Loading YAML Files
---------------------------
import yaml

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)  # Returns a dict


HINT 4: Loading JSON Files
---------------------------
import json

with open(config_path, 'r') as f:
    config = json.load(f)  # Returns a dict


HINT 5: Formatting Output
--------------------------
Expected format:
    You are {name}, a {role}.
    
    Your capabilities include:
    - {capability1}
    - {capability2}
    
    Communication style: {style}

You can build this string like:
    name = config.get('name', 'Assistant')
    role = config.get('role', 'helpful assistant')
    capabilities = config.get('capabilities', [])
    style = config.get('style', 'Professional')
    
    caps_text = '\n'.join([f"- {cap}" for cap in capabilities])
    
    result = f"You are {name}, a {role}.\\n\\n"
    result += f"Your capabilities include:\\n{caps_text}\\n\\n"
    result += f"Communication style: {style}"
    
    return result


HINT 6: Complete Flow
---------------------
def load_identity(config_path: str) -> str:
    # 1. Check file exists
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(...)
    
    # 2. Check file type
    suffix = path.suffix
    if suffix not in ['.yaml', '.yml', '.json']:
        raise ValueError(...)
    
    # 3. Load config
    with open(config_path, 'r') as f:
        if suffix in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        else:  # .json
            config = json.load(f)
    
    # 4. Format and return
    return format_identity(config)
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

# class ConfigParser:
#     @staticmethod
#     def load_identity(config_path: str) -> str:
#         # Check file exists
#         path = Path(config_path)
#         if not path.exists():
#             raise FileNotFoundError(f"Config file not found: {config_path}")
#         
#         # Check file type
#         suffix = path.suffix
#         if suffix not in ['.yaml', '.yml', '.json']:
#             raise ValueError(f"Unsupported file type: {suffix}")
#         
#         # Load config
#         with open(config_path, 'r') as f:
#             if suffix in ['.yaml', '.yml']:
#                 config = yaml.safe_load(f)
#             else:  # .json
#                 config = json.load(f)
#         
#         # Format
#         name = config.get('name', 'Assistant')
#         role = config.get('role', 'helpful assistant')
#         capabilities = config.get('capabilities', [])
#         style = config.get('style', 'Professional')
#         
#         caps_text = '\n'.join([f"- {cap}" for cap in capabilities])
#         
#         result = f"You are {name}, a {role}.\n\n"
#         result += f"Your capabilities include:\n{caps_text}\n\n"
#         result += f"Communication style: {style}"
#         
#         return result

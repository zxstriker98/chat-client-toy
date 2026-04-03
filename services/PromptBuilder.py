"""
Challenge 6: Full PromptBuilder — The Final Boss! 🎯

Your task: Combine ALL previous challenges into one complete PromptBuilder class.

What it uses:
- Challenge 1 → SectionBuilder logic (assemble sections with headers)
- Challenge 2 → ConfigParser logic (load identity from YAML/JSON)
- Challenge 3 → ToolFormatter logic (format tool specs)
- Challenge 4 → SmartTruncator logic (context window management)
- Challenge 5 → ModeController logic (filter sections by mode)

Usage (what the final API looks like):
    builder = PromptBuilder(mode="full", max_chars=32000)
    builder.add_identity("config.yaml")
    builder.add_tools(tool_registry)
    builder.add_datetime()
    builder.add_memory(rag_results)
    builder.add_bootstrap(".")
    prompt = builder.build()
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# Section priority constants (same as Challenge 4)
# ─────────────────────────────────────────────────────────────────────────────
PRIORITY = {
    "identity":  1,
    "datetime":  2,
    "tools":     3,
    "bootstrap": 5,
    "memory":    8,
    "workspace": 10,
}

# Sections allowed per mode (same as Challenge 5)
MODE_SECTIONS = {
    "full":    {"identity", "datetime", "tools", "memory", "bootstrap", "workspace"},
    "minimal": {"identity", "datetime", "tools"},
    "none":    set(),
}

PRICE_MAP = {
    "PRICE_LEVEL_FREE":           "Free",
    "PRICE_LEVEL_INEXPENSIVE":    "$",
    "PRICE_LEVEL_MODERATE":       "$$",
    "PRICE_LEVEL_EXPENSIVE":      "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}


# ─────────────────────────────────────────────────────────────────────────────
# Section dataclass (same as Challenge 4)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Section:
    name: str
    content: str
    priority: int


# ─────────────────────────────────────────────────────────────────────────────
# PromptBuilder
# ─────────────────────────────────────────────────────────────────────────────
class PromptBuilder:
    """
    Dynamically build system prompts from multiple sections.
    Combines identity, tools, memory, bootstrap, and datetime.
    """

    def __init__(self, mode: str = "full", max_chars: int = 32000):
        """
        Initialize the PromptBuilder.

        Args:
            mode: "full", "minimal", or "none"
            max_chars: Maximum characters allowed in final prompt
        """
        self.mode = mode
        self.max_chars = max_chars
        self.sections: Dict[str, str] = {}

    # ─────────────────────────────────────────
    # Section adders (all return self for chaining)
    # ─────────────────────────────────────────

    def add_identity(self, config_path: str) -> "PromptBuilder":
        """
        Load identity from a YAML or JSON config file.

        Config structure:
        {
            "name": "My Delhi",
            "role": "Restaurant assistant",
            "capabilities": ["menu info", "hours", "reservations"],
            "style": "Friendly and helpful"
        }

        Expected section content:
            You are {name}, a {role}.

            Your capabilities include:
            - {cap1}
            - {cap2}

            Communication style: {style}
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        suffix = path.suffix
        if suffix not in [".yml", ".yaml", ".json"]:
            raise ValueError(f"Unsupported format: {suffix}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f) if suffix in [".yaml", ".yml"] else json.load(f)

        name = config.get("name", "Assistant")
        role = config.get("role", "helpful assistant")
        caps = config.get("capabilities", [])
        style = config.get("style", "Professional")

        caps_text = "\n".join([f"- {c}" for c in caps])
        content = f"You are {name}, a {role}.\n\nYour capabilities include:\n{caps_text}\n\nCommunication style: {style}"

        self.sections["identity"] = content
        return self

    def add_tools(self, tool_registry) -> "PromptBuilder":
        """Format tools from a ToolRegistry into the prompt."""
        tool_spec = tool_registry.tool_spec
        result = ""
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
        self.sections["tools"] = result
        return self

    def add_datetime(self) -> "PromptBuilder":
        """Inject current date and time."""
        now = datetime.now()
        formatted = now.strftime("%A, %Y-%m-%d %H:%M:%S")
        self.sections["datetime"] = f"Current date and time: {formatted}"
        return self

    def add_memory(self, rag_results: List[Dict[str, Any]]) -> "PromptBuilder":
        """Add RAG search results as memory section."""
        if not rag_results:
            return self
        parts = []
        for r in rag_results:
            file_path = r.get("file_path", "unknown")
            page_num = r.get("page_num", "?")
            score = r.get("score", 0)
            text = r.get("chunk_text", "")
            parts.append(f"From: {file_path} (page {page_num}) [score: {score:.2f}]\n{text}")
        self.sections["memory"] = "\n\n".join(parts)
        return self

    def add_bootstrap(self, workspace_dir: str) -> "PromptBuilder":
        """Load workspace rules from AGENTS.md files."""
        parts = []
        for filename in ["AGENTS.md", "AGENTS.local.md"]:
            filepath = Path(workspace_dir) / filename
            if filepath.exists():
                parts.append(filepath.read_text())
        if parts:
            self.sections["bootstrap"] = "\n\n".join(parts)
        return self

    # ─────────────────────────────────────────
    # Build (Challenge 1 + 4 + 5 combined!)
    # ─────────────────────────────────────────

    def build(self) -> str:
        """
        Build the final prompt string.

        Steps:
        1. Filter sections by mode (Challenge 5)
        2. Convert to Section objects with priorities (Challenge 4)
        3. Truncate if needed (Challenge 4)
        4. Format with headers (Challenge 1)
        """
        # Step 1: Get allowed sections for current mode
        allowed = MODE_SECTIONS.get(self.mode, set())

        # Step 2: Filter to only allowed sections
        filtered = {k: v for k, v in self.sections.items() if k in allowed}

        # Step 3: Nothing to show
        if not filtered:
            return ""

        # Step 4: Convert to Section objects with priorities
        section_list = [
            Section(name=k, content=v, priority=PRIORITY.get(k, 99))
            for k, v in filtered.items()
        ]

        # Step 5: Sort by priority (1 = most important first)
        section_list = sorted(section_list, key=lambda s: s.priority)

        # Step 6: Truncate if over limit
        total = sum(len(s.content) + len(s.name) + 10 for s in section_list)
        if total > self.max_chars:
            section_list = self._truncate(section_list)

        # Step 7: Format with headers
        return "".join([f"## {s.name.upper()}\n{s.content}\n\n" for s in section_list])

    # ─────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────

    def _truncate(self, sections: List[Section]) -> List[Section]:
        """
        Greedily keep sections that fit within max_chars.
        (Reuse your Challenge 4 greedy algorithm!)
        """
        # TODO:
        # Greedy: add sections from highest priority until no more fit
        remaining = []
        for section in sections:
            test = remaining + [section]
            total = sum(len(s.content) + len(s.name) + 10 for s in test)
            if total <= self.max_chars:
                remaining.append(section)
        return remaining


# ─────────────────────────────────────────────────────────────────────────────
# HINTS
# ─────────────────────────────────────────────────────────────────────────────

"""
HINT 1: __init__
-----------------
def __init__(self, mode="full", max_chars=32000):
    self.mode = mode
    self.max_chars = max_chars
    self.sections = {}  # {name: content}


HINT 2: add_identity (same as Challenge 2!)
--------------------------------------------
path = Path(config_path)
if not path.exists():
    raise FileNotFoundError(f"Config not found: {config_path}")

suffix = path.suffix
if suffix not in [".yaml", ".yml", ".json"]:
    raise ValueError(f"Unsupported format: {suffix}")

with open(config_path, "r") as f:
    config = yaml.safe_load(f) if suffix in [".yaml", ".yml"] else json.load(f)

name = config.get("name", "Assistant")
role = config.get("role", "helpful assistant")
caps = config.get("capabilities", [])
style = config.get("style", "Professional")

caps_text = "\n".join([f"- {c}" for c in caps])
content = f"You are {name}, a {role}.\n\nYour capabilities include:\n{caps_text}\n\nCommunication style: {style}"

self.sections["identity"] = content
return self


HINT 3: add_tools (same as Challenge 3!)
------------------------------------------
tool_spec = tool_registry.tool_spec
result = ""
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

self.sections["tools"] = result
return self


HINT 4: add_datetime
----------------------
now = datetime.now()
formatted = now.strftime("%A, %Y-%m-%d %H:%M:%S")
self.sections["datetime"] = f"Current date and time: {formatted}"
return self


HINT 5: add_memory
-------------------
if not rag_results:
    return self

parts = []
for r in rag_results:
    file_path = r.get("file_path", "unknown")
    page_num = r.get("page_num", "?")
    score = r.get("score", 0)
    text = r.get("chunk_text", "")
    parts.append(f"From: {file_path} (page {page_num}) [score: {score:.2f}]\n{text}")

self.sections["memory"] = "\n\n".join(parts)
return self


HINT 6: add_bootstrap
----------------------
content_parts = []
for filename in ["AGENTS.md", "AGENTS.local.md"]:
    filepath = Path(workspace_dir) / filename
    if filepath.exists():
        content_parts.append(filepath.read_text())

if content_parts:
    self.sections["bootstrap"] = "\n\n".join(content_parts)
return self


HINT 7: build
--------------
def build(self) -> str:
    allowed = MODE_SECTIONS.get(self.mode, set())
    filtered = {k: v for k, v in self.sections.items() if k in allowed}
    
    if not filtered:
        return ""
    
    section_list = [
        Section(name=k, content=v, priority=PRIORITY.get(k, 99))
        for k, v in filtered.items()
    ]
    section_list = sorted(section_list, key=lambda s: s.priority)
    
    total = sum(len(s.content) + len(s.name) + 10 for s in section_list)
    if total > self.max_chars:
        section_list = self._truncate(section_list)
    
    return "".join([f"## {s.name.upper()}\n{s.content}\n\n" for s in section_list])
"""

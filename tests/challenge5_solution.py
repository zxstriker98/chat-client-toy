"""
Challenge 5: Mode System

Your task: Implement a mode system that controls which sections
are included in the final prompt.

3 modes:
- FULL    → All sections included
- MINIMAL → Only identity, datetime, tools
- NONE    → Empty prompt (no sections)

Requirements:
1. Use Enum for type safety
2. Define which sections belong to each mode
3. Implement should_include() to check a single section
4. Implement filter_sections() to filter a dictionary
"""

from enum import Enum
from typing import Dict, Set


class PromptMode(Enum):
    """Different prompt construction modes."""
    FULL    = "full"
    MINIMAL = "minimal"
    NONE    = "none"


class ModeController:
    """Controls which sections to include based on mode."""

    # Define which sections are allowed in each mode
    MODE_SECTIONS: Dict[PromptMode, Set[str]] = {
        PromptMode.FULL:    {"identity", "datetime", "tools", "memory", "bootstrap", "workspace"},
        PromptMode.MINIMAL: {"identity", "datetime", "tools"},
        PromptMode.NONE:    set()  # Empty set = no sections
    }

    def __init__(self, mode: PromptMode):
        self.mode = mode

    def should_include(self, section_name: str) -> bool:
        return section_name in self.MODE_SECTIONS[self.mode]

    def filter_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        return {k: v for k, v in sections.items() if self.should_include(k)}


# ============================================
# HINTS & GUIDANCE
# ============================================

"""
HINT 1: Enum Usage
------------------
PromptMode is already defined for you!

Usage:
    mode = PromptMode.FULL
    mode = PromptMode.MINIMAL
    mode = PromptMode.NONE
    
    mode.value  # → "full", "minimal", "none"


HINT 2: __init__
----------------
def __init__(self, mode: PromptMode):
    self.mode = mode


HINT 3: should_include
----------------------
The allowed sections for each mode are in MODE_SECTIONS:
    
    MODE_SECTIONS[PromptMode.FULL]    = {"identity", "datetime", "tools", "memory", "bootstrap", "workspace"}
    MODE_SECTIONS[PromptMode.MINIMAL] = {"identity", "datetime", "tools"}
    MODE_SECTIONS[PromptMode.NONE]    = set()  (empty!)

So to check if a section is allowed:
    allowed = self.MODE_SECTIONS[self.mode]  # Get the set for current mode
    return section_name in allowed           # Check if section is in that set

Combined:
    return section_name in self.MODE_SECTIONS[self.mode]


HINT 4: filter_sections
-----------------------
You want to keep only sections where should_include() returns True.

Using dictionary comprehension:
    return {
        name: content
        for name, content in sections.items()
        if self.should_include(name)
    }

This is equivalent to:
    result = {}
    for name, content in sections.items():
        if self.should_include(name):
            result[name] = content
    return result
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
# ============================================
# SOLUTION (Try not to peek!)
# ============================================

# Uncomment below if you want to see the solution:

# class ModeController:
#     MODE_SECTIONS = {
#         PromptMode.FULL:    {"identity", "datetime", "tools", "memory", "bootstrap", "workspace"},
#         PromptMode.MINIMAL: {"identity", "datetime", "tools"},
#         PromptMode.NONE:    set()
#     }
#
#     def __init__(self, mode: PromptMode):
#         self.mode = mode
#
#     def should_include(self, section_name: str) -> bool:
#         return section_name in self.MODE_SECTIONS[self.mode]
#
#     def filter_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
#         return {
#             name: content
#             for name, content in sections.items()
#             if self.should_include(name)
#         }

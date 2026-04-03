"""
Challenge 4: Smart Truncation Algorithm

Your task: Implement an intelligent truncation algorithm that keeps the most 
important sections when the total prompt exceeds a character limit.

Requirements:
1. Preserve high-priority sections (always keep)
2. Remove low-priority sections first
3. If still too long, truncate individual sections
4. Add "...[truncated]" markers where text is cut
"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Section:
    """Represents a prompt section with priority."""
    name: str
    content: str
    priority: int  # 1 = highest priority, 10 = lowest priority


class SmartTruncator:
    """
    Intelligently truncate a prompt to fit within character limits
    while preserving the most important sections.
    """
    
    def __init__(self, max_chars: int):
        self.max_chars = max_chars
    
    def truncate(self, sections: List[Section]) -> str:
        # 1. Handle empty input
        if not sections:
            return ""

        # 2. Already fits? Return everything
        if self._calculate_total_length(sections) <= self.max_chars:
            return self._format_sections(sections)

        # 3. Sort by priority (1 = highest = keep first)
        sorted_sections = sorted(sections, key=lambda s: s.priority)

        # 4. Greedily add sections while they fit
        remaining = []
        for section in sorted_sections:
            test = remaining + [section]
            if self._calculate_total_length(test) <= self.max_chars:
                remaining.append(section)

        # 5. Format final result
        result = self._format_sections(remaining)

        # 6. Safety net: if still too long, hard truncate
        if len(result) > self.max_chars:
            return result[:self.max_chars] + "\n...[truncated]"

        return result
    
    def _calculate_total_length(self, sections: List[Section]) -> int:
        return sum(len(s.content) + len(s.name) + 10 for s in sections)
    
    def _format_sections(self, sections: List[Section]) -> str:
        return "".join([f"## {s.name.upper()}\n{s.content}\n\n" for s in sections])
    
    def _truncate_section(self, content: str, max_len: int) -> str:
        if len(content) <= max_len:
            return content
        marker = "\n...[truncated]"
        return content[:max_len - len(marker)] + marker


# ============================================
# HINTS & GUIDANCE
# ============================================

"""
HINT 1: Understanding Priority
-------------------------------
Priority scale:
- 1 = Identity (always keep)
- 2 = DateTime (always keep)
- 3 = Tools (keep unless desperate)
- 5 = Bootstrap (can remove)
- 8 = Memory/RAG (can remove)
- 10 = Workspace context (remove first)

Lower number = higher priority = more important


HINT 2: Algorithm Steps
-----------------------
def truncate(self, sections: List[Section]) -> str:
    # Step 1: Check if already under limit
    total = self._calculate_total_length(sections)
    if total <= self.max_chars:
        return self._format_sections(sections)
    
    # Step 2: Sort by priority (lowest priority first to remove)
    sections_by_priority = sorted(sections, key=lambda s: s.priority)
    
    # Step 3: Remove lowest priority sections until under limit
    remaining = []
    for section in sections_by_priority:
        test_sections = remaining + [section]
        if self._calculate_total_length(test_sections) <= self.max_chars:
            remaining.append(section)
    
    # Step 4: If still over (only high priority sections left), truncate them
    if self._calculate_total_length(remaining) > self.max_chars:
        # Allocate space proportionally to remaining sections
        # ...truncation logic...
        pass
    
    return self._format_sections(remaining)


HINT 3: Total Length Calculation
---------------------------------
def _calculate_total_length(self, sections: List[Section]) -> int:
    total = 0
    for section in sections:
        total += len(section.content)
        total += len(section.name) + 5  # For section header overhead
    return total

Or using sum():
    return sum(len(s.content) + len(s.name) + 5 for s in sections)


HINT 4: Formatting Sections
---------------------------
def _format_sections(self, sections: List[Section]) -> str:
    result = ""
    for section in sections:
        result += f"## {section.name.upper()}\\n{section.content}\\n\\n"
    return result


HINT 5: Truncating a Section
-----------------------------
def _truncate_section(self, content: str, max_len: int) -> str:
    if len(content) <= max_len:
        return content
    
    # Keep max_len characters, minus room for marker
    marker = "\\n...[truncated]"
    return content[:max_len - len(marker)] + marker


HINT 6: The Greedy Algorithm
-----------------------------
The key insight: use a GREEDY approach

1. Sort sections by priority (ascending - lowest first)
2. Start with ALL sections
3. Remove the lowest priority section
4. Check if we're under limit
5. If yes, keep it removed and move to next lowest
6. If no, add it back and stop removing sections
7. If still over limit, truncate individual sections

This is called a GREEDY algorithm because we greedily remove
the least important items until we fit.


HINT 7: Example Flow
--------------------
Sections:
- Identity (priority=1) "I am AI" (50 chars)
- Tools (priority=3) "Tool list..." (200 chars)
- Memory (priority=8) "RAG results..." (5000 chars)
- Bootstrap (priority=5) "Workspace rules..." (500 chars)

Max chars: 1000

Total: 50 + 200 + 5000 + 500 = 5750 (over limit!)

Step 1: Sort by priority
- Memory (priority=8) ← remove first
- Bootstrap (priority=5)
- Tools (priority=3)
- Identity (priority=1)

Step 2: Try removing Memory
- Remaining: Identity + Tools + Bootstrap = 750 chars ✓ Under 1000!

Step 3: Return "Identity + Tools + Bootstrap"
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

# class SmartTruncator:
#     def __init__(self, max_chars: int):
#         self.max_chars = max_chars
#     
#     def truncate(self, sections: List[Section]) -> str:
#         # Check if already under limit
#         total = self._calculate_total_length(sections)
#         if total <= self.max_chars:
#             return self._format_sections(sections)
#         
#         # Sort by priority (lowest first - remove these first)
#         sorted_sections = sorted(sections, key=lambda s: s.priority)
#         
#         # Greedily remove lowest priority sections
#         remaining = []
#         for section in sorted_sections:
#             test_sections = remaining + [section]
#             if self._calculate_total_length(test_sections) <= self.max_chars:
#                 remaining.append(section)
#         
#         # If still over limit, truncate remaining sections
#         if self._calculate_total_length(remaining) > self.max_chars:
#             result = self._format_sections(remaining)
#             if len(result) > self.max_chars:
#                 return result[:self.max_chars] + "\n...[truncated]"
#         
#         return self._format_sections(remaining)
#     
#     def _calculate_total_length(self, sections: List[Section]) -> int:
#         total = 0
#         for section in sections:
#             # Content length + header overhead
#             total += len(section.content) + len(section.name) + 10
#         return total
#     
#     def _format_sections(self, sections: List[Section]) -> str:
#         result = ""
#         for section in sections:
#             result += f"## {section.name.upper()}\n{section.content}\n\n"
#         return result
#     
#     def _truncate_section(self, content: str, max_len: int) -> str:
#         if len(content) <= max_len:
#             return content
#         marker = "\n...[truncated]"
#         return content[:max_len - len(marker)] + marker

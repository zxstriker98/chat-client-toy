# Challenge 4: Smart Truncation Algorithm

## The Problem

When building a prompt, you have multiple sections:
- **Identity** (important - always keep)
- **Tools** (important - usually keep)
- **DateTime** (important - always keep)
- **Bootstrap** (medium importance - can remove)
- **Memory/RAG** (lower priority - remove first)
- **Workspace context** (lowest priority - remove first)

But the **context window** (like GPT-4's 8K, 32K, 128K tokens) has a limit!

If your prompt is **10,000 chars** but the limit is **5,000 chars**, you need to:
1. **Remove** the least important sections first
2. **Truncate** remaining sections if needed
3. Keep high-priority content no matter what

---

## The Algorithm: Greedy Approach

### Step 1: Check if Under Limit
```python
total = sum of all section lengths
if total <= max_chars:
    return all sections (no truncation needed)
```

### Step 2: Sort by Priority
```python
sorted_sections = sorted(sections, key=lambda s: s.priority)
# Lowest priority numbers first (to remove first)
```

### Step 3: Greedily Remove Low Priority
```python
remaining = []
for section in sorted_sections:
    # Try adding this section
    test = remaining + [section]
    
    if length(test) <= max_chars:
        # Fits! Keep it
        remaining.append(section)
    # If doesn't fit, skip it and move to next
```

### Step 4: Truncate If Still Over
```python
if length(remaining) > max_chars:
    truncate individual sections
```

---

## Example: Real Flow

```
Input Sections:
┌──────────────────────────────────────────────┐
│ Identity (priority=1)      Length: 50        │ ← Keep always
│ DateTime (priority=2)      Length: 100       │ ← Keep always
│ Tools (priority=3)         Length: 500       │ ← Keep
│ Bootstrap (priority=5)     Length: 1000      │ ← Can remove
│ Memory (priority=8)        Length: 5000      │ ← Remove first
└──────────────────────────────────────────────┘

Max chars: 1500
Total: 50 + 100 + 500 + 1000 + 5000 = 6650 (OVER LIMIT!)

Step 1: Sort by priority (ascending)
- Memory (8)
- Bootstrap (5)
- Tools (3)
- DateTime (2)
- Identity (1)

Step 2: Greedy removal (try from lowest priority)
- Try adding Memory: 5000 > 1500? NO, skip it ✗
- Try adding Bootstrap: 1000 > 1500? NO, skip it ✗
- Try adding Tools: 500 > 1500? NO, skip it ✗
  Wait, that's wrong...

Actually, we build UP from highest priority:

remaining = []
for section in [Memory, Bootstrap, Tools, DateTime, Identity]:
    test = remaining + [section]
    
    # Try Memory
    test = [] + [Memory (5000)] = 5000 > 1500? YES, skip ✗
    
    # Try Bootstrap
    test = [] + [Bootstrap (1000)] = 1000 > 1500? NO, add it ✓
    remaining = [Bootstrap]
    
    # Try Tools
    test = [Bootstrap] + [Tools] = 1000 + 500 = 1500 > 1500? NO, add it ✓
    remaining = [Bootstrap, Tools]
    
    # Try DateTime
    test = [Bootstrap, Tools] + [DateTime] = 1500 + 100 = 1600 > 1500? YES, skip ✗
    
    # Try Identity
    test = [Bootstrap, Tools] + [Identity] = 1500 + 50 = 1550 > 1500? YES, skip ✗

Step 3: Result
remaining = [Bootstrap, Tools] = 1500 chars (exact fit!)

Wait, this doesn't preserve Identity and DateTime...
```

Actually, the correct approach is:

### Better Algorithm: Priority-Based Removal

```python
# Sort by priority (HIGHEST first - these stay)
sorted_sections = sorted(sections, key=lambda s: -s.priority)
# Now lowest priority is at the end

remaining = []
for section in sorted_sections:
    if remaining + [section] fits:
        remaining.append(section)
```

---

## Data Classes: Section

```python
@dataclass
class Section:
    name: str              # "identity", "tools", "memory"
    content: str           # The actual text
    priority: int          # 1-10 (1=highest, 10=lowest)
```

---

## Key Functions You Need

### 1. __init__
```python
def __init__(self, max_chars: int):
    self.max_chars = max_chars
```

### 2. truncate (main function)
```python
def truncate(self, sections: List[Section]) -> str:
    # 1. Check if under limit
    # 2. Sort by priority
    # 3. Greedily remove lowest priority
    # 4. Truncate if needed
    # 5. Return result
```

### 3. _calculate_total_length
```python
def _calculate_total_length(self, sections: List[Section]) -> int:
    # Sum up all content lengths + overhead
    return sum(len(s.content) + len(s.name) + 10 for s in sections)
```

### 4. _format_sections
```python
def _format_sections(self, sections: List[Section]) -> str:
    # Join sections with headers
    result = ""
    for s in sections:
        result += f"## {s.name.upper()}\n{s.content}\n\n"
    return result
```

### 5. _truncate_section (optional)
```python
def _truncate_section(self, content: str, max_len: int) -> str:
    # Cut content and add marker
    if len(content) <= max_len:
        return content
    marker = "\n...[truncated]"
    return content[:max_len - len(marker)] + marker
```

---

## Test Cases to Pass

1. **Under limit** - All sections included, no truncation
2. **Remove low priority** - Memory section removed, keep high priority
3. **All high priority** - Truncate content of high priority sections
4. **Priority order** - Remove sections in correct order
5. **Exact limit** - Handle edge case at exact limit
6. **Empty sections** - Handle empty input

---

## Complexity Analysis

- **Time**: O(n log n) for sorting + O(n²) for greedy testing = O(n²)
- **Space**: O(n) for storing sections

This is acceptable for typical prompt building (usually < 20 sections).

---

## When This Is Used

In the real PromptBuilder:

```python
builder = PromptBuilder(max_chars=32000)
builder.add_identity(...)
builder.add_tools(...)
builder.add_memory(...)  # RAG results

# If total > 32000:
truncator = SmartTruncator(max_chars=32000)
final_prompt = truncator.truncate([
    Section("identity", identity_text, priority=1),
    Section("tools", tools_text, priority=2),
    Section("memory", memory_text, priority=8),
])
```

---

Good luck! This is the hardest challenge. 🚀

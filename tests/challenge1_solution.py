"""
Challenge 1: String Section Builder

Your task: Implement the SectionBuilder class below.

Requirements:
1. Store sections in a dictionary
2. Support method chaining (return self)
3. Format sections with uppercase headers
4. Preserve insertion order
"""

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
        """Initialize the section builder."""
        self.sections: dict[str, str] = dict()
    
    def add_section(self, name: str, content: str) -> "SectionBuilder":
        """
        Add a named section with content.
        
        Args:
            name: Section name (will be converted to uppercase for header)
            content: Section content
            
        Returns:
            self (for method chaining)
        """
        self.sections[name] = content
        return self
    
    def build(self) -> str:
        """
        Build the final string with all sections.
        
        Format for each section:
        ## SECTION_NAME
        {content}
        
        (blank line between sections)
        
        Returns:
            Combined string with all sections
        """
        return ''.join([f"## {k.upper()}\n{v}\n\n" for k, v in self.sections.items()])


# ============================================
# HINTS & GUIDANCE
# ============================================

"""
HINT 1: Dictionary Storage
--------------------------
Python 3.7+ dictionaries preserve insertion order, so:
    self.sections = {}
will work perfectly!

HINT 2: Method Chaining
-----------------------
To enable chaining like builder.add().add().build():
    def add_section(self, name, content):
        self.sections[name] = content
        return self  # <-- This is the key!

HINT 3: String Formatting
-------------------------
For each section, you want:
    ## {NAME_UPPERCASE}
    {content}
    
You can use:
    - f-strings: f"## {name.upper()}\n{content}\n\n"
    - .format(): "## {}\n{}\n\n".format(name.upper(), content)

HINT 4: Building the Final String
---------------------------------
Approach 1 - List comprehension + join:
    parts = [f"## {name.upper()}\n{content}\n\n" 
             for name, content in self.sections.items()]
    return "".join(parts)

Approach 2 - Loop with accumulation:
    result = ""
    for name, content in self.sections.items():
        result += f"## {name.upper()}\n{content}\n\n"
    return result

HINT 5: Empty Builder
---------------------
If no sections added, return empty string:
    if not self.sections:
        return ""
"""

# ============================================
# TRY IT YOURSELF FIRST!
# ============================================
# Don't scroll down yet - try implementing it yourself
# Only look at the solution if you're really stuck!
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

# class SectionBuilder:
#     def __init__(self):
#         self.sections = {}
#     
#     def add_section(self, name: str, content: str) -> "SectionBuilder":
#         self.sections[name] = content
#         return self
#     
#     def build(self) -> str:
#         if not self.sections:
#             return ""
#         
#         parts = []
#         for name, content in self.sections.items():
#             parts.append(f"## {name.upper()}\n{content}\n\n")
#         
#         return "".join(parts)

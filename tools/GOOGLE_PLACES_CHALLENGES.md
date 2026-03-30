# 🗺️ Google Places API Tool — LeetCode Challenges

You will build a real `google_places_search` tool that plugs into your chat-client-toy
project and lets the LLM search for restaurants, cafes, hospitals — anything!

Complete all 5 challenges in order. At the end, you'll have a working tool.

---

## 🔧 How Tools Work in This Project

Before you start, understand the pattern from `readFile.py`:

```python
# Step 1: Define parameters using Pydantic
class ReadFileParams(BaseModel):
    path: str = Field(description="The file path to read")

# Step 2: Register with @tool decorator
@tool("read_file", "Read the contents of a file", ReadFileParams)
def read_file(path: str) -> str:
    # Step 3: Implement the function — always returns a string!
    return "file content here"
```

That's it! 3 steps:
1. **Pydantic model** for parameters
2. **@tool decorator** to register
3. **Function** that returns a string

---

## 🌐 Google Places API Quick Reference

### Endpoint
```
POST https://places.googleapis.com/v1/places:searchText
```

### Required Headers
```http
X-Goog-Api-Key: YOUR_API_KEY
X-Goog-FieldMask: places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.currentOpeningHours,places.types
Content-Type: application/json
```

### Request Body
```json
{
  "textQuery": "restaurants in Sydney",
  "maxResultCount": 5
}
```

### Response
```json
{
  "places": [
    {
      "displayName": { "text": "Aria Restaurant" },
      "formattedAddress": "1 Macquarie St, Sydney NSW 2000",
      "rating": 4.7,
      "priceLevel": "PRICE_LEVEL_VERY_EXPENSIVE",
      "currentOpeningHours": { "openNow": true },
      "types": ["restaurant", "food", "establishment"]
    }
  ]
}
```

### Price Levels
- `PRICE_LEVEL_FREE` → Free
- `PRICE_LEVEL_INEXPENSIVE` → $
- `PRICE_LEVEL_MODERATE` → $$
- `PRICE_LEVEL_EXPENSIVE` → $$$
- `PRICE_LEVEL_VERY_EXPENSIVE` → $$$$

---

## 🏆 Challenge 1: Copy the Pattern (Easy)

**Difficulty**: Easy  
**Time**: 10 minutes  
**Goal**: Understand the tool pattern by creating a dummy tool

### Problem

Create a tool called `greet_place` that takes a `place_name` parameter and returns a greeting string.

This teaches you the tool pattern WITHOUT worrying about API calls.

### Requirements

```python
# File: tools/greet_place.py

from pydantic import BaseModel, Field
from tools.tools import tool


class GreetPlaceParams(BaseModel):
    place_name: str = Field(description="???")  # Fill in description


@tool("greet_place", "???", GreetPlaceParams)  # Fill in description
def greet_place(place_name: str) -> str:
    # Return: "Hello from {place_name}! 👋"
    pass
```

### Test Cases

```python
# Test 1
result = greet_place("Sydney")
assert result == "Hello from Sydney! 👋"

# Test 2
result = greet_place("Tokyo")
assert result == "Hello from Tokyo! 👋"
```

### Run it:
```bash
cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
python tests/test_challenge_places1.py
```

### Learning Goal
✅ Understand how the @tool decorator works  
✅ Understand Pydantic params  
✅ Understand the function signature pattern

---

## 🏆 Challenge 2: Build the Params Model (Easy-Medium)

**Difficulty**: Easy-Medium  
**Time**: 20 minutes  
**Goal**: Build the Pydantic parameter model for the Places tool

### Problem

The Google Places tool needs these parameters:
- `query` (required): What to search for e.g. "coffee shops in Melbourne"
- `max_results` (optional, default=5): How many results to return (1-20)

### Requirements

```python
# File: tools/google_places.py

from pydantic import BaseModel, Field
from tools.tools import tool


class GooglePlacesParams(BaseModel):
    query: str = Field(description="???")           # Fill in
    max_results: int = Field(default=???, description="???")  # Fill in


# Leave the function empty for now
@tool("google_places_search", "Search for places using Google Places API", GooglePlacesParams)
def google_places_search(query: str, max_results: int = 5) -> str:
    return f"Searching for: {query} (max {max_results} results)"
```

### Test Cases

```python
from tools.google_places import GooglePlacesParams

# Test 1: Required field only
params = GooglePlacesParams(query="coffee shops")
assert params.query == "coffee shops"
assert params.max_results == 5  # Default

# Test 2: Both fields
params = GooglePlacesParams(query="restaurants", max_results=10)
assert params.max_results == 10

# Test 3: Schema check - verify it generates the right spec
schema = GooglePlacesParams.model_json_schema()
assert "query" in schema["properties"]
assert "max_results" in schema["properties"]
print("Schema:", schema)
```

### Run it:
```bash
cd /Users/rgupta6/Desktop/chat-client-toy/chat-client-toy
python tests/test_challenge_places2.py
```

### Learning Goal
✅ Pydantic BaseModel with required and optional fields  
✅ Field() with default values and descriptions  
✅ Understanding how model_json_schema() works (this becomes your tool_spec!)

---

## 🏆 Challenge 3: Make the HTTP Request (Medium)

**Difficulty**: Medium  
**Time**: 30 minutes  
**Goal**: Build the HTTP request to Google Places API

### Problem

Implement a function `call_places_api(query, max_results)` that makes the actual HTTP request and returns the raw JSON response.

### Context

```
POST https://places.googleapis.com/v1/places:searchText

Headers:
  X-Goog-Api-Key: from environment variable GOOGLE_PLACES_API_KEY
  X-Goog-FieldMask: places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.currentOpeningHours,places.types
  Content-Type: application/json

Body:
  { "textQuery": query, "maxResultCount": max_results }
```

### Requirements

```python
# File: tools/google_places.py (update this)

import os
import requests


PLACES_API_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.currentOpeningHours,places.types"


def call_places_api(query: str, max_results: int) -> dict:
    """
    Make HTTP request to Google Places API.
    
    Args:
        query: Search query string
        max_results: Max number of results (1-20)
    
    Returns:
        Parsed JSON response as dict
        
    Raises:
        ValueError: If API key not found in environment
        requests.HTTPError: If API returns error status
    """
    # TODO: Step 1 - Get API key from environment
    # Hint: os.environ.get("GOOGLE_PLACES_API_KEY")
    # Raise ValueError if not found
    
    # TODO: Step 2 - Build headers dict
    # Needs: X-Goog-Api-Key, X-Goog-FieldMask, Content-Type
    
    # TODO: Step 3 - Build request body dict
    # Needs: textQuery, maxResultCount
    
    # TODO: Step 4 - Make POST request using requests.post()
    # Hint: response = requests.post(url, headers=headers, json=body)
    
    # TODO: Step 5 - Check for errors
    # Hint: response.raise_for_status()
    
    # TODO: Step 6 - Return parsed JSON
    # Hint: return response.json()
    pass
```

### Test Cases

```python
# Test 1: No API key set
import os
os.environ.pop("GOOGLE_PLACES_API_KEY", None)

try:
    call_places_api("coffee", 5)
    assert False, "Should raise ValueError"
except ValueError as e:
    print("✅ Test 1 passed: ValueError raised when no API key")

# Test 2: With mock (don't need real API key)
# (We'll mock the requests.post call)
import unittest.mock as mock

mock_response = mock.Mock()
mock_response.json.return_value = {"places": []}
mock_response.raise_for_status.return_value = None

os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

with mock.patch("requests.post", return_value=mock_response) as mock_post:
    result = call_places_api("coffee", 5)
    
    # Verify request was made correctly
    call_args = mock_post.call_args
    assert call_args[0][0] == PLACES_API_URL  # URL correct
    assert call_args[1]["headers"]["X-Goog-Api-Key"] == "test-key"
    assert call_args[1]["json"]["textQuery"] == "coffee"
    assert call_args[1]["json"]["maxResultCount"] == 5
    print("✅ Test 2 passed: HTTP request built correctly")
```

### Hints

**Step 1 - API Key:**
```python
api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_PLACES_API_KEY not set in environment")
```

**Step 2 - Headers:**
```python
headers = {
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": FIELD_MASK,
    "Content-Type": "application/json"
}
```

**Step 3 - Body:**
```python
body = {
    "textQuery": query,
    "maxResultCount": max_results
}
```

**Step 4 - Request:**
```python
import requests
response = requests.post(PLACES_API_URL, headers=headers, json=body)
response.raise_for_status()
return response.json()
```

### Learning Goal
✅ Making HTTP POST requests with requests library  
✅ Environment variables for secrets  
✅ Headers and request body structure  
✅ Error handling for HTTP errors  

---

## 🏆 Challenge 4: Parse the Response (Medium)

**Difficulty**: Medium  
**Time**: 30 minutes  
**Goal**: Transform the raw API response into a readable string for the LLM

### Problem

The API returns JSON like this:
```json
{
  "places": [
    {
      "displayName": { "text": "Aria Restaurant" },
      "formattedAddress": "1 Macquarie St, Sydney NSW 2000",
      "rating": 4.7,
      "priceLevel": "PRICE_LEVEL_VERY_EXPENSIVE",
      "currentOpeningHours": { "openNow": true },
      "types": ["restaurant", "food", "establishment"]
    }
  ]
}
```

You need to format it as a readable string like this:
```
Found 1 place(s) for "restaurants in Sydney":

1. Aria Restaurant
   📍 1 Macquarie St, Sydney NSW 2000
   ⭐ Rating: 4.7/5
   💰 Price: $$$$
   🕐 Status: Open now
   🏷️ Types: restaurant, food
```

### Requirements

```python
def format_places_response(data: dict, query: str) -> str:
    """
    Format the API response into a readable string.
    
    Args:
        data: Parsed JSON response from API
        query: Original search query (for the header line)
    
    Returns:
        Human-readable formatted string
    """
    places = data.get("places", [])
    
    if not places:
        return f'No places found for "{query}"'
    
    result = f'Found {len(places)} place(s) for "{query}":\n\n'
    
    for i, place in enumerate(places, 1):
        # TODO: Extract name
        # Hint: place.get("displayName", {}).get("text", "Unknown")
        
        # TODO: Extract address
        # Hint: place.get("formattedAddress", "No address")
        
        # TODO: Extract rating
        # Hint: place.get("rating") — could be None!
        
        # TODO: Extract price level and convert to $ symbols
        # Hint: Use the PRICE_MAP below
        
        # TODO: Extract open now status
        # Hint: place.get("currentOpeningHours", {}).get("openNow")
        
        # TODO: Extract types (first 3 only, exclude generic ones)
        # Hint: place.get("types", [])
        
        # TODO: Build the formatted entry string
        pass
    
    return result


# Helper: Price level mapping
PRICE_MAP = {
    "PRICE_LEVEL_FREE": "Free",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}
```

### Test Cases

```python
data = {
    "places": [
        {
            "displayName": {"text": "Aria Restaurant"},
            "formattedAddress": "1 Macquarie St, Sydney NSW 2000",
            "rating": 4.7,
            "priceLevel": "PRICE_LEVEL_VERY_EXPENSIVE",
            "currentOpeningHours": {"openNow": True},
            "types": ["restaurant", "food", "establishment"]
        }
    ]
}

result = format_places_response(data, "restaurants in Sydney")

# Checks
assert "Aria Restaurant" in result
assert "1 Macquarie St" in result
assert "4.7" in result
assert "$$$$" in result
assert "Open" in result
assert "restaurant" in result.lower()
print("✅ All checks passed!")
print(result)

# Test: Empty result
empty = format_places_response({"places": []}, "unicorns")
assert "No places found" in empty
```

### Learning Goal
✅ Parsing nested JSON responses  
✅ Handling missing/None fields safely  
✅ Formatting output for LLM consumption  
✅ String building  

---

## 🏆 Challenge 5: Full Tool Integration (Hard)

**Difficulty**: Hard  
**Time**: 45 minutes  
**Goal**: Combine everything into a complete, working tool

### Problem

Wire together Challenge 2 (params), Challenge 3 (HTTP), and Challenge 4 (parsing) into the final `google_places_search` tool.

### Requirements

```python
# File: tools/google_places.py
# This is the FINAL version - combine all previous challenges

import os
import requests
from pydantic import BaseModel, Field
from tools.tools import tool


# --- Constants ---
PLACES_API_URL = "???"
FIELD_MASK = "???"
PRICE_MAP = {???}


# --- Params Model (from Challenge 2) ---
class GooglePlacesParams(BaseModel):
    query: str = Field(description="???")
    max_results: int = Field(default=5, description="???")


# --- Helper: HTTP Request (from Challenge 3) ---
def call_places_api(query: str, max_results: int) -> dict:
    # Your Challenge 3 implementation
    pass


# --- Helper: Format Response (from Challenge 4) ---
def format_places_response(data: dict, query: str) -> str:
    # Your Challenge 4 implementation
    pass


# --- The Tool (puts it all together!) ---
@tool("google_places_search", "Search for restaurants, cafes, shops and other places using Google Places API", GooglePlacesParams)
def google_places_search(query: str, max_results: int = 5) -> str:
    """
    Search Google Places and return formatted results.
    
    This tool:
    1. Validates inputs
    2. Calls the API
    3. Formats the response
    4. Returns readable text for the LLM
    """
    # TODO: Step 1 - Validate max_results (clamp to 1-20)
    
    # TODO: Step 2 - Call the API (use call_places_api)
    # Handle errors gracefully - return error string instead of raising
    
    # TODO: Step 3 - Format and return the response
    pass
```

### Test Cases

```python
# Test 1: Tool registered in registry
from tools.tools import registry
assert "google_places_search" in registry.tool_spec
assert "google_places_search" in registry.tool_function
print("✅ Test 1: Tool registered correctly")

# Test 2: Tool spec has correct structure
spec = registry.tool_spec["google_places_search"]
assert spec["type"] == "function"
assert spec["name"] == "google_places_search"
assert "query" in spec["parameters"]["properties"]
print("✅ Test 2: Tool spec correct")

# Test 3: Tool execution via registry (mock API)
import json
import unittest.mock as mock
import os
os.environ["GOOGLE_PLACES_API_KEY"] = "test-key"

mock_data = {
    "places": [{
        "displayName": {"text": "Test Cafe"},
        "formattedAddress": "123 Test St",
        "rating": 4.5,
        "priceLevel": "PRICE_LEVEL_MODERATE",
        "currentOpeningHours": {"openNow": True},
        "types": ["cafe"]
    }]
}

mock_response = mock.Mock()
mock_response.json.return_value = mock_data
mock_response.raise_for_status.return_value = None

with mock.patch("requests.post", return_value=mock_response):
    result = registry.execute(
        "google_places_search",
        json.dumps({"query": "cafes", "max_results": 3})
    )

assert "Test Cafe" in result
assert "123 Test St" in result
print("✅ Test 3: Full execution works!")
print("\nResult:")
print(result)
```

### Learning Goal
✅ Integrating multiple components  
✅ Error handling at the tool level  
✅ Input validation (clamping max_results)  
✅ Real tool development workflow  

---

## 🔑 Setup: API Key

Before testing with real API:

1. Get a Google Places API key from https://console.cloud.google.com/
2. Enable "Places API (New)" in your project
3. Add to your `.env` file:
   ```
   GOOGLE_PLACES_API_KEY=your_key_here
   ```
4. The `.env` is already gitignored ✅

---

## 📂 File Structure

```
chat-client-toy/
├── tools/
│   ├── tools.py                    (existing - don't modify)
│   ├── readFile.py                 (existing - use as reference)
│   ├── runBash.py                  (existing - use as reference)
│   └── google_places.py           (YOU CREATE THIS)
├── tests/
│   ├── test_challenge_places1.py  (YOU CREATE THIS)
│   ├── test_challenge_places2.py  (YOU CREATE THIS)
│   ├── test_challenge_places3.py  (YOU CREATE THIS)
│   ├── test_challenge_places4.py  (YOU CREATE THIS)
│   └── test_challenge_places5.py  (YOU CREATE THIS)
```

---

## 🚀 Start with Challenge 1!

Open `tools/google_places.py` and begin. The challenges build on each other.

Good luck! 🗺️

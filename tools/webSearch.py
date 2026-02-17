import json
import os
from pydantic import BaseModel, Field
import httpx
from tools.tools import tool


class WebSearchParams(BaseModel):
    query: str = Field(description="Web search query to run against Brave Search")
    count: int = Field(default=5, ge=1, le=10, description="Number of results to return (1-10)")


class BraveSearchClient(BaseModel):
    api_key: str = Field(description="Brave Search API key")
    base_url: str = Field(default="https://api.search.brave.com/res/v1/web/search")
    timeout_seconds: int = Field(default=10, ge=1)

    def search(self, query: str, count: int = 5) -> dict:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {"q": query, "count": count}

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()


@tool("web_search", "Search the web using Brave Search API", WebSearchParams)
def web_search(query: str, count: int = 5) -> str:
    """Search the web via Brave Search API and return a compact JSON summary."""
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        return "Missing BRAVE_SEARCH_API_KEY env var. Set it to use web_search."

    try:
        client = BraveSearchClient(api_key=api_key)
        data = client.search(query=query, count=count)
    except Exception as exc:
        return f"Brave Search request failed: {exc}"

    results = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "description": item.get("description"),
            } for item in data.get("web", {}).get("results", [])[:count]]
    
    return json.dumps({"query": query, "results": results}, ensure_ascii=False)

import os
import requests
from pathlib import Path
from pydantic import BaseModel, Field
from tools.tools import tool

_CONFIG_PATH = Path(__file__).parent.parent / "restaurants" / "my-delhi" / "config.json"
_PLACES_API_BASE = "https://places.googleapis.com/v1"


class GetPlacePhotosParams(BaseModel):
    max_photos: int = Field(default=5, description="Maximum number of photo URLs to return (1-10)")
    max_width_px: int = Field(default=800, description="Maximum width of photos in pixels")


@tool("get_place_photos", "Get photo URLs for this restaurant from Google Places", GetPlacePhotosParams)
def get_place_photos(max_photos: int = 5, max_width_px: int = 800) -> str:
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return "Configuration error: GOOGLE_PLACES_API_KEY not set in environment"

    # Load place_id from config
    import json
    try:
        config = json.loads(_CONFIG_PATH.read_text())
        place_id = config.get("place_id")
        if not place_id:
            return "Configuration error: place_id not found in config.json"
    except Exception as e:
        return f"Configuration error: Could not read config: {e}"

    # Step 1: Fetch photo references
    try:
        response = requests.get(
            f"{_PLACES_API_BASE}/places/{place_id}",
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "photos",
            }
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"Error fetching photos from Google Places API: {e}"

    photos = data.get("photos", [])
    if not photos:
        return "No photos found for this restaurant."

    # Step 2: Resolve photo URLs (follow redirects)
    max_photos = min(max_photos, 10, len(photos))
    photo_urls = []

    for photo in photos[:max_photos]:
        photo_name = photo.get("name", "")
        author = photo.get("authorAttributions", [{}])[0].get("displayName", "Unknown")
        width = photo.get("widthPx", "?")
        height = photo.get("heightPx", "?")

        try:
            media_response = requests.get(
                f"{_PLACES_API_BASE}/{photo_name}/media",
                params={"maxWidthPx": max_width_px, "key": api_key},
                allow_redirects=False
            )
            photo_url = media_response.headers.get("location", "")
            if photo_url:
                photo_urls.append({
                    "url": photo_url,
                    "author": author,
                    "width": width,
                    "height": height,
                })
        except Exception:
            continue

    if not photo_urls:
        return "Could not resolve photo URLs."

    # Step 3: Format result
    result = f"📸 Photos for My Delhi Newcastle ({len(photo_urls)} found):\n\n"
    for i, p in enumerate(photo_urls, 1):
        result += f"{i}. {p['url']}\n"
        result += f"   📐 {p['width']}x{p['height']}px | 📷 {p['author']}\n\n"

    return result.strip()

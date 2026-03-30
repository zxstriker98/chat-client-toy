"""
Google Place Details Tool

Fetches rich details about a specific place using its hardcoded Place ID.
Uses the Google Places API (New) Place Details endpoint.

Endpoint: GET https://places.googleapis.com/v1/places/{place_id}

Usage by LLM:
    get_place_details()                        → Full details + reviews
    get_place_details(include_reviews=False)   → Details only (faster)
"""

import os
import json
import requests
from pathlib import Path
from pydantic import BaseModel, Field
from tools.tools import tool


# ──────────────────────────────────────────
# Constants
# ──────────────────────────────────────────

PLACES_API_BASE = "https://places.googleapis.com/v1/places"

# Fields to fetch — only pay for what we need
FIELD_MASK_NO_REVIEWS = ",".join([
    "displayName",
    "formattedAddress",
    "rating",
    "userRatingCount",
    "priceLevel",
    "currentOpeningHours",
    "internationalPhoneNumber",
    "websiteUri",
    "businessStatus",
    "types",
    "location",
])

FIELD_MASK_WITH_REVIEWS = FIELD_MASK_NO_REVIEWS + ",reviews"

PRICE_MAP = {
    "PRICE_LEVEL_FREE":           "Free",
    "PRICE_LEVEL_INEXPENSIVE":    "$",
    "PRICE_LEVEL_MODERATE":       "$$",
    "PRICE_LEVEL_EXPENSIVE":      "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

# Load place_id from the restaurant config file
_CONFIG_PATH = Path(__file__).parent.parent / "restaurants" / "delhi-darbar" / "config.json"


def _load_place_id() -> str:
    """Load the place_id from the restaurant config file."""
    try:
        with open(_CONFIG_PATH, "r") as f:
            config = json.load(f)
        place_id = config.get("place_id", "")
        if not place_id:
            raise ValueError("place_id not set in config.json")
        return place_id
    except FileNotFoundError:
        raise ValueError(f"Restaurant config not found at: {_CONFIG_PATH}")


# ──────────────────────────────────────────
# HTTP Request
# ──────────────────────────────────────────

def _call_place_details_api(place_id: str, include_reviews: bool) -> dict:
    """
    Make GET request to Google Places Details API.

    Args:
        place_id: Google Place ID
        include_reviews: Whether to fetch reviews (costs more quota)

    Returns:
        Parsed JSON response

    Raises:
        ValueError: If API key not configured
        requests.HTTPError: If API returns an error
    """
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_PLACES_API_KEY not set in environment")

    url = f"{PLACES_API_BASE}/{place_id}"
    field_mask = FIELD_MASK_WITH_REVIEWS if include_reviews else FIELD_MASK_NO_REVIEWS

    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": field_mask,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# ──────────────────────────────────────────
# Response Formatter
# ──────────────────────────────────────────

def _format_place_details(data: dict, include_reviews: bool) -> str:
    """Format raw API response into a readable string for the LLM."""

    lines = []

    # ── Name & Status ──
    name = data.get("displayName", {}).get("text", "Unknown")
    status = data.get("businessStatus", "")
    status_emoji = "✅" if status == "OPERATIONAL" else "⚠️"
    lines.append(f"📍 {name} {status_emoji}")
    lines.append("")

    # ── Address ──
    address = data.get("formattedAddress", "Address not available")
    lines.append(f"🗺️  Address: {address}")

    # ── Location coords ──
    location = data.get("location", {})
    if location:
        lat = location.get("latitude", "")
        lng = location.get("longitude", "")
        lines.append(f"🧭 Coordinates: {lat}, {lng}")

    lines.append("")

    # ── Rating ──
    rating = data.get("rating")
    rating_count = data.get("userRatingCount")
    if rating:
        stars = "⭐" * round(rating)
        count_str = f" ({rating_count:,} reviews)" if rating_count else ""
        lines.append(f"⭐ Rating: {rating}/5 {stars}{count_str}")

    # ── Price Level ──
    price_raw = data.get("priceLevel", "")
    price = PRICE_MAP.get(price_raw, "")
    if price:
        lines.append(f"💰 Price: {price}")

    lines.append("")

    # ── Opening Hours ──
    hours_data = data.get("currentOpeningHours", {})
    if hours_data:
        open_now = hours_data.get("openNow")
        if open_now is True:
            lines.append("🕐 Currently: OPEN ✅")
        elif open_now is False:
            lines.append("🕐 Currently: CLOSED ❌")

        weekday_desc = hours_data.get("weekdayDescriptions", [])
        if weekday_desc:
            lines.append("📅 Opening Hours:")
            for day in weekday_desc:
                lines.append(f"   {day}")

    lines.append("")

    # ── Contact ──
    phone = data.get("internationalPhoneNumber")
    website = data.get("websiteUri")
    if phone or website:
        lines.append("📞 Contact:")
        if phone:
            lines.append(f"   Phone: {phone}")
        if website:
            lines.append(f"   Website: {website}")
        lines.append("")

    # ── Types ──
    types = data.get("types", [])
    # Filter out overly generic types
    skip_types = {"point_of_interest", "establishment", "food", "store"}
    clean_types = [t.replace("_", " ") for t in types if t not in skip_types]
    if clean_types:
        lines.append(f"🏷️  Type: {', '.join(clean_types[:5])}")
        lines.append("")

    # ── Reviews ──
    if include_reviews:
        reviews = data.get("reviews", [])
        if reviews:
            lines.append(f"💬 Recent Reviews ({len(reviews)} shown):")
            lines.append("")
            for i, review in enumerate(reviews[:5], 1):
                author = review.get("authorAttribution", {}).get("displayName", "Anonymous")
                r_rating = review.get("rating", "?")
                r_text = review.get("text", {}).get("text", "")
                r_time = review.get("relativePublishTimeDescription", "")
                stars = "⭐" * int(r_rating) if isinstance(r_rating, int) else ""

                lines.append(f"  {i}. {author} — {r_rating}/5 {stars} ({r_time})")
                if r_text:
                    # Wrap long reviews
                    if len(r_text) > 200:
                        r_text = r_text[:200] + "..."
                    lines.append(f"     \"{r_text}\"")
                lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────
# Tool Definition
# ──────────────────────────────────────────

class GetPlaceDetailsParams(BaseModel):
    include_reviews: bool = Field(
        default=True,
        description="Whether to include customer reviews in the response"
    )


@tool(
    "get_place_details",
    "Get current details for this restaurant including address, opening hours, ratings, contact info and customer reviews from Google",
    GetPlaceDetailsParams
)
def get_place_details(include_reviews: bool = True) -> str:
    """
    Fetch and format place details from Google Places API.

    Returns rich information including:
    - Address and coordinates
    - Current open/closed status
    - Full weekly opening hours
    - Rating and review count
    - Price level
    - Phone and website
    - Recent customer reviews (if include_reviews=True)
    """
    try:
        place_id = _load_place_id()
        data = _call_place_details_api(place_id, include_reviews)
        return _format_place_details(data, include_reviews)

    except ValueError as e:
        return f"Configuration error: {e}"
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        if status == 403:
            return "Error: Google Places API key is invalid or doesn't have Places API enabled."
        elif status == 404:
            return "Error: Place not found. The place_id may be incorrect."
        elif status == 429:
            return "Error: Google Places API quota exceeded. Try again later."
        return f"Error calling Google Places API (HTTP {status}): {e}"
    except requests.ConnectionError:
        return "Error: Could not connect to Google Places API. Check your internet connection."
    except Exception as e:
        return f"Unexpected error fetching place details: {type(e).__name__}: {e}"

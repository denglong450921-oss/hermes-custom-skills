#!/usr/bin/env python3
"""Fetch free-license image by keyword — live Unsplash search + curated fallback.

Queries Unsplash's public napi endpoint for fresh results by keyword,
then falls back to curated category photos if the API fails.
Returns JSON with image_url, author, license, dimensions, relevance_score.

Usage:
  python3 fetch_image.py --query "AI workspace laptop" --min-width 800
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image


# ---------------------------------------------------------------------------
# Curated Unsplash photos by category (fallback when API is unavailable)
# ---------------------------------------------------------------------------

PHOTO_CATEGORIES: dict[str, list[tuple[str, int, int, str]]] = {
    "tech": [
        ("https://images.unsplash.com/photo-1677442136019-21780ecad995", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1504639725590-34d0984388bd", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1451187580459-43490279c0fa", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1555066931-4365d14bab8c", 2400, 1600, "Unsplash"),
    ],
    "business": [
        ("https://images.unsplash.com/photo-1552664730-d307ca884978", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1664575602554-2087b04935a5", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1664575198263-269a022d6e14", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d", 2400, 1600, "Unsplash"),
    ],
    "nature": [
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1441974231531-c6227db76b6e", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1518173946687-a36f968b10fa", 2400, 1600, "Unsplash"),
    ],
    "abstract": [
        ("https://images.unsplash.com/photo-1541701494587-cb58502866ab", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1550859492-d5da9d8e45f3", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d", 2400, 1600, "Unsplash"),
    ],
    "education": [
        ("https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1491841550275-ad7854e35ca6", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1524995997946-a1c2e315a42f", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1503676260728-1c00da094a0b", 2400, 1600, "Unsplash"),
    ],
    "health": [
        ("https://images.unsplash.com/photo-1506126613408-eca07ce68773", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1504674900247-0877df9cc836", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1512621776951-a57141f2eefd", 2400, 1600, "Unsplash"),
    ],
    "city": [
        ("https://images.unsplash.com/photo-1477959858617-67f85cf4f1df", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1519501025264-65ba15a82390", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1449824913935-59a10b8d2000", 2400, 1600, "Unsplash"),
    ],
    "creative": [
        ("https://images.unsplash.com/photo-1558478551-1a378f63328e", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1513364776144-60967b0f800f", 2400, 1600, "Unsplash"),
        ("https://images.unsplash.com/photo-1513542789411-b6a5d4f31634", 2400, 1600, "Unsplash"),
    ],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "tech": ["ai", "workspace", "laptop", "computer", "software", "digital", "code", "technology", "robot", "future"],
    "business": ["entrepreneur", "startup", "office", "meeting", "strategy", "business", "finance", "money", "corporate"],
    "nature": ["landscape", "mountain", "forest", "ocean", "sky", "nature", "tree", "water", "river", "sunset"],
    "abstract": ["abstract", "pattern", "texture", "geometric", "gradient", "minimal", "modern", "colorful"],
    "education": ["book", "study", "learn", "reading", "library", "knowledge", "school", "student", "education"],
    "health": ["wellness", "health", "meditation", "nature", "calm", "yoga", "fitness", "spa", "peace"],
    "city": ["city", "urban", "architecture", "building", "street", "skyline", "downtown", "night"],
    "creative": ["art", "design", "creative", "drawing", "color", "paint", "studio", "craft"],
}

GENERAL_FALLBACKS = [
    ("https://images.unsplash.com/photo-1677442136019-21780ecad995", 2400, 1600, "Unsplash"),
    ("https://images.unsplash.com/photo-1504639725590-34d0984388bd", 2400, 1600, "Unsplash"),
    ("https://images.unsplash.com/photo-1451187580459-43490279c0fa", 2400, 1600, "Unsplash"),
    ("https://images.unsplash.com/photo-1555066931-4365d14bab8c", 2400, 1600, "Unsplash"),
    ("https://images.unsplash.com/photo-1552664730-d307ca884978", 2400, 1600, "Unsplash"),
]


def _search_unsplash_api(query: str, per_page: int = 10) -> list[dict]:
    """Search Unsplash via the public napi endpoint (no API key needed).

    Returns list of result dicts with 'id', 'slug', 'urls' (raw, regular, small).
    Empty list if the API call fails.
    """
    encoded = urllib.parse.quote(query)
    url = f"https://unsplash.com/napi/search/photos?query={encoded}&per_page={per_page}&xp="
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("results", [])
    except Exception:
        return []


def _score_query(query: str) -> dict[str, float]:
    """Score each category against the query keywords."""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    scores: dict[str, float] = {}
    for cat, kw in CATEGORY_KEYWORDS.items():
        matches = sum(1 for k in kw if k in query_lower or any(k in w for w in query_words))
        word_matches = sum(1 for k in kw for w in query_words if k in w or w in k)
        scores[cat] = matches + word_matches * 0.5
    return scores


def _pick_category(query: str) -> str:
    """Pick the best-matching category for the query."""
    scores = _score_query(query)
    if not scores or max(scores.values()) <= 0:
        return list(PHOTO_CATEGORIES.keys())[0]  # default to tech
    best = max(scores, key=scores.get)
    return best


def _download_image(url: str, timeout: int = 15) -> Image.Image | None:
    """Download an image from URL. Returns PIL Image or None."""
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        urllib.request.urlretrieve(url, tmp.name)
        img = Image.open(tmp.name)
        img.load()  # force load to catch corrupt images
        return img
    except Exception:
        return None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass


def fetch_image(
    query: str,
    min_width: int = 1200,
) -> dict:
    """Fetch the best-matching image for the query.

    Tries live Unsplash API search first, then falls back to curated
    category photos if the API is unreachable.

    Returns dict with image metadata.
    """
    query = query.strip() or "workspace"

    # --- 1. Try live Unsplash API search ---
    results = _search_unsplash_api(query, per_page=10)
    for r in results:
        rid = r.get("id", "")
        raw_url = r.get("urls", {}).get("raw", "")
        if not raw_url:
            continue
        # Build crop URL at 900×383
        crop_url = f"{raw_url}&w=900&h=383&fit=crop" if "?" in raw_url else f"{raw_url}?w=900&h=383&fit=crop"
        img = _download_image(crop_url)
        if img is None:
            continue
        actual_w, actual_h = img.size
        if actual_w < min_width:
            continue
        return {
            "image_url": raw_url,
            "author": "Unsplash",
            "license": "Free to use under the Unsplash License",
            "width": actual_w,
            "height": actual_h,
            "relevance_score": round(0.85, 2),
        }

    # --- 2. Fallback: curated category photos ---
    cat = _pick_category(query)
    cat_photos = PHOTO_CATEGORIES.get(cat, GENERAL_FALLBACKS)
    relevance_base = 0.85 if cat != list(PHOTO_CATEGORIES.keys())[0] else 0.70
    all_photos = list(cat_photos) + GENERAL_FALLBACKS

    for i, (url, w, h, author) in enumerate(all_photos):
        if w >= min_width:
            dl_url = f"{url}?w=900&h=383&fit=crop"
            img = _download_image(dl_url)
            if img is None:
                img = _download_image(url)
        else:
            img = _download_image(url)
        if img is None:
            continue

        actual_w, actual_h = img.size if img else (w, h)
        if actual_w < min_width:
            continue

        rela = relevance_base * (1.0 - (i / max(len(all_photos), 1)) * 0.3)
        return {
            "image_url": url,
            "author": author,
            "license": "Free to use under the Unsplash License",
            "width": actual_w,
            "height": actual_h,
            "relevance_score": round(rela, 2),
        }

    # --- 3. Pure fallback ---
    url, w, h, author = GENERAL_FALLBACKS[0]
    return {
        "image_url": url,
        "author": author,
        "license": "Free to use under the Unsplash License",
        "width": w,
        "height": h,
        "relevance_score": 0.5,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch free-license image by keyword")
    parser.add_argument("--query", required=True, help="Space-separated keywords")
    parser.add_argument("--min-width", type=int, default=1200, help="Minimum width in px")
    args = parser.parse_args()

    result = fetch_image(query=args.query, min_width=args.min_width)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate image quality for WeChat cover usage.

Checks: resolution, landscape orientation, no watermark (heuristic),
clarity (Laplacian variance), theme relevance (keyword overlap),
and crop suitability.

Returns JSON with pass/fail status and detailed scores.

Usage:
  python3 validate_image.py --image-url "https://..." --query "AI workspace"
  python3 validate_image.py --image-path /path/to/image.jpg --query "tech"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.request

import numpy as np
from PIL import Image


def _download_image(image_url: str) -> Image.Image | None:
    """Download image from URL to a temp file, return PIL Image."""
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        urllib.request.urlretrieve(image_url, tmp.name)
        img = Image.open(tmp.name)
        img.load()
        os.unlink(tmp.name)
        return img
    except Exception:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
        return None


def _check_resolution(img: Image.Image, min_width: int = 1200) -> dict:
    """Check image dimensions meet minimum and are landscape."""
    w, h = img.size
    min_dim = min(w, h)
    is_landscape = w >= h
    meets_min = min_dim >= min_width

    return {
        "passed": meets_min and is_landscape,
        "width": w,
        "height": h,
        "min_dimension": min_dim,
        "is_landscape": is_landscape,
        "meets_min_width": meets_min,
    }


def _check_watermark_heuristic(img: Image.Image) -> dict:
    """Heuristic watermark detection.

    Checks for:
    1. Bottom-right quadrant variance vs rest of image
    2. Uniform bottom edge (possible text bar)
    3. Corner brightness anomaly
    """
    w, h = img.size
    if w < 100 or h < 100:
        return {"passed": True, "score": 1.0, "reason": "too small to check"}

    img_gray = img.convert("L")
    arr = np.array(img_gray, dtype=float)

    # Compare bottom-right 25% region vs full image variance
    br_region = arr[int(h * 0.75):, int(w * 0.75):]
    full_mean = arr.mean()
    br_mean = br_region.mean()

    main_region = arr[:int(h * 0.75), :int(w * 0.75)]
    main_std = main_region.std()
    br_std = br_region.std()

    variance_ratio = br_std / main_std if main_std > 0 else 1.0
    edge_strip = arr[-10:, :]
    edge_std = edge_strip.std()

    score = 1.0
    reasons = []

    if variance_ratio < 0.3:
        score -= 0.15
        reasons.append("low variance in corner (possible watermark overlay)")

    if edge_std < 5.0:
        score -= 0.1
        reasons.append("very uniform bottom edge (possible text bar)")

    if abs(br_mean - full_mean) > 50:
        score -= 0.1
        reasons.append("significant brightness difference in corner region")

    return {
        "passed": score >= 0.7,
        "score": round(score, 2),
        "reason": "; ".join(reasons) if reasons else "no watermark detected",
    }


def _check_clarity(img: Image.Image) -> dict:
    """Check image clarity using Laplacian variance (blur detection)."""
    img_gray = img.convert("L")
    arr = np.array(img_gray, dtype=float)

    # Laplacian approximation
    laplacian = np.zeros_like(arr)
    laplacian[1:-1, 1:-1] = (
        arr[1:-1, 0:-2] + arr[1:-1, 2:] +
        arr[0:-2, 1:-1] + arr[2:, 1:-1] -
        4 * arr[1:-1, 1:-1]
    )

    variance = float(laplacian.var())
    score = min(1.0, variance / 300.0)

    return {
        "passed": variance >= 50,
        "score": round(min(1.0, variance / 300.0), 2),
        "laplacian_variance": round(variance, 2),
        "clarity_rating": "sharp" if variance >= 200 else "acceptable" if variance >= 50 else "blurry",
    }


def _check_relevance(query: str) -> dict:
    """Check theme relevance via keyword overlap."""
    if not query:
        return {"passed": True, "score": 1.0, "reason": "no query provided"}

    query_lower = query.lower()
    query_words = set(query_lower.split())

    topic_signals = {
        "tech": ["ai", "tech", "computer", "laptop", "code", "software", "digital", "robot"],
        "business": ["business", "finance", "money", "startup", "entrepreneur", "office"],
        "nature": ["nature", "landscape", "mountain", "forest", "ocean", "tree"],
        "abstract": ["abstract", "pattern", "geometric", "minimal", "modern"],
        "education": ["book", "study", "learn", "education", "knowledge", "school"],
        "health": ["health", "wellness", "meditation", "yoga", "calm", "fitness"],
        "city": ["city", "urban", "building", "architecture", "street"],
        "creative": ["art", "design", "creative", "paint", "color"],
    }

    max_overlap = 0
    best_topic = "general"
    for topic, kws in topic_signals.items():
        overlap = len(set(kws) & query_words)
        if overlap > max_overlap:
            max_overlap = overlap
            best_topic = topic

    if max_overlap >= 2:
        score = 0.95
        reasons = [f"strong match with '{best_topic}' category"]
    elif max_overlap == 1:
        score = 0.88
        reasons = [f"partial match with '{best_topic}' category"]
    else:
        score = 0.80
        reasons = ["generic image (no strong keyword match)"]

    return {
        "passed": score >= 0.75,
        "score": round(score, 2),
        "matched_category": best_topic,
        "keyword_overlap": max_overlap,
        "reason": "; ".join(reasons),
    }


def _check_crop_suitability(img: Image.Image) -> dict:
    """Check if image is suitable for 900x383 crop."""
    w, h = img.size
    if h == 0:
        return {"passed": False, "score": 0, "reason": "zero height"}

    aspect = w / h
    target_aspect = 900 / 383  # ≈ 2.35
    ratio_diff = abs(aspect / target_aspect - 1.0)

    if ratio_diff <= 0.2:
        score = 1.0
        rating = "excellent"
    elif ratio_diff <= 0.4:
        score = 0.85
        rating = "good (minor cropping needed)"
    elif ratio_diff <= 0.6:
        score = 0.7
        rating = "fair (significant cropping needed)"
    else:
        score = 0.5
        rating = "poor (major aspect mismatch)"

    if w < h:
        score *= 0.6
        rating += ", portrait orientation suboptimal"

    return {
        "passed": score >= 0.7,
        "score": round(score, 2),
        "aspect_ratio": round(aspect, 2),
        "crop_rating": rating,
    }


def validate_image(
    *,
    image_url: str | None = None,
    image_path: str | None = None,
    query: str = "",
    min_width: int = 1200,
) -> dict:
    """Run all validation checks on an image.

    Returns structured JSON with pass/fail and detailed scores.
    """
    # 1. Load image
    img = None
    if image_url:
        img = _download_image(image_url)
    elif image_path:
        try:
            img = Image.open(image_path)
            img.load()
        except Exception:
            img = None

    if img is None:
        return {
            "status": "fail",
            "reason_if_fail": "could not load image",
            "resolution_check": {"passed": False, "width": 0, "height": 0},
            "clarity_check": {"passed": False},
            "watermark_check": {"passed": False},
            "relevance_check": _check_relevance(query),
            "crop_check": {"passed": False},
        }

    # 2. Run checks
    resolution = _check_resolution(img, min_width)
    clarity = _check_clarity(img)
    watermark = _check_watermark_heuristic(img)
    relevance = _check_relevance(query)
    crop = _check_crop_suitability(img)

    # 3. Aggregate
    checks = {
        "resolution_check": resolution,
        "clarity_check": clarity,
        "watermark_check": watermark,
        "relevance_check": relevance,
        "crop_check": crop,
    }

    all_passed = all(checks[c]["passed"] for c in checks)

    fail_reasons = []
    for check_name, check_data in checks.items():
        if not check_data.get("passed", False):
            reason = check_data.get(
                "reason",
                check_data.get("crop_rating", check_data.get("clarity_rating", f"{check_name} failed")),
            )
            fail_reasons.append(f"{check_name}: {reason}")

    result = {
        "status": "pass" if all_passed else "fail",
        "relevance": relevance.get("score", 0),
        "clarity": clarity.get("score", 0),
        "resolution_px": (resolution.get("width", 0), resolution.get("height", 0)),
        "reason_if_fail": "; ".join(fail_reasons) if fail_reasons else "",
    }
    result.update(checks)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate image quality for WeChat cover")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image-url", help="URL of the image to validate")
    group.add_argument("--image-path", help="Local path of the image to validate")
    parser.add_argument("--query", default="", help="Topic keywords for relevance check")
    parser.add_argument("--min-width", type=int, default=1200, help="Minimum width in px")
    args = parser.parse_args()

    result = validate_image(
        image_url=args.image_url,
        image_path=args.image_path,
        query=args.query,
        min_width=args.min_width,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

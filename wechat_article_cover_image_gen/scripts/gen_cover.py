#!/usr/bin/env python3
"""
Generate a WeChat Official Account cover image from an article title.
Downloads a stock photo, applies a uniform dark overlay, and draws
centered, outlined text onto a 900x383 PNG.

Usage:
  python3 gen_cover.py \
    --title "AI 时代的 OPC" \
    --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
    --tagline "决策者 + AI 工具链 · 可验证需求 · 商业闭环系统" \
    --output /path/to/cover.png \
    --image-url "https://images.unsplash.com/photo-xxx?w=900&h=383&fit=crop"
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import numpy as np


FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
FALLBACK_FONTS = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]

CANVAS_W = 900
CANVAS_H = 383

UNSPLASH_FALLBACKS = [
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=900&h=383&fit=crop",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_font() -> str:
    for p in [FONT, *FALLBACK_FONTS]:
        if os.path.exists(p):
            return p
    raise RuntimeError("No Chinese-capable font found. Install STHeiti or Songti.")


def _get_bounds(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int, int]:
    """Render text to a mask and return (left_offset, right_offset, height)."""
    off = 500
    m = Image.new("L", (CANVAS_W + off * 2, 200), 0)
    ImageDraw.Draw(m).text((off, 5), text, fill=255, font=font)
    arr = np.array(m)
    cols = arr.any(axis=0).nonzero()[0]
    if len(cols) == 0:
        return 0, 0, 0
    rows = arr.any(axis=1).nonzero()[0]
    return int(cols[0]) - off, int(cols[-1]) - off, int(rows[-1]) - int(rows[0]) + 1


def _center_x(text: str, font: ImageFont.FreeTypeFont) -> int:
    l, r, _ = _get_bounds(text, font)
    return int(round((CANVAS_W - 1 - l - r) / 2))


def _pick_title_font(text: str) -> ImageFont.FreeTypeFont:
    """Pick the largest font size that keeps the title within canvas width
    (target ~92-94%). Falls back to min size if even the smallest overflows."""
    target = int(CANVAS_W * 0.92)
    font_path = _resolve_font()
    best = 60
    for fs in range(60, 200, 5):
        ft = ImageFont.truetype(font_path, fs)
        w = _get_bounds(text, ft)[1] - _get_bounds(text, ft)[0] + 1
        if w <= target:
            best = fs  # fits within target — keep increasing
        elif w <= CANVAS_W:
            best = fs  # fits within canvas but exceeds target — keep going
        else:
            # Exceeds canvas — stop; use the previous size that fit
            break
    return ImageFont.truetype(font_path, best)


def _download_image(url: str | None) -> Image.Image:
    """Download a stock image or use the provided URL. Falls back on failure."""
    urls = [url] if url else []
    urls += UNSPLASH_FALLBACKS
    for u in urls:
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            urllib.request.urlretrieve(u, tmp.name)
            img = Image.open(tmp.name).convert("RGBA")
            if img.size == (CANVAS_W, CANVAS_H):
                return img
            img = img.resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
            return img
        except Exception:
            continue
    # Pure fallback: solid dark gradient
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (20, 30, 50, 255))
    return img


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render(
    *,
    title: str,
    subtitle: str,
    tagline: str,
    label: str,
    output: str,
    image_url: str | None = None,
    outline_width: int = 2,
) -> dict:
    """Generate a WeChat cover image and write to ``output``.

    Returns a dict with metadata about the generated image.
    """
    font_path = _resolve_font()

    # 1. Load background
    bg = _download_image(image_url)
    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 2. Uniform translucent layer
    draw.rectangle([0, 0, CANVAS_W, CANVAS_H], fill=(5, 8, 15, 165))

    # 3. Fonts
    ft_title = _pick_title_font(title)
    ft_label = ImageFont.truetype(font_path, 14)
    ft_sub = ImageFont.truetype(font_path, 26)
    ft_tag = ImageFont.truetype(font_path, 13)

    _, _, th = _get_bounds(title, ft_title)
    _, _, sub_h = _get_bounds(subtitle, ft_sub)

    # 4. Vertical centering
    gaps = {"lg": 28, "ts": 16, "sb": 14, "bt": 14}
    total_h = 16 + gaps["lg"] + th + gaps["ts"] + sub_h + gaps["sb"] + 2 + gaps["bt"] + 18
    v_off = (CANVAS_H - total_h) // 2

    ly = v_off
    ty = ly + gaps["lg"]
    sy = ty + th + gaps["ts"]
    bar_y = sy + sub_h + gaps["sb"]
    tgy = bar_y + gaps["bt"]

    # 5. Draw label
    lx = _center_x(label, ft_label)
    for ox in range(-1, 2):
        for oy in range(-1, 2):
            if ox == 0 and oy == 0:
                continue
            draw.text((lx + ox, ly + oy), label, fill=(0, 0, 0, 160), font=ft_label)
    draw.text((lx, ly), label, fill=(196, 156, 82, 220), font=ft_label)

    # 6. Draw title (outline + white fill)
    tx = _center_x(title, ft_title)
    o = outline_width
    for ox in range(-o, o + 1):
        for oy in range(-o, o + 1):
            if ox == 0 and oy == 0:
                continue
            draw.text((tx + ox, ty + oy), title, fill=(0, 0, 0, 200), font=ft_title)
    draw.text((tx, ty), title, fill=(255, 255, 255, 255), font=ft_title)

    # 7. Draw subtitle (outline + white fill)
    sx = _center_x(subtitle, ft_sub)
    for ox in range(-1, 2):
        for oy in range(-1, 2):
            if ox == 0 and oy == 0:
                continue
            draw.text((sx + ox, sy + oy), subtitle, fill=(0, 0, 0, 180), font=ft_sub)
    draw.text((sx, sy), subtitle, fill=(255, 255, 255, 240), font=ft_sub)

    # 8. Gold accent bar
    bar_len = 260
    bar_x1 = (CANVAS_W - bar_len) // 2
    for xp in range(bar_x1, bar_x1 + bar_len):
        dist = abs(xp - (bar_x1 + bar_len // 2))
        a = max(0, 220 - int(dist * 2.2))
        overlay.putpixel((xp, bar_y), (196, 156, 82, a))

    # 9. Draw tagline (outline + warm fill)
    tx4 = _center_x(tagline, ft_tag)
    for ox in range(-1, 2):
        for oy in range(-1, 2):
            if ox == 0 and oy == 0:
                continue
            draw.text((tx4 + ox, tgy + oy), tagline, fill=(0, 0, 0, 160), font=ft_tag)
    draw.text((tx4, tgy), tagline, fill=(200, 195, 185, 220), font=ft_tag)

    # 10. Composite & save
    result = Image.alpha_composite(bg, overlay).convert("RGB")
    result.save(output, "PNG")

    tw = _get_bounds(title, ft_title)[1] - _get_bounds(title, ft_title)[0] + 1
    return {
        "output": str(Path(output).resolve()),
        "canvas": f"{CANVAS_W}x{CANVAS_H}",
        "title_font_size": ft_title.size,
        "title_coverage_pct": round(100 * tw / CANVAS_W),
        "vertical_offset": v_off,
        "status": "ok",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a WeChat Official Account cover image."
    )
    parser.add_argument("--title", required=True, help="Main title text")
    parser.add_argument("--subtitle", default="", help="Subtitle text")
    parser.add_argument("--tagline", default="", help="Bottom tagline text")
    parser.add_argument(
        "--label", default="FEATURED ARTICLE",
        help="Top label text (default: FEATURED ARTICLE)",
    )
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument(
        "--image-url", default=None,
        help="Stock image URL (900x383 preferred). Auto-falls back if omitted or fails.",
    )
    parser.add_argument(
        "--outline-width", type=int, default=2,
        help="Text outline radius in px (default: 2)",
    )
    args = parser.parse_args()

    try:
        result = render(
            title=args.title,
            subtitle=args.subtitle,
            tagline=args.tagline,
            label=args.label,
            output=args.output,
            image_url=args.image_url,
            outline_width=args.outline_width,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Cover generated: {result['output']}")
    print(f"  Canvas: {result['canvas']}")
    print(f"  Title: {args.title}")
    print(f"  Title font: {result['title_font_size']}px")
    print(f"  Title width coverage: {result['title_coverage_pct']}%")
    print(f"  Vertical offset: {result['vertical_offset']}px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

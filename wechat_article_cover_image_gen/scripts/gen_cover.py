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


# ---------------------------------------------------------------------------
# Text layout rules — adaptive proportions with aesthetic breathing space
# ---------------------------------------------------------------------------
# Principles:
# 1. More text → tighter fit. Less text → more breathing room.
# 2. Minimum side margin: 50px. Target 60-110px ideal.
# 3. Short titles (1-4 chars) should not fill width — use ~55-65%.
# 4. Vertical gaps scale with content density.
# 5. Total text block never exceeds 85% of canvas height.

def _title_target_width(text: str) -> int:
    """Return target width in px based on text length.
    
    Short text → smaller target (more breathing room).
    Long text → larger target (fills width reasonably).
    """
    n = len(text)
    if n <= 4:      ratio = 0.55
    elif n <= 8:    ratio = 0.70
    elif n <= 12:   ratio = 0.78
    elif n <= 18:   ratio = 0.82
    else:           ratio = 0.85
    return int(CANVAS_W * ratio)


def _vertical_gaps(char_count: int, has_sub: bool, has_tag: bool) -> dict[str, int]:
    """Return vertical gaps (px) between elements.
    
    Dense content → tighter gaps. Sparse content → wider gaps for breathing.
    """
    # Base gaps
    g = {"lg": 28, "ts": 18, "sb": 16, "bt": 16}
    
    # If very little content, expand gaps to fill space elegantly
    sparse = char_count <= 10 and (not has_sub or not has_tag)
    if sparse:
        g["lg"] = 36
        g["ts"] = 24
        g["sb"] = 22
        g["bt"] = 20
    return g


def _pick_title_font(text: str) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Pick the font size closest to target width and wrap text if needed.
    
    Returns (font, lines) where lines has 1+ strings.
    If the text overflows canvas at minimum font, it's wrapped across lines.
    """
    target = _title_target_width(text)
    font_path = _resolve_font()
    
    # Find best font size for single-line rendering
    best = 45
    ft = ImageFont.truetype(font_path, best)
    best_dist = abs(_get_bounds(text, ft)[1] - _get_bounds(text, ft)[0] + 1 - target)
    
    for fs in range(50, 200, 5):
        ft = ImageFont.truetype(font_path, fs)
        w = _get_bounds(text, ft)[1] - _get_bounds(text, ft)[0] + 1
        if w > CANVAS_W:
            break
        dist = abs(w - target)
        if dist < best_dist:
            best = fs
            best_dist = dist
        elif dist > best_dist and w > target:
            break
    
    # Check if text fits on one line at the chosen font
    ft_best = ImageFont.truetype(font_path, best)
    single_w = _get_bounds(text, ft_best)[1] - _get_bounds(text, ft_best)[0] + 1
    
    if single_w <= CANVAS_W:
        return ft_best, [text]  # single line — no wrapping needed
    
    # Wrap across two lines
    lines = _wrap_text(text, ft_best, CANVAS_W - 60)
    return ft_best, lines


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Split text so each line fits within max_width. Returns 2+ lines."""
    # For English text with spaces, split at spaces
    if " " in text:
        words = text.split(" ")
        lines: list[str] = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            tw = _get_bounds(test, font)[1] - _get_bounds(test, font)[0] + 1
            if tw <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines if lines else [text]
    
    # Chinese/other text — split by character count
    # Find the largest first-line length that fits
    n = len(text)
    best_split = n // 2  # start at midpoint
    best_width = _get_bounds(text[:best_split], font)[1] - _get_bounds(text[:best_split], font)[0] + 1
    
    # Try splits around the midpoint
    for split_at in range(max(1, n // 2 - 5), min(n - 1, n // 2 + 5)):
        if split_at <= 0 or split_at >= n:
            continue
        w = _get_bounds(text[:split_at], font)[1] - _get_bounds(text[:split_at], font)[0] + 1
        if w <= max_width and abs(w - max_width / 2) < abs(best_width - max_width / 2):
            best_split = split_at
            best_width = w
    
    line1 = text[:best_split]
    line2 = text[best_split:]
    return [line1, line2]


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

    # 2. Uniform translucent layer (lighter for breathing space)
    draw.rectangle([0, 0, CANVAS_W, CANVAS_H], fill=(5, 8, 15, 150))

    # 3. Fonts
    ft_title, title_lines = _pick_title_font(title)
    ft_label = ImageFont.truetype(font_path, 14)
    ft_sub = ImageFont.truetype(font_path, 24) if subtitle else None
    ft_tag = ImageFont.truetype(font_path, 13) if tagline else None

    # Multi-line title support
    num_title_lines = len(title_lines)
    line_h = _get_bounds(title_lines[0], ft_title)[2]  # height of one line
    title_gap = max(4, line_h // 5)  # gap between wrapped lines
    th = line_h * num_title_lines + title_gap * (num_title_lines - 1)
    sub_h = _get_bounds(subtitle, ft_sub)[2] if ft_sub else 0
    tag_h = 14 if tagline else 0

    # 4. Adaptive vertical layout
    has_sub = bool(subtitle)
    has_tag = bool(tagline)
    gaps = _vertical_gaps(len(title), has_sub, has_tag)

    label_h = 16
    bar_h = 2 if has_sub or has_tag else 0
    
    total_h = label_h + gaps["lg"] + th
    if has_sub:
        total_h += gaps["ts"] + sub_h
    if bar_h:
        total_h += gaps["sb"] + bar_h
    if has_tag:
        total_h += gaps["bt"] + tag_h

    # Minimum top/bottom padding: 48px
    v_off = max(48, (CANVAS_H - total_h) // 2)

    ly = v_off
    ty = ly + gaps["lg"]
    sy = ty + th + gaps["ts"] if has_sub else 0
    bar_y = (sy + sub_h + gaps["sb"]) if has_sub else (ty + th + gaps["sb"])
    tgy = bar_y + gaps["bt"] if has_tag else 0

    # 5. Draw label
    lx = _center_x(label, ft_label)
    for ox in range(-1, 2):
        for oy in range(-1, 2):
            if ox == 0 and oy == 0:
                continue
            draw.text((lx + ox, ly + oy), label, fill=(0, 0, 0, 160), font=ft_label)
    draw.text((lx, ly), label, fill=(196, 156, 82, 220), font=ft_label)

    # 6. Draw title (outline + white fill) — supports multi-line
    o = outline_width
    for li, line in enumerate(title_lines):
        tl = ty + li * (line_h + title_gap)
        tx = _center_x(line, ft_title)
        for ox in range(-o, o + 1):
            for oy in range(-o, o + 1):
                if ox == 0 and oy == 0:
                    continue
                draw.text((tx + ox, tl + oy), line, fill=(0, 0, 0, 200), font=ft_title)
        draw.text((tx, tl), line, fill=(255, 255, 255, 255), font=ft_title)

    # 7. Draw subtitle (outline + white fill) — only if provided
    if ft_sub and subtitle:
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

    # 9. Draw tagline (outline + warm fill) — only if provided
    if ft_tag and tagline:
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

    # Coverage based on longest line
    longest_line = max(title_lines, key=lambda l: _get_bounds(l, ft_title)[1] - _get_bounds(l, ft_title)[0] + 1)
    tw = _get_bounds(longest_line, ft_title)[1] - _get_bounds(longest_line, ft_title)[0] + 1
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

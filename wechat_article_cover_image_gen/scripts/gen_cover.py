#!/usr/bin/env python3
"""Generate a high-end WeChat Official Account cover image (900×383).

Follows professional editorial design principles:
- Single focal idea
- Strong contrast + minimal text
- Clear hierarchy (BIG → SMALL → MICRO)
- Breathing space = luxury signal
- Left or center alignment
- Template-based style kits

Usage:
  python3 gen_cover.py \
    --title "AI 时代的 OPC" \
    --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
    --tagline "决策者 + AI 工具链 · 可验证需求 · 商业闭环" \
    --output /path/to/cover.png \
    --image-url "https://images.unsplash.com/photo-xxx?w=900&h=383&fit=crop" \
    --template tech --align left
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

# --- Safe zone constants ---
LEFT_SAFE_PX = 72   # ~8% of 900, within 60-100px recommendation
RIGHT_SAFE_PX = 72
MIN_TOP_BOTTOM_PX = 40

# --- Unsplash fallback URLs (all 900×383 cropped) ---
UNSPLASH_FALLBACKS = [
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=900&h=383&fit=crop",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=900&h=383&fit=crop",
]

# --- Template style kits ---
TEMPLATES = {
    "auto": {
        "overlay": (0, 0, 0, 89),        # 35% black
        "label_color": (196, 156, 82, 220),  # gold
        "title_color": (255, 255, 255, 255),
        "subtitle_color": (255, 255, 255, 240),
        "tagline_color": (200, 195, 185, 220),
        "show_gold_bar": True,
        "description": "Auto-detect based on content",
    },
    "tech": {
        "overlay": (0, 0, 0, 102),       # 40% black — deeper for tech
        "label_color": (100, 180, 255, 220),  # cool blue
        "title_color": (255, 255, 255, 255),
        "subtitle_color": (220, 230, 240, 240),
        "tagline_color": (180, 200, 220, 200),
        "show_gold_bar": False,
        "description": "Dark + minimal + high contrast. Tech / AI / Systems",
    },
    "insight": {
        "overlay": (255, 248, 240, 80),  # 31% warm white — editorial feel
        "label_color": (180, 120, 60, 220),  # warm brown
        "title_color": (30, 30, 30, 255),
        "subtitle_color": (80, 70, 60, 240),
        "tagline_color": (120, 110, 100, 220),
        "show_gold_bar": True,
        "description": "Light editorial / magazine style. Insight / Thinking",
    },
    "business": {
        "overlay": (5, 8, 15, 89),       # 35% very dark blue-black
        "label_color": (196, 156, 82, 220),  # gold
        "title_color": (255, 255, 255, 255),
        "subtitle_color": (200, 195, 185, 240),
        "tagline_color": (180, 170, 155, 220),
        "show_gold_bar": True,
        "description": "Black + gold accent + minimal text. Business / Wealth",
    },
}

# ---------------------------------------------------------------------------
# Font resolution
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


def _text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
    l, r, _ = _get_bounds(text, font)
    return r - l + 1


def _center_x(text: str, font: ImageFont.FreeTypeFont) -> int:
    l, r, _ = _get_bounds(text, font)
    return int(round((CANVAS_W - 1 - l - r) / 2))


def _left_x(text: str, font: ImageFont.FreeTypeFont) -> int:
    """Left-aligned x with safe padding. L margin = LEFT_SAFE_PX."""
    l, _, _ = _get_bounds(text, font)
    return LEFT_SAFE_PX - l  # offset so first rendered pixel lands at LEFT_SAFE_PX


# ---------------------------------------------------------------------------
# Pick font size within a constrained range
# ---------------------------------------------------------------------------

def _pick_font_in_range(
    text: str,
    min_size: int,
    max_size: int,
    target_width: int,
    step: int = 2,
) -> tuple[int, ImageFont.FreeTypeFont]:
    """Pick largest font size within [min_size, max_size] that fits target_width.

    If even min_size overflows, returns min_size (will trigger wrapping later).
    """
    font_path = _resolve_font()
    best_size = min_size
    best_font = ImageFont.truetype(font_path, min_size)
    best_dist = abs(_text_width(text, best_font) - target_width)

    for fs in range(min_size, max_size + 1, step):
        ft = ImageFont.truetype(font_path, fs)
        w = _text_width(text, ft)
        if w > CANVAS_W:
            break
        dist = abs(w - target_width)
        if dist < best_dist:
            best_size = fs
            best_font = ft
            best_dist = dist
        elif dist > best_dist and w > target_width:
            break

    return best_size, best_font


# ---------------------------------------------------------------------------
# Title sizing + wrapping (constrained to 28-40px)
# ---------------------------------------------------------------------------

def _title_target_width(text: str, align: str) -> int:
    """Target width for title based on text length and alignment."""
    n = len(text)
    if n <= 4:
        ratio = 0.55
    elif n <= 8:
        ratio = 0.70
    elif n <= 12:
        ratio = 0.78
    elif n <= 18:
        ratio = 0.82
    else:
        ratio = 0.85
    return int(CANVAS_W * ratio)


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Split text so each line fits within max_width. Returns 2+ lines."""
    if " " in text:
        words = text.split(" ")
        lines: list[str] = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if _text_width(test, font) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines if lines else [text]

    # Chinese/other text — find balanced split
    n = len(text)
    best_split = n // 2
    best_width = _text_width(text[:best_split], font)
    for split_at in range(max(1, n // 2 - 5), min(n - 1, n // 2 + 5)):
        w = _text_width(text[:split_at], font)
        if w <= max_width and abs(w - max_width / 2) < abs(best_width - max_width / 2):
            best_split = split_at
            best_width = w

    line1 = text[:best_split]
    line2 = text[best_split:]
    return [line1, line2]


def _prepare_title(
    text: str,
    align: str,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Prepare title: pick font 28-40px with adaptive target, wrap if needed."""
    target = _title_target_width(text, align)
    font_path = _resolve_font()

    best_size, best_font = _pick_font_in_range(text, 28, 40, target, step=2)

    # Check if it fits at chosen size
    if _text_width(text, best_font) <= CANVAS_W - LEFT_SAFE_PX * (1 if align == "left" else 0):
        return best_font, [text]

    # Wrap across two lines at 28px (minimum)
    wrap_font = ImageFont.truetype(font_path, 28)
    lines = _wrap_text(text, wrap_font, CANVAS_W - LEFT_SAFE_PX * 2)
    return wrap_font, lines


# ---------------------------------------------------------------------------
# Image download
# ---------------------------------------------------------------------------

def _download_image(url: str | None) -> Image.Image:
    """Download stock image or use provided URL. Fallback to solid gradient."""
    urls = [url] if url else []
    urls += UNSPLASH_FALLBACKS
    for u in urls:
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            urllib.request.urlretrieve(u, tmp.name)
            img = Image.open(tmp.name).convert("RGBA")
            if img.size != (CANVAS_W, CANVAS_H):
                resize_kw = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS  # type: ignore[attr-defined]
                img = img.resize((CANVAS_W, CANVAS_H), resize_kw)
            return img
        except Exception:
            continue
    # Pure fallback: solid dark gradient
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (20, 30, 50, 255))
    return img


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    outline_color: tuple[int, int, int, int] = (0, 0, 0, 200),
    outline_width: int = 2,
) -> None:
    """Draw text with 8-direction outline + core fill."""
    x, y = xy
    for ox in range(-outline_width, outline_width + 1):
        for oy in range(-outline_width, outline_width + 1):
            if ox == 0 and oy == 0:
                continue
            draw.text((x + ox, y + oy), text, fill=outline_color, font=font)
    draw.text((x, y), text, fill=fill, font=font)


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
    align: str = "center",
    template: str = "auto",
    overlay_opacity: float | None = None,
    outline_width: int = 2,
) -> dict:
    """Generate a high-end WeChat cover (900×383) and write to ``output``.

    Returns metadata dict.
    """
    # Resolve template
    tmpl = TEMPLATES.get(template, TEMPLATES["auto"])

    # Override overlay opacity if explicitly provided
    overlay = tmpl["overlay"]
    if overlay_opacity is not None:
        alpha = max(0, min(255, int(overlay_opacity * 255)))
        overlay = (overlay[0], overlay[1], overlay[2], alpha)

    # --- Layout calculations ---
    font_path = _resolve_font()

    # 1. Font sizes (capped per design rules)
    ft_title, title_lines = _prepare_title(title, align)
    ft_label = ImageFont.truetype(font_path, 13)   # 12-14px
    ft_sub = ImageFont.truetype(font_path, 18) if subtitle else None  # 14-18px
    ft_tag = ImageFont.truetype(font_path, 13) if tagline else None  # 12-14px

    # Title block height (multi-line support)
    num_lines = len(title_lines)
    line_h = _get_bounds(title_lines[0], ft_title)[2]
    title_gap = max(4, line_h // 6)
    title_block_h = line_h * num_lines + title_gap * (num_lines - 1)

    # Subtitle height
    sub_h = _get_bounds(subtitle, ft_sub)[2] if ft_sub else 0
    tag_h = 14 if tagline else 0
    label_h = 16
    bar_h = 2 if (tmpl["show_gold_bar"] and (subtitle or tagline)) else 0

    # 2. Vertical spacing — adaptive
    has_sub = bool(subtitle)
    has_tag = bool(tagline)
    dense = len(title) > 10 and has_sub and has_tag

    gaps = {
        "lg": 18 if dense else 28,     # label → title
        "ts": 12 if dense else 18,     # title → subtitle
        "sb": 10 if dense else 16,     # subtitle → bar
        "bt": 12 if dense else 16,     # bar → tagline
    }

    total_h = label_h + gaps["lg"] + title_block_h
    if has_sub:
        total_h += gaps["ts"] + sub_h
    if bar_h:
        total_h += gaps["sb"] + bar_h
    if has_tag:
        total_h += gaps["bt"] + tag_h

    v_off = max(MIN_TOP_BOTTOM_PX, (CANVAS_H - total_h) // 2)

    ly = v_off
    ty = ly + gaps["lg"]
    sy = ty + title_block_h + gaps["ts"] if has_sub else 0
    bar_y = (sy + sub_h + gaps["sb"]) if has_sub else (ty + title_block_h + gaps["sb"]) if bar_h else 0
    tgy = bar_y + gaps["bt"] + (bar_h if bar_h else 0) if has_tag else 0
    # If no subtitle/bar but has tagline, compute tagline y
    if not has_sub and not bar_h and has_tag:
        tgy = ty + title_block_h + gaps["bt"]

    # 3. Horizontal positioning
    is_left = align == "left"

    if is_left:
        label_x = LEFT_SAFE_PX
    else:
        label_x = _center_x(label, ft_label)

    # Title lines: each independently positioned
    title_positions = []
    for li, line in enumerate(title_lines):
        tl = ty + li * (line_h + title_gap)
        if is_left:
            tx = LEFT_SAFE_PX
        else:
            tx = _center_x(line, ft_title)
        title_positions.append((tx, tl))

    # Subtitle
    if ft_sub and subtitle:
        if is_left:
            sub_x = LEFT_SAFE_PX
        else:
            sub_x = _center_x(subtitle, ft_sub)
    else:
        sub_x = 0

    # Tagline
    if ft_tag and tagline:
        if is_left:
            tag_x = LEFT_SAFE_PX
        else:
            tag_x = _center_x(tagline, ft_tag)
    else:
        tag_x = 0

    # --- Render ---
    bg = _download_image(image_url)
    overlay_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay_layer)

    # Uniform translucent overlay
    draw.rectangle([0, 0, CANVAS_W, CANVAS_H], fill=overlay)

    # Label (top)
    _draw_text_with_outline(
        draw, label, (label_x, ly), ft_label,
        fill=tmpl["label_color"],
        outline_color=(0, 0, 0, 120),
        outline_width=1,
    )

    # Title (multi-line)
    for tx, tl in title_positions:
        _draw_text_with_outline(
            draw, title_lines[title_positions.index((tx, tl))],
            (tx, tl), ft_title,
            fill=tmpl["title_color"],
            outline_width=outline_width,
        )

    # Subtitle
    if ft_sub and subtitle:
        _draw_text_with_outline(
            draw, subtitle, (sub_x, sy), ft_sub,
            fill=tmpl["subtitle_color"],
            outline_color=(0, 0, 0, 160),
            outline_width=1,
        )

    # Gold accent bar (only when template says so)
    if bar_h:
        bar_len = 260
        if is_left:
            bar_x1 = LEFT_SAFE_PX
        else:
            bar_x1 = (CANVAS_W - bar_len) // 2
        for xp in range(bar_x1, bar_x1 + bar_len):
            dist = abs(xp - (bar_x1 + bar_len // 2))
            a = max(0, 220 - int(dist * 2.2))
            overlay_layer.putpixel((xp, bar_y), (196, 156, 82, a))

    # Tagline (bottom)
    if ft_tag and tagline:
        _draw_text_with_outline(
            draw, tagline, (tag_x, tgy), ft_tag,
            fill=tmpl["tagline_color"],
            outline_color=(0, 0, 0, 140),
            outline_width=1,
        )

    # Composite & save
    result = Image.alpha_composite(bg, overlay_layer).convert("RGB")
    result.save(output, "PNG")

    # --- Verification report ---
    longest_line = max(
        title_lines,
        key=lambda l: _text_width(l, ft_title),
    )
    tw = _text_width(longest_line, ft_title)
    safe_left_ok = True
    safe_right_ok = True

    # Check safe zone compliance
    if is_left:
        safe_left_ok = label_x >= 60  # label is leftmost element
        # Rightmost element: check longest title line
        last_line = title_lines[-1]
        l, r, _ = _get_bounds(last_line, ft_title)
        right_edge = title_positions[-1][0] + r
        safe_right_ok = (CANVAS_W - right_edge - 1) >= 60
    else:
        l, r, _ = _get_bounds(longest_line, ft_title)
        tx = _center_x(longest_line, ft_title)
        safe_left_ok = (tx + l) >= 60
        safe_right_ok = (CANVAS_W - (tx + r) - 1) >= 60

    return {
        "output": str(Path(output).resolve()),
        "canvas": f"{CANVAS_W}x{CANVAS_H}",
        "template": template,
        "align": align,
        "title_font_size": ft_title.size,
        "title_lines": num_lines,
        "title_coverage_pct": round(100 * tw / CANVAS_W),
        "vertical_offset": v_off,
        "safe_zone_left_ok": safe_left_ok,
        "safe_zone_right_ok": safe_right_ok,
        "status": "ok",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a high-end WeChat Official Account cover image.",
    )
    parser.add_argument("--title", required=True, help="Main title (keep ≤ 20 chars for best results)")
    parser.add_argument("--subtitle", default="", help="Subtitle (14-18px)")
    parser.add_argument("--tagline", default="", help="Bottom tagline (12-14px)")
    parser.add_argument(
        "--label", default="FEATURED ARTICLE",
        help="Top label (default: FEATURED ARTICLE)",
    )
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument(
        "--image-url", default=None,
        help="Stock image URL (900×383 preferred). Auto-fallback if omitted.",
    )
    parser.add_argument(
        "--align", default="center", choices=["center", "left"],
        help="Text alignment: center (modern tech) or left (premium editorial)",
    )
    parser.add_argument(
        "--template", default="auto", choices=list(TEMPLATES.keys()),
        help="Visual style template",
    )
    parser.add_argument(
        "--overlay-opacity", type=float, default=None,
        help="Overlay opacity 0.0-1.0. Overrides template default if set.",
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
            align=args.align,
            template=args.template,
            overlay_opacity=args.overlay_opacity,
            outline_width=args.outline_width,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Cover generated: {result['output']}")
    print(f"  Canvas: {result['canvas']}")
    print(f"  Template: {result['template']}  Align: {result['align']}")
    print(f"  Title: {args.title}")
    print(f"  Title font: {result['title_font_size']}px  Lines: {result['title_lines']}")
    print(f"  Title width coverage: {result['title_coverage_pct']}%")
    print(f"  Vertical offset: {result['vertical_offset']}px")
    print(f"  Safe zone L: {'✓' if result['safe_zone_left_ok'] else '✗'}  R: {'✓' if result['safe_zone_right_ok'] else '✗'}")

    # TDD-style test checklist
    checks = []
    checks.append(("✔" if result["safe_zone_left_ok"] and result["safe_zone_right_ok"] else "✗", "Safe zones ≥ 60px on both sides"))
    checks.append(("✔" if result["title_font_size"] <= 40 else "✗", "Title font ≤ 40px"))
    checks.append(("✔" if result["title_font_size"] >= 28 else "✗", "Title font ≥ 28px"))
    checks.append(("✔" if result["title_coverage_pct"] >= 40 else "✗", "Title readable (coverage ≥ 40%)"))
    checks.append(("✔" if result["title_lines"] <= 2 else "✗", "Title ≤ 2 lines"))

    print()
    print("  TDD Checklist:")
    for mark, check in checks:
        print(f"    {mark}  {check}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Generate a WeChat article cover image with text overlay.

Downloads a stock photo (or uses a local file), adds a uniform translucent
overlay, and draws centered title/subtitle/tagline text with heavy shadow
and outline for readability. Designed for WeChat's 900×383 cover format.

Usage:
  python3 scripts/draw_cover.py \\
    --image /tmp/cover_source.jpg \\
    --title "AI 时代的 OPC" \\
    --subtitle "一个人如何用最小成本跑通自己的商业闭环" \\
    --tagline "决策者 + AI 工具链 · 可验证需求 · 商业闭环系统" \\
    --output /path/to/cover.png

Requirements:
  pip install Pillow numpy

Font note:
  On macOS the script auto-detects STHeiti Medium or falls back to a
  system Chinese font.  On Linux, install a CJK font (e.g. Noto Sans CJK)
  and set --font-path or update FONT_PATHS at the top of the script.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Default font paths (macOS) — add Linux/Windows paths here
# ---------------------------------------------------------------------------
FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",   # Linux alt
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_font(size: int) -> ImageFont.FreeTypeFont:
    """Return a Chinese-capable font at the given size."""
    for fp in FONT_PATHS:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except (OSError, IOError):
                continue
    raise RuntimeError(
        f"No CJK font found. Tried: {FONT_PATHS}\n"
        f"Install Noto Sans CJK on Linux or check the path on macOS."
    )


def get_rendered_bounds(text: str, font: ImageFont.FreeTypeFont,
                        canvas_w: int = 1900) -> tuple[int, int, int]:
    """Render text to a mask and return (left, right, height) relative to draw origin.

    Uses a generous off-screen mask so glyph bearings are fully captured.
    """
    offset = 500
    m = Image.new("L", (canvas_w + offset * 2, 200), 0)
    ImageDraw.Draw(m).text((offset, 5), text, fill=255, font=font)
    arr = np.array(m)
    cols = arr.any(axis=0).nonzero()[0]
    if len(cols) == 0:
        return 0, 0, 0
    rows = arr.any(axis=1).nonzero()[0]
    return (
        int(cols[0]) - offset,
        int(cols[-1]) - offset,
        int(rows[-1]) - int(rows[0]) + 1,
    )


def centered_x(text: str, font: ImageFont.FreeTypeFont,
               canvas_w: int = 900) -> int:
    """Return the draw-x that makes L_margin == R_margin after rendering.

    Uses mask-based pixel bounds rather than ``getbbox()``, which can
    overestimate width by 4-9px for large Chinese text.
    """
    l, r, _ = get_rendered_bounds(text, font, canvas_w)
    return int(round((canvas_w - 1 - l - r) / 2))


def pick_font_size(text: str, target_width: int,
                   min_size: int = 80, max_size: int = 200,
                   step: int = 5) -> tuple[int, ImageFont.FreeTypeFont]:
    """Pick the largest font size where the rendered text fits ``target_width``."""
    best = min_size
    for fs in range(min_size, max_size + 1, step):
        font = resolve_font(fs)
        l, r, _ = get_rendered_bounds(text, font, target_width + 200)
        if (r - l + 1) >= target_width:
            return fs, font
        best = fs
    return best, resolve_font(best)


def draw_shadow_and_outline(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    *,
    shadow_range: tuple[int, int] = (6, 11),
    shadow_alpha: int = 100,
    outline_width: int = 2,
    outline_alpha: int = 200,
    fill: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> None:
    """Draw text with heavy shadow (multi-offset) + outline (8-direction) + core.

    Shadow layers use a stepped alpha from the outer edge inward for a
    natural fade.
    """
    x, y = xy

    # --- Heavy shadow (outer ring) ---
    lo, hi = shadow_range
    for ox in range(lo, hi + 1):
        for oy in range(lo, hi + 1):
            # Fade: farthest pixels are darkest, nearest are lighter
            dist = max(abs(ox - lo), abs(oy - lo))
            alpha = max(40, shadow_alpha - dist * 12)
            draw.text((x + ox, y + oy), text, fill=(0, 0, 0, alpha), font=font)

    # --- Outline (8-direction stroke) ---
    for ox in range(-outline_width, outline_width + 1):
        for oy in range(-outline_width, outline_width + 1):
            if ox == 0 and oy == 0:
                continue
            draw.text(
                (x + ox, y + oy), text,
                fill=(0, 0, 0, outline_alpha), font=font,
            )

    # --- Core text ---
    draw.text((x, y), text, fill=fill, font=font)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_cover(
    image_path: str,
    title: str,
    subtitle: str,
    tagline: str,
    output_path: str,
    *,
    label: str = "AI ERA  ·  ONE PERSON COMPANY",
    overlay_color: tuple[int, int, int, int] = (5, 8, 15, 165),
    title_min_size: int = 100,
    title_target_pct: float = 0.92,
    shadow: tuple[int, int] = (6, 11),
) -> dict[str, Any]:
    """Generate a WeChat cover image (900×383) with full text overlay.

    Returns a result dict with centering verification and output path.
    """
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size  # Should be 900 x 383

    # --- Uniform translucent overlay covering the entire image ---
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([0, 0, w, h], fill=overlay_color)

    # --- Fonts ---
    title_target = int(w * title_target_pct)
    title_size, ft_title = pick_font_size(title, title_target, title_min_size)
    ft_sub = resolve_font(26)
    ft_label = resolve_font(14)
    ft_tag = resolve_font(13)

    # --- Measure ---
    _, _, th = get_rendered_bounds(title, ft_title, w)
    _, _, sub_h = get_rendered_bounds(subtitle, ft_sub, w)

    # --- Vertical centering of the entire text block ---
    total_block = 16 + 28 + th + 16 + sub_h + 14 + 2 + 14 + 18
    v_offset = (h - total_block) // 2
    ly = v_offset                     # label y
    ty = ly + 28                      # title y
    sy = ty + th + 16                 # subtitle y
    bar_y = sy + sub_h + 14           # gold bar y
    tgy = bar_y + 18                  # tagline y

    # --- Draw label (gold, centered, subtle outline) ---
    lx = centered_x(label, ft_label, w)
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            if ox == 0 and oy == 0:
                continue
            draw.text((lx + ox, ly + oy), label, fill=(0, 0, 0, 160), font=ft_label)
    draw.text((lx, ly), label, fill=(196, 156, 82, 220), font=ft_label)

    # --- Title (heavy shadow + outline) ---
    tx = centered_x(title, ft_title, w)
    draw_shadow_and_outline(
        draw, title, (tx, ty), ft_title,
        shadow_range=shadow,
        shadow_alpha=130,
        outline_width=2,
        outline_alpha=200,
        fill=(255, 255, 255, 255),
    )

    # --- Subtitle (lighter shadow + outline) ---
    sx = centered_x(subtitle, ft_sub, w)
    draw_shadow_and_outline(
        draw, subtitle, (sx, sy), ft_sub,
        shadow_range=(3, 5),
        shadow_alpha=100,
        outline_width=1,
        outline_alpha=180,
        fill=(255, 255, 255, 240),
    )

    # --- Gold accent bar ---
    bar_len = 260
    bar_x1 = (w - bar_len) // 2
    for xp in range(bar_x1, bar_x1 + bar_len):
        dist = abs(xp - (bar_x1 + bar_len // 2))
        a = max(0, 220 - int(dist * 2.2))
        overlay.putpixel((xp, bar_y), (196, 156, 82, a))

    # --- Tagline ---
    tx4 = centered_x(tagline, ft_tag, w)
    draw_shadow_and_outline(
        draw, tagline, (tx4, tgy), ft_tag,
        shadow_range=(2, 3),
        shadow_alpha=80,
        outline_width=1,
        outline_alpha=160,
        fill=(200, 195, 185, 220),
    )

    # --- Composite & save ---
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "PNG")

    # --- Verification ---
    def verify(text, font, name, dx):
        l, r, _ = get_rendered_bounds(text, font, w)
        lm = dx + l
        rm = w - (dx + r) - 1
        return {"name": name, "L": lm, "R": rm, "diff": abs(lm - rm)}

    results = {
        "status": "ok",
        "output": str(Path(output_path).resolve()),
        "size": f"{w}x{h}",
        "title_font": f"{title_size}px",
        "title_coverage": f"{get_rendered_bounds(title, ft_title, w)[1] - get_rendered_bounds(title, ft_title, w)[0] + 1}/{w}px",
        "vertical": {"top": v_offset, "bottom": h - total_block - v_offset},
        "centering": [
            verify(label, ft_label, "label", lx),
            verify(title, ft_title, "title", tx),
            verify(subtitle, ft_sub, "subtitle", sx),
            verify(tagline, ft_tag, "tagline", tx4),
        ],
    }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate WeChat article cover image with text overlay.",
    )
    parser.add_argument("--image", required=True, help="Source image path or URL")
    parser.add_argument("--title", required=True, help="Main title text")
    parser.add_argument("--subtitle", default="", help="Subtitle text")
    parser.add_argument("--tagline", default="", help="Tagline / bottom text")
    parser.add_argument("--label", default="AI ERA  ·  ONE PERSON COMPANY",
                        help="Top label (default: AI ERA ...)")
    parser.add_argument("-o", "--output", required=True,
                        help="Output PNG path")
    parser.add_argument("--title-size", type=int, default=100,
                        help="Minimum title font size (default: 100)")
    parser.add_argument("--title-coverage", type=float, default=0.92,
                        help="Title width as fraction of canvas (default: 0.92)")
    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f"ERROR: Image not found: {args.image}", file=sys.stderr)
        return 1

    try:
        result = generate_cover(
            image_path=args.image,
            title=args.title,
            subtitle=args.subtitle,
            tagline=args.tagline,
            output_path=args.output,
            label=args.label,
            title_min_size=args.title_size,
            title_target_pct=args.title_coverage,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Print results
    print(f"Cover: {result['output']}")
    print(f"Title font: {result['title_font']}  coverage: {result['title_coverage']}")
    v = result["vertical"]
    print(f"Vertical: top={v['top']}px  bottom={v['bottom']}px")
    for c in result["centering"]:
        status = "✓" if c["diff"] <= 1 else f"off={c['diff']}px"
        print(f"  {c['name']:10s}: L={c['L']:3d} R={c['R']:3d}  {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

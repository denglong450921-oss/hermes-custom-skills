#!/usr/bin/env python3
"""Generate a sharp WeChat Official Account cover PNG (900x383)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat
except ModuleNotFoundError:
    bundled_python = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    )
    if bundled_python.exists() and Path(sys.executable).resolve() != bundled_python.resolve():
        os.execv(str(bundled_python), [str(bundled_python), __file__, *sys.argv[1:]])
    pip = shutil.which("pip3") or "python3 -m pip"
    raise SystemExit(
        "ERROR: Pillow is required to render PNG covers. "
        f"Install it with `{pip} install pillow`, or run this inside the Codex bundled Python runtime."
    )


CANVAS_W = 900
CANVAS_H = 383
SAFE_X = 72
MIN_Y = 40
DEFAULT_SCALE = 4

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

STOCK_FALLBACKS = [
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1600&h=681&fit=crop",
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1600&h=681&fit=crop",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&h=681&fit=crop",
]

TEMPLATES = {
    "auto": {
        "mode": "dark",
        "bg": ("#172033", "#6b3f16", "#111827"),
        "accent": "#d8aa55",
        "label": "#f4c76b",
        "title": "#ffffff",
        "subtitle": "#f5f1e8",
        "tagline": "#d7cfc0",
        "panel": (0, 0, 0, 34),
        "overlay_left": (8, 12, 22, 190),
        "overlay_right": (8, 12, 22, 72),
    },
    "tech": {
        "mode": "dark",
        "bg": ("#0f172a", "#1e3a8a", "#0891b2"),
        "accent": "#64b5ff",
        "label": "#93c5fd",
        "title": "#ffffff",
        "subtitle": "#e2ecf7",
        "tagline": "#b9d4ee",
        "panel": (3, 7, 18, 38),
        "overlay_left": (2, 6, 23, 205),
        "overlay_right": (2, 6, 23, 82),
    },
    "insight": {
        "mode": "light",
        "bg": ("#f8efe0", "#d7b98a", "#6b4e31"),
        "accent": "#9a6b3f",
        "label": "#8b5e34",
        "title": "#1f2933",
        "subtitle": "#463a30",
        "tagline": "#76685a",
        "panel": (255, 250, 242, 118),
        "overlay_left": (255, 250, 242, 218),
        "overlay_right": (255, 250, 242, 118),
    },
    "business": {
        "mode": "dark",
        "bg": ("#111827", "#78350f", "#1f2937"),
        "accent": "#f2bd54",
        "label": "#f6c85f",
        "title": "#ffffff",
        "subtitle": "#eee3d2",
        "tagline": "#d8c7ae",
        "panel": (0, 0, 0, 42),
        "overlay_left": (6, 9, 18, 218),
        "overlay_right": (61, 28, 6, 92),
    },
}


def _hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.strip().lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha


def _scale_color(color: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return color


def _resolve_font() -> str:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise RuntimeError("No CJK-capable font found. Install STHeiti, PingFang, or Songti.")


def _font(size: int, scale: int = 1) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_resolve_font(), size * scale)


def _bbox(text: str, font: ImageFont.FreeTypeFont, stroke_width: int = 0) -> tuple[int, int, int, int]:
    return font.getbbox(text, stroke_width=stroke_width)


def _text_size(text: str, font: ImageFont.FreeTypeFont, stroke_width: int = 0) -> tuple[int, int]:
    left, top, right, bottom = _bbox(text, font, stroke_width)
    return right - left, bottom - top


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _wrap_words(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if current and _text_size(trial, font)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [text]


def _wrap_cjk(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        if current and _text_size(trial, font)[0] > max_width:
            lines.append(current)
            current = ch
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [text]


def _truncate_to_width(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    ellipsis = "..."
    if _contains_cjk(text):
        ellipsis = "…"
    if _text_size(text, font)[0] <= max_width:
        return text
    current = text
    while current and _text_size(current + ellipsis, font)[0] > max_width:
        current = current[:-1]
    return (current + ellipsis) if current else ellipsis


def _wrap_title(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines = _wrap_words(text, font, max_width) if " " in text.strip() and not _contains_cjk(text) else _wrap_cjk(text, font, max_width)
    if len(lines) <= 2:
        return lines
    return [lines[0], _truncate_to_width("".join(lines[1:]) if _contains_cjk(text) else " ".join(lines[1:]), font, max_width)]


def _fit_title(text: str, align: str, scale: int) -> tuple[int, ImageFont.FreeTypeFont, list[str], int]:
    max_width = CANVAS_W - SAFE_X * 2
    if align == "left":
        max_width = CANVAS_W - SAFE_X - 84
    max_size = 72 if len(text) <= 14 else 64
    min_size = 38
    for size in range(max_size, min_size - 1, -2):
        font = _font(size, 1)
        lines = _wrap_title(text, font, max_width)
        line_widths = [_text_size(line, font, stroke_width=2)[0] for line in lines]
        line_height = max(_text_size(line, font, stroke_width=2)[1] for line in lines)
        block_h = line_height * len(lines) + max(8, size // 6) * (len(lines) - 1)
        if len(lines) <= 2 and max(line_widths) <= max_width and block_h <= 150:
            return size, _font(size, scale), lines, max_width
    font = _font(min_size, scale)
    final_font = _font(min_size, 1)
    lines = _wrap_title(text, final_font, max_width)
    return min_size, font, lines[:2], max_width


def _center_crop(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    target_w, target_h = size
    target_ratio = target_w / target_h
    w, h = img.size
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img.resize(size, Image.Resampling.LANCZOS)


def _gradient_background(template: str, scale: int, seed_text: str) -> Image.Image:
    style = TEMPLATES.get(template, TEMPLATES["auto"])
    colors = [_hex_to_rgba(item)[:3] for item in style["bg"]]
    w, h = CANVAS_W * scale, CANVAS_H * scale
    img = Image.new("RGB", (w, h), colors[0])
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / max(1, w - 1)) * 0.72 + (y / max(1, h - 1)) * 0.28
            if t < 0.55:
                local = t / 0.55
                c1, c2 = colors[0], colors[1]
            else:
                local = (t - 0.55) / 0.45
                c1, c2 = colors[1], colors[2]
            px[x, y] = tuple(int(c1[i] * (1 - local) + c2[i] * local) for i in range(3))

    draw = ImageDraw.Draw(img, "RGBA")
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    accent = _hex_to_rgba(style["accent"], 32)
    for i in range(9):
        cx = int(digest[i] / 255 * w)
        cy = int(digest[i + 9] / 255 * h)
        radius = (110 + digest[i + 18] % 150) * scale
        alpha = 18 + digest[i] % 34
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(accent[0], accent[1], accent[2], alpha),
        )
    return img.convert("RGBA")


def _download_to_image(url: str) -> Image.Image:
    tmp_name = ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tmp:
            tmp_name = tmp.name
        urllib.request.urlretrieve(url, tmp_name)
        return Image.open(tmp_name)
    finally:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass


def _load_background(
    *,
    image_path: str | None,
    image_url: str | None,
    template: str,
    scale: int,
    seed_text: str,
    no_image: bool,
    stock_fallbacks: bool,
) -> tuple[Image.Image, str]:
    size = (CANVAS_W * scale, CANVAS_H * scale)
    if not no_image and image_path:
        try:
            return _center_crop(Image.open(image_path), size).convert("RGBA"), f"local:{image_path}"
        except Exception:
            pass
    if not no_image and image_url:
        try:
            return _center_crop(_download_to_image(image_url), size).convert("RGBA"), image_url
        except Exception:
            pass
    if not no_image and stock_fallbacks:
        for url in STOCK_FALLBACKS:
            try:
                return _center_crop(_download_to_image(url), size).convert("RGBA"), url
            except Exception:
                continue
    return _gradient_background(template, scale, seed_text), "deterministic_gradient"


def _scaled_box(box: tuple[int, int, int, int], scale: int) -> tuple[int, int, int, int]:
    return tuple(int(v * scale) for v in box)


def _draw_gradient_overlay(layer: Image.Image, style: dict, align: str, scale: int) -> None:
    w, h = layer.size
    left = style["overlay_left"]
    right = style["overlay_right"]
    px = layer.load()
    for x in range(w):
        t = x / max(1, w - 1)
        if align == "center":
            t = abs(t - 0.5) * 1.35
        for y in range(h):
            yy = y / max(1, h - 1)
            vignette = 0.82 + 0.18 * math.cos((yy - 0.5) * math.pi)
            color = tuple(int(left[i] * (1 - t) + right[i] * t) for i in range(4))
            px[x, y] = (color[0], color[1], color[2], int(color[3] * vignette))


def _draw_text(
    layer: Image.Image,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: str,
    *,
    scale: int,
    stroke_fill: tuple[int, int, int, int],
    stroke_width: int,
    shadow: bool = True,
) -> tuple[int, int, int, int]:
    x, y = xy
    sx, sy = x * scale, y * scale
    sw = max(1, stroke_width * scale)
    fill_rgba = _hex_to_rgba(fill) if isinstance(fill, str) else fill
    draw = ImageDraw.Draw(layer)
    bbox = draw.textbbox((sx, sy), text, font=font, stroke_width=sw)
    if shadow:
        shadow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.text(
            (sx + 2 * scale, sy + 3 * scale),
            text,
            font=font,
            fill=(0, 0, 0, 160),
            stroke_width=sw,
            stroke_fill=(0, 0, 0, 135),
        )
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(max(1, int(1.05 * scale))))
        layer.alpha_composite(shadow_layer)
    draw.text(
        (sx, sy),
        text,
        font=font,
        fill=fill_rgba,
        stroke_width=sw,
        stroke_fill=stroke_fill,
    )
    return tuple(int(v / scale) for v in bbox)


def _line_height(font: ImageFont.FreeTypeFont, scale: int) -> int:
    left, top, right, bottom = font.getbbox("国Ag", stroke_width=2 * scale)
    return int((bottom - top) / scale)


def _text_width_final(text: str, font: ImageFont.FreeTypeFont, scale: int, stroke: int = 0) -> int:
    left, top, right, bottom = font.getbbox(text, stroke_width=stroke * scale)
    return int((right - left) / scale)


def _contrast_stroke(style: dict, template: str) -> tuple[int, int, int, int]:
    if style["mode"] == "light":
        return (255, 255, 255, 218)
    return (0, 0, 0, 218)


def _sharpness_score(img: Image.Image, boxes: list[tuple[int, int, int, int]]) -> float:
    if not boxes:
        return 0.0
    scores = []
    for box in boxes:
        left, top, right, bottom = box
        left = max(0, left - 8)
        top = max(0, top - 8)
        right = min(CANVAS_W, right + 8)
        bottom = min(CANVAS_H, bottom + 8)
        if right <= left or bottom <= top:
            continue
        crop = img.crop((left, top, right, bottom)).convert("L")
        edges = crop.filter(ImageFilter.FIND_EDGES)
        scores.append(ImageStat.Stat(edges).mean[0])
    return round(sum(scores) / len(scores), 2) if scores else 0.0


def render(
    *,
    title: str,
    subtitle: str,
    tagline: str,
    label: str,
    output: str,
    image_url: str | None = None,
    image_path: str | None = None,
    align: str = "center",
    template: str = "auto",
    overlay_opacity: float | None = None,
    outline_width: int = 2,
    no_image: bool = False,
    stock_fallbacks: bool = False,
    render_scale: int = DEFAULT_SCALE,
    report: str | None = None,
) -> dict:
    scale = max(2, min(5, int(render_scale)))
    style = TEMPLATES.get(template, TEMPLATES["auto"])
    title = " ".join(title.split()).strip()
    subtitle = " ".join(subtitle.split()).strip()
    tagline = " ".join(tagline.split()).strip()
    label = " ".join(label.split()).strip() or "FEATURED ARTICLE"

    background, image_source = _load_background(
        image_path=image_path,
        image_url=image_url,
        template=template,
        scale=scale,
        seed_text=f"{title}|{subtitle}|{tagline}|{template}",
        no_image=no_image,
        stock_fallbacks=stock_fallbacks,
    )
    overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
    _draw_gradient_overlay(overlay, style, align, scale)
    draw = ImageDraw.Draw(overlay, "RGBA")

    title_size, title_font, title_lines, max_text_width = _fit_title(title, align, scale)
    label_font = _font(16, scale)
    sub_font = _font(24 if len(subtitle) <= 24 else 21, scale) if subtitle else None
    tag_font = _font(16, scale) if tagline else None

    title_line_h = _line_height(title_font, scale)
    title_gap = max(8, title_size // 7)
    title_block_h = title_line_h * len(title_lines) + title_gap * (len(title_lines) - 1)
    label_h = _line_height(label_font, scale)
    sub_h = _line_height(sub_font, scale) if sub_font else 0
    tag_h = _line_height(tag_font, scale) if tag_font else 0
    accent_h = 4
    dense = bool(subtitle and tagline and len(title) > 16)
    gap_label_title = 18 if dense else 24
    gap_title_sub = 12 if dense else 18
    gap_sub_accent = 12 if dense else 16
    gap_accent_tag = 12 if dense else 14
    total_h = label_h + gap_label_title + title_block_h
    if subtitle:
        total_h += gap_title_sub + sub_h
    if subtitle or tagline:
        total_h += gap_sub_accent + accent_h
    if tagline:
        total_h += gap_accent_tag + tag_h
    top = max(MIN_Y, (CANVAS_H - total_h) // 2)

    left_aligned = align == "left"
    title_widths = [_text_width_final(line, title_font, scale, outline_width) for line in title_lines]
    content_w = max([_text_width_final(label, label_font, scale, 1), *title_widths])
    if subtitle and sub_font:
        content_w = max(content_w, min(max_text_width, _text_width_final(subtitle, sub_font, scale, 1)))
    if tagline and tag_font:
        content_w = max(content_w, min(max_text_width, _text_width_final(tagline, tag_font, scale, 1)))

    if left_aligned:
        origin_x = SAFE_X
    else:
        origin_x = (CANVAS_W - content_w) // 2

    panel_pad_x = 24
    panel_pad_y = 18
    panel_box = (
        max(24, origin_x - panel_pad_x),
        max(20, top - panel_pad_y),
        min(CANVAS_W - 24, origin_x + content_w + panel_pad_x),
        min(CANVAS_H - 20, top + total_h + panel_pad_y),
    )
    draw.rounded_rectangle(
        _scaled_box(panel_box, scale),
        radius=18 * scale,
        fill=style["panel"],
    )

    y = top
    stroke = _contrast_stroke(style, template)
    text_boxes: list[tuple[int, int, int, int]] = []
    label_w = _text_width_final(label, label_font, scale, 1)
    label_x = origin_x if left_aligned else origin_x + (content_w - label_w) // 2
    text_boxes.append(
        _draw_text(
            overlay,
            label,
            (label_x, y),
            label_font,
            style["label"],
            scale=scale,
            stroke_fill=stroke,
            stroke_width=1,
            shadow=style["mode"] == "dark",
        )
    )
    y += label_h + gap_label_title

    title_boxes = []
    for line in title_lines:
        line_w = _text_width_final(line, title_font, scale, outline_width)
        x = origin_x if left_aligned else origin_x + (content_w - line_w) // 2
        box = _draw_text(
            overlay,
            line,
            (x, y),
            title_font,
            style["title"],
            scale=scale,
            stroke_fill=stroke,
            stroke_width=outline_width,
            shadow=True,
        )
        title_boxes.append(box)
        text_boxes.append(box)
        y += title_line_h + title_gap
    y -= title_gap

    if subtitle and sub_font:
        y += gap_title_sub
        sub_line = _truncate_to_width(subtitle, _font(sub_font.size // scale, 1), max_text_width)
        sub_w = _text_width_final(sub_line, sub_font, scale, 1)
        x = origin_x if left_aligned else origin_x + (content_w - sub_w) // 2
        text_boxes.append(
            _draw_text(
                overlay,
                sub_line,
                (x, y),
                sub_font,
                style["subtitle"],
                scale=scale,
                stroke_fill=stroke,
                stroke_width=1,
                shadow=style["mode"] == "dark",
            )
        )
        y += sub_h

    if subtitle or tagline:
        y += gap_sub_accent
        accent_len = min(320, max(160, int(content_w * 0.48)))
        accent_x = origin_x if left_aligned else origin_x + (content_w - accent_len) // 2
        accent = _hex_to_rgba(style["accent"], 230)
        draw.rounded_rectangle(
            _scaled_box((accent_x, y, accent_x + accent_len, y + accent_h), scale),
            radius=2 * scale,
            fill=accent,
        )
        y += accent_h

    if tagline and tag_font:
        y += gap_accent_tag
        tag_line = _truncate_to_width(tagline, _font(tag_font.size // scale, 1), max_text_width)
        tag_w = _text_width_final(tag_line, tag_font, scale, 1)
        x = origin_x if left_aligned else origin_x + (content_w - tag_w) // 2
        text_boxes.append(
            _draw_text(
                overlay,
                tag_line,
                (x, y),
                tag_font,
                style["tagline"],
                scale=scale,
                stroke_fill=stroke,
                stroke_width=1,
                shadow=style["mode"] == "dark",
            )
        )

    composed = Image.alpha_composite(background, overlay).convert("RGB")
    final = composed.resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)
    final = final.filter(ImageFilter.UnsharpMask(radius=0.65, percent=155, threshold=2))
    output_path = Path(output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, format="PNG", optimize=True)

    left_edge = min(box[0] for box in text_boxes)
    right_edge = max(box[2] for box in text_boxes)
    safe_left_ok = left_edge >= 60
    safe_right_ok = (CANVAS_W - right_edge) >= 60
    title_coverage = round(100 * max(title_widths) / CANVAS_W)
    sharpness = _sharpness_score(final, title_boxes)
    status = "passed" if safe_left_ok and safe_right_ok and len(title_lines) <= 2 and sharpness >= 7.0 else "blocked"
    result = {
        "skill_name": "wechat-article-cover-image-gen",
        "status": status,
        "output": str(output_path.resolve()),
        "format": "PNG",
        "canvas": [CANVAS_W, CANVAS_H],
        "template": template,
        "align": align,
        "image_source": image_source,
        "title": title,
        "title_font_size": title_size,
        "title_lines": title_lines,
        "title_line_count": len(title_lines),
        "title_coverage_pct": title_coverage,
        "render_scale": scale,
        "downsample_filter": "LANCZOS",
        "unsharp_mask": {"radius": 0.65, "percent": 155, "threshold": 2},
        "text_sharpness_score": sharpness,
        "safe_zone_left_ok": safe_left_ok,
        "safe_zone_right_ok": safe_right_ok,
        "text_bounds": [left_edge, min(box[1] for box in text_boxes), right_edge, max(box[3] for box in text_boxes)],
        "manual_review": [],
    }
    if report:
        report_path = Path(report).expanduser()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["report"] = str(report_path.resolve())
    return result


def print_summary(result: dict) -> None:
    print(f"Cover generated: {result['output']}")
    print(f"  Format: {result['format']}")
    print(f"  Canvas: {result['canvas'][0]}x{result['canvas'][1]}")
    print(f"  Template: {result['template']}  Align: {result['align']}")
    print(f"  Title: {result['title']}")
    print(f"  Title font: {result['title_font_size']}px  Lines: {result['title_line_count']}")
    print(f"  Title width coverage: {result['title_coverage_pct']}%")
    print(f"  Render scale: {result['render_scale']}x")
    print(f"  Text sharpness score: {result['text_sharpness_score']}")
    print(f"  Safe zone L: {'✓' if result['safe_zone_left_ok'] else '✗'}  R: {'✓' if result['safe_zone_right_ok'] else '✗'}")
    if result.get("report"):
        print(f"  Report: {result['report']}")
    checks = [
        (result["format"] == "PNG", "PNG output format"),
        (result["canvas"] == [CANVAS_W, CANVAS_H], "Canvas is exactly 900x383"),
        (result["render_scale"] >= 3, "High-resolution text render scale >= 3x"),
        (result["text_sharpness_score"] >= 7.0, "Text sharpness score >= 7.0"),
        (result["safe_zone_left_ok"] and result["safe_zone_right_ok"], "Safe zones >= 60px"),
        (result["title_font_size"] >= 38, "Title font >= 38px"),
        (result["title_line_count"] <= 2, "Title <= 2 lines"),
    ]
    print()
    print("  TDD Checklist:")
    for passed, text in checks:
        print(f"    {'✔' if passed else '✗'}  {text}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a sharp WeChat Official Account cover PNG.")
    parser.add_argument("--title", required=True, help="Main title. Keep short for thumbnail clarity.")
    parser.add_argument("--subtitle", default="", help="Subtitle shown below the title.")
    parser.add_argument("--tagline", default="", help="Bottom micro tagline.")
    parser.add_argument("--label", default="FEATURED ARTICLE", help="Top label.")
    parser.add_argument("--output", required=True, help="Output PNG path.")
    parser.add_argument("--report", default="", help="Optional JSON report path.")
    parser.add_argument("--image-url", default=None, help="Optional background image URL.")
    parser.add_argument("--image-path", default=None, help="Optional local background image path.")
    parser.add_argument("--no-image", action="store_true", help="Use deterministic gradient background only.")
    parser.add_argument("--stock-fallbacks", action="store_true", help="Try built-in stock photo fallbacks if no image is provided.")
    parser.add_argument("--align", default="center", choices=["center", "left"], help="Text alignment.")
    parser.add_argument("--template", default="auto", choices=list(TEMPLATES.keys()), help="Visual style template.")
    parser.add_argument("--overlay-opacity", type=float, default=None, help="Reserved for compatibility; template gradient is used by default.")
    parser.add_argument("--outline-width", type=int, default=2, help="Title stroke width in final pixels.")
    parser.add_argument("--render-scale", type=int, default=DEFAULT_SCALE, help="Internal render scale, 2-5. Default: 4.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        result = render(
            title=args.title,
            subtitle=args.subtitle,
            tagline=args.tagline,
            label=args.label,
            output=args.output,
            report=args.report or None,
            image_url=args.image_url,
            image_path=args.image_path,
            align=args.align,
            template=args.template,
            overlay_opacity=args.overlay_opacity,
            outline_width=args.outline_width,
            no_image=args.no_image,
            stock_fallbacks=args.stock_fallbacks,
            render_scale=args.render_scale,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print_summary(result)
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

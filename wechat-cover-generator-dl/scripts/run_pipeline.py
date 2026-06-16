#!/usr/bin/env python3
"""Self-contained WeChat cover pipeline.

Creates a 900x383 PNG cover plus title metadata and a JSON report from either a
Markdown file, a topic, or explicit title metadata. The script intentionally has
no network requirement: provided images are optional, and the default path uses
deterministic gradients so the skill remains useful when installed alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont
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
MAX_TITLE_WIDTH = CANVAS_W - SAFE_X * 2

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

STYLE_PALETTES = {
    "tech": {
        "bg": ("#0f172a", "#1e40af", "#0891b2"),
        "accent": "#60a5fa",
        "label": "TECH SYSTEM",
        "subtitle": "从概念到可执行路径",
    },
    "business": {
        "bg": ("#111827", "#78350f", "#b45309"),
        "accent": "#fbbf24",
        "label": "BUSINESS",
        "subtitle": "把想法变成可验证的商业闭环",
    },
    "cognitive": {
        "bg": ("#1f2937", "#4338ca", "#7c3aed"),
        "accent": "#c4b5fd",
        "label": "COGNITIVE",
        "subtitle": "从信息输入到结构化行动",
    },
    "health": {
        "bg": ("#064e3b", "#047857", "#84cc16"),
        "accent": "#bbf7d0",
        "label": "WELLNESS",
        "subtitle": "稳态、节律与可持续改善",
    },
    "professional": {
        "bg": ("#111827", "#374151", "#64748b"),
        "accent": "#e5e7eb",
        "label": "FEATURED",
        "subtitle": "专业视角与方法框架",
    },
}


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _resolve_font() -> str:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise RuntimeError("No CJK-capable system font found.")


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_resolve_font(), size)


def _text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
    box = font.getbbox(text)
    return box[2] - box[0]


def _text_height(text: str, font: ImageFont.FreeTypeFont) -> int:
    box = font.getbbox(text)
    return box[3] - box[1]


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _compact_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_markdown(path: Path | None) -> tuple[str, str]:
    if path is None:
        return "", ""
    text = path.read_text(encoding="utf-8")
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    body = re.sub(r"^# .*$", "", text, count=1, flags=re.MULTILINE)
    return title, body


def infer_style(topic: str, requested: str) -> str:
    if requested and requested != "auto":
        aliases = {
            "high-level": "business",
            "biz": "business",
            "learning": "cognitive",
            "wellness": "health",
        }
        return aliases.get(requested.lower(), requested.lower())
    lower = topic.lower()
    if any(k in lower for k in ["health", "wellness", "meditation", "冥想", "健康"]):
        return "health"
    if any(k in lower for k in ["learning", "knowledge", "cognitive", "认知", "学习"]):
        return "cognitive"
    if any(k in lower for k in ["business", "startup", "opc", "商业"]):
        return "business"
    if any(k in lower for k in ["ai", "tech", "system", "数字", "技术"]):
        return "tech"
    return "professional"


def shorten_title(raw: str, topic: str, style: str) -> tuple[str, str]:
    source = _compact_spaces(raw or topic or "未命名文章")
    full_title = source
    if len(source) <= 22:
        return source, full_title

    if "：" in source:
        head, tail = source.split("：", 1)
        candidate = f"{head}：{tail[:18]}"
    elif ":" in source:
        head, tail = source.split(":", 1)
        candidate = f"{head}: {tail.strip()[:28]}"
    elif _contains_cjk(source):
        candidate = source[:20]
    else:
        candidate = " ".join(source.split()[:8])

    return candidate.rstrip("，。,. "), full_title


def build_metadata(*, title: str, topic: str, style: str, subtitle: str, label: str) -> dict:
    style = infer_style(topic or title, style)
    palette = STYLE_PALETTES.get(style, STYLE_PALETTES["professional"])
    cover_title, full_title = shorten_title(title, topic, style)
    final_subtitle = subtitle or palette["subtitle"]
    final_label = label or palette["label"]
    tagline = "可验证 · 可复用 · 可发布"
    if style == "health":
        tagline = "稳定节律 · 身心恢复 · 日常实践"
    elif style == "cognitive":
        tagline = "输入 · 结构 · 输出"
    elif style == "business":
        tagline = "需求验证 · MVP · 商业闭环"
    elif style == "tech":
        tagline = "系统思维 · AI 工具链 · 自动化"
    return {
        "title": cover_title,
        "full_title": full_title,
        "subtitle": final_subtitle,
        "tagline": tagline,
        "label": final_label,
        "style": style,
    }


def write_title_md(metadata: dict, output_path: Path) -> Path:
    path = output_path.with_name(f"{output_path.stem}-title.md")
    content = "\n".join(
        [
            f"# {metadata['title']}",
            "",
            "## 副标题",
            metadata["subtitle"],
            "",
            "## 标签",
            metadata["tagline"],
            "",
            "## 原标题",
            metadata["full_title"],
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    return path


def _gradient_background(style: str, seed_text: str) -> Image.Image:
    palette = STYLE_PALETTES.get(style, STYLE_PALETTES["professional"])
    c1, c2, c3 = [_hex_to_rgb(v) for v in palette["bg"]]
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), c1)
    px = img.load()
    for y in range(CANVAS_H):
        for x in range(CANVAS_W):
            t = (x / CANVAS_W) * 0.65 + (y / CANVAS_H) * 0.35
            mid = c2 if t < 0.55 else c3
            local_t = t / 0.55 if t < 0.55 else (t - 0.55) / 0.45
            base = c1 if t < 0.55 else c2
            px[x, y] = tuple(int(base[i] * (1 - local_t) + mid[i] * local_t) for i in range(3))

    draw = ImageDraw.Draw(img, "RGBA")
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    for i in range(8):
        cx = int(digest[i] / 255 * CANVAS_W)
        cy = int(digest[i + 8] / 255 * CANVAS_H)
        radius = 80 + digest[i + 16] % 120
        color = (*c3, 24 + digest[i] % 36)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    return img


def _load_background(image_path: str | None, image_url: str | None, style: str, seed_text: str) -> tuple[Image.Image, str]:
    if image_path:
        try:
            return Image.open(image_path).convert("RGB"), f"local:{image_path}"
        except Exception:
            pass
    if image_url:
        tmp_name = ""
        try:
            with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tmp:
                tmp_name = tmp.name
            urllib.request.urlretrieve(image_url, tmp_name)
            return Image.open(tmp_name).convert("RGB"), image_url
        except Exception:
            pass
        finally:
            if tmp_name:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
    return _gradient_background(style, seed_text), "deterministic_gradient"


def _center_crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    target = CANVAS_W / CANVAS_H
    current = w / h
    if current > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        new_h = int(w / target)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)
    return img.crop(box).resize((CANVAS_W, CANVAS_H), Image.LANCZOS)


def wrap_title(title: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if _text_width(title, font) <= max_width:
        return [title]
    if _contains_cjk(title):
        lines: list[str] = []
        current = ""
        for ch in title:
            trial = current + ch
            if current and _text_width(trial, font) > max_width:
                lines.append(current)
                current = ch
            else:
                current = trial
        if current:
            lines.append(current)
        return lines[:2]

    words = title.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if current and _text_width(trial, font) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines[:2]


def fit_title(title: str) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(54, 27, -2):
        font = _load_font(size)
        lines = wrap_title(title, font, MAX_TITLE_WIDTH)
        if all(_text_width(line, font) <= MAX_TITLE_WIDTH for line in lines):
            return font, lines
    font = _load_font(28)
    return font, wrap_title(title, font, MAX_TITLE_WIDTH)


def _draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: str, stroke: int = 2) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 150))


def render_cover(metadata: dict, output: Path, image_path: str | None = None, image_url: str | None = None) -> tuple[Path, str, dict]:
    bg, source = _load_background(image_path, image_url, metadata["style"], metadata["full_title"])
    bg = _center_crop(bg).convert("RGBA")

    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    if source == "deterministic_gradient":
        draw.rectangle([0, 0, CANVAS_W, CANVAS_H], fill=(0, 0, 0, 36))
    else:
        draw.rectangle([0, 0, CANVAS_W, CANVAS_H], fill=(0, 0, 0, 108))

    font_title, title_lines = fit_title(metadata["title"])
    font_label = _load_font(16)
    font_sub = _load_font(22)
    font_tag = _load_font(15)

    line_gap = 8
    title_h = sum(_text_height(line, font_title) for line in title_lines) + line_gap * (len(title_lines) - 1)
    block_h = 18 + 24 + title_h + 20 + _text_height(metadata["subtitle"], font_sub) + 20 + _text_height(metadata["tagline"], font_tag)
    y = max(42, (CANVAS_H - block_h) // 2)

    accent = STYLE_PALETTES.get(metadata["style"], STYLE_PALETTES["professional"])["accent"]
    _draw_text(draw, (SAFE_X, y), metadata["label"], font_label, accent, stroke=1)
    y += 42

    max_title_width = 0
    for line in title_lines:
        _draw_text(draw, (SAFE_X, y), line, font_title, "#ffffff", stroke=2)
        max_title_width = max(max_title_width, _text_width(line, font_title))
        y += _text_height(line, font_title) + line_gap

    y += 10
    draw.rectangle([SAFE_X, y, SAFE_X + min(280, max_title_width), y + 3], fill=_hex_to_rgb(accent) + (220,))
    y += 18
    _draw_text(draw, (SAFE_X, y), metadata["subtitle"], font_sub, "#f8fafc", stroke=1)
    y += 40
    _draw_text(draw, (SAFE_X, y), metadata["tagline"], font_tag, "#d1d5db", stroke=1)

    final = Image.alpha_composite(bg, overlay).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    final.save(output, "PNG")

    validation = validate_cover(output, metadata, title_lines, max_title_width)
    return output, source, validation


def validate_cover(path: Path, metadata: dict, title_lines: list[str], title_width: int) -> dict:
    blockers = []
    try:
        img = Image.open(path)
        dims = list(img.size)
    except Exception as exc:
        return {"status": "fail", "blockers": [f"cover not readable: {exc}"], "dimensions": [0, 0]}

    if dims != [CANVAS_W, CANVAS_H]:
        blockers.append(f"invalid dimensions: {dims}")
    if not metadata.get("title"):
        blockers.append("missing title")
    if len(title_lines) > 2:
        blockers.append("title wraps to more than 2 lines")
    if title_width <= 0:
        blockers.append("title not rendered")
    if title_width > MAX_TITLE_WIDTH:
        blockers.append("title exceeds safe width")

    return {
        "status": "pass" if not blockers else "fail",
        "dimensions": dims,
        "blockers": blockers,
        "title_lines": title_lines,
        "title_width_px": title_width,
        "safe_area_px": SAFE_X,
    }


def build_report(*, output: Path, title_md: Path, metadata: dict, image_source: str, validation: dict) -> dict:
    return {
        "skill_name": "wechat-cover-generator-dl",
        "status": "passed" if validation["status"] == "pass" else "failed",
        "cover_image_url": str(output.resolve()),
        "cover_image_path": str(output.resolve()),
        "title_md_path": str(title_md.resolve()),
        "layout": "left-title-overlay",
        "text_render_quality": "high" if validation["status"] == "pass" else "blocked",
        "validation": validation["status"],
        "validation_details": validation,
        "dimensions": validation["dimensions"],
        "image_source": image_source,
        "image_validation_attempts": 1,
        "title_metadata": metadata,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a WeChat cover PNG and JSON report.")
    parser.add_argument("--input", help="Markdown article file")
    parser.add_argument("--topic", default="", help="Article topic if no Markdown file is available")
    parser.add_argument("--title", default="", help="Exact or preferred cover title")
    parser.add_argument("--subtitle", default="", help="Optional subtitle override")
    parser.add_argument("--label", default="", help="Optional label override")
    parser.add_argument("--style", default="auto", help="auto, tech, business, cognitive, health, professional")
    parser.add_argument("--image-path", default=None, help="Optional local background image")
    parser.add_argument("--image-url", default=None, help="Optional remote background image")
    parser.add_argument("--output", default="/tmp/wechat-cover.png", help="Output PNG path")
    parser.add_argument("--report", default="", help="Output JSON report path")
    args = parser.parse_args(list(argv) if argv is not None else None)

    md_path = Path(args.input).expanduser() if args.input else None
    if md_path and not md_path.exists():
        print(f"ERROR: input Markdown not found: {md_path}", file=sys.stderr)
        return 2

    md_title, body = parse_markdown(md_path)
    topic = args.topic or md_title or _compact_spaces(body[:160])
    title = args.title or md_title or topic
    if not title and not topic:
        print("ERROR: provide --input, --topic, or --title", file=sys.stderr)
        return 2

    output = Path(args.output).expanduser()
    report_path = Path(args.report).expanduser() if args.report else output.with_suffix(".json")

    try:
        metadata = build_metadata(
            title=title,
            topic=topic,
            style=args.style,
            subtitle=args.subtitle,
            label=args.label,
        )
        title_md = write_title_md(metadata, output)
        cover_path, image_source, validation = render_cover(metadata, output, args.image_path, args.image_url)
        report = build_report(
            output=cover_path,
            title_md=title_md,
            metadata=metadata,
            image_source=image_source,
            validation=validation,
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

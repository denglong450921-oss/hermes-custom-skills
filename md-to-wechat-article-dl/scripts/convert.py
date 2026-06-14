#!/usr/bin/env python3
"""Convert Markdown to audited, WeChat-compatible inline-style HTML."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import bleach
    import yaml
    from bs4 import BeautifulSoup, Tag
    from markdown import markdown
except ImportError as error:  # pragma: no cover - exercised by CLI environments
    print(
        json.dumps(
            {
                "status": "error",
                "message": f"Missing dependency: {error.name}",
                "install": "pip install markdown PyYAML beautifulsoup4 bleach",
            },
            ensure_ascii=False,
        )
    )
    raise SystemExit(1)

from quality import audit_html
from official_verify import verify_article_structure
from highlighting import (
    preprocess_callouts,
    preprocess_inline_highlights,
    apply_highlight_styles,
)


THEMES: dict[str, dict[str, str]] = {
    "minimal": {
        "page": "#FFFFFF",
        "surface": "#F7F8FA",
        "title": "#111827",
        "text": "#374151",
        "muted": "#6B7280",
        "border": "#E5E7EB",
        "accent": "#2563EB",
        "code": "#F3F4F6",
        "callout_problem": "#E53E3E",
        "callout_strategy": "#3182CE",
        "callout_thinking": "#805AD5",
    },
    "tech": {
        "page": "#FFFFFF",
        "surface": "#F8FAFC",
        "title": "#0F172A",
        "text": "#334155",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "accent": "#2563EB",
        "code": "#F1F5F9",
        "callout_problem": "#DC2626",
        "callout_strategy": "#2563EB",
        "callout_thinking": "#7C3AED",
    },
    "cognition": {
        "page": "#FFFDF8",
        "surface": "#F8F4EA",
        "title": "#292524",
        "text": "#44403C",
        "muted": "#78716C",
        "border": "#E7E1D5",
        "accent": "#9A6B3F",
        "code": "#F4EFE5",
        "callout_problem": "#B91C1C",
        "callout_strategy": "#6B8F5E",
        "callout_thinking": "#6366F1",
    },
    "wealth": {
        "page": "#FFFEF8",
        "surface": "#F6F3E8",
        "title": "#17352C",
        "text": "#35443E",
        "muted": "#6B756F",
        "border": "#E2DDCE",
        "accent": "#A47C42",
        "code": "#F3F0E6",
        "callout_problem": "#B85450",
        "callout_strategy": "#5B8C6F",
        "callout_thinking": "#5B7FAF",
    },
    "health": {
        "page": "#FFFFFF",
        "surface": "#F3F8F6",
        "title": "#183B38",
        "text": "#36514E",
        "muted": "#6A7F7C",
        "border": "#DDE9E5",
        "accent": "#3F7D78",
        "code": "#EEF5F2",
        "callout_problem": "#C62828",
        "callout_strategy": "#3F7D78",
        "callout_thinking": "#1565C0",
    },
}

ALLOWED_TAGS = [
    "section",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "strong",
    "em",
    "del",
    "ul",
    "ol",
    "li",
    "blockquote",
    "pre",
    "code",
    "a",
    "img",
    "span",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "br",
]


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)(.*)\Z", text, re.S)
    if not match:
        return {}, text
    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError("YAML frontmatter must be a mapping.")
    return metadata, match.group(2)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "、".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def infer_theme(metadata: dict[str, Any], body: str) -> str:
    declared_type = normalize_text(metadata.get("type")).lower()
    if declared_type in THEMES:
        return declared_type
    signal = " ".join(
        [
            normalize_text(metadata.get("type")),
            normalize_text(metadata.get("category")),
            normalize_text(metadata.get("tags")),
            body[:4000],
        ]
    ).lower()
    keyword_groups = {
        "health": ("健康", "医学", "运动", "睡眠", "营养", "疾病", "wellness", "health"),
        "tech": (
            "ai",
            "人工智能",
            "软件",
            "代码",
            "架构",
            "模型",
            "api",
            "技术",
            "tech",
        ),
        "wealth": ("财富", "金融", "投资", "商业", "战略", "finance", "business"),
        "cognition": ("认知", "成长", "学习", "长期主义", "思维", "自我提升"),
    }
    scores = {
        theme: sum(signal.count(keyword) for keyword in keywords)
        for theme, keywords in keyword_groups.items()
    }
    winner = max(scores, key=scores.get)
    return winner if scores[winner] > 0 else "minimal"


def safe_markdown(body: str) -> BeautifulSoup:
    body = preprocess_callouts(body)
    body = preprocess_inline_highlights(body)
    raw_html = markdown(
        body,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    cleaned = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes={
            "a": ["href", "title"],
            "img": ["src", "alt", "title"],
            "span": ["data-hl"],
            "section": ["data-callout"],
            "th": ["colspan", "rowspan"],
            "td": ["colspan", "rowspan"],
        },
        protocols=["http", "https", "mailto"],
        strip=True,
        strip_comments=True,
    )
    soup = BeautifulSoup(cleaned, "html.parser")
    for tag in soup.find_all(True):
        for attribute in list(tag.attrs):
            if attribute.lower().startswith("on") or attribute in {"class", "id", "style"}:
                del tag.attrs[attribute]
    for heading in soup.find_all("h1"):
        heading.name = "h2"
    for pre in list(soup.find_all("pre")):
        code = pre.find("code")
        if code is None:
            paragraph = soup.new_tag("p")
            paragraph.string = pre.get_text()
            pre.replace_with(paragraph)
            continue
        container = soup.new_tag("section")
        code.extract()
        container.append(code)
        pre.replace_with(container)
    return soup


def style_map(theme: dict[str, str], *, strict: bool) -> dict[str, str]:
    radius = "10px" if strict else "14px"
    return {
        "h2": (
            f"margin:32px 0 12px;font-size:20px;line-height:1.45;font-weight:700;"
            f"color:{theme['title']};letter-spacing:0.01em;"
        ),
        "h3": (
            f"margin:24px 0 10px;font-size:17px;line-height:1.5;font-weight:650;"
            f"color:{theme['title']};"
        ),
        "h4": (
            f"margin:20px 0 8px;font-size:16px;line-height:1.5;font-weight:650;"
            f"color:{theme['title']};"
        ),
        "p": (
            f"margin:0 0 15px;font-size:16px;line-height:1.82;color:{theme['text']};"
            "letter-spacing:0.02em;text-align:left;"
        ),
        "strong": f"font-weight:700;color:{theme['title']};",
        "em": f"font-style:italic;color:{theme['text']};",
        "del": f"color:{theme['muted']};",
        "ul": "margin:8px 0 18px;padding-left:1.3em;",
        "ol": "margin:8px 0 18px;padding-left:1.4em;",
        "li": (
            f"margin:0 0 8px;font-size:16px;line-height:1.78;color:{theme['text']};"
        ),
        "blockquote": (
            f"margin:24px 0;padding:18px 18px;background:{theme['surface']};"
            f"border-left:3px solid {theme['accent']};border-radius:0 {radius} {radius} 0;"
            f"color:{theme['title']};"
        ),
        "code": (
            f"padding:2px 5px;background:{theme['code']};border-radius:4px;"
            f"font-size:13px;color:{theme['title']};"
        ),
        "a": f"color:{theme['accent']};text-decoration:none;border-bottom:1px solid {theme['border']};",
        "img": (
            f"display:block;width:100%;max-width:100%;height:auto;margin:24px auto;"
            f"border-radius:{radius};"
        ),
        "table": (
            "width:100%;margin:18px 0;border-collapse:collapse;table-layout:fixed;"
            "font-size:13px;line-height:1.6;word-break:break-word;"
        ),
        "th": (
            f"padding:10px 8px;background:{theme['surface']};"
            f"border:1px solid {theme['border']};color:{theme['title']};"
            "font-weight:650;text-align:left;"
        ),
        "td": (
            f"padding:10px 8px;border:1px solid {theme['border']};"
            f"color:{theme['text']};vertical-align:top;"
        ),
        "hr": f"margin:32px 0;border:0;border-top:1px solid {theme['border']};",
    }


def apply_styles(soup: BeautifulSoup, theme: dict[str, str], *, strict: bool) -> None:
    radius = "10px" if strict else "14px"
    styles = style_map(theme, strict=strict)
    for tag_name, css in styles.items():
        for tag in soup.find_all(tag_name):
            tag["style"] = css
    for code in soup.find_all("code"):
        if code.parent and code.parent.name == "section":
            code.parent["style"] = (
                f"margin:20px 0;padding:16px;background:{theme['code']};"
                f"border:1px solid {theme['border']};border-radius:{radius};"
                "overflow:hidden;"
            )
            code["style"] = (
                f"padding:0;background:transparent;border-radius:0;"
                f"display:block;white-space:pre-wrap;word-break:break-word;"
                f"font-size:13px;line-height:1.65;color:{theme['title']};"
            )
    for quote in soup.find_all("blockquote"):
        for paragraph in quote.find_all("p"):
            paragraph["style"] = (
                f"margin:0;font-size:16px;line-height:1.82;font-weight:600;"
                f"color:{theme['title']};"
            )


def section_map(soup: BeautifulSoup, theme: dict[str, str]) -> str:
    headings = [heading.get_text(" ", strip=True) for heading in soup.find_all("h2")]
    headings = [heading for heading in headings if heading][:4]
    if len(headings) < 2:
        return ""
    items = "".join(
        (
            f'<p style="margin:0 0 8px;font-size:14px;line-height:1.65;'
            f'color:{theme["text"]};"><strong style="font-weight:700;'
            f'color:{theme["accent"]};">{index:02d}</strong>'
            f'<span style="color:{theme["muted"]};"> · </span>{html.escape(label)}</p>'
        )
        for index, label in enumerate(headings, start=1)
    )
    return (
        f'<section style="margin:24px 0 30px;padding:18px 18px 10px;'
        f'background:{theme["surface"]};border:1px solid {theme["border"]};'
        f'border-radius:12px;">'
        f'<p style="margin:0 0 10px;font-size:13px;line-height:1.5;font-weight:700;'
        f'letter-spacing:0.08em;color:{theme["muted"]};">阅读路径</p>{items}</section>'
    )


def render(
    metadata: dict[str, Any],
    body: str,
    *,
    title_override: str | None,
    theme_name: str,
    strict: bool,
) -> str:
    palette = THEMES[theme_name]
    title = title_override or normalize_text(metadata.get("title")) or "未命名文章"
    author = normalize_text(metadata.get("author"))
    date_value = normalize_text(metadata.get("date"))
    summary = normalize_text(metadata.get("summary") or metadata.get("description"))
    soup = safe_markdown(body)
    apply_styles(soup, palette, strict=strict)
    apply_highlight_styles(soup, palette)

    meta_parts = [part for part in (author, date_value) if part]
    meta_line = " · ".join(meta_parts)
    summary_html = ""
    if summary:
        summary_html = (
            f'<p style="margin:14px 0 0;font-size:15px;line-height:1.8;'
            f'color:{palette["muted"]};">{html.escape(summary)}</p>'
        )
    meta_html = ""
    if meta_line:
        meta_html = (
            f'<p style="margin:12px 0 0;font-size:13px;line-height:1.6;'
            f'color:{palette["muted"]};">{html.escape(meta_line)}</p>'
        )
    path_html = section_map(soup, palette)
    body_html = str(soup)

    footer = ""
    if author:
        footer = (
            f'<p style="margin:34px 0 0;padding-top:18px;border-top:1px solid '
            f'{palette["border"]};font-size:12px;line-height:1.6;text-align:center;'
            f'color:{palette["muted"]};">© {html.escape(author)}</p>'
        )

    root_radius = "0" if strict else "2px"
    return (
        f'<section style="max-width:680px;margin:0 auto;padding:24px 18px 36px;'
        f'background:{palette["page"]};color:{palette["text"]};'
        f'border-radius:{root_radius};word-break:break-word;">'
        f'<section style="margin:0 0 28px;padding:2px 0 22px;'
        f'border-bottom:1px solid {palette["border"]};">'
        f'<p style="margin:0 0 9px;font-size:12px;line-height:1.5;font-weight:700;'
        f'letter-spacing:0.1em;color:{palette["accent"]};">WECHAT FEATURE</p>'
        f'<h1 style="margin:0;font-size:26px;line-height:1.35;font-weight:750;'
        f'letter-spacing:-0.01em;color:{palette["title"]};">{html.escape(title)}</h1>'
        f"{summary_html}{meta_html}</section>{path_html}"
        f'<section style="margin:0;padding:0;">{body_html}</section>{footer}</section>'
    )


def convert(
    input_path: Path,
    output_path: Path,
    *,
    theme_name: str,
    title: str | None,
    threshold: int,
    report_path: Path,
    official_check: bool = False,
    official_timeout: float = 15.0,
) -> dict[str, Any]:
    if not input_path.is_file():
        raise ValueError(f"Input file not found: {input_path}")
    text = input_path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    if not body.strip():
        raise ValueError("Markdown body is empty.")
    selected_theme = infer_theme(metadata, body) if theme_name == "auto" else theme_name
    if selected_theme not in THEMES:
        raise ValueError(
            f"Unknown theme '{selected_theme}'. Choose: {', '.join(THEMES)}"
        )

    output_html = render(
        metadata,
        body,
        title_override=title,
        theme_name=selected_theme,
        strict=False,
    )
    audit = audit_html(output_html, threshold=threshold)
    auto_repaired = False
    if audit["status"] != "passed":
        auto_repaired = True
        output_html = render(
            metadata,
            body,
            title_override=title,
            theme_name=selected_theme,
            strict=True,
        )
        audit = audit_html(output_html, threshold=threshold)
    official_validation = {
        "status": "skipped",
        "is_valid": None,
        "reason": "not_requested",
        "violations": [],
        "violation_count": 0,
        "transport": None,
    }
    if official_check and audit["status"] == "passed":
        official_validation = verify_article_structure(
            output_html,
            timeout=official_timeout,
        )
    elif official_check:
        official_validation = {
            "status": "skipped",
            "is_valid": False,
            "reason": "local_audit_failed",
            "violations": [],
            "violation_count": 0,
            "transport": None,
        }
    final_status = audit["status"]
    if official_check and official_validation["status"] != "passed":
        final_status = "blocked"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_html + "\n", encoding="utf-8")
    result = {
        "status": final_status,
        "output": str(output_path.resolve()),
        "report": str(report_path.resolve()),
        "title": title or normalize_text(metadata.get("title")) or "未命名文章",
        "theme": selected_theme,
        "auto_repaired": auto_repaired,
        "scores": audit["scores"],
        "failed_dimensions": audit["failed_dimensions"],
        "warnings": audit["warnings"],
        "manual_review": audit["manual_review"],
        "official_validation": official_validation,
        "source_chars": len(body),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps({**result, "checks": audit["checks"]}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to premium WeChat-compatible HTML."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", required=True, type=Path)
    parser.add_argument("--title")
    parser.add_argument(
        "--theme",
        default="auto",
        choices=["auto", *THEMES.keys()],
    )
    parser.add_argument("--quality-threshold", type=int, default=90)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--official-check",
        action="store_true",
        help="Explicitly transmit final HTML to WeChat's official structure verifier.",
    )
    parser.add_argument("--official-timeout", type=float, default=15.0)
    args = parser.parse_args()
    report_path = args.report or Path(str(args.output) + ".report.json")
    try:
        result = convert(
            args.input,
            args.output,
            theme_name=args.theme,
            title=args.title,
            threshold=args.quality_threshold,
            report_path=report_path,
            official_check=args.official_check,
            official_timeout=args.official_timeout,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

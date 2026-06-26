#!/usr/bin/env python3
"""Markdown pre/post-processing for content highlighting.

Converts custom inline markers and callout blocks to styled HTML elements
that conform to WeChat Official Account inline-CSS constraints.

Inline highlights use restrained bold + colour changes (no background pills).
Callout blocks use coloured left-border cards (layout variation).

Syntax:
  ==core concept==    → bold + accent colour (core concepts, key definitions)
  ^^key viewpoint^^   → bold + title colour (viewpoints, arguments)
  !!emphasis text!!   → bold only (what the article emphasises)

  :::problem Title     callout block — problem statement
  ...content...
  :::

  :::strategy Title    callout block — strategies and approaches
  ...content...
  :::

  :::thinking Title    callout block — thinking methods / mental models
  ...content...
  :::

  :::key Title         callout block — core insight / key takeaway
  ...content...
  :::
"""

from __future__ import annotations

import html
import re
from typing import Any

from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Callout configuration per type
# ---------------------------------------------------------------------------

CALLOUT_META: dict[str, dict[str, str]] = {
    "problem":   {"emoji": "❗", "label": "问题"},
    "strategy":  {"emoji": "🎯", "label": "策略"},
    "thinking":  {"emoji": "💡", "label": "思维方法"},
    "key":       {"emoji": "⭐", "label": "核心洞察"},
}

# --- Inline highlight patterns ---------------------------------------------

INLINE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"==(.+?)=="),  "hl_core"),
    (re.compile(r"\^\^(.+?)\^\^"), "hl_view"),
    (re.compile(r"!!(.+?)!!"),  "hl_em"),
]


# ---------------------------------------------------------------------------
# 1. Pre-process callout blocks before markdown conversion
# ---------------------------------------------------------------------------

def _auto_close_callouts(text: str) -> str:
    """Auto-close unclosed ::: callout fences.

    Missing ``:::`` closers cause the preprocessor to consume the entire
    rest of the document as callout content, producing broken HTML.
    Inserts ``:::`` before each subsequent ``:::type`` opener, and at EOF.
    """
    lines = text.split("\n")
    out: list[str] = []
    open_count = 0
    for line in lines:
        if re.match(r"^:::(problem|strategy|thinking|key)\s", line):
            if open_count > 0:
                out.append(":::")
                open_count -= 1
            open_count += 1
            out.append(line)
        elif line.strip() == ":::":
            open_count -= 1
            out.append(line)
        else:
            out.append(line)
    if open_count > 0:
        out.append(":::")
    return "\n".join(out)


def preprocess_callouts(text: str) -> str:
    """Convert ``:::type ... :::`` fences into raw HTML ``<section>`` elements.

    The inner content is left for the markdown engine to parse.  Each section
    carries a ``data-callout`` attribute that survives bleach and is replaced
    with inline styles later.
    """
    text = _auto_close_callouts(text)
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        match = re.match(r"^:::(problem|strategy|thinking|key)\s*(.*)$", line)
        if match:
            ctype = match.group(1)
            title = match.group(2).strip()
            content_lines: list[str] = []
            i += 1
            while i < n and lines[i].strip() != ":::":
                content_lines.append(lines[i])
                i += 1
            inner = "\n".join(content_lines).strip()
            title_html = ""
            if title:
                meta = CALLOUT_META.get(ctype, {"emoji": "📌", "label": ""})
                title_html = (
                    f'<p style="margin:0 0 8px;font-size:15px;line-height:1.6;'
                    f'font-weight:700;">{meta["emoji"]} {html.escape(title)}</p>'
                )
            out.append(
                f'<section data-callout="{ctype}">'
                f"{title_html}"
                f"{inner}"
                f"</section>"
            )
        else:
            out.append(line)
        i += 1

    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2. Pre-process inline highlight markers before markdown conversion
# ---------------------------------------------------------------------------

def preprocess_inline_highlights(text: str) -> str:
    """Replace ``==text==`` / ``^^text^^`` / ``!!text!!`` with ``<span data-hl="...">``."""
    for pattern, hl_type in INLINE_PATTERNS:
        text = pattern.sub(f'<span data-hl="{hl_type}">\\1</span>', text)
    return text


# ---------------------------------------------------------------------------
# 3. Post-process: apply highlight styles
# ---------------------------------------------------------------------------

def apply_highlight_styles(soup: BeautifulSoup, theme_palette: dict[str, str]) -> None:
    """Apply inline styles to data-hl and data-callout elements.

    ``theme_palette`` should be the resolved colour dict from THEMES (in
    convert.py), containing keys like 'accent', 'title', 'text', 'surface',
    'code', 'border', etc.
    """
    accent = theme_palette.get("accent", "#2563EB")
    title = theme_palette.get("title", "#111827")
    surface = theme_palette.get("surface", "#F7F8FA")

    # --- Inline highlights — bold + colour only, no background ---
    hl_styles = {
        "hl_core": f"color:{accent};font-weight:700;",
        "hl_view": f"color:{title};font-weight:600;",
        "hl_em":   f"font-weight:700;",
    }
    for span in list(soup.find_all("span", attrs={"data-hl": True})):
        hl_type = span["data-hl"]
        span["style"] = hl_styles.get(hl_type, hl_styles["hl_em"])
        del span["data-hl"]

    # --- Callout blocks — left-border cards ---
    for section in list(soup.find_all("section", attrs={"data-callout": True})):
        ctype = section["data-callout"]
        border_color = theme_palette.get(f"callout_{ctype}", accent)

        section_style = (
            f"margin:28px 0;padding:16px 18px;background:{surface};"
            f"border-left:4px solid {border_color};"
            f"border-radius:0 12px 12px 0;"
        )
        section["style"] = section_style
        del section["data-callout"]

        # Title <p> — first p with a <strong>
        first_p = section.find("p")
        if first_p is not None and first_p.find("strong"):
            first_p["style"] = (
                f"margin:0 0 8px;font-size:15px;line-height:1.6;"
                f"font-weight:700;"
            )

        # Body paragraphs
        for p in section.find_all("p"):
            if "style" not in (p.get("style") or ""):
                p["style"] = f"margin:0 0 10px;font-size:15px;line-height:1.75;"

        last_ps = section.find_all("p")
        if last_ps:
            last_ps[-1]["style"] = re.sub(
                r"margin-bottom:[^;]+",
                "margin-bottom:0",
                last_ps[-1].get("style", ""),
            )

        # List items inside callouts
        for li in section.find_all("li"):
            li["style"] = f"margin:0 0 6px;font-size:15px;line-height:1.7;"
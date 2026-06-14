#!/usr/bin/env python3
"""Markdown pre/post-processing for sophisticated content highlighting.

Converts custom inline markers and callout blocks to styled HTML elements
that conform to WeChat Official Account inline-CSS constraints.

Syntax:
  ==core concept==    → inline highlight (core concepts)
  ^^key viewpoint^^   → inline highlight (key viewpoints, arguments)
  !!emphasis text!!   → inline highlight (what the article emphasises)

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

from bs4 import BeautifulSoup, Tag

# ---------------------------------------------------------------------------
# Callout configuration per type
# ---------------------------------------------------------------------------

CALLOUT_META: dict[str, dict[str, str]] = {
    "problem":   {"emoji": "❗", "label": "问题"},
    "strategy":  {"emoji": "🎯", "label": "策略"},
    "thinking":  {"emoji": "💡", "label": "思维方法"},
    "key":       {"emoji": "⭐", "label": "核心洞察"},
}

# --- Inline highlight patterns (order matters: longer markers first) --------

INLINE_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"==(.+?)=="),  "hl_core", "核心概念"),
    (re.compile(r"\^\^(.+?)\^\^"), "hl_view", "关键观点"),
    (re.compile(r"!!(.+?)!!"),  "hl_em",   "重点强调"),
]

# ---------------------------------------------------------------------------
# Callout colour tokens per theme
# ---------------------------------------------------------------------------
# Each theme provides:
#   callout_problem_bg, callout_problem_border
#   callout_strategy_bg, callout_strategy_border
#   callout_thinking_bg, callout_thinking_border
#   callout_key_bg, callout_key_border
#   hl_core_bg, hl_core_color
#   hl_view_bg, hl_view_color
#   hl_em_bg, hl_em_color

HIGHLIGHT_TOKENS: dict[str, dict[str, str]] = {
    "minimal": {
        "hl_core_bg": "#EEF2FF",       "hl_core_color": "#111827",
        "hl_view_bg": "#F3F4F6",       "hl_view_color": "#374151",
        "hl_em_bg":   "#FEFCE8",       "hl_em_color":   "#111827",
        "callout_problem_bg": "#F7F8FA",    "callout_problem_border": "#E53E3E",
        "callout_strategy_bg": "#F3F4F6",   "callout_strategy_border": "#3182CE",
        "callout_thinking_bg": "#F7F8FA",   "callout_thinking_border": "#805AD5",
        "callout_key_bg": "#F7F8FA",        "callout_key_border": "#2563EB",
    },
    "tech": {
        "hl_core_bg": "#E8F0FE",       "hl_core_color": "#0F172A",
        "hl_view_bg": "#F1F5F9",       "hl_view_color": "#334155",
        "hl_em_bg":   "#FEFCE8",       "hl_em_color":   "#0F172A",
        "callout_problem_bg": "#F8FAFC",    "callout_problem_border": "#DC2626",
        "callout_strategy_bg": "#F1F5F9",   "callout_strategy_border": "#2563EB",
        "callout_thinking_bg": "#F8FAFC",   "callout_thinking_border": "#7C3AED",
        "callout_key_bg": "#F8FAFC",        "callout_key_border": "#4F46E5",
    },
    "cognition": {
        "hl_core_bg": "#EDE9E0",       "hl_core_color": "#292524",
        "hl_view_bg": "#F5F0E8",       "hl_view_color": "#44403C",
        "hl_em_bg":   "#FEF3C7",       "hl_em_color":   "#292524",
        "callout_problem_bg": "#F8F4EA",    "callout_problem_border": "#B91C1C",
        "callout_strategy_bg": "#F4EFE5",   "callout_strategy_border": "#6B8F5E",
        "callout_thinking_bg": "#F8F4EA",   "callout_thinking_border": "#6366F1",
        "callout_key_bg": "#F8F4EA",        "callout_key_border": "#9A6B3F",
    },
    "wealth": {
        "hl_core_bg": "#E8F0E4",       "hl_core_color": "#17352C",
        "hl_view_bg": "#F3EFE3",       "hl_view_color": "#35443E",
        "hl_em_bg":   "#FFF5E0",       "hl_em_color":   "#17352C",
        "callout_problem_bg": "#F6F3E8",    "callout_problem_border": "#B85450",
        "callout_strategy_bg": "#F3F0E6",   "callout_strategy_border": "#5B8C6F",
        "callout_thinking_bg": "#F6F3E8",   "callout_thinking_border": "#5B7FAF",
        "callout_key_bg": "#F6F3E8",        "callout_key_border": "#A47C42",
    },
    "health": {
        "hl_core_bg": "#E8F5E9",       "hl_core_color": "#183B38",
        "hl_view_bg": "#F0F7F4",       "hl_view_color": "#36514E",
        "hl_em_bg":   "#FFF8E1",       "hl_em_color":   "#183B38",
        "callout_problem_bg": "#F3F8F6",    "callout_problem_border": "#C62828",
        "callout_strategy_bg": "#EEF5F2",   "callout_strategy_border": "#3F7D78",
        "callout_thinking_bg": "#F3F8F6",   "callout_thinking_border": "#1565C0",
        "callout_key_bg": "#F3F8F6",        "callout_key_border": "#3F7D78",
    },
}


# ---------------------------------------------------------------------------
# 1. Pre-process callout blocks before markdown conversion
# ---------------------------------------------------------------------------

def preprocess_callouts(text: str) -> str:
    """Convert ``:::type ... :::`` fences into raw HTML ``<section>`` elements.

    The inner content is left as-is (will be parsed by the markdown engine
    along with the rest of the document).  Each section carries a
    ``data-callout`` attribute that survives bleach and is later replaced
    with inline styles.
    """
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
            # i is now at the closing ::: line
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
    for pattern, hl_type, _ in INLINE_PATTERNS:
        text = pattern.sub(f'<span data-hl="{hl_type}">\\1</span>', text)
    return text


# ---------------------------------------------------------------------------
# 3. Post-process: apply highlight styles to data-hl / data-callout elements
# ---------------------------------------------------------------------------

def _hl_style(token_key: str, theme_tokens: dict[str, str], fallback: str = "") -> str:
    return theme_tokens.get(token_key, fallback)


def apply_highlight_styles(soup: BeautifulSoup, theme_name: str) -> None:
    """Find data-hl and data-callout markers and replace with inline-styled HTML.

    Must be called AFTER ``apply_styles()`` because it depends on the theme
    palette being resolved.
    """
    tokens = HIGHLIGHT_TOKENS.get(theme_name, HIGHLIGHT_TOKENS["minimal"])

    # --- Inline highlights ---
    for span in list(soup.find_all("span", attrs={"data-hl": True})):
        hl_type = span["data-hl"]
        bg = tokens.get(f"{hl_type}_bg", "")
        color = tokens.get(f"{hl_type}_color", "")
        style = (
            f"background:{bg};color:{color};padding:1px 8px;"
            f"border-radius:4px;font-weight:600;"
        )
        span["style"] = style
        del span["data-hl"]

    # --- Callout blocks ---
    for section in list(soup.find_all("section", attrs={"data-callout": True})):
        ctype = section["data-callout"]
        bg = tokens.get(f"callout_{ctype}_bg", "")
        border_color = tokens.get(f"callout_{ctype}_border", "")

        section_style = (
            f"margin:28px 0;padding:16px 18px;background:{bg};"
            f"border-left:4px solid {border_color};"
            f"border-radius:0 12px 12px 0;"
        )
        section["style"] = section_style
        del section["data-callout"]

        # Style the title <p> inside the callout
        first_p = section.find("p")
        if first_p is not None and first_p.find("strong"):
            first_p["style"] = (
                f"margin:0 0 8px;font-size:15px;line-height:1.6;"
                f"font-weight:700;"
            )

        # Style remaining <p> tags (body text)
        for p in section.find_all("p"):
            if "style" not in (p.get("style") or ""):
                p["style"] = (
                    f"margin:0 0 10px;font-size:15px;line-height:1.75;"
                )
            # Mark the last paragraph's margin as 0
        last_p = section.find_all("p")
        if last_p:
            last_p[-1]["style"] = re.sub(
                r"margin-bottom:[^;]+",
                "margin-bottom:0",
                last_p[-1].get("style", ""),
            )

        # Style list items inside callouts
        for li in section.find_all("li"):
            li["style"] = (
                f"margin:0 0 6px;font-size:15px;line-height:1.7;"
            )

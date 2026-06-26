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


def _callout_inner_to_html(text: str) -> str:
    """Convert markdown inside callout blocks to HTML.

    Python-Markdown does not parse markdown inside raw HTML <section> blocks,
    so lists and emphasis inside ::: callouts must be pre-converted.
    """
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        
        # Numbered list: "1. item"
        m = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if m:
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", m.group(2))
            result.append(f'<div style="margin:0 0 8px;font-size:15px;line-height:1.75;">{content}</div>')
            continue
            
        # Bullet list: "- item" or "* item"
        m = re.match(r"^[-*]\s+(.*)", stripped)
        if m:
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", m.group(1))
            result.append(f'<div style="margin:0 0 8px;font-size:15px;line-height:1.75;">• {content}</div>')
            continue
            
        # Plain text (including empty lines) — convert **bold**
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        result.append(line)
    
    return "\n".join(result)


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
            inner = _callout_inner_to_html("\n".join(content_lines).strip())
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
# 1b. Pre-process math formulas before markdown conversion
# ---------------------------------------------------------------------------

MATH_REPLACEMENTS: dict[str, str] = {
    r"\\times": "×",
    r"\\approx": "≈",
    r"\\rightarrow": "→",
    r"\\to": "→",
    r"\\cdot": "·",
    r"\\sum": "∑",
    r"\\pi": "π",
    r"\\infty": "∞",
    r"\\ge": "≥",
    r"\\le": "≤",
    r"\\pm": "±",
    r"\\uparrow": "↑",
    r"\\downarrow": "↓",
}


def _replace_latex_commands(text: str) -> str:
    for cmd, uni in MATH_REPLACEMENTS.items():
        text = re.sub(cmd, uni, text)
    text = re.sub(r"\\text\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1 / \2", text)
    return text


def _latex_to_readable(text: str) -> str:
    text = _replace_latex_commands(text)
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_math(text: str) -> str:
    """Convert LaTeX math blocks into WeChat-stable styled HTML.

    Handles $$...$$ and \\[...\\] display math.
    Skips content inside ```..``` code fences.
    """
    protected: dict[str, str] = {}
    def _protect(m: re.Match) -> str:
        t = f"__MATH_PROTECT_{len(protected)}__"
        protected[t] = m.group(0)
        return t

    text = re.sub(r"```.*?```", _protect, text, flags=re.DOTALL)

    for delim_open, delim_close in [
        (re.escape("$$"), re.escape("$$")),
        (re.escape(r"\["), re.escape(r"\]")),
    ]:
        text = re.sub(
            f"{delim_open}(.+?){delim_close}",
            lambda m: f'<section data-math="true">{_latex_to_readable(m.group(1))}</section>',
            text,
            flags=re.DOTALL,
        )

    for token, original in protected.items():
        text = text.replace(token, original)
    return text


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
        # Reset ul/ol padding inside callouts
        for ul in section.find_all(["ul", "ol"]):
            ul["style"] = "margin:8px 0 0;padding-left:1.5em;"

    # --- Math formula blocks ---
    for section in list(soup.find_all("section", attrs={"data-math": True})):
        section["style"] = (
            "margin:20px 0;padding:14px 18px;"
            "background:#F6F3E8;border:1px solid #E2DDCE;"
            "border-radius:10px;font-family:Georgia,serif;"
            "font-size:16px;line-height:1.7;text-align:center;"
        )
        del section["data-math"]

    # --- Convert ALL ul/ol/li to WeChat-compatible div+• ---
    for list_tag in list(soup.find_all(["ul", "ol"])):
        parent = list_tag.parent
        div_container = soup.new_tag("div")
        for li in list_tag.find_all("li"):
            text = li.get_text("", strip=True)
            marker = "• " if list_tag.name == "ul" else ""
            new_div = soup.new_tag(
                "div",
                style="margin:0 0 8px;font-size:15px;line-height:1.75;",
            )
            # Keep any <strong> tags inside the li
            for child in li.children:
                if child.name == "strong":
                    strong_tag = soup.new_tag("strong")
                    strong_tag.string = child.get_text()
                    new_div.append(marker)
                    new_div.append(strong_tag)
                    for sibling in child.next_siblings:
                        if isinstance(sibling, str):
                            new_div.append(sibling)
                elif isinstance(child, str):
                    text_content = child.strip()
                    if text_content:
                        if marker:
                            new_div.append(marker)
                            marker = ""
                        new_div.append(text_content)
            # If we couldn't extract structured content, use plain text
            if not new_div.contents:
                new_div.string = f"{marker}{text}"
            div_container.append(new_div)
        list_tag.replace_with(div_container)
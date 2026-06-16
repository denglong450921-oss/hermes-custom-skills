#!/usr/bin/env python3
"""Deterministic quality scoring for WeChat article HTML."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup


DIMENSIONS = (
    "visual_hierarchy",
    "readability",
    "restraint",
    "consistency",
    "wechat_compatibility",
)


def parse_style(value: str) -> dict[str, str]:
    declarations: dict[str, str] = {}
    for part in value.split(";"):
        if ":" not in part:
            continue
        key, raw_value = part.split(":", 1)
        declarations[key.strip().lower()] = raw_value.strip().lower()
    return declarations


def pixel_value(value: str) -> float | None:
    match = re.search(r"(-?\d+(?:\.\d+)?)px", value)
    return float(match.group(1)) if match else None


def numeric_value(value: str) -> float | None:
    match = re.search(r"(-?\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else None


def css_rgb(value: str) -> tuple[int, int, int] | None:
    value = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return tuple(int(character * 2, 16) for character in value[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))
    match = re.fullmatch(
        r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)",
        value,
    )
    if not match:
        return None
    channels = tuple(int(channel) for channel in match.groups())
    return channels if all(channel <= 255 for channel in channels) else None


def contrast_ratio(foreground: str, background: str) -> float | None:
    foreground_rgb = css_rgb(foreground)
    background_rgb = css_rgb(background)
    if foreground_rgb is None or background_rgb is None:
        return None

    def luminance(rgb: tuple[int, int, int]) -> float:
        channels = []
        for channel in rgb:
            normalized = channel / 255
            channels.append(
                normalized / 12.92
                if normalized <= 0.04045
                else ((normalized + 0.055) / 1.055) ** 2.4
            )
        return (
            0.2126 * channels[0]
            + 0.7152 * channels[1]
            + 0.0722 * channels[2]
        )

    light = max(luminance(foreground_rgb), luminance(background_rgb))
    dark = min(luminance(foreground_rgb), luminance(background_rgb))
    return (light + 0.05) / (dark + 0.05)


def horizontal_padding(value: str) -> float | None:
    values = [
        float(item)
        for item in re.findall(r"(-?\d+(?:\.\d+)?)px", value)
    ]
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    if len(values) in {2, 3}:
        return values[1]
    return values[1]


def add_check(
    checks: list[dict[str, Any]],
    dimension: str,
    name: str,
    passed: bool,
    penalty: int,
    evidence: str,
) -> None:
    checks.append(
        {
            "dimension": dimension,
            "name": name,
            "passed": passed,
            "penalty": 0 if passed else penalty,
            "evidence": evidence,
        }
    )


def maximum_same_tag_depth(tags: list[Any]) -> int:
    maximum = 0
    for tag in tags:
        same_name_ancestors = sum(
            1 for parent in tag.parents if getattr(parent, "name", None) == tag.name
        )
        maximum = max(maximum, same_name_ancestors + 1)
    return maximum


def audit_html(content: str, *, threshold: int = 90) -> dict[str, Any]:
    soup = BeautifulSoup(content, "html.parser")
    checks: list[dict[str, Any]] = []
    all_tags = soup.find_all(True)
    root = soup.find("section")
    direct_sections = (
        root.find_all("section", recursive=False) if root is not None else []
    )
    prose_sections = [
        section for section in direct_sections if section.find("p") is not None
    ]

    def prose_score(section: Any) -> int:
        return (
            len(section.find_all("p"))
            + 5 * len(section.find_all(["h2", "h3", "h4"]))
            + 3
            * len(
                section.find_all(
                    ["blockquote", "ul", "ol", "table", "code"]
                )
            )
        )

    body_container = (
        max(prose_sections, key=prose_score)
        if prose_sections
        else root
    )
    h1 = soup.find("h1")
    h2 = soup.find("h2")
    paragraphs = soup.find_all("p")
    body_paragraphs = (
        body_container.find_all("p") if body_container is not None else paragraphs
    )

    root_style = parse_style(root.get("style", "")) if root else {}
    h1_style = parse_style(h1.get("style", "")) if h1 else {}
    h2_style = parse_style(h2.get("style", "")) if h2 else {}
    body_paragraph = next(
        (
            tag
            for tag in body_paragraphs
            if 15
            <= (
                pixel_value(parse_style(tag.get("style", "")).get("font-size", ""))
                or 0
            )
            <= 16
            and (
                numeric_value(
                    parse_style(tag.get("style", "")).get("line-height", "")
                )
                or 0
            )
            >= 1.75
        ),
        body_paragraphs[0] if body_paragraphs else None,
    )
    paragraph_style = (
        parse_style(body_paragraph.get("style", "")) if body_paragraph else {}
    )

    h1_size = pixel_value(h1_style.get("font-size", ""))
    h2_size = pixel_value(h2_style.get("font-size", ""))
    body_size_candidates = body_paragraphs or soup.find_all(["p", "li"])
    body_sizes = [
        pixel_value(parse_style(tag.get("style", "")).get("font-size", ""))
        for tag in body_size_candidates
    ]
    body_sizes = [size for size in body_sizes if size is not None and size >= 14]
    body_size = max(set(body_sizes), key=body_sizes.count) if body_sizes else None

    add_check(
        checks,
        "visual_hierarchy",
        "single_primary_title",
        len(soup.find_all("h1")) == 1,
        20,
        f"h1_count={len(soup.find_all('h1'))}",
    )
    add_check(
        checks,
        "visual_hierarchy",
        "title_scale",
        h1_size is not None and 22 <= h1_size <= 28,
        15,
        f"h1_font_size={h1_size}",
    )
    add_check(
        checks,
        "visual_hierarchy",
        "heading_scale",
        h2 is None or (h2_size is not None and 18 <= h2_size <= 21),
        15,
        f"h2_font_size={h2_size}",
    )
    add_check(
        checks,
        "visual_hierarchy",
        "descending_type_scale",
        (
            h1_size is not None
            and body_size is not None
            and h1_size >= body_size + 6
            and (h2_size is None or h1_size > h2_size > body_size)
        ),
        20,
        f"title={h1_size}, h2={h2_size}, body={body_size}",
    )
    heading_spacing = [
        pixel_value(parse_style(tag.get("style", "")).get("margin", ""))
        for tag in soup.find_all(["h2", "h3"])
    ]
    add_check(
        checks,
        "visual_hierarchy",
        "section_spacing",
        not heading_spacing
        or all(value is not None and value >= 20 for value in heading_spacing),
        15,
        f"heading_top_margins={heading_spacing}",
    )
    add_check(
        checks,
        "visual_hierarchy",
        "structural_landmarks",
        bool(soup.find(["blockquote", "ul", "ol", "table"]))
        or any(
            code.parent is not None and code.parent.name == "section"
            for code in soup.find_all("code")
        )
        or len(soup.find_all("h2")) >= 2,
        15,
        "Found a key judgment, list, table, code block, or multiple sections.",
    )

    root_padding = horizontal_padding(root_style.get("padding", ""))
    root_width = pixel_value(root_style.get("max-width", ""))
    paragraph_line_height = numeric_value(paragraph_style.get("line-height", ""))
    add_check(
        checks,
        "readability",
        "mobile_body_size",
        body_size is not None and 15 <= body_size <= 16,
        25,
        f"dominant_body_font_size={body_size}",
    )
    add_check(
        checks,
        "readability",
        "comfortable_line_height",
        paragraph_line_height is not None and 1.75 <= paragraph_line_height <= 1.9,
        25,
        f"paragraph_line_height={paragraph_line_height}",
    )
    add_check(
        checks,
        "readability",
        "mobile_side_padding",
        root_padding is not None and 16 <= root_padding <= 20,
        15,
        f"root_padding={root_padding}",
    )
    add_check(
        checks,
        "readability",
        "controlled_measure",
        root_width is not None and root_width <= 680,
        15,
        f"max_width={root_width}",
    )
    long_paragraphs = [
        len(tag.get_text("", strip=True))
        for tag in soup.find_all("p")
        if len(tag.get_text("", strip=True)) > 360
    ]
    add_check(
        checks,
        "readability",
        "paragraph_rhythm",
        len(long_paragraphs) <= 1,
        10,
        f"paragraphs_over_360_chars={len(long_paragraphs)}",
    )
    text_color = paragraph_style.get("color", "")
    add_check(
        checks,
        "readability",
        "soft_text_contrast",
        text_color not in {"", "#000", "#000000", "black"},
        10,
        f"paragraph_color={text_color}",
    )

    colors = set()
    gradient_elements = []
    text_gradient_elements = []
    background_image_text_elements = []
    low_contrast_elements = []
    for tag in all_tags:
        style = tag.get("style", "")
        declarations = parse_style(style)
        colors.update(match.upper() for match in re.findall(r"#[0-9a-fA-F]{6}", style))
        background_value = " ".join(
            filter(
                None,
                (
                    declarations.get("background", ""),
                    declarations.get("background-image", ""),
                ),
            )
        )
        has_text = bool(tag.get_text("", strip=True))
        if "gradient(" in background_value:
            gradient_elements.append(tag.name)
            if has_text:
                text_gradient_elements.append(tag.name)
        if "url(" in background_value and has_text:
            background_image_text_elements.append(tag.name)
        ratio = contrast_ratio(
            declarations.get("color", ""),
            declarations.get("background-color", "")
            or declarations.get("background", ""),
        )
        if ratio is not None and ratio < 3:
            low_contrast_elements.append(f"{tag.name}:{ratio:.2f}")
    content_lower = content.lower()
    # Count box-shadow inside code blocks separately
    shadow_in_code = 0
    for code_tag in soup.find_all("code"):
        shadow_in_code += code_tag.get_text().lower().count("box-shadow")
    radius_values = [
        pixel_value(value)
        for tag in all_tags
        for key, value in parse_style(tag.get("style", "")).items()
        if key == "border-radius"
    ]
    radius_values = [value for value in radius_values if value is not None]
    add_check(
        checks,
        "restraint",
        "controlled_palette",
        len(colors) <= 12,
        30,
        f"unique_hex_colors={len(colors)} ({sorted(colors)})",
    )
    add_check(
        checks,
        "restraint",
        "no_text_over_gradients",
        not text_gradient_elements,
        25,
        (
            f"gradient_elements={gradient_elements}, "
            f"text_gradient_elements={text_gradient_elements}"
        ),
    )
    add_check(
        checks,
        "restraint",
        "no_heavy_shadows",
        content_lower.count("box-shadow") - shadow_in_code <= 1
        and not re.search(
            r"box-shadow:[^;]*(?:0\.[1-9]|rgba\([^)]*,\s*[1-9])",
            content_lower,
        ),
        20,
        f"box_shadow_count={content_lower.count('box-shadow')}",
    )
    add_check(
        checks,
        "restraint",
        "restrained_radius",
        not radius_values or max(radius_values) <= 16,
        15,
        f"max_radius={max(radius_values) if radius_values else 0}",
    )
    semantic_spans = [
        span
        for span in soup.find_all("span")
        if "font-weight" in span.get("style", "")
        and "font-size" not in span.get("style", "")
        and "margin-right" not in span.get("style", "")
    ]
    emphasized = len(soup.find_all(["strong", "blockquote"])) + len(semantic_spans)
    prose_blocks = max(1, len(soup.find_all(["p", "li"])))
    add_check(
        checks,
        "restraint",
        "limited_emphasis",
        emphasized <= max(10, int(prose_blocks * 0.5)),
        10,
        f"emphasis={emphasized}, prose_blocks={prose_blocks}",
    )
    add_check(
        checks,
        "readability",
        "moderate_text_contrast",
        not low_contrast_elements,
        20,
        f"contrast_ratio_below_3={low_contrast_elements}",
    )

    styles_by_tag: dict[str, set[str]] = defaultdict(set)
    missing_inline = []
    styled_targets = {
        "section",
        "span",
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "strong",
        "em",
        "ul",
        "ol",
        "li",
        "blockquote",
        "pre",
        "code",
        "a",
        "img",
        "table",
        "th",
        "td",
        "hr",
    }
    for tag in all_tags:
        if tag.name in styled_targets:
            style = tag.get("style", "").strip()
            if not style:
                missing_inline.append(tag.name)
            else:
                styles_by_tag[tag.name].add(style)
    stable_component_tags = {
        "h2",
        "h3",
        "h4",
        "ul",
        "ol",
        "li",
        "blockquote",
        "pre",
        "img",
        "table",
        "th",
        "td",
        "hr",
    }
    inconsistent = {
        name: len(values)
        for name, values in styles_by_tag.items()
        if name in stable_component_tags and len(values) > 1
    }
    body_paragraph_styles = {
        tag.get("style", "")
        for tag in body_paragraphs
        if 15
        <= (
            pixel_value(parse_style(tag.get("style", "")).get("font-size", ""))
            or 0
        )
        <= 16
        and (
            numeric_value(parse_style(tag.get("style", "")).get("line-height", ""))
            or 0
        )
        >= 1.75
        and tag.parent
        and tag.parent.name != "blockquote"
        and tag.parent.name != "li"
        and not (
            tag.parent.name == "section"
            and tag.parent.get("style", "").find("margin:28") != -1
        )
    }
    if len(body_paragraph_styles) > 1:
        inconsistent["body_paragraph"] = len(body_paragraph_styles)
    add_check(
        checks,
        "consistency",
        "inline_styles_complete",
        not missing_inline,
        35,
        f"missing_inline_styles={missing_inline[:10]}",
    )
    add_check(
        checks,
        "consistency",
        "repeated_components_match",
        not inconsistent,
        35,
        f"inconsistent_style_counts={inconsistent}",
    )
    duplicate_style = bool(re.search(r"<[^>]+\sstyle=[^>]+\sstyle=", content, re.I))
    add_check(
        checks,
        "consistency",
        "no_duplicate_style_attributes",
        not duplicate_style,
        20,
        f"duplicate_style_attributes={duplicate_style}",
    )
    add_check(
        checks,
        "consistency",
        "stable_spacing_tokens",
        len(set(heading_spacing)) <= 3,
        10,
        f"heading_spacing_tokens={sorted(set(heading_spacing), key=str)}",
    )

    forbidden_tags = [
        tag.name
        for tag in all_tags
        if tag.name in {"style", "script", "iframe", "form", "input", "button"}
    ]
    unsafe_attrs = []
    unsafe_urls = []
    fixed_dimensions = []
    zero_line_heights = []
    nonportable_alignments = []
    custom_fonts = []
    dark_mode_fragile_css = []
    invisible_editor_controls = []
    for tag in all_tags:
        style_map = parse_style(tag.get("style", ""))
        width = style_map.get("width")
        height = style_map.get("height")
        line_height = style_map.get("line-height")
        text_align = style_map.get("text-align")
        if width and width not in {"auto", "100%", "inherit", "initial", "unset"}:
            fixed_dimensions.append(f"{tag.name}:width={width}")
        if height and height not in {"auto", "100%", "inherit", "initial", "unset"}:
            fixed_dimensions.append(f"{tag.name}:height={height}")
        if line_height is not None and (numeric_value(line_height) or 0) <= 0:
            zero_line_heights.append(f"{tag.name}:line-height={line_height}")
        if text_align in {"start", "end"}:
            nonportable_alignments.append(f"{tag.name}:text-align={text_align}")
        if "font-family" in style_map:
            custom_fonts.append(f"{tag.name}:font-family={style_map['font-family']}")
        if (
            "!important" in tag.get("style", "").lower()
            or style_map.get("position") in {"absolute", "fixed"}
            or "transform" in style_map
        ):
            dark_mode_fragile_css.append(f"{tag.name}:{tag.get('style', '')}")
        if tag.name == "img" and numeric_value(style_map.get("opacity", "1")) == 0:
            invisible_editor_controls.append("img:opacity=0")
        if style_map.get("caret-color") in {
            "transparent",
            "rgba(0,0,0,0)",
            "rgba(0, 0, 0, 0)",
        }:
            invisible_editor_controls.append(
                f"{tag.name}:caret-color={style_map['caret-color']}"
            )
        for attribute, value in tag.attrs.items():
            if attribute in {"class", "id"} or attribute.lower().startswith("on"):
                unsafe_attrs.append(f"{tag.name}:{attribute}")
            if attribute in {"href", "src"}:
                raw_value = str(value).strip()
                parsed = urlparse(raw_value)
                if parsed.scheme and parsed.scheme not in {"http", "https", "mailto"}:
                    unsafe_urls.append(raw_value)
    fragile_css = [
        feature
        for feature in ("display:grid", "display:flex", "var(--")
        if feature in content_lower.replace(" ", "")
    ]
    pre_elements = [str(tag)[:160] for tag in soup.find_all("pre")]
    same_tag_depth = maximum_same_tag_depth(all_tags)
    block_tags = {
        "section",
        "div",
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "ul",
        "ol",
        "li",
        "blockquote",
        "pre",
        "table",
    }
    invalid_leaf_nodes = []
    for tag in soup.find_all("span", attrs={"leaf": True}):
        if tag.find(list(block_tags)):
            invalid_leaf_nodes.append("span[leaf] contains a block element")
    for tag in soup.find_all("section", attrs={"nodeleaf": True}):
        disallowed = [
            child.name
            for child in tag.find_all(recursive=False)
            if child.name not in {"img"}
        ]
        if disallowed:
            invalid_leaf_nodes.append(
                f"section[nodeleaf] contains {sorted(set(disallowed))}"
            )
    svg_begin_issues = []
    for animate in soup.find_all("animate"):
        begin = str(animate.get("begin", "")).lower()
        if "touchstart" in begin and "click" not in begin:
            svg_begin_issues.append(begin)
    data_no_dark_scope_issues = []
    for container in soup.find_all(attrs={"data-no-dark": True}):
        styled_descendants = [
            descendant.name
            for descendant in container.find_all(True)
            if descendant.get("style", "").strip()
        ]
        if styled_descendants:
            data_no_dark_scope_issues.append(
                f"{container.name}:styled_descendants={styled_descendants[:8]}"
            )
    fixed_svg_colors = []
    dark_svg_colors = {
        "black",
        "#000",
        "#000000",
        "rgb(0,0,0)",
        "rgb(0, 0, 0)",
        "#191919",
    }
    for svg in soup.find_all("svg"):
        for node in [svg, *svg.find_all(True)]:
            declarations = parse_style(node.get("style", ""))
            for attribute in ("fill", "stroke"):
                value = str(
                    node.get(attribute) or declarations.get(attribute) or ""
                ).strip().lower()
                if value in dark_svg_colors:
                    fixed_svg_colors.append(
                        f"{node.name}:{attribute}={value}"
                    )
    add_check(
        checks,
        "wechat_compatibility",
        "safe_tags",
        not forbidden_tags,
        30,
        f"forbidden_tags={forbidden_tags}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "safe_attributes",
        not unsafe_attrs,
        25,
        f"unsafe_attributes={unsafe_attrs}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "safe_urls",
        not unsafe_urls,
        20,
        f"unsafe_urls={unsafe_urls}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "inline_css_only",
        "<style" not in content_lower and not soup.find_all(class_=True),
        15,
        "No style blocks or class-dependent styling.",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "no_fragile_layout_css",
        not fragile_css,
        10,
        f"fragile_css={fragile_css}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "no_fixed_dimensions",
        not fixed_dimensions,
        15,
        f"fixed_dimensions={fixed_dimensions}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "positive_line_height",
        not zero_line_heights,
        15,
        f"zero_line_heights={zero_line_heights}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "portable_text_alignment",
        not nonportable_alignments,
        10,
        f"nonportable_alignments={nonportable_alignments}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "no_pre_elements",
        not pre_elements,
        15,
        f"pre_elements={pre_elements}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "same_tag_nesting_limit",
        same_tag_depth <= 15,
        15,
        f"maximum_same_tag_depth={same_tag_depth}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "editor_leaf_node_contracts",
        not invalid_leaf_nodes,
        10,
        f"invalid_leaf_nodes={invalid_leaf_nodes}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "platform_default_font",
        not custom_fonts,
        15,
        f"custom_fonts={custom_fonts}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "dark_mode_safe_css",
        not dark_mode_fragile_css,
        15,
        f"dark_mode_fragile_css={dark_mode_fragile_css}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "editor_controls_remain_visible",
        not invisible_editor_controls,
        10,
        f"invisible_editor_controls={invisible_editor_controls}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "cross_device_svg_trigger",
        not svg_begin_issues,
        10,
        f"svg_begin_issues={svg_begin_issues}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "data_no_dark_scope",
        not data_no_dark_scope_issues,
        10,
        f"data_no_dark_scope_issues={data_no_dark_scope_issues}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "svg_uses_adaptive_color",
        not fixed_svg_colors,
        15,
        f"fixed_dark_svg_colors={fixed_svg_colors}",
    )
    add_check(
        checks,
        "wechat_compatibility",
        "background_image_text_awareness",
        not background_image_text_elements,
        0,
        f"background_images_beneath_text={background_image_text_elements}",
    )

    scores = {dimension: 100 for dimension in DIMENSIONS}
    for check in checks:
        scores[check["dimension"]] -= check["penalty"]
    scores = {key: max(0, value) for key, value in scores.items()}
    failed_dimensions = [
        dimension for dimension, score in scores.items() if score < threshold
    ]
    warnings = [
        check["evidence"]
        for check in checks
        if not check["passed"] and check["penalty"] < 20
    ]
    manual_review = []
    if soup.find("img"):
        manual_review.append(
            "Review images for embedded text and transparent areas against both "
            "light and #191919 dark backgrounds."
        )
    if background_image_text_elements:
        manual_review.append(
            "Review text placed over background images because Dark Mode preserves "
            "the light-mode text color and may apply image complementing."
        )
    return {
        "status": "passed" if not failed_dimensions else "blocked",
        "threshold": threshold,
        "scores": scores,
        "failed_dimensions": failed_dimensions,
        "warnings": warnings,
        "manual_review": manual_review,
        "checks": checks,
    }

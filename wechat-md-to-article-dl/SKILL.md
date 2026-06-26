---
name: wechat-md-to-article-dl
description: Convert Chinese or English Markdown into restrained, premium, mobile-first HTML for WeChat Official Accounts, then audit, automatically repair, and optionally validate it against WeChat's official editor structure API. Use this skill whenever a user asks to format, beautify, typeset, convert, restyle, validate, or prepare Markdown/HTML for a WeChat article, especially when they mention advanced CSS, magazine style, card layout, inline CSS, mobile readability, Dark Mode, editor plugin compatibility, technical articles, cognition essays, business/wealth content, or health education.
compatibility: Python 3.10+ with markdown, PyYAML, beautifulsoup4, and bleach.
---

# Markdown to WeChat Article

Create WeChat-ready HTML whose polish comes from design order: restraint, clarity,
whitespace, consistency, and hierarchy. Decoration must support comprehension.

## Default workflow

1. Inspect the Markdown structure and frontmatter.
2. Select a theme from `minimal`, `tech`, `cognition`, `wealth`, or `health`.
3. Convert Markdown with `scripts/convert.py`.
4. Read the generated quality report.
5. Treat any quality dimension below 90 as a failed layout.
6. Let the converter rerender in strict mode, then inspect the second report.
7. Run the official structure verifier only when the user explicitly requests it.
8. **Open** the generated HTML in browser for visual inspection: `open <output-path>`
9. Return the HTML path, selected theme, five scores, official validation status,
   automated warnings, and image-related manual review items.

Do not manually recreate the template when the bundled converter can perform the
transformation. The script makes output deterministic and keeps future runs consistent.

## Quick start

```bash
python3 scripts/convert.py article.md \
  --output article.wechat.html \
  --theme auto
```

### Cover image generation

After converting, generate a social-media-ready cover for the article:

```bash
python3 scripts/draw_cover.py \
  --image /tmp/photo.jpg \
  --title "Article Title" \
  --subtitle "Subtitle text" \
  --tagline "Tagline" \
  --output /path/to/cover.png
```

See `scripts/draw_cover.py --help` for all options.
Read `references/image-text-rendering.md` for font selection, centering,
shadow/outline, and platform-specific pitfalls (macOS STHeiti vs Songti,
PingFang TTC limitation).

Choose a theme explicitly when the article domain is known:

```bash
python3 scripts/convert.py article.md \
  --output article.wechat.html \
  --theme health \
  --quality-threshold 90
```

Audit existing HTML without converting Markdown:

```bash
python3 scripts/audit.py article.wechat.html \
  --report article.audit.json \
  --threshold 90
```

Explicitly send the final HTML to WeChat's official structure verifier:

```bash
python3 scripts/convert.py article.md \
  --output article.wechat.html \
  --theme auto \
  --official-check
```

`--official-check` transmits the complete generated HTML to
`mp.weixin.qq.com`. It is opt-in because drafts may contain private or
unpublished content.

## Input contract

| Field | Required | Notes |
|---|---:|---|
| Markdown path | Yes | UTF-8 `.md` file |
| Output path | Yes | HTML fragment suitable for WeChat |
| `--theme` | No | `auto`, `minimal`, `tech`, `cognition`, `wealth`, `health` |
| `--title` | No | Overrides frontmatter title. **Must be the full article title** — an abbreviated title (e.g. `--title "恒生科技"` instead of the complete 30‑char title) produces "未命名文章" or a truncated h1 in the WeChat draft. When omitted and no frontmatter `title:` exists, the h1 defaults to "未命名文章". **Always pass the exact published title as `--title`.** |
| `--quality-threshold` | No | Defaults to 90 for every quality dimension |
| `--report` | No | Defaults to `<output>.report.json` |
| `--official-check` | No | Opt-in upload to WeChat's official structure verifier |
| `--official-timeout` | No | Official verifier timeout in seconds; defaults to 15 |

## Highlight and callout syntax

Mark key content types with special markers for sophisticated visual emphasis.

### Inline highlights

Wrap text with one of these marker pairs to add bold or coloured emphasis:

| Marker | Purpose | Visual |
|---|---|---|
| `==text==` | Core concept, key definition | **Bold + accent colour** |
| `^^text^^` | Key viewpoint, argument | **Bold + title colour** |
| `!!text!!` | Emphasis, important point | **Bold** only |

Example:
```markdown
The core idea is ==OPC = decision-maker + AI tool chain==.
^^This changes how individuals approach business.^^
!!Always validate demand before building a product!!
```

### Math formulas

Display math delimited by `$$...$$` or `\[...\]` is converted to a WeChat-stable
styled `<section>` card with the formula rendered in readable text:

```markdown
$$
PE = \frac{price}{earnings}
$$

\[
ROI = \frac{gain}{cost} \times 100\%
\]
```

Common LaTeX commands are replaced with Unicode equivalents:

| Command | Rendered as |
|---------|------------|
| `\frac{a}{b}` | `a / b` |
| `\times` | `×` |
| `\approx` | `≈` |
| `\rightarrow` | `→` |
| `\sum` | `∑` |
| `\text{...}` | text content only |

Inline math `$...$` and `\(...\)` are NOT handled — use `$$` or `\[` for all
formulas that need rendering.

Content inside `` ``` `` code fences is protected and not converted.

### Callout blocks

Fence a block with `:::type` / `:::` to get a coloured left-border card:

| Type | Purpose | Border colour |
|---|---|---|
| `:::problem` | Problem statement or challenge | Red/muted red |
| `:::strategy` | Strategy or approach | Green/teal |
| `:::thinking` | Thinking method or mental model | Blue/purple |
| `:::key` | Core insight or takeaway | Theme accent |

Optionally add a title on the same line as the `:::` marker:

```markdown
:::problem 需求验证的陷阱
很多创业者跳过需求直接做产品。
而市场的反应往往与预期完全不同。
:::

:::strategy
Start with an MVP and test willingness to pay.
:::

:::thinking 最小可行性思维
MVP 的关键不是"完整"，而是"能否换取真实支付"。
:::
```

🔴 **CRITICAL — missing `:::` closing breaks all subsequent content**: Every callout block MUST end with a standalone `:::` line on its own. If the closing marker is omitted, the preprocessor in `scripts/highlighting.py` silently treats every line after the opening `:::` as callout content, consuming all remaining sections (headings, tables, lists, blockquotes) into the callout `<section>` element. These sections then render as raw markdown text in the WeChat article — `## 二、...` shows literally, not as an `<h2>` heading. **The quality score report (all 100) does NOT catch this failure.**

`scripts/highlighting.py` now includes `_auto_close_callouts()` as a safety net: it scans for unclosed `:::` blocks before processing and inserts `:::` before each subsequent `:::type` opener, plus at EOF for any remaining open block. This prevents catastrophic document-wide breakage. However, the auto-close cannot reconstruct the author's intended boundary — all content from the unclosed opener to the auto-inserted closer becomes part of the callout card, which is rarely correct.

**Always close `:::` blocks properly.** The safety net prevents total document loss but cannot fix boundary errors. Verify the output HTML contains `<h2>` tags for every section heading, not raw `##` markdown.

Supported frontmatter keys include `title`, `author`, `date`, `summary`,
`description`, `type`, `category`, and `tags`.

## Output contract

The command prints JSON and writes the same audit data to the report:

```json
{
  "status": "passed",
  "output": "/absolute/path/article.wechat.html",
  "report": "/absolute/path/article.wechat.html.report.json",
  "theme": "tech",
  "auto_repaired": false,
  "scores": {
    "visual_hierarchy": 100,
    "readability": 100,
    "restraint": 100,
    "consistency": 100,
    "wechat_compatibility": 100
  },
  "official_validation": {
    "status": "skipped",
    "is_valid": null,
    "reason": "not_requested",
    "violations": [],
    "violation_count": 0,
    "transport": null
  },
  "manual_review": []
}
```

## Design rules

- Use one accent color and a small neutral palette.
- Keep body text at 15–16px with 1.75–1.9 line height.
- Keep article padding at 16–20px and section spacing at 24–36px.
- Use light borders and restrained radius; avoid loud gradients and heavy shadows.
- For inline emphasis, always prefer the simplest treatment: bold weight and/or
  colour changes. Background pills, tinted highlights, and other visual effects
  add palette complexity and harm Dark Mode stability without improving readability.
- Emphasize only genuine judgments, not every sentence.
- Prefer structural modules: conclusion, problem, comparison, framework, checklist,
  resources, and synthesis.
- Give the reader a ten-second path through title, summary, key judgment, and sections.
- Use inline CSS only. Avoid external CSS, `<style>`, scripts, event handlers, layout
  systems that WeChat may strip, and unsafe URL schemes.
- Lists must use `<div>` + `•` format, NOT `<ul>`, `<ol>`, or `<li>`.
  WeChat's editor breaks standard HTML list elements — they lose indentation, spacing,
  and bullet markers. The converter&#x27;s `apply_highlight_styles()` post-process converts
  every `<ul>`, `<ol>`, and `<li>` in the rendered HTML into `<div>` elements with
  `•` bullet markers and per-item inline styles. This applies both to lists inside
  `::: callout` blocks (handled by `_callout_inner_to_html()`) and to regular markdown
  lists in the article body (handled by the global post-processor).
  **Do NOT write `<ul>`/`<ol>`/`<li>` directly in source markdown** — the converter
  already handles conversion automatically.\
- **Long, CSS-adjusted text blocks must be visually enhanced, not simply simplified.**
  When a paragraph carries complex content (multi-clause argument, layered data,
  conditional logic) that was deliberately styled for readability, the converter
  must preserve its information density by adding visual structure: break it into
  multiple shorter paragraphs, extract key claims into bullet lists, wrap core
  judgments in blockquotes or callout cards, and use bold anchors for signposts.
  Simply stripping the CSS and leaving a 500‑character wall of plain text destroys
  the original context. If the enhanced version exceeds a 90 readability score
  despite higher paragraph density, that is correct — the original 100‑score plain
  wall was an artifact of aggressive simplification, not genuine readability.
- Do not set `font-family`; preserve the platform's default font.
- Do not use fixed `width` or `height`, zero line height, `text-align:start/end`,
  `position:absolute/fixed`, transforms, or `!important`.
- Render fenced code as a wrapping `section > code` block, not `<pre>`.
- Keep same-tag nesting at 15 levels or fewer.
- Favor solid container backgrounds and moderate contrast for Dark Mode. Decorative
  gradients without text are allowed; text-on-gradient is not.
- Keep shared backgrounds on a structural container rather than repeating them on
  each text node.
- Treat `data-no-dark` as applying only to the marked node. Inline styles on its
  descendants are still transformed.
- Use SVG `currentColor` for black or text-like line art that must adapt to Dark Mode.
- Put images containing text, transparent images, and text over background images
  through manual light/dark review because HTML inspection cannot prove legibility.

Read [references/list-rendering-wechat.md](references/list-rendering-wechat.md) for why
lists use `<div>`+`•` instead of `<ul>`/`<ol>`/`<li>` and how the two conversion paths
(callout inner lists + global body lists) work together.
Read [references/callout-close-bug.md](references/callout-close-bug.md) for the
debugging transcript of unclosed `:::` blocks and reading-path cap bugs — consult
when the output shows raw markdown despite perfect quality scores.
Read [references/callout-list-rendering.md](references/callout-list-rendering.md)
for the WeChat-compatible list rendering inside callout blocks (`div`+`•`+`strong`,
no `ul`/`ol`/`li`).
Read [references/callout-inner-lists.md](references/callout-inner-lists.md) for the
reason raw markdown lists appear inside callout cards and the `_callout_inner_to_html`
workaround — consult when numbered lists or bold text inside `:::thinking` blocks
render as raw text instead of styled divs.
Read [references/design-system.md](references/design-system.md) when changing themes,
spacing, typography, cards, or article-type behavior.
Read [references/wechat-editor-plugin-spec.md](references/wechat-editor-plugin-spec.md)
when changing tags, CSS compatibility checks, Dark Mode behavior, or official validation.
Read [references/wechat-highlighting-strategy.md](references/wechat-highlighting-strategy.md)
for the full WeChat CSS compatibility table and highlight technique guide — consult
when tuning emphasis styles or debugging highlight rendering in WeChat.

## Theme selection

| Theme | Best for | Visual direction |
|---|---|---|
| `minimal` | General and mixed topics | White, graphite, quiet gray |
| `tech` | AI, software, architecture | Deep blue-gray with cool blue accent |
| `cognition` | Essays, learning, self-development | Warm paper, ink, muted brown |
| `wealth` | Business, finance, strategy | Ivory, deep green, restrained gold |
| `health` | Health education and wellness | Soft green-gray, calm blue-green |

With `--theme auto`, the converter uses frontmatter first and article vocabulary second.
If the signal is ambiguous, use `minimal`.

## Source structure guidance

The converter does not invent claims. Improve the ten-second reading path by providing:

```markdown
---
title: Article title
summary: One sentence explaining the reader value
type: tech
---

> The single most important judgment.

## First major question

...
```

When at least two level-two headings exist, the converter creates a section
map from every `##` label (no cap — all chapters appear). It does not fabricate
an executive summary.

## Quality gate

The audit produces five scores:

1. `visual_hierarchy`: title, heading, body, and spacing hierarchy.
2. `readability`: mobile font size, line height, width, paragraph rhythm, and contrast.
3. `restraint`: controlled colors, borders, radius, shadows, and emphasis.
4. `consistency`: repeated elements share the same visual language.
5. `wechat_compatibility`: inline CSS, safe tags and URLs, official editor constraints,
   Dark Mode safety, adaptive SVG, scoped opt-outs, and no fragile features.

Every score must meet the threshold. A low score means the output is not ready merely
because it looks plausible in a desktop browser.

## Failure handling

| Failure | Response |
|---|---|
| Missing dependency | Report the exact package; do not silently use a weaker parser |
| Invalid or empty Markdown | Stop with structured JSON and a nonzero exit code |
| Unsafe raw HTML | Strip unsafe tags, event attributes, classes, IDs, and URL schemes |
| First audit below threshold | Rerender using strict mode and audit again |
| Second audit below threshold | Return `blocked` with failed dimensions and report path |
| Official verifier rejects HTML | Return `blocked` with `invalid_info`; repair locally and retry |
| Official verifier unavailable | Return `blocked` with status `error`; keep the local report |
| Image or background-image uncertainty | Keep the automated score and add a `manual_review` item |
| Unknown theme | Stop and list supported themes |

## Verification

Run:

```bash
python3 -m unittest discover -s tests
python3 scripts/convert.py evals/files/technical.md \
  --output /tmp/technical.wechat.html \
  --theme tech
python3 scripts/audit.py /tmp/technical.wechat.html \
  --report /tmp/technical.audit.json
python3 scripts/audit.py /tmp/technical.wechat.html \
  --report /tmp/technical.official.json \
  --official-check
```

Before claiming completion, confirm:

- all five scores are at least 90;
- no `<style>`, `<script>`, `class`, `id`, or event attributes remain;
- no `font-family`, `<pre>`, fixed dimensions, zero line height, fragile positioning,
  transforms, or `!important` remain;
- dangerous links and embedded raw HTML were removed;
- the output preserves headings, lists, blockquotes, code, tables, images, and links;
- `manual_review` has been completed when images or background images are present;
- the official verifier passes when the user authorized `--official-check`;
- the result remains readable at a narrow mobile width.
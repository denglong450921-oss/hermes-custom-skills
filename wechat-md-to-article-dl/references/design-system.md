# WeChat Premium Design System

Use this reference when changing visual tokens, theme behavior, or quality thresholds.

## Design thesis

Premium WeChat typography is restrained, clear, spacious, unified, and hierarchical.
Design should make the argument easier to understand, not advertise the designer.

## Core measurements

| Element | Recommended range |
|---|---|
| Body font | 15–16px |
| Body line height | 1.75–1.9 |
| Small annotation | 12–13px |
| Primary title | 22–28px |
| Section title | 18–21px |
| Card title | 16–18px |
| Article side padding | 16–20px |
| Section spacing | 24–36px |
| Card padding | 18–24px |
| Paragraph spacing | 12–16px |
| Card radius | 8–16px |

## Restraint rules

- Keep one accent color and a compact neutral palette.
- Prefer a subtle border to a strong shadow.
- Avoid saturated rainbow palettes, fluorescent highlighting, loud gradients, and
  oversized radius.
- Limit high-emphasis treatments to the few judgments that define the article.
- Reuse spacing and component styles rather than styling each module independently.
- Highlighted content (`==`, `^^`, `!!`) uses bold weight and colour changes
  (not background pills). Use them sparingly — aim for at most 10–15% of
  prose blocks.
- Callout cards (`:::problem`, `:::strategy`, `:::thinking`, `:::key`) use
  coloured left borders and tinted backgrounds. The visual difference comes
  from the border colour; card layout (padding, radius, margin) stays
  consistent across all types so the reader learns the pattern once.
- Limit callout blocks to 1–2 per section. Too many callouts in a row
  devalue the visual signal.

## Ten-second reading path

The opening should reveal:

1. what the article is about;
2. the core value or judgment;
3. why the reader should continue;
4. the major sections.

Use frontmatter `summary`, an opening blockquote, and meaningful `h2` headings to
provide this path without generating unsupported claims.

## Article-type strategies

### Technology

Use deep blue-gray, cool blue accent, clear steps, code blocks, comparison tables,
architecture explanations, error cases, and checklists.

### Cognition

Use warm paper and ink colors, generous whitespace, quotations, opposing viewpoints,
transfer frameworks, and action lists. Avoid slogans and emotional overstatement.

### Wealth and business

Use ivory, deep green, and restrained muted gold. Prioritize trust, assumptions, risks,
case analysis, and execution. Avoid bright gold, red promotional styling, and promises.

### Health

Use soft green-gray and calm blue-green. Prioritize evidence, misconception correction,
boundaries, actionable guidance, and references. Avoid fear, certainty beyond evidence,
and visual urgency that resembles advertising.

## WeChat constraints

- Use inline CSS because style blocks and selectors may be removed.
- Avoid JavaScript, event handlers, forms, iframes, and external stylesheets.
- Avoid CSS Grid, flex-dependent layouts, fixed or absolute positioning, transforms,
  `!important`, and CSS variables.
- Preserve the platform default font; do not set `font-family`.
- Avoid fixed `width` and `height`; use responsive width, `max-width`, and `height:auto`.
- Keep line height positive and use `left`, `center`, or `right` rather than
  `text-align:start/end`.
- Do not emit `<pre>`; use a wrapping `section > code` block with
  `white-space:pre-wrap`.
- Keep identical-tag nesting at 15 levels or fewer.
- For Dark Mode, prefer solid container backgrounds, moderate contrast, transparent
  image assets with light and dark contrast, and SVG colors based on `currentColor`.
- Allow a decorative gradient only when its container has no text. Put shared
  backgrounds on one structural container instead of repeating them on each text node.
- Remember that `data-no-dark` affects only the marked node; inline-styled descendants
  are still transformed.
- Treat images containing text, transparent PNG/WebP assets, and text over CSS
  background images as manual light/dark review items.
- Keep tables readable with fixed layout, compact text, and word wrapping.
- Use HTTP(S) images and links; remove unsafe URL schemes.

See [wechat-editor-plugin-spec.md](wechat-editor-plugin-spec.md) for the official
editor rules and opt-in structure verification API.

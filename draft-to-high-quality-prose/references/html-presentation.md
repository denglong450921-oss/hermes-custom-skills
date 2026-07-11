# HTML Presentation Mode

Use this reference when the user asks to convert, enhance, redesign, polish, or output prose as HTML. The goal is a best-in-class article page: a quiet reading environment with modern navigation, selective highlights, and enough visual hierarchy for both scanning and long-form reading.

The page should feel like a carefully typeset publication, not a dashboard full of competing cards.

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Content Rules](#content-rules)
- [Progressive Disclosure](#progressive-disclosure)
- [Recommended Structure](#recommended-structure)
- [Layout Specifications](#layout-specifications)
- [Typography](#typography)
- [English Text and Long Strings](#english-text-and-long-strings)
- [Vertical Rhythm](#vertical-rhythm)
- [Color and Contrast](#color-and-contrast)
- [Summary and Table of Contents](#summary-and-table-of-contents)
- [Reading Prompt Contract](#reading-prompt-contract)
- [Cards, Callouts, and Highlights](#cards-callouts-and-highlights)
- [Figures, Quotes, Lists, Tables, and Code](#figures-quotes-lists-tables-and-code)
- [Links, Sidebar, and Reading Utilities](#links-sidebar-and-reading-utilities)
- [Accessibility and Performance](#accessibility-and-performance)
- [Final Takeaways](#final-takeaways)
- [HTML Requirements](#html-requirements)
- [Acceptance Checklist](#acceptance-checklist)
- [Starter Skeleton](#starter-skeleton)

## Design Philosophy

Design for reading first.

- Let readers understand the article's value within 10 seconds.
- Make long-form reading comfortable for 15-20 minutes.
- Preserve a visible logic path for scanners.
- Keep the article body as the strongest visual element.
- Keep navigation, metadata, sidebars, and related material secondary.
- Use cards for summaries, key conclusions, examples, and special resources; do not wrap every section in a card.

Use this rhythm:

```text
heading -> short orientation -> paragraphs -> evidence/example -> synthesis -> breathing space
```

Avoid placing several visually dominant elements back to back.

## Content Rules

- Preserve all core claims, facts, names, numbers, and nuance.
- Keep the full context needed for comprehension.
- Lightly edit confusing, repetitive, or bloated sentences when they harm reading.
- Remove filler, duplicated transitions, vague throat-clearing, and obvious AI-style scaffolding.
- Do not invent facts, examples, citations, or conclusions.
- Add headings, executive summaries, callouts, tables, and final takeaways only when they clarify the source.
- If the user asks to preserve text exactly, style and structure it without rewriting the prose.

## Progressive Disclosure

Support three reading depths:

1. **10 seconds**: title, subtitle, executive summary, key conclusion.
2. **2 minutes**: headings, highlighted arguments, figures, conclusion.
3. **Full reading**: evidence, examples, reasoning, references, and related material.

The opening screen should answer:

- What is this about?
- Why does it matter?
- What is the main conclusion?
- How is the argument organized?

## Recommended Structure

Use this structure for most long-form article outputs:

```html
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <main>
    <article>
      <header class="article-header"></header>
      <aside class="article-summary"></aside>
      <nav class="table-of-contents"></nav>
      <aside class="reading-tip" aria-labelledby="reading-tip-title"></aside>
      <div class="article-layout">
        <div class="article-content" id="content"></div>
        <aside class="article-sidebar"></aside>
      </div>
      <footer class="article-footer"></footer>
    </article>
  </main>
</body>
```

Recommended article header order:

1. category or series name
2. article title
3. subtitle or one-sentence value proposition
4. author, date, update status, reading time when available
5. optional cover image
6. executive summary

Do not insert ads, recommendations, or oversized sharing controls between the title and opening paragraph.

## Layout Specifications

Reading width matters more than screen width.

Recommended article widths:

- General editorial content: `680-760px`
- Technical articles with code: `720-820px`
- Chinese-heavy content: `680-740px`
- Avoid body paragraphs wider than `820px`

Target line length:

- English: about `55-75` characters per line.
- Chinese: about `28-38` full-width characters per line.
- Good default: about `65` English characters or `32` Chinese characters.

Article alignment:

- Treat the article text column as the alignment anchor.
- Header, subtitle, metadata, executive summary, article body, and final footer/takeaways must share the same left edge on desktop.
- **Center the article column in the viewport.** Do not push content with a left margin to clear a fixed TOC. Instead, let the TOC float beside the centered column using `calc()` positioning.
- If a TOC or reading utility is fixed outside the article column, position it relative to the centered column (not relative to the viewport edge).

Desktop with sidebar:

```css
.article-layout {
  max-width: 1180px;
  margin-inline: auto;
  display: grid;
  grid-template-columns: minmax(0, 740px) 240px;
  gap: 72px;
  align-items: start;
}
```

Desktop with fixed side rails (centered article column):

```css
:root {
  --content-width: 740px;
  --toc-width: 248px;
}

.reading-tip {
  width: min(100%, var(--content-width));
  margin: 32px auto 0;
  padding: 18px 20px;
  background: var(--quote-bg);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
}

@media (min-width: 1180px) {
  main {
    max-width: var(--content-width);
    margin-inline: auto;
  }

  .article-header,
  .article-summary,
  .article-content,
  .article-footer {
    width: min(100%, var(--content-width));
    margin-inline: auto;
  }

  .table-of-contents {
    position: fixed;
    top: 104px;
    left: calc(50% - var(--content-width) / 2 - var(--toc-width) - 44px);
    width: var(--toc-width);
    max-height: calc(100vh - 128px);
    overflow-y: auto;
  }
}

@media (min-width: 1500px) {
  .reading-tip {
    position: fixed;
    top: 104px;
    right: calc(50% - var(--content-width) / 2 - 260px);
    width: 220px;
    margin: 0;
    max-height: calc(100vh - 128px);
    overflow-y: auto;
  }
}
```

The key principle: **center the article column in the viewport, then position the TOC and reading tip relative to the centered column** using `calc()`. Do not push the main content with a `margin-left` to clear the TOC — the TOC should float beside the centered column without shifting it.

Responsive padding:

| Viewport | Horizontal article padding |
|---|---:|
| Under 480px | 18-20px |
| 480-767px | 24px |
| 768-1199px | 32-40px |
| 1200px+ | centered max-width |

Mobile:

- Use one column.
- Move sidebars below or above the article.
- Do not allow horizontal page scrolling.
- Keep body text at least `16-17px`.
- Keep touch targets at least `44 x 44px`.

## Typography

Use no more than two font families.

Mixed Chinese and English:

```css
font-family:
  Inter,
  "SF Pro Text",
  "PingFang SC",
  "Hiragino Sans GB",
  "Microsoft YaHei",
  system-ui,
  sans-serif;
```

More literary article body:

```css
font-family:
  "Source Serif 4",
  "Noto Serif SC",
  "Songti SC",
  Georgia,
  serif;
```

Recommended body typography:

- Chinese: `17-18px`, line-height `1.75-1.9`.
- English: `18-20px`, line-height `1.6-1.75`.
- Paragraph spacing: `1.1-1.4em`.
- Metadata: `13-15px`.
- Keep `letter-spacing: 0`; avoid negative tracking.

Practical heading scale:

```css
h1 {
  font-size: clamp(2.25rem, 5vw, 4.25rem);
  line-height: 1.08;
  letter-spacing: 0;
  text-wrap: balance;
}

h2 {
  font-size: clamp(1.65rem, 3vw, 2.25rem);
  line-height: 1.25;
}

h3 {
  font-size: clamp(1.25rem, 2vw, 1.55rem);
  line-height: 1.35;
}
```

Use a limited weight hierarchy:

- Title: `700-800`
- H2: `650-750`
- H3: `600-700`
- Body: `400-450`
- Strong emphasis: `600-650`

Avoid bolding entire paragraphs.

## English Text and Long Strings

English prose should read vertically with the rest of the article. Do not place ordinary sentences, quotations, vocabulary examples, or before/after rewrites in `<pre><code>` merely to create a styled box. That treatment preserves whitespace and often forces readers to scroll sideways.

Use semantic prose elements and let them wrap:

```html
<figure class="sentence-feature">
  <figcaption>Original sentence</figcaption>
  <blockquote class="english-text" lang="en">
    A complete English sentence remains visible and wraps naturally at word boundaries.
  </blockquote>
</figure>
```

```css
.english-text {
  max-width: 100%;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: normal;
  hyphens: none;
}

.sentence-feature,
.comparison-grid > *,
.bilingual-row > * {
  min-width: 0;
}

.unbroken-token {
  overflow-wrap: anywhere;
  word-break: break-word;
}
```

Apply `overflow-wrap: anywhere` only to strings that may have no spaces, such as URLs, hashes, filenames, or generated identifiers. Normal English prose should prefer natural word boundaries.

For language-learning or bilingual pages, use the shared featured-sentence, comparison, bilingual-row, and unbroken-token patterns in `english-text-display.md`. The canonical rendered reference is `../assets/english-text-display-examples.html`.

English reading-content rules:

- Keep the complete sentence visible without an internal horizontal scrollbar.
- Avoid clipping, ellipsis, fixed-height text boxes, and `white-space: nowrap`.
- Use `<p lang="en">` for model sentences and `<blockquote lang="en">` for quotations.
- Preserve whole words with `hyphens: none` in language-learning examples; automatic hyphenation can make spelling and phrase boundaries harder to study.
- Add `min-width: 0` to grid and flex children that contain text.
- Collapse two-column comparisons to one column on narrow screens.
- Keep code behavior separate: exact source code may scroll horizontally when wrapping would damage meaning.

## Vertical Rhythm

Use spacing based on 4px or 8px increments.

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
}
```

Recommended article spacing:

| Element | Space before | Space after |
|---|---:|---:|
| Paragraph | 0 | 1.2em |
| H2 | 3.5em | 1em |
| H3 | 2.5em | 0.75em |
| Image | 2.5em | 2.5em |
| Blockquote | 2em | 2em |
| List | 1em | 1.5em |
| Code block | 2em | 2em |
| Major section | 64-96px | - |

A heading should visually belong to the content below it: space above should be larger than space below.

## Color and Contrast

Use one primary accent color and at most one semantic highlight color.

Light theme:

```css
:root {
  --page-bg: #f7f7f5;
  --article-bg: #ffffff;
  --text-primary: #1b1b1b;
  --text-secondary: #666666;
  --text-muted: #8a8a8a;
  --border: #e7e7e4;
  --accent: #315efb;
  --accent-soft: #eef2ff;
  --quote-bg: #f5f6f8;
}
```

Dark theme, if requested:

```css
:root[data-theme="dark"] {
  --page-bg: #111214;
  --article-bg: #17181b;
  --text-primary: #ededed;
  --text-secondary: #b2b4b8;
  --text-muted: #85888f;
  --border: #2b2d31;
  --accent: #8ba4ff;
  --accent-soft: #20283f;
  --quote-bg: #1e2024;
}
```

Contrast rules:

- Normal body text: at least `4.5:1`.
- Large text and interactive controls: at least `3:1`.
- Never use light gray for important body text.
- Do not communicate meaning through color alone.

## Summary and Table of Contents

Provide an executive summary for long articles.

Recommended content:

- one core conclusion
- three to five key points
- optional "who this is for"
- optional reading time or difficulty

Design:

- distinct but quieter than the title
- soft background or subtle border
- padding `24-32px`
- no strong shadow
- only one summary module near the beginning

Use a table of contents when:

- the article exceeds roughly `1,500` words
- the article has at least four major sections
- readers may need to return to specific sections

**TOC must always be visible on all screen sizes.** Do not hide it. On narrow screens, render it as an inline card in normal flow (below the summary, above the content). On wide screens, pin it as a fixed left-side rail.

Desktop TOC:

- fixed sidebar
- width `220-260px`
- top offset `96-120px`
- position using `calc()` relative to the centered article column: `left: calc(50% - var(--content-width) / 2 - var(--toc-width) - 36px)`
- current section may be highlighted if implemented simply
- If fixed to the left rail, position it outside the article column and verify it does not overlap the header, article body, footer, or any reading-tip card.
- Use a single article-column anchor so the header, summary card, main text, and footer line up even when the TOC lives in a left rail.

Mobile/narrow TOC:

- render as a bordered card in normal document flow, below the summary and above the first content section
- inline layout: TOC links display horizontally or wrap naturally
- always visible, never collapsed or toggled
- keeps readers oriented without requiring a wide viewport

Always use real anchor links and correct heading IDs.

## Reading Prompt Contract

Every polished HTML reading page includes one visible reading prompt, labeled `阅读提示`, `Reading Prompt`, or an equivalent phrase in the page language. Its job is to orient the next reading action, not to summarize the entire article again.

Good reading prompts may tell the reader to:

- read the original passage once before opening the explanation
- compare two versions and notice one specific structural difference
- keep one guiding question in mind while reading
- scan headings first, then return for evidence or examples
- distinguish a surface phenomenon from the mechanism underneath it

Keep the prompt concise: usually a short heading plus one to three sentences or bullets. Derive it from the actual content; avoid generic instructions such as “read carefully.”

Visibility and placement rules:

- Render the prompt as a semantic `<aside class="reading-tip">` with a labeled heading.
- On wide desktop layouts with sufficient side space, place it in a dedicated right rail outside the article column.
- Below the right-rail breakpoint, keep the same prompt in normal document flow near the summary or table of contents.
- Never hide it with `display: none`, `visibility: hidden`, clipping, a collapsed disclosure, or an off-screen position.
- Do not place it inside the TOC, inside the executive-summary card, or inside another card.
- Keep it independent from the article body so a fixed version cannot cover text while scrolling.

Recommended markup:

```html
<aside class="reading-tip" aria-labelledby="reading-tip-title">
  <h2 id="reading-tip-title">阅读提示</h2>
  <p>先读原文，再看结构拆解；第二遍只追踪每句话如何承接上一句。</p>
</aside>
```

## Cards, Callouts, and Highlights

Use cards only for repeated or framed content:

- key insight cards
- executive summary points
- definition cards
- warning or principle callouts
- final takeaway cards

Card rules:

- card radius at or below `8px`, unless matching an existing design system
- no card inside another card
- no heavy shadows
- no decorative containers around every section
- concise labels such as `Principle`, `Warning`, `Method`, `Takeaway`

Paragraph emphasis:

- Prefer 2-5 sentences per paragraph.
- Break long conceptual blocks into smaller units.
- Avoid single-sentence paragraphs everywhere; reserve them for emphasis.
- Do not justify body text.
- Use left alignment for Chinese and English web content.

Bold text:

- Use bold for conclusions, key terms, contrast, and short scanning phrases.
- Avoid entire bold paragraphs.
- Avoid multiple bold fragments in every sentence.
- Do not combine bold, underline, color, and background on the same phrase.

Highlighting:

```css
mark {
  background: linear-gradient(
    transparent 58%,
    rgba(255, 214, 102, 0.45) 58%
  );
}
```

Highlight sparingly. If everything is highlighted, nothing is.

**Per-paragraph key-point highlights:** For articles where the user has asked for key-point marking, use a dedicated `.key-point` class (distinct from `<mark>`) to highlight the single most valuable sentence in each paragraph. Style it with a subtle treatment — a soft left border, low-opacity background glow, or a `💡` inline marker — so it guides the skim reader without competing with the main flow. Show at most one key-point highlight per paragraph. Skip the highlight when the topic sentence already carries the point clearly.

## Figures, Quotes, Lists, Tables, and Code

Images:

- standard images should match article width
- wide images may use `960-1120px`
- reserve full-bleed images for high-value photography or diagrams
- avoid enlarging low-resolution images
- use meaningful `alt`, explicit `width` and `height`, responsive sources, and lazy loading below the fold

Captions:

```css
figcaption {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.55;
  color: var(--text-muted);
}
```

Quotes:

- Evidence quotes use semantic `blockquote` and `cite`.
- Use a `3px` left border and `20-24px` left padding.
- Pull quotes should be rare: about one per major article, `24-34px`, max width `650-760px`.
- Do not use pull quotes merely to repeat nearby text.

Lists:

- Use lists when items are genuinely parallel.
- Use ordered lists for procedures.
- Avoid turning every group of three points into a card grid.

Tables:

- Use tables only when comparison matters.
- Make header rows distinct.
- Use `12-16px` cell padding.
- Keep table text at least about `14px`.
- Wrap wide tables in `.table-wrapper { overflow-x: auto; }`.

Code:

- Inline code gets subtle background and `5px` radius.
- Code blocks need horizontal scrolling, language label when known, high contrast, `14-16px` font, `1.55-1.7` line-height, and `20-24px` padding.
- Do not force line wrapping by default in code blocks.
- Do not use code blocks for English prose, example sentences, quotations, vocabulary definitions, or rewritten passages. Those should use the wrapping prose patterns above.

## Links, Sidebar, and Reading Utilities

Links must look like links:

```css
.article-content a {
  color: var(--accent);
  text-decoration-line: underline;
  text-decoration-thickness: 0.08em;
  text-underline-offset: 0.18em;
}
```

A sidebar may contain:

- table of contents
- article progress
- author information
- article series navigation
- one restrained call to action

The sidebar must not contain several unrelated promotional cards, and it must not be required for understanding the article.

Fixed side-rail rules:

- **Center the article column.** Position the TOC and reading tip relative to the centered column using `calc()`, not relative to viewport edges. The TOC should float beside the centered column without pushing it.
- Keep the TOC and reading-tip/utility card in separate rails or separate normal-flow blocks; never stack a sticky card under a sticky TOC in the same narrow column if their boxes can overlap while scrolling.
- For wide desktop layouts, use a fixed TOC on the left, centered article column, and visible reading prompt on the right.
- If the right reading tip is fixed, give it its own width and right offset (relative to the centered column); do not place it inside the article content box.
- At narrower desktop and mobile widths, keep the reading prompt in normal flow near the summary or TOC so it remains visible without colliding with the left rail.
- After generating HTML with fixed side rails, verify the rendered boxes at the top and after scrolling: TOC left of content, reading tip outside content, and no overlap between TOC, reading tip, content, header, or footer.

Optional utilities:

- reading progress bar
- copy link
- font-size adjustment
- light/dark mode
- print view
- back to top after substantial scrolling

Keep utilities visually quiet. Avoid floating toolbars that cover text.

## Accessibility and Performance

Use semantic HTML:

```html
<header>
<nav>
<main>
<article>
<section>
<aside>
<figure>
<figcaption>
<footer>
```

Required practices:

- one primary `h1`
- logical heading order
- skip-to-content link
- visible `:focus-visible` states
- descriptive link labels
- meaningful image alt text
- empty alt text for decorative images
- native HTML before ARIA
- browser zoom to at least 200%
- no fixed-height text containers

Respect reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Performance:

- Article text should appear without JavaScript.
- Avoid JavaScript-dependent article rendering.
- Keep self-contained pages lightweight.
- Reserve media dimensions to prevent layout shifts.
- Defer nonessential scripts.
- Avoid autoplay media, heavy widgets, and pop-ups during the first reading minute.

## Final Takeaways

Add a final summary for polished HTML pages unless the user forbids it.

Rules:

- Use 4-7 bullets or compact cards.
- Extract takeaways from the actual text.
- Do not add new arguments.
- Make each takeaway decision-ready, not generic.
- Put it near the end under a heading such as `Key Takeaways`, `最后记住`, or `What To Keep`.

## HTML Requirements

Unless the user requests otherwise:

- produce a complete HTML5 document
- include CSS inline in a `<style>` block
- avoid external network dependencies for standalone files
- preserve semantic tags
- include responsive CSS
- include accessible contrast and focus states
- keep print readability reasonable
- ensure text fits on mobile
- include one visible, content-specific reading prompt
- place the reading prompt in the right rail when side space permits and keep it in normal flow otherwise
- keep English prose fully visible without internal horizontal scrolling
- defensively wrap unbroken URLs and identifiers so they cannot widen the page
- do not rely on JavaScript for core reading

If saving to disk, use a clear filename and open it only when the user asks or when preview/open behavior is part of the task.

## Acceptance Checklist

Reading quality:

- The first screen explains the subject and value.
- The body remains comfortable after 15-20 minutes.
- Lines are not excessively long.
- Header, executive summary, article body, and footer align to the same article-column left edge.
- Paragraphs are distinguishable without huge gaps.
- Headings create a clear argument map.
- Highlighting is selective.
- A content-specific reading prompt is present and visible.
- On wide desktop, the reading prompt occupies the right rail; below that breakpoint, it remains visible in normal flow.
- Fixed TOC and reading-tip/sidebar boxes do not overlap each other or the article content at top or scrolled positions.

Mobile quality:

- No horizontal page scrolling.
- Long English sentences wrap at natural word boundaries and remain fully visible.
- Sentence, quotation, and rewrite panels have no internal horizontal scrollbar, clipping, or ellipsis.
- URLs and other unbroken strings wrap defensively without widening the document.
- Text remains at least `16-17px`.
- Tables and code remain usable.
- Controls are easy to tap.
- The title does not overwhelm the viewport.

Accessibility:

- Heading structure is valid.
- Keyboard navigation works.
- Focus states are visible.
- Contrast is sufficient.
- Reduced-motion preferences are respected.
- Images and controls have appropriate labels.

Editorial quality:

- The page offers a rapid summary.
- The introduction does not simply repeat the title.
- Visual elements clarify rather than decorate.
- The conclusion synthesizes the argument.
- References and update information are transparent when present.

## Starter Skeleton

Use or adapt this skeleton for a self-contained article page:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Article Title</title>
  <meta name="description" content="Clear one-sentence article summary." />
  <style>
    :root {
      --page-bg: #f7f7f5;
      --article-bg: #ffffff;
      --text-primary: #1b1b1b;
      --text-secondary: #666666;
      --text-muted: #8a8a8a;
      --border: #e7e7e4;
      --accent: #315efb;
      --accent-soft: #eef2ff;
      --quote-bg: #f5f6f8;
      --content-width: 720px;
      --radius: 8px;
    }

    * { box-sizing: border-box; }

    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      background: var(--page-bg);
      color: var(--text-primary);
      font-family: Inter, "SF Pro Text", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif;
      font-size: 18px;
      line-height: 1.78;
      letter-spacing: 0;
    }

    .skip-link {
      position: absolute;
      left: 16px;
      top: -48px;
      padding: 10px 14px;
      background: var(--article-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      color: var(--text-primary);
      z-index: 10;
    }

    .skip-link:focus { top: 16px; }

    :focus-visible {
      outline: 3px solid rgba(49, 94, 251, 0.35);
      outline-offset: 3px;
    }

    main {
      max-width: var(--content-width);
      margin-inline: auto;
      padding: 64px 0 88px;
    }

    .article-header,
    .article-summary,
    .article-content,
    .article-footer {
      width: min(100%, var(--content-width));
      margin-inline: auto;
    }

    .article-kicker {
      margin: 0 0 12px;
      color: var(--accent);
      font-size: 0.8125rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .article-title {
      max-width: 900px;
      margin: 0;
      font-size: clamp(2.25rem, 5vw, 4.25rem);
      line-height: 1.08;
      letter-spacing: 0;
      text-wrap: balance;
    }

    .article-subtitle {
      max-width: 760px;
      margin: 20px 0 0;
      color: var(--text-secondary);
      font-size: clamp(1.125rem, 2vw, 1.375rem);
      line-height: 1.6;
    }

    .article-meta {
      margin-top: 18px;
      color: var(--text-muted);
      font-size: 0.875rem;
    }

    .article-summary {
      margin-top: 40px;
      padding: 28px;
      background: var(--accent-soft);
      border: 1px solid var(--border);
      border-radius: var(--radius);
    }

    .article-summary h2 {
      margin: 0 0 12px;
      font-size: 1.25rem;
      line-height: 1.3;
    }

    .reading-tip {
      width: min(100%, var(--content-width));
      margin: 32px auto 0;
      padding: 18px 20px;
      background: var(--quote-bg);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      border-radius: var(--radius);
    }

    .reading-tip h2 {
      margin: 0 0 8px;
      font-size: 1rem;
      line-height: 1.35;
    }

    .reading-tip p { margin: 0; }

    .article-layout {
      margin: 56px auto 0;
    }

    .article-content {
      width: 100%;
    }

    .article-content h2 {
      margin: 3.5em 0 1em;
      font-size: clamp(1.65rem, 3vw, 2.25rem);
      line-height: 1.25;
      letter-spacing: 0;
    }

    .article-content h2:first-child { margin-top: 0; }

    .article-content h3 {
      margin: 2.5em 0 0.75em;
      font-size: clamp(1.25rem, 2vw, 1.55rem);
      line-height: 1.35;
    }

    .article-content p {
      margin: 0 0 1.2em;
    }

    .table-of-contents {
      position: sticky;
      top: 104px;
      color: var(--text-secondary);
      font-size: 0.9375rem;
    }

    .table-of-contents a {
      display: block;
      padding: 8px 0;
      color: var(--text-secondary);
      text-decoration: none;
      border-top: 1px solid var(--border);
    }

    .table-of-contents a:hover {
      color: var(--accent);
    }

    .callout,
    blockquote {
      margin: 2em 0;
      padding: 18px 22px;
      background: var(--quote-bg);
      border-left: 3px solid var(--accent);
      border-radius: var(--radius);
    }

    mark {
      background: linear-gradient(transparent 58%, rgba(255, 214, 102, 0.45) 58%);
    }

    .article-content a {
      color: var(--accent);
      text-decoration-line: underline;
      text-decoration-thickness: 0.08em;
      text-underline-offset: 0.18em;
    }

    .article-footer {
      margin-top: 72px;
      padding-top: 32px;
      border-top: 1px solid var(--border);
    }

    @media (min-width: 1280px) {
      .reading-tip {
        position: fixed;
        top: 104px;
        right: 24px;
        width: 220px;
        margin: 0;
        max-height: calc(100vh - 128px);
        overflow-y: auto;
      }
    }

    @media (max-width: 860px) {
      body {
        font-size: 17px;
        line-height: 1.75;
      }

      main {
        padding-top: 36px;
      }

      .article-layout {
        margin-top: 32px;
      }

      .table-of-contents {
        margin-top: 32px;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        scroll-behavior: auto !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }
  </style>
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <main>
    <article>
      <header class="article-header">
        <p class="article-kicker">Series or category</p>
        <h1 class="article-title">Article Title</h1>
        <p class="article-subtitle">A one-sentence value proposition that tells readers why the article matters.</p>
        <p class="article-meta">Author · 2026-07-01 · Updated 2026-07-01 · 8 min read</p>
      </header>

      <aside class="article-summary" aria-labelledby="summary-title">
        <h2 id="summary-title">In Brief</h2>
        <p><strong>Core conclusion:</strong> State the main conclusion early.</p>
        <ul>
          <li>Key point one.</li>
          <li>Key point two.</li>
          <li>Key point three.</li>
        </ul>
      </aside>

      <aside class="reading-tip" aria-labelledby="reading-tip-title">
        <h2 id="reading-tip-title">阅读提示</h2>
        <p>先快速浏览标题和摘要，再带着一个问题进入正文：作者如何从现象推进到原因与证据？</p>
      </aside>

      <div class="article-layout">
        <div class="article-content" id="content">
          <section id="section-1">
            <h2>Section Heading</h2>
            <p>Article prose goes here. Keep the content column readable and the visual hierarchy calm.</p>
            <div class="callout"><strong>Key idea:</strong> Use callouts for genuinely important synthesis.</div>
          </section>
        </div>

        <nav class="table-of-contents" aria-label="Table of contents">
          <strong>Contents</strong>
          <a href="#section-1">Section Heading</a>
        </nav>
      </div>

      <footer class="article-footer">
        <h2>Key Takeaways</h2>
        <ul>
          <li>Faithful takeaway from the article.</li>
          <li>Faithful takeaway from the article.</li>
        </ul>
      </footer>
    </article>
  </main>
</body>
</html>
```

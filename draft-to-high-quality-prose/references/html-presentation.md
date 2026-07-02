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
- [Vertical Rhythm](#vertical-rhythm)
- [Color and Contrast](#color-and-contrast)
- [Summary and Table of Contents](#summary-and-table-of-contents)
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
- Do not center the header or summary independently when the body uses a grid or fixed side rails.
- If a TOC or reading utility is fixed outside the article column, reserve side space for it and keep it visually independent from the article column.

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

Desktop with fixed side rails:

```css
:root {
  --content-width: 740px;
  --page-width: 1180px;
  --toc-width: 248px;
}

@media (min-width: 1180px) {
  main {
    width: min(calc(100vw - 360px), var(--page-width));
    margin-left: 320px;
    margin-right: auto;
  }

  .article-header,
  .article-summary,
  .article-layout,
  .article-footer {
    margin-left: 0;
    margin-right: auto;
  }

  .article-header,
  .article-summary,
  .article-content,
  .article-footer {
    width: min(100%, var(--content-width));
  }

  .table-of-contents {
    position: fixed;
    top: 104px;
    left: 32px;
    width: var(--toc-width);
    max-height: calc(100vh - 128px);
    overflow-y: auto;
  }
}

@media (min-width: 1500px) {
  .reading-tip {
    position: fixed;
    top: 104px;
    right: 32px;
    width: 250px;
    max-height: calc(100vh - 128px);
    overflow-y: auto;
  }
}
```

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

Desktop TOC:

- sticky or fixed sidebar depending on available viewport width
- width `220-260px`
- top offset `96-120px`
- current section may be highlighted if implemented simply
- If fixed to the left rail, position it outside the article column and verify it does not overlap the header, article body, footer, or any reading-tip card.
- Use a single article-column anchor so the header, summary card, main text, and footer line up even when the TOC lives in a left rail.

Mobile TOC:

- move below the summary
- make it collapsible for long articles
- keep it open only when navigation is essential

Always use real anchor links and correct heading IDs.

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

- Keep the TOC and reading-tip/utility card in separate rails or separate normal-flow blocks; never stack a sticky card under a sticky TOC in the same narrow column if their boxes can overlap while scrolling.
- For wide desktop layouts, a safe pattern is: fixed TOC on the left, article column in the middle, fixed or normal-flow reading tip on the right.
- If the right reading tip is fixed, give it its own width and right offset; do not place it inside the article content box.
- At narrower desktop widths, collapse the reading tip below the article content or keep it in normal flow so it cannot collide with the fixed left TOC.
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
- Fixed TOC and reading-tip/sidebar boxes do not overlap each other or the article content at top or scrolled positions.

Mobile quality:

- No horizontal page scrolling.
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
      --page-width: 1180px;
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
      width: min(100% - 40px, var(--page-width));
      margin-inline: auto;
      padding: 64px 0 88px;
    }

    .article-header,
    .article-summary,
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

    .article-layout {
      max-width: var(--page-width);
      margin: 56px auto 0;
      display: grid;
      grid-template-columns: minmax(0, 740px) 240px;
      gap: 72px;
      align-items: start;
    }

    .article-content {
      width: min(100%, 740px);
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

    @media (max-width: 860px) {
      body {
        font-size: 17px;
        line-height: 1.75;
      }

      main {
        width: min(100% - 36px, 720px);
        padding-top: 36px;
      }

      .article-layout {
        display: block;
        margin-top: 40px;
      }

      .table-of-contents {
        position: static;
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

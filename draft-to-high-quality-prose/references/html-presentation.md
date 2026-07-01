# HTML Presentation Mode

Use this reference when the user asks to convert, enhance, redesign, polish, or output prose as HTML. The goal is to preserve the core text and full context while making the reading experience dramatically clearer, more modern, and more visually engaging.

## Table of Contents

- [Purpose](#purpose)
- [Content Rules](#content-rules)
- [Information Architecture](#information-architecture)
- [Visual Direction](#visual-direction)
- [Layout Pattern](#layout-pattern)
- [Typography](#typography)
- [Color System](#color-system)
- [Cards and Highlights](#cards-and-highlights)
- [Final Takeaways](#final-takeaways)
- [HTML Requirements](#html-requirements)
- [Quality Checklist](#quality-checklist)
- [Starter Skeleton](#starter-skeleton)

## Purpose

Create a high-quality reading page, not a generic document dump. The page should feel like a modern editorial letter or briefing: calm, precise, lightly technical, and easy to scan.

Prioritize:

1. preserving the user's meaning and full context
2. removing junk sentences and confusing phrasing
3. improving paragraph flow and section logic
4. making key points visually legible
5. delivering a polished, self-contained HTML file

## Content Rules

- Preserve all core claims, facts, names, numbers, and nuance.
- Keep the full context needed for comprehension; do not summarize away essential reasoning.
- Lightly edit unclear, repetitive, or bloated sentences when they harm reading.
- Remove filler, duplicated transitions, vague throat-clearing, and obvious AI-style scaffolding.
- Do not invent facts, examples, citations, or conclusions.
- Add short headings, subheadings, callouts, and a final takeaway summary when they clarify the text.
- If the source is already carefully written and the user asks to keep it intact, only wrap and style it.

## Information Architecture

Use this order for most longform HTML outputs:

1. **Letter-style header**: title, subtitle/deck, date or context if available.
2. **Opening note**: one concise paragraph that orients the reader.
3. **Key insight strip**: 3-5 short points extracted from the content.
4. **Main article**: full text in well-spaced sections.
5. **Inline highlights**: selected principles, warnings, or definitions.
6. **Final takeaways**: concise summary at the end.

For analytical or technical prose, add:

- a small "Reader Map" or table of contents
- comparison tables when the source naturally contains options
- compact definition cards for key terms

## Visual Direction

Aim for a sleek but understated tech aesthetic:

- clean editorial layout
- off-white or very light neutral background
- dark charcoal text
- restrained accent colors
- subtle borders and shadows
- generous whitespace
- card radius 8px or less
- no decorative blobs, orbs, bokeh, or noisy gradients

Avoid:

- one-note dark blue or slate interfaces
- loud neon cyberpunk styling
- marketing hero sections
- oversized typography inside compact panels
- nested cards
- dense walls of text
- decorative icons that do not help reading

## Layout Pattern

Recommended desktop structure:

```text
body
  .page-shell
    .letter-head
    .insight-grid
    .content-grid
      aside.reader-map
      main.article
    .takeaways
```

On mobile:

- stack everything in one column
- keep the reader map near the top
- keep cards full-width
- ensure long words and Chinese/English mixed text wrap cleanly

Use a max reading width around `760px` for article prose. Wider shells can hold sidebars, but body paragraphs should not stretch across the screen.

## Typography

Use system fonts by default:

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

For Chinese-heavy text, include:

```css
font-family: Inter, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif;
```

Guidelines:

- body font: 16-18px
- paragraph line-height: 1.72-1.9 for Chinese, 1.65-1.8 for English
- headings: clear hierarchy, not oversized
- letter spacing: 0
- avoid viewport-scaled font sizes
- keep code or prompt blocks in a readable monospace

## Color System

Use a restrained palette with contrast:

```css
:root {
  --bg: #f7f8f5;
  --paper: #ffffff;
  --ink: #202124;
  --muted: #626a73;
  --line: #d9ded8;
  --accent: #0f766e;
  --accent-2: #b45309;
  --soft: #edf5f3;
  --soft-2: #fff7ed;
}
```

Rules:

- Use `--ink` for main text.
- Use `--muted` for metadata, captions, and secondary labels.
- Use `--accent` for links, key labels, and structural highlights.
- Use `--accent-2` sparingly for warnings or contrast.
- Keep backgrounds quiet; let typography and spacing do most of the work.

## Cards and Highlights

Use cards only for repeated or framed content:

- key insight cards
- definition cards
- warning or principle callouts
- takeaway cards

Card rules:

- border radius at or below 8px
- no card inside another card
- no heavy shadows
- no decorative containers around every section
- use concise labels such as `Principle`, `Warning`, `Method`, `Takeaway`

Highlight key points with:

- left borders
- subtle background fills
- inline strong text
- small uppercase labels
- pull quotes only when the sentence is strong and short

Do not over-highlight. If everything is highlighted, nothing is.

## Final Takeaways

Always add a final summary when producing a polished HTML page unless the user forbids it.

Rules:

- Use 4-7 bullets or compact cards.
- Extract takeaways from the actual text.
- Do not add new arguments.
- Make each takeaway decision-ready, not generic.
- Keep it near the end under a heading such as `Key Takeaways`, `最后记住`, or `What To Keep`.

Good takeaway:

```text
If a paragraph carries more than one job, split it before polishing the sentence style.
```

Weak takeaway:

```text
Writing should be clear and beautiful.
```

## HTML Requirements

Unless the user requests otherwise:

- produce a complete HTML5 document
- include all CSS inline in a `<style>` block
- avoid external network dependencies
- preserve semantic tags: `article`, `section`, `aside`, `header`, `footer`
- include responsive CSS
- include accessible color contrast
- keep print readability reasonable
- ensure all text fits on mobile
- do not rely on JavaScript for core reading

If saving to disk, use a clear filename and open it only when the user asks or when the task explicitly includes preview/open behavior.

## Quality Checklist

Before finalizing, verify:

- The core text and necessary context are preserved.
- Junk, repetition, and confusing phrasing are cleaned.
- The page has a clear title, deck, and reader orientation.
- Headings reveal the structure.
- Paragraphs are readable and not too wide.
- Key points are highlighted selectively.
- The final takeaways are faithful to the content.
- The style is modern, calm, and not visually noisy.
- The page works on mobile without overlapping text.
- No unsupported claims or invented citations were added.

## Starter Skeleton

Use or adapt this skeleton when creating a self-contained page:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Document Title</title>
  <style>
    :root {
      --bg: #f7f8f5;
      --paper: #ffffff;
      --ink: #202124;
      --muted: #626a73;
      --line: #d9ded8;
      --accent: #0f766e;
      --accent-2: #b45309;
      --soft: #edf5f3;
      --soft-2: #fff7ed;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif;
      font-size: 17px;
      line-height: 1.8;
    }

    .page-shell {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 48px 0 72px;
    }

    .letter-head {
      max-width: 820px;
      margin: 0 auto 28px;
      padding: 32px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
    }

    .eyebrow {
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      font-size: 34px;
      line-height: 1.18;
      letter-spacing: 0;
    }

    .deck {
      margin: 16px 0 0;
      color: var(--muted);
      font-size: 18px;
    }

    .insight-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin: 28px 0;
    }

    .insight-card,
    .reader-map,
    .article,
    .takeaways {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
    }

    .insight-card {
      padding: 18px;
      min-height: 120px;
    }

    .label {
      display: block;
      margin-bottom: 8px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .content-grid {
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }

    .reader-map {
      position: sticky;
      top: 20px;
      padding: 18px;
      color: var(--muted);
      font-size: 14px;
    }

    .reader-map a {
      display: block;
      color: var(--ink);
      text-decoration: none;
      padding: 6px 0;
    }

    .article {
      padding: 36px;
    }

    .article section + section {
      margin-top: 36px;
      padding-top: 28px;
      border-top: 1px solid var(--line);
    }

    h2 {
      margin: 0 0 14px;
      font-size: 24px;
      line-height: 1.28;
      letter-spacing: 0;
    }

    p { margin: 0 0 16px; }

    .callout {
      margin: 22px 0;
      padding: 16px 18px;
      background: var(--soft);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
    }

    .takeaways {
      max-width: 820px;
      margin: 28px auto 0;
      padding: 28px;
      background: var(--soft-2);
    }

    .takeaways li + li { margin-top: 10px; }

    @media (max-width: 820px) {
      .page-shell {
        width: min(100% - 24px, 720px);
        padding-top: 24px;
      }

      .letter-head,
      .article,
      .takeaways {
        padding: 22px;
      }

      .insight-grid,
      .content-grid {
        grid-template-columns: 1fr;
      }

      .reader-map {
        position: static;
      }

      h1 { font-size: 28px; }
    }
  </style>
</head>
<body>
  <div class="page-shell">
    <header class="letter-head">
      <p class="eyebrow">Briefing</p>
      <h1>Document Title</h1>
      <p class="deck">One-sentence orientation for the reader.</p>
    </header>

    <section class="insight-grid" aria-label="Key insights">
      <div class="insight-card"><span class="label">Point 01</span>Key insight text.</div>
      <div class="insight-card"><span class="label">Point 02</span>Key insight text.</div>
      <div class="insight-card"><span class="label">Point 03</span>Key insight text.</div>
    </section>

    <div class="content-grid">
      <aside class="reader-map" aria-label="Reader map">
        <strong>Reader Map</strong>
        <a href="#section-1">Section One</a>
        <a href="#section-2">Section Two</a>
      </aside>

      <article class="article">
        <section id="section-1">
          <h2>Section One</h2>
          <p>Preserved and lightly cleaned prose goes here.</p>
          <div class="callout"><strong>Principle:</strong> Highlight one important idea.</div>
        </section>
      </article>
    </div>

    <footer class="takeaways">
      <h2>Key Takeaways</h2>
      <ul>
        <li>Faithful takeaway from the content.</li>
        <li>Faithful takeaway from the content.</li>
      </ul>
    </footer>
  </div>
</body>
</html>
```

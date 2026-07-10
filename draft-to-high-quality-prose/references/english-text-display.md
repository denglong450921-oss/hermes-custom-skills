# English Text Display

Use this reference whenever an HTML output contains English sentences, quotations, vocabulary examples, bilingual analysis, before/after rewrites, or long Latin-script text. The aim is simple: readers should see the complete language example at a glance and continue reading vertically. A sentence should not behave like a code sample.

Preview the shared visual system in `../assets/english-text-display-examples.html`.

## Core Principle

Choose the HTML element from the meaning of the text:

- prose or a model sentence: `<p lang="en">`
- a quotation used as evidence: `<blockquote lang="en">`
- a term or short phrase: `<span lang="en">` or `<dfn lang="en">`
- code that must preserve exact whitespace: `<pre><code>`
- tabular comparison: semantic `<table>` only when rows and columns carry real meaning

Do not use a code block merely to obtain a gray box or monospace font. Code blocks imply machine syntax, preserve whitespace, and commonly introduce horizontal scrolling. English learning content is usually better served by a prose panel with a readable serif or sans-serif face.

## Wrapping Contract

English reading content should remain fully visible inside the page at desktop, mobile, and 200% zoom.

```css
.english-text,
[lang="en"].reading-text {
  max-width: 100%;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: normal;
  hyphens: none;
}

.example-panel,
.comparison-item,
.bilingual-row > * {
  min-width: 0;
}

.unbroken-token {
  overflow-wrap: anywhere;
  word-break: break-word;
}
```

Use `overflow-wrap: break-word` and `hyphens: none` for normal prose so browsers preserve complete words, which matters when readers are studying spelling or phrasing. Use `overflow-wrap: anywhere` only for URLs, hashes, filenames, generated identifiers, or other strings that may contain no spaces. This keeps prose elegant while still preventing page overflow.

Avoid these rules on reading content:

```css
white-space: nowrap;
text-overflow: ellipsis;
overflow-x: auto;
height: 120px;
```

They hide or displace content and make the reader perform an extra horizontal gesture. Internal scrolling is acceptable for genuine code or a wide data table, not for sentences the reader is expected to study.

## Shared Visual Language

Use one restrained family of components:

- neutral page and panel backgrounds
- dark, high-contrast text
- one blue accent for structure and focus
- one warm semantic color for revisions or highlights
- square or lightly rounded corners, at most `8px`
- no heavy shadows, ornamental gradients, or decorative card stacks

Recommended tokens:

```css
:root {
  --paper: #f5f6f3;
  --surface: #ffffff;
  --ink: #17202a;
  --muted: #66717f;
  --line: #dfe3e6;
  --accent: #2457c5;
  --accent-soft: #edf3ff;
  --warm: #9a4d16;
  --warm-soft: #fff4e8;
  --radius: 8px;
}
```

Labels should be short and functional: `Original`, `Plain`, `Polished`, `Meaning`, `Pattern`, or their Chinese equivalents. Keep them visually secondary to the English sentence.

## Pattern 1: Featured Sentence

Use this for the primary sentence being explained. It should feel like a reading specimen, not a terminal window.

```html
<figure class="sentence-feature">
  <figcaption>Original sentence</figcaption>
  <blockquote class="english-text" lang="en">
    As far as goods transport is concerned, growth is due to a large extent to changes in the European economy and its system of production.
  </blockquote>
</figure>
```

```css
.sentence-feature {
  margin: 2rem 0;
  padding: 1.25rem 1.35rem 1.35rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius);
}

.sentence-feature figcaption {
  margin-bottom: 0.7rem;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

.sentence-feature blockquote {
  margin: 0;
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.22rem, 2.5vw, 1.72rem);
  line-height: 1.55;
}
```

## Pattern 2: Before and After

Use a responsive comparison for rewrites. A two-column desktop layout may collapse to one column on mobile. Preserve reading order: original first, revision second.

```html
<div class="comparison-grid">
  <section class="comparison-item comparison-before">
    <p class="example-label">Plain</p>
    <p class="english-text" lang="en">Freight transport has grown because the European economy has changed.</p>
  </section>
  <section class="comparison-item comparison-after">
    <p class="example-label">Polished</p>
    <p class="english-text" lang="en">The expansion of freight transport can be attributed largely to structural changes in Europe’s economy and production systems.</p>
  </section>
</div>
```

```css
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.comparison-item {
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
}

.comparison-after {
  background: var(--accent-soft);
  border-color: #cbd9f7;
}

@media (max-width: 680px) {
  .comparison-grid { grid-template-columns: 1fr; }
}
```

## Pattern 3: Bilingual Explanation

Use a compact bilingual row when readers need to connect an English expression to a Chinese explanation. Keep the English expression prominent and avoid pill-shaped containers for full sentences.

```html
<dl class="bilingual-list">
  <div class="bilingual-row">
    <dt lang="en">be due largely to</dt>
    <dd>主要归因于；用于正式地解释原因。</dd>
  </div>
  <div class="bilingual-row">
    <dt lang="en">structural changes</dt>
    <dd>结构性变化，强调变化不是暂时或表面的。</dd>
  </div>
</dl>
```

```css
.bilingual-row {
  display: grid;
  grid-template-columns: minmax(10rem, 0.8fr) minmax(0, 1.4fr);
  gap: 1rem;
  padding: 0.95rem 0;
  border-top: 1px solid var(--line);
}

.bilingual-row dt {
  color: var(--accent);
  font-weight: 700;
  overflow-wrap: break-word;
}

.bilingual-row dd { margin: 0; }

@media (max-width: 600px) {
  .bilingual-row { grid-template-columns: 1fr; gap: 0.25rem; }
}
```

## Pattern 4: Long Unbroken Data

When content has no legal word boundary, keep it visible with defensive wrapping and a quieter technical treatment. Do not apply this style to ordinary sentences.

```html
<p class="token-line">
  <span class="example-label">Reference ID</span>
  <code class="unbroken-token">freight-transport-european-production-system-structural-change-reference-2026</code>
</p>
```

For a URL, make the entire URL a normal anchor and apply `.unbroken-token` to it. For actual source code, keep `<pre><code>` and allow horizontal scrolling because exact token order and indentation may matter.

## Composition Rules

- Use one featured sentence near the top, then lighter comparison or bilingual components in the body.
- Keep full sentences in blocks, not chips. Chips are suitable only for short labels or terms.
- Do not place a sentence panel inside another card.
- Keep English examples left-aligned; do not justify them.
- Set `lang="en"` on English passages so browsers and assistive technology can apply appropriate pronunciation and hyphenation.
- Use `text-wrap: balance` for short headings only. Do not balance multi-sentence prose.
- Use `font-variant-ligatures: common-ligatures` if desired, but do not reduce letter spacing below zero.
- When English and Chinese share one paragraph, give the line-height enough room for both scripts, usually `1.7-1.85`.

## Verification

Check at minimum:

1. Desktop around `1440 x 900`.
2. Mobile around `390 x 844`.
3. Browser zoom at `200%` or an equivalent narrow layout.
4. A sentence longer than 150 characters.
5. An unbroken identifier longer than 80 characters.

The page passes when:

- the document has no horizontal page scroll
- sentence panels have no horizontal scrollbar
- no English content is clipped or replaced by an ellipsis
- grid and flex children shrink because they use `min-width: 0`
- normal prose wraps at words, while unbroken technical strings break only when necessary
- the complete sentence remains readable without horizontal interaction

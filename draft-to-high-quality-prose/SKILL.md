---
name: draft-to-high-quality-prose
description: Transform rough drafts, notes, academic prose, essays, long-form articles, speeches, scripts, reports, emails, HTML documents, or bilingual Chinese/English text into clear, fluent, high-quality prose and polished reading experiences. Use when the user asks to polish, rewrite, smooth, tighten, improve readability, remove AI-flavored or bureaucratic writing, strengthen sentence and paragraph flow, convert or enhance HTML presentation, create a premium editorial article page, modern letter-style HTML, quiet tech-style reading layout, executive summary, table of contents, key-point highlights, final takeaways, save Markdown/HTML outputs, open generated HTML previews, copy Markdown outputs to the liuskill Obsidian vault, or apply Liu Junqiang's "flow" method from Writing Is a Craft.
---

# Draft To High Quality Prose

Rewrite drafts by rebuilding the reader's path. Do not merely beautify wording. Preserve the user's meaning, facts, stance, names, numbers, citations, and necessary terminology while improving clarity, flow, structure, and rhythm.

This skill uses a harness extracted from Liu Junqiang's "flow" framework in `references/liu-flow-framework.md`. Read that reference when the request is substantial, the draft is more than a few paragraphs, the user asks for diagnosis, or the prose has academic, bureaucratic, AI-flavored, or structural problems. For converted HTML, article-page design, visual enhancement, letter-style layouts, quiet tech aesthetics, or polished reading pages, also read `references/html-presentation.md`.

## Default Response Contract

For ordinary rewrite requests, return:

```markdown
## 改写稿
<rewritten prose>

## 关键改动
- <3-6 notes on the structural changes that most improved the prose>

## 仍需确认
- <only include if audience, facts, tone, or missing context materially affect the rewrite>
```

If the user asks for only the revised text, return only the revised text. If the user asks for diagnosis, diagnose before rewriting and wait if they asked to review first.

For HTML presentation requests, return or save a complete self-contained HTML document unless the user asks for a fragment. Preserve the core text and full context, but remove junk sentences, confusing phrasing, repetition, and needless complexity when it improves comprehension. Build a premium article reading page with a clear first screen, readable article column, executive summary when useful, table of contents for longer pieces, selective highlights, and final key takeaways that reflect the source without inventing new claims.

## Key Point Marking

In every output mode, mark the most valuable and memorable key point of each paragraph.

**Markdown mode:**
- When the key point is also the topic sentence, no extra markup is needed. The reader can see it.
- When the key point sits mid-paragraph or end-paragraph and deserves emphasis, append a callout: `> 💡 **要点**: [key point sentence]`
- Use these callouts sparingly — only for genuinely valuable, memorable claims. Not every paragraph needs one.

**HTML mode:**
- Wrap the key sentence in each paragraph with a `<span class="key-point">` or `<mark>` if the sentence is genuinely remarkable. Do not highlight every paragraph.
- Alternatively, add a marginal note or inline `💡` badge next to the key sentence.
- Use at most one highlight per paragraph. If a paragraph needs two, split it.
- The visual treatment must be subtle: a soft underline, a low-opacity background glow, or a sidebar marker — not a bright banner.

**Plain text / minimal mode:**
- Prefix the key sentence with `[要点]` or `[Key]` inline. Avoid changing the surrounding format.

## HTML Layout Rules

For premium article HTML outputs:

- **Center the article column in the viewport.** Do not push content with a left margin to clear a fixed TOC. Position the TOC and reading tip relative to the centered column using `calc()`. (See `references/html-presentation.md` for the CSS pattern.)
- Align the article header, executive summary, main text column, and footer/takeaway text to the same article-column left edge — the centered column is the alignment anchor.
- **TOC must always be visible.** On narrow screens, render it as a card in normal flow (below the summary, above the content). On wide screens (≥1180px), pin it as a fixed left-side rail using `calc()` relative to the centered article column. Never hide the TOC on any screen size.
- Keep `阅读提示` separate from `目录`; they must never overlap each other, the article text, the header, or the footer.
- After generating HTML with fixed side rails, verify the rendered layout at the top and after scrolling: TOC left of content, reading tip outside content, and no overlapping boxes.

## HTML Key Point Visual Design

When generating HTML with per-paragraph key-point highlights:

- Use a single subtle highlight treatment across the whole page. One of:
  - `span.key-point` with a soft left border + lighter background (like callout but thinner)
  - A `💡` marker placed beside the key sentence via a superscript or inline icon
  - A `mark` highlight with reduced opacity so it doesn't compete with the main text
- Define the highlight in the page `<style>` block. Example:
  ```css
  .key-point {
    background: linear-gradient(transparent 60%, rgba(255, 214, 102, 0.30) 60%);
    font-weight: 500;
  }
  ```
- Show no more than one key-point highlight per paragraph.
- If a paragraph's key point is already the first sentence and obvious as a topic sentence, skip the highlight — let the structure speak.
- Do not highlight the same paragraph type repeatedly (e.g. every evidence paragraph). Vary the marking pattern so highlights stay meaningful.
- Keep highlights visually quieter than headings, callouts, and blockquotes.

## File Output Workflow

**Input:** Accepts a URL (WeChat, blog, web page), a local file path (markdown, HTML, Obsidian clippings with YAML frontmatter), or inline text. Strip YAML frontmatter from Obsidian/markdown files before running the rewrite harness — the frontmatter contains metadata, not prose. Preserve source URL and author from frontmatter for attribution.

**Default (paired output):** When the user invokes this skill on a file or asks to rewrite/save content without specifying an output format, produce both `.md` and `.html` by default. Do not wait for the user to ask for HTML — pair them from the start. Use `html-presentation` mode for the HTML output. Only skip the HTML when the user explicitly says "markdown only" or "text only".

When producing paired output:

- Save generated files to `~/Downloads` unless the user gives another output folder.
- Use a clear shared basename for paired outputs, with `.md` for the polished Markdown and `.html` for the self-contained reading page.
- When a Markdown file is written, automatically copy it to `/Users/f/Documents/dennon_obsidian_vault_important/den-llm-wiki/liuskill/`. Create that folder if needed.
- When an HTML file is written for preview, automatically open it unless the user explicitly says not to.
- Report the absolute paths for the Markdown file, HTML file, and vault copy (even if the vault copy path is just a note saying what was done).
- If copying or opening fails, say so plainly and keep the generated file in `~/Downloads`.

## Rewrite Harness

Use this sequence unless the user specifies a narrower edit.

1. **Lock invariants**: Identify facts, claims, names, numbers, citations, voice constraints, audience, format, and any forbidden changes.
2. **Find the main line**: State internally what the piece is really trying to say. Rebuild around that line.
3. **Choose mode**:
   - `transparent-glass`: clear public explanation, report, article, educational prose.
   - `academic-clarity`: paper, proposal, literature review, research memo; preserve precision and hedging.
   - `public-essay`: newsletter, post, speech, op-ed; sharpen rhythm without sacrificing accuracy.
   - `minimal-edit`: preserve the author's voice and only fix clarity blockers.
   - `html-presentation`: preserve and lightly clean the text, then convert it into a refined HTML reading page.
4. **Diagnose by layer**: Check word abstraction, sentence trunk, sentence chaining, rhythm, paragraph job, section route, and layout.
5. **Rewrite structurally**: Move, split, combine, concretize, and re-sequence before polishing word choice.
6. **Extract per-paragraph key points**: For each rewritten paragraph, identify the single most valuable or memorable claim. Ensure it appears as the topic sentence (preferred), or tag it with a `💡 要点` callout after the paragraph. If a paragraph produces no worthwhile key point, remove or merge it.
7. **Verify**: Confirm the rewrite preserves meaning, reduces friction, and makes the reader's route visible.

## Core Moves

- **Lower empty abstractions**: Replace vague nouns and verbs with concrete actors, actions, mechanisms, examples, or stakes.
- **Expose sentence trunks**: Keep concrete subjects near observable verbs; move heavy conditions after the main clause.
- **Chain sentences**: Start with old or familiar information, end with new information, and let the next sentence pick it up.
- **Vary rhythm**: Split blocked long sentences; combine choppy short ones; land key points with shorter sentences.
- **One paragraph, one job**: Give each paragraph one purpose and make the first sentence carry the point when possible.
- **Make sections navigable**: Use headings, topic sentences, and signposts when they reduce reader effort.
- **Mark paragraph key points**: After rewriting, identify the single most valuable or memorable claim in each paragraph. Make it visible — as the paragraph's topic sentence, as a `> 💡 **要点**` callout after the paragraph in Markdown, or as a subtle highlighted sentence within the paragraph in HTML. If a paragraph yields no memorable point, it likely doesn't serve the main line. Delete or merge it.

## Guardrails

- Do not invent evidence, examples, citations, statistics, or claims.
- Do not flatten the user's distinctive voice unless clarity requires it.
- Do not over-polish into slogans, generic inspirational prose, or "AI essay" symmetry.
- Do not replace domain terms that are necessary for precision; define or scaffold them instead.
- Do not explain every micro-edit unless the user asks for an edit memo.
- For HTML, do not use visual polish to hide weak structure. Improve structure first, then design the reading experience.

## Quick Diagnostic

When prose still feels wrong, check in this order:

1. Does the piece know what it wants?
2. Can the reader follow one main path?
3. Are key claims too abstract or unsupported?
4. Can the reader quickly find who does what?
5. Does each sentence hand something to the next?
6. Does old information come before new information?
7. Are sentence lengths controlled and varied?
8. Does each paragraph do one job?
9. Can a skim reader find the memorable point of each paragraph at a glance?
10. Can a skim reader understand the argument from headings and first sentences?

## Reference Loading

Load `references/liu-flow-framework.md` for:

- detailed rewrite rules and decision tables
- Chinese prose revision heuristics
- academic and bureaucratic prose cleanup
- paragraph and section restructuring
- a ready-to-use prompt template

Load `references/html-presentation.md` for:

- modern, understated tech and letter-style HTML layouts
- premium editorial article page specifications
- executive summaries, article-width rules, table of contents behavior, and reading rhythm
- typography, color, spacing, and card guidelines
- rules for preserving text while cleaning confusing phrasing
- key-point highlighting and final takeaway summaries
- accessibility, performance, responsive behavior, and self-contained HTML output requirements

Load `references/content-types.md` for:

- handling non-prose inputs: structured lists, catalogs, mixed prose+lists, tables, code-heavy content
- decision table for choosing rewrite depth per format
- HTML and Markdown patterns for list/reference content
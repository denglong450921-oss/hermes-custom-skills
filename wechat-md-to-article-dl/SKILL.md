---
name: wechat-md-to-article-dl
description: >
  Transform Markdown drafts into focused, public-account-ready WeChat articles
  and audited inline-CSS HTML. Use when the user asks to rewrite, polish,
  typeset, convert, beautify, style, validate, or prepare Markdown or HTML for a
  WeChat Official Account article, especially for 公众号文章, copywriting,
  public-account style, style variations, article tone, titles, openings,
  mobile readability, magazine-style layouts, technical essays, cognition
  columns, business analysis, health education, Dark Mode, or WeChat editor
  compatibility.
---

# Markdown to WeChat Article

Create WeChat-ready articles in two passes:

1. **Editorial pass:** make the article sharper, more focused, and better matched
   to a public-account style profile.
2. **Production pass:** convert the final Markdown to restrained, mobile-first
   inline-CSS HTML and audit it against WeChat constraints.

Do not jump straight to HTML when the user asks for "更像公众号文章", "更有风格",
"更聚焦", "文案更好", or "适合公众阅读". Run the editorial pass first.

## Quick Workflow

Generate a writing brief:

```bash
python3 scripts/style_brief.py article.md \
  --profile auto \
  --output article.style.json \
  --md-output article.style.md
```

Revise the Markdown according to the brief and, when needed, read
`references/article-style-playbook.md`.

Convert the revised Markdown:

```bash
python3 scripts/convert.py article.revised.md \
  --output article.wechat.html \
  --theme auto \
  --quality-threshold 90
```

Audit existing HTML:

```bash
python3 scripts/audit.py article.wechat.html \
  --report article.audit.json \
  --threshold 90
```

Use `--official-check` only when the user explicitly authorizes sending the
generated HTML to WeChat's official verifier.

## Editorial Pass

Use `scripts/style_brief.py` to choose or force a writing profile:

| Profile | Best for | WeChat theme |
|---|---|---|
| `explainer` | General public explanation and concept clarification | `minimal` |
| `opinion` | Cognition columns, trends, contrarian judgments | `cognition` |
| `story` | Cases, memoirs, founder stories, brand narratives | `minimal` |
| `framework` | How-to, productivity, learning methods, playbooks | `cognition` |
| `business` | Strategy, growth, wealth, organization, execution | `wealth` |
| `technical` | AI, software, architecture, engineering practice | `tech` |
| `health` | Health, wellness, psychology, sleep, exercise, nutrition | `health` |

For style variation requests, produce 2-3 variants by changing the profile, not
just the visual theme. Each variant should differ in title logic, opening move,
section order, tone, and ending.

## Public-Account Writing Standard

Before conversion, make the copy pass these checks:

- One core promise: the reader knows what they gain by finishing.
- First screen works: title, summary, first paragraph, and first H2 create a
  ten-second reading path.
- Opening is specific: question, scene, contrarian judgment, result promise, or
  misconception correction.
- Each H2 advances one reader question or argument step.
- Paragraphs are mobile-friendly: usually 1-3 sentences and one beat each.
- Key claims have support: example, data, mechanism, contrast, or scene.
- Tone matches the topic: health is calm, business names risks, technical explains
  mechanisms, opinion earns its sharpness.
- Ending gives a checklist, decision rule, next action, or reusable mental model.
- Remove generic filler, motivational slogans, repeated setup, and AI-like summary
  phrases.

The converter does not invent claims. If the source lacks evidence, examples, or
reader value, improve the Markdown first and clearly preserve uncertainty.

## Markdown Enhancements

Use these markers sparingly before conversion:

| Marker | Use |
|---|---|
| `==text==` | Core concept or key definition |
| `^^text^^` | Key judgment or argument |
| `!!text!!` | Important point without color |
| `:::problem` | Problem or risk callout |
| `:::strategy` | Strategy or approach callout |
| `:::thinking` | Mental model callout |
| `:::key` | Core insight callout |

Do not highlight more than 10-15% of the prose. Too much emphasis makes the
article feel promotional and harder to scan.

Supported frontmatter keys include `title`, `author`, `date`, `summary`,
`description`, `type`, `category`, and `tags`.

## Production Pass

Use `scripts/convert.py` for deterministic HTML generation. Do not recreate the
template manually when the converter can do the work.

Input contract:

| Field | Required | Notes |
|---|---:|---|
| Markdown path | Yes | UTF-8 `.md` file |
| `--output` | Yes | WeChat-compatible HTML fragment |
| `--theme` | No | `auto`, `minimal`, `tech`, `cognition`, `wealth`, `health` |
| `--title` | No | Overrides frontmatter title |
| `--quality-threshold` | No | Defaults to 90 |
| `--report` | No | Defaults to `<output>.report.json` |
| `--official-check` | No | Opt-in upload to WeChat verifier |
| `--card-padding` | No | List item padding in px |

Output JSON includes:

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
    "reason": "not_requested"
  },
  "manual_review": []
}
```

Treat any score below the threshold as not ready.

## Visual and WeChat Rules

- Use one accent color and a compact neutral palette.
- Keep body text at 15-16px with 1.75-1.9 line height.
- Keep article padding at 16-20px and section spacing at 24-36px.
- Use inline CSS only. Avoid external CSS, `<style>`, scripts, event handlers,
  classes, IDs, unsafe URL schemes, and layout features WeChat may strip.
- Do not set `font-family`; preserve the platform default font.
- Do not use fixed dimensions, zero line height, `text-align:start/end`,
  fragile positioning, transforms, CSS variables, or `!important`.
- Do not emit `<pre>`; fenced code must become wrapping `section > code`.
- Do not rely on `<ol>`, `<ul>`, or `<li>` in the final HTML; the converter
  normalizes lists into WeChat-stable blocks.
- Keep same-tag nesting at 15 levels or fewer.
- Treat images containing text, transparent images, and text over background
  images as manual light/dark review items.

## References

- Read `references/article-style-playbook.md` when rewriting copy, creating
  style variations, title/opening variants, or public-account voice guidance.
- Read `references/design-system.md` when changing themes, spacing, typography,
  cards, or article-type behavior.
- Read `references/wechat-editor-plugin-spec.md` when changing tags, CSS
  compatibility checks, Dark Mode behavior, or official validation.
- Read `references/wechat-highlighting-strategy.md` when tuning emphasis styles
  or debugging highlight rendering.
- Read `references/image-text-rendering.md` before changing cover image text
  rendering.

## Failure Handling

| Failure | Response |
|---|---|
| Missing dependency | Report the exact package; do not silently use a weaker parser |
| Invalid or empty Markdown | Stop with structured JSON and nonzero exit code |
| Weak article focus | Generate style brief and revise Markdown before conversion |
| Unsafe raw HTML | Strip unsafe tags, event attributes, classes, IDs, and URL schemes |
| First audit below threshold | Rerender in strict mode, then inspect the second report |
| Second audit below threshold | Return `blocked` with failed dimensions and report path |
| Official verifier rejects HTML | Return `blocked` with `invalid_info`; repair locally and retry only if authorized |
| Official verifier unavailable | Return `blocked` with status `error`; keep the local report |
| Image uncertainty | Keep automated score and add a `manual_review` item |
| Unknown theme or profile | Stop and list supported values |

## Verification

Run:

```bash
python3 -m unittest discover -s tests
python3 scripts/style_brief.py evals/files/cognition.md \
  --output /tmp/cognition.style.json \
  --md-output /tmp/cognition.style.md
python3 scripts/convert.py evals/files/technical.md \
  --output /tmp/technical.wechat.html \
  --theme tech
python3 scripts/audit.py /tmp/technical.wechat.html \
  --report /tmp/technical.audit.json
```

Before claiming completion, confirm:

- the style brief has a profile, reader promise, title options, outline, and
  quality findings;
- all converter scores are at least 90;
- no `<style>`, `<script>`, `class`, `id`, event attributes, `font-family`,
  fixed dimensions, `<pre>`, transforms, or `!important` remain;
- headings, lists, blockquotes, code, tables, images, and links are preserved;
- manual image review is completed when images are present;
- official verification passes only when the user authorized `--official-check`;
- the result remains readable at a narrow mobile width.

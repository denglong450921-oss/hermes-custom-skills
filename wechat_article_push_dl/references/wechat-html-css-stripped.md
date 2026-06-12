# WeChat Article: HTML CSS Stripped / Broken

## Symptom Diagnosis

| Symptom | Root Cause |
|---------|------------|
| "my card's CSS is not working" | `<style>` block in HTML — WeChat strips external CSS |
| "backgrounds disappeared" | `background` with gradient or CSS var won't render |
| "gradients are gone" | `linear-gradient` / `radial-gradient` not supported |
| "layout collapsed" | `display: flex` or `display: grid` stripped |
| "bullet points missing" | `::before` / `::after` pseudo-elements stripped |

## Why It Happens

WeChat's article renderer **only supports inline styles**. HTML passed via `--html` is uploaded as-is — the tool does NOT convert CSS. If your source file has:

```html
<style>
  .card { background: linear-gradient(...); }
</style>
<div class="card">Content</div>
```

WeChat sees only `<div>Content</div>` — the `<style>` block is stripped entirely.

## Fix Options (preferred first)

### Option A: Convert to Markdown (Prefer `--markdown`)

```bash
# Instead of:
md2wechat --html article.html --cover <url>

# Convert to markdown first, then:
md2wechat --markdown article.md --cover <url>
```

The MD2WeChat converter built into the CLI generates proper WeChat-compatible HTML. This is the cleanest fix.

### Option B: Rewrite HTML with inline styles only

```html
<!-- Before (broken in WeChat) -->
<style>.card{background:linear-gradient(red,blue)}</style>
<div class="card">text</div>

<!-- After (works in WeChat) -->
<div style="background:#1a1a2e;color:#eee;padding:16px;">text</div>
```

### Option C: Use `wechat_article_css_dl` skill

Load that skill to auto-check and auto-fix HTML violations:
- Scans for `<style>` blocks, CSS vars, gradients, flex/grid, `::before`, etc.
- Applies regex-based micro-fixes (removes style blocks, replaces gradients with solid colors, etc.)
- Writes fixed output to a new file

## Prevention

- **Rule of thumb:** If the source is Markdown, always use `--markdown`, never `--html`
- Only use `--html` when you control the HTML and have verified it uses only inline styles with WeChat-compatible properties
- Run `wechat_article_css_dl` check-mode on any HTML before pushing via `--html`

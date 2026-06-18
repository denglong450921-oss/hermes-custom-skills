# Mermaid Diagrams in HTML Output

When embedding Mermaid diagrams in html-output pages, use the dark-theme inline config for proper rendering in both light/dark modes.

## Pattern

```html
<div class="mermaid">
%%{init: {"theme": "dark", "themeVariables": {
  "fontSize": "14px",
  "fontFamily": "Segoe UI, system-ui, sans-serif",
  "primaryColor": "#1e293b",
  "primaryTextColor": "#e2e8f0",
  "primaryBorderColor": "#38bdf8",
  "secondaryColor": "#0f172a",
  "tertiaryColor": "#334155",
  "lineColor": "#64748b",
  "textColor": "#e2e8f0"
}, "flowchart": {
  "htmlLabels": true,
  "curve": "basis",
  "nodeSpacing": 40,
  "rankSpacing": 50,
  "useMaxWidth": true
}}}%%
flowchart LR
    A["Node A"] --> B["Node B"]
</div>

<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
```

## CSS class for mermaid container

Add to the page CSS (already in output.css? check — if not, add):

```css
.mermaid {
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin: 1em 0;
  overflow-x: auto;
}
```

## Why `<div>` not `<pre>`

- `<div>` respects the CSS `background` and `border-radius` from the theme
- `<pre>` has browser-default monospace that interferes with Mermaid SVG
- The inline `%%{init: ...}%%` block handles all theming — no need for `<pre>`

## Color-class mapping

Use `classDef` with `class` assignments for node type coloring:

| Class name | fill | stroke | text | Use for |
|-----------|------|--------|------|---------|
| `module` | `#172554` | `#60a5fa` | `#dbeafe` | Modules/files |
| `function` | `#0f172a` | `#38bdf8` | `#e0f2fe` | Functions |
| `klass` | `#064e3b` | `#34d399` | `#d1fae5` | Classes/constants |
| `entry` | `#422006` | `#fbbf24` | `#fde68a` | Entry points |
| `api` | `#450a0a` | `#f87171` | `#fee2e2` | API endpoints |
| `async` | `#2e1065` | `#a78bfa` | `#ede9fe` | Async functions |
| `ui` | `#831843` | `#f472b6` | `#fce7f3` | UI components |
| `concept` | `#292524` | `#a8a29e` | `#fafaf9` | Abstract concepts |

## When to use

Only use Mermaid when `.steps` list or `.card-grid` truly can't express the relationship — adds a CDN dependency and breaks offline.

## Script placement

Place `<script>` tag before `</body>` (or in `<head>` for early load). Mermaid auto-inits when the script loads and finds `.mermaid` elements.

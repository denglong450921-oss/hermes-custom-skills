# WeChat HTML CSS Compatibility

WeChat's article renderer supports only inline styles — `<style>` blocks are stripped.

## ✅ Works in WeChat (inline styles)

| Property | Example |
|----------|---------|
| `color` | `color:#333;` |
| `background-color` | `background-color:#fff;` |
| `font-size` | `font-size:16px;` |
| `font-weight` | `font-weight:700;` |
| `font-family` | `font-family:"PingFang SC",sans-serif;` |
| `font-style` | `font-style:italic;` |
| `text-align` | `text-align:center;` |
| `text-decoration` | `text-decoration:none;` |
| `line-height` | `line-height:1.7;` |
| `margin` | `margin:8px 0;` |
| `padding` | `padding:10px;` |
| `border` | `border:1px solid #ddd;` |
| `border-left` | `border-left:4px solid #e8633a;` |
| `border-collapse` | `border-collapse:collapse;` |
| `width` | `width:100%;` |
| `max-width` | `max-width:800px;` |
| `display: block` / `inline-block` / `inline` | `display:block;` |
| `position` | `position:relative;` / `position:absolute;` |
| `top`, `left` | `top:0; left:0;` |
| `vertical-align` | `vertical-align:middle;` |
| `list-style` | `list-style:none;` |
| `border-radius` | `border-radius:10px;` (simple uniform only) |
| `background` | `background:#fff;` (solid colors only) |

## ❌ Does NOT work in WeChat

| Feature | Why it breaks | Replacement |
|---------|--------------|-------------|
| `<style>` block | WeChat strips `<style>` entirely | Inline `style=""` on each element |
| CSS variables (`--var`) | No custom properties support | Hardcode hex/rgb values |
| `linear-gradient` / `radial-gradient` | Gradients not rendered | Solid `background-color` |
| `-webkit-background-clip: text` | Chromium-only feature, stripped | Solid `color` value |
| `display: flex` / `display: grid` | Layout models not supported | `<table>` or stacked `<div>` blocks |
| `::before` / `::after` | Pseudo-elements stripped | Write literal characters: `▸`, `•`, `①` |
| `counter-increment` / `counter-reset` | CSS counters not supported | Manual numbering (1, 2, 3...) |
| `:hover` / `:nth-child` / `:last-child` / `:first-child` | Pseudo-classes stripped | Apply style to every element directly |
| `@media` queries | No responsive support | Single layout optimized for mobile |
| `box-shadow` | Unreliable — may render or not | Remove or use `border` |
| `transform` / `transition` / `animation` | Not supported | Remove entirely |
| `opacity` | Unreliable | Remove |

## Recommended HTML Strategy

- All styles inline: `<div style="color:#333;margin:8px 0;">Content</div>`
- Replace gradient text → solid `color`
- Replace `::before` bullets → literal `<span>▸</span>` elements
- Replace CSS counter numbering → manual `<li>1.</li>`
- Replace `display:flex`/`grid` layouts → `<table>` or stacked blocks
- Replace dark gradient sections → solid `background-color`
- Keep table formatting simple — no `border-radius` on `thead th`
- Use `<br>` for line breaks inside elements

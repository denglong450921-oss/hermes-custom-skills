# "My CSS Doesn't Render" — Diagnosis & Fix

## Symptom

You push an HTML file to WeChat via `--html`. Locally in the browser,
the page looks great — cards with background colors, gradient headers,
numbered steps, flexbox layouts, dark sections, rounded corners.
In WeChat's article editor / rendered page: **no background colors,
gradients are gone, flex/grid layouts collapsed, cards are invisible,
step numbers don't show, dark sections have white background.**

## Root Cause

WeChat's WYSIWYG editor strips the following from `--html` content:

| Your HTML | WeChat sees |
|-----------|-------------|
| `<style>` block with all your CSS | Nothing — `<style>` is removed entirely |
| `background:` on `<div>`/`<section>` | Stripped (only works on `<table>` cells in some cases) |
| `background: linear-gradient(...)` | Stripped (gradients not supported) |
| `display: flex`, `display: grid` | Stripped — layout collapses |
| `::before`, `::after` | Stripped — content missing |
| `position: absolute` for step numbers | Stripped — overlays break |
| `box-shadow` | Stripped (unreliable) |
| `border-radius` on `<thead>` | Stripped |
| `-webkit-background-clip: text` | Stripped |
| CSS variables `var(--accent)` | Stripped — colors fall back to nothing |

## Why It's Confusing

The HTML renders perfectly in every browser. The error is **invisible
until the article hits WeChat's server-side HTML sanitizer**. There's
no local preview that reveals the problem. You only discover it after
creating a draft and viewing it on mp.weixin.qq.com.

## The Fix: Use `--markdown` Instead

```bash
# ❌ Don't do this with styled HTML:
md2wechat --html article.html --title "..." --cover <url>

# ✅ Do this instead:
# 1. Convert your content to Markdown
# 2. Push via --markdown
md2wechat --markdown article.md --style tech --author "Name" --cover <url>
```

The `md2wechat` CLI's MD2WeChat converter automatically generates
WeChat-compatible HTML from Markdown — inline styles only, no `<style>`
blocks, proper table-based cards, safe color/border usage.

## When --html IS the Right Choice

Only when your HTML is **already WeChat-compatible**:
- All styles inline (`style="color:#333;margin:8px 0;"`)
- No `<style>` block, no `<link>` stylesheet
- No CSS variables, no gradients
- No flex/grid — use `<table>` or stacked blocks
- Pseudo-element content (`::before` bullets) written as literal `<span>` tags
- Manual numbering instead of `counter()`
- Solid `background-color` only (on `<td>` inside `<table>` for reliability)
- No `box-shadow`, `transform`, `transition`, `opacity`

## Diagnosis Checklist

When a user says "my HTML's CSS is missing in WeChat":

- [ ] Did they use `--html` or `--markdown`?
- [ ] If `--html`: does the HTML have `<style>` blocks? CSS vars? gradients? flex/grid?
- [ ] Recommendation: convert to Markdown and use `--markdown`
- [ ] If they must use `--html`: run `wechat_article_css_dl` check-mode first to detect violations

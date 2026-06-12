---
name: wechat_article_css_dl
description: Inspect HTML for WeChat CSS compatibility issues and apply micro-fixes to make it render correctly in WeChat Official Account articles. Use when you have raw HTML (from a video transcript, web page, AI output) that needs tuning for WeChat without a full markdown rewrite. Does NOT handle WeChat API calls (use wechat_article_push_dl for that).
contract_version: "1.0"
---

# wechat_article_css_dl

Micro-tune HTML to follow WeChat article CSS rules. This skill detects violations, reports them, and applies targeted fixes — no full rewrite, no markdown conversion.

## Quick Reference

Check an HTML file for WeChat CSS violations:

```bash
python3 -c "
import re, sys

with open('input.html') as f:
    html = f.read()

violations = []

if re.search(r'<style[^>]*>', html):
    n = len(re.findall(r'<style[^>]*>', html))
    violations.append(f'{n} <style> block(s) found — WeChat strips these. Move to inline styles.')

if re.search(r'--[\w-]+:', html):
    n = len(re.findall(r'--[\w-]+:', html))
    violations.append(f'{n} CSS variable(s) found (e.g. --var) — hardcode hex values instead.')

if re.search(r'linear-gradient|radial-gradient', html):
    n = len(re.findall(r'linear-gradient|radial-gradient', html))
    violations.append(f'{n} gradient(s) found — replace with solid background-color.')

if re.search(r'display:\s*flex|display:\s*inline-flex', html):
    n = len(re.findall(r'display:\s*flex|display:\s*inline-flex', html))
    violations.append(f'{n} flexbox layout(s) found — use <table> or stacked blocks instead.')

if re.search(r'display:\s*grid|display:\s*inline-grid', html):
    violations.append('grid layout(s) found — use <table> or stacked blocks instead.')

if re.search(r'::before|::after', html):
    n = len(re.findall(r'::before|::after', html))
    violations.append(f'{n} ::before/::after pseudo-element(s) found — write literal characters instead.')

if re.search(r'counter-increment|counter\(', html):
    violations.append('counter/counter-increment found — use manual numbering.')

if re.search(r'@media', html):
    violations.append('@media query found — WeChat ignores them. Single layout only.')

if re.search(r'-webkit-background-clip', html):
    violations.append('-webkit-background-clip found — replace gradient text with solid color.')

if re.search(r'box-shadow', html):
    violations.append('box-shadow found — unreliable in WeChat. Remove or replace with border.')

if re.search(r':hover|:nth-child|:last-child|:first-child|:nth-of-type', html):
    violations.append(':hover/:nth-child/:last-child pseudo-classes found — apply inline styles to every element directly.')

if not violations:
    print('No WeChat CSS violations found.')
else:
    print(f'Found {len(violations)} issue(s):')
    for v in violations:
        print(f'  - {v}')
    sys.exit(1)
"
```

## Input Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| HTML file path | `string` | Yes | Path to HTML file to check/fix |
| Fix mode | `boolean` | No | `true` to auto-fix violations (default: check-only) |

## Output Contract

```json
{
  "status": "clean | fixed | violations_found",
  "violations": ["description of each issue"],
  "fixes_applied": ["description of each fix"],
  "output_path": "path/to/fixed.html"
}
```

## Preconditions

- Input HTML file exists and is readable
- Python 3 available
- For check-only: no side effects
- For fix mode: output file path known

## Process

1. **Read** the HTML file.
2. **Scan** for all WeChat violations.
3. **Report** all violations found, grouped by type.
4. **If fix mode** — apply automated micro-fixes per violation.
5. **Write** fixed HTML to a new file (never overwrite source).
6. **Return** status summary.

## Micro-Fixes Applied

| Violation | Fix Strategy | Automated? |
|-----------|-------------|:----------:|
| `<style>` block | Extract rules → convert to inline styles on matching elements | Partial |
| CSS variable `--var` | Hardcode the actual hex/rgb value | Manual (need to know value) |
| `linear-gradient` | Replace with solid `background-color` (#1a1a2e / fallback) | Yes |
| `display: flex` / `grid` | Replace with `display: block` (may need manual `<table>` layout) | Auto-fallback |
| `::before` / `::after` | Remove from CSS, content must be added as literal `<span>` | Partial |
| `counter-increment` | Remove, replace with explicit numbers | Partial |
| `-webkit-background-clip: text` | Remove property, add solid `color` fallback | Yes |
| `box-shadow` | Remove property | Yes |
| `@media` | Remove entire block | Yes |
| `:hover` / `:nth-child` | Remove pseudo-class rules from CSS | Automated for `<style>` blocks |

### Automated fix script

```bash
python3 -c "
import re, sys

with open('$INPUT') as f:
    html = f.read()

fixes = []

# Fix 1: remove ::before/::after blocks
html, n = re.subn(r'::before\s*\{[^}]*\}', '', html)
if n: fixes.append(f'Removed {n} ::before block(s) — content must be added as literal HTML')
html, n = re.subn(r'::after\s*\{[^}]*\}', '', html)
if n: fixes.append(f'Removed {n} ::after block(s) — content must be added as literal HTML')

# Fix 2: remove @media blocks
html, n = re.subn(r'@media[^{]*\{[^}]*\}', '', html)
if n: fixes.append(f'Removed {n} @media block(s)')

# Fix 3: remove webkit-background-clip + text-fill
html, n = re.subn(r'-webkit-background-clip:\s*text;?\s*-webkit-text-fill-color:\s*transparent;?', '', html)
if n: fixes.append(f'Removed {n} -webkit-background-clip/text-fill (gradient text)')

# Fix 4: remove box-shadow
html, n = re.subn(r'box-shadow:\s*[^;]+;', '', html)
if n: fixes.append(f'Removed {n} box-shadow(s)')

# Fix 5: replace linear-gradient with solid fallback
html, n = re.subn(r'background:\s*linear-gradient[^;]+;', 'background: #1a1a2e;', html)
if n: fixes.append(f'Replaced {n} linear-gradient(s) with solid fallback')
html, n = re.subn(r'background:\s*radial-gradient[^;]+;', 'background: #1a1a2e;', html)
if n: fixes.append(f'Replaced {n} radial-gradient(s) with solid fallback')

# Fix 6: replace CSS variable refs in inline styles with accent color
html, n = re.subn(r'var\(--[\w-]+\)', '#e8633a', html)
if n: fixes.append(f'Replaced {n} CSS variable reference(s) with #e8633a — may need manual value tweak')

# Fix 7: remove counter-increment/reset
html, n = re.subn(r'counter-increment:\s*[^;]+;', '', html)
if n: fixes.append(f'Removed {n} counter-increment(s)')
html, n = re.subn(r'counter-reset:\s*[^;]+;', '', html)
if n: fixes.append(f'Removed {n} counter-reset(s)')

# Fix 8: replace display:flex/grid with block
html, n = re.subn(r'display:\s*flex\b', 'display: block', html)
if n: fixes.append(f'Replaced {n} display:flex with display:block — may need manual table layout')
html, n = re.subn(r'display:\s*(inline-)?grid\b', 'display: block', html)
if n: fixes.append(f'Replaced {n} display:grid with display:block')

# Fix 9: remove opacity
html, n = re.subn(r'opacity:\s*[^;]+;', '', html)
if n: fixes.append(f'Removed {n} opacity(s) — unreliable in WeChat')

outpath = '$OUTPUT'
with open(outpath, 'w') as f:
    f.write(html)
print(f'Applied {len(fixes)} fix(es)')
for f in fixes:
    print(f'  - {f}')
"
```

## WeChat CSS Compatibility Reference

### ✅ Works (inline only)
- `color`, `background-color`, `font-size`, `font-weight`, `font-style`, `font-family`
- `text-align`, `text-decoration`, `line-height`
- `margin`, `padding`, `border`, `border-collapse`, `border-left`, `border-top`, `border-bottom`
- `width`, `height`, `max-width`
- `display: block`, `display: inline-block`, `display: inline`
- `position: relative`, `position: absolute`, `top`, `left`
- `vertical-align`, `list-style`
- `border-radius` (simple uniform)
- `background` (solid colors only)

### ❌ Stripped / Broken
| Feature | Replacement |
|---------|-------------|
| `<style>` block | Inline `style=""` on each element |
| CSS vars `--var` | Hardcode hex colors |
| `linear-gradient` | Solid `background-color` |
| `-webkit-background-clip: text` | Solid `color` |
| `display: flex` / `grid` | `<table>` or stacked `<div>` |
| `::before` / `::after` | Literal `<span>▸</span>` |
| `counter-increment` | Manual 1, 2, 3... |
| `:hover` / `:nth-child` | Apply to every element |
| `@media` | Single mobile layout |
| `box-shadow` | Remove or use `border` |
| `transform` / `transition` / `animation` | Remove entirely |
| `opacity` | Remove (unreliable) |

## Verification

1. Check-mode on raw HTML with `<style>` block, gradients, flex → confirm all detected
2. Fix-mode on same file → confirm fixes applied, output path reported
3. Open fixed HTML in browser → visually acceptable
4. Push with `wechat_article_push_dl` → renders correctly in WeChat

## Related Skills

- `wechat_article_push_dl` — Push HTML to WeChat drafts (handles creds, cover, API errors)
- `md2wechat` — Convert Markdown to WeChat-compatible HTML (MD2WeChat converter)
- `ato-arche-dl` — Atomic skill workflow design pattern
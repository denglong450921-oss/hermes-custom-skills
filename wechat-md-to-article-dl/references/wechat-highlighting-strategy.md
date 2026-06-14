# WeChat Article Highlighting Strategy

Source: UX research from a WeChat CSS deep-dive article reviewed
during a 2026-06-14 session.  Distilled into rules the converter
already implements, plus strategic guidance for manual authoring.

## Core Principle

> Highlight = structure + contrast + spacing, not decoration.

WeChat renders are not a full web environment.  The goal is reading
signals, not visual design.

## Safe CSS for WeChat

| ✅ Safe | ⚠️ Partial | ❌ Avoid |
|---------|-------------|---------|
| `color` | `border-radius` (some clients ignore) | `position: absolute/fixed` |
| `font-size` | `box-shadow` (often dropped) | `flex / grid` |
| `font-weight` | | `animation` |
| `line-height` | | `filter` |
| `margin` / `padding` | | `transform` |
| `background-color` | | pseudo-elements (`::before/::after`) |
| `border` / `border-left` | | advanced selectors |
| `text-align` | | external CSS files |

## The 70/20/10 Ratio

A high-class WeChat article follows this composition:

```
70% plain text
20% structured cards (callouts, insight boxes)
10% strong highlight blocks (key judgments)
```

## Highlight Techniques (Reliable in WeChat)

### 1. Left-border card (most professional)
```html
<div style="border-left:4px solid #2F6FED;padding:12px 14px;background:#F5F7FF;">
  <b>Key insight:</b> Content here.
</div>
```
→ Used by the converter for `:::key`, `:::strategy`, `:::thinking`, `:::problem`.

### 2. Bold + colour (minimal, works everywhere)
```html
<span style="font-weight:700;color:#2563EB;">key term</span>
```
→ Used by the converter for `==core concept==`.

### 3. Strong conclusion card (sparingly — max 2–3 per article)
```html
<div style="padding:14px;background:#111827;color:#ffffff;border-radius:10px;">
  Final conclusion here.
</div>
```

### 4. Numbered insight cards (for step-by-step methods)
```html
<div style="padding:12px;border:1px solid #E5E7EB;border-radius:10px;">
  <b>01｜Demand first</b><br>
  Validate before building.
</div>
```

### 5. Inline tag highlight (for labels / micro-emphasis)
```html
<span style="background:#FEF3C7;padding:2px 6px;border-radius:4px;">key conclusion</span>
```
→ Not used by the converter — background pills add palette complexity.

## Anti-Patterns

| Mistake | Why |
|---------|-----|
| Over-decorating (shadows, gradients everywhere) | Looks like marketing spam |
| Too many highlights per paragraph | Nothing stands out |
| Mixed colour systems (blue + green + red + purple cards) | Breaks design language |
| Background pills for inline emphasis | Adds hex colours, Dark Mode fragile |

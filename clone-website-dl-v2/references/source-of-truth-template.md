# <PageName> Static Source Of Truth

Canonical static reconstruction record for `<URL or local source>`.

Complete this before implementation. Derived component specs and code must trace back here.

## Page Identity

- **URL/source:** `<https://example.com/path>`
- **Page slug:** `<path-slug>`
- **Captured at:** `<timestamp>`
- **Scope:** `<full page | section | multi-page>`
- **Project root:** `<path>`
- **Resource budget:** `500 MB` unless overridden

## Visual References

- **Desktop 1440px:** `docs/design-references/<page>-desktop.png`
- **Tablet 768px:** `docs/design-references/<page>-tablet.png` or `<reason omitted>`
- **Mobile 390px:** `docs/design-references/<page>-mobile.png`

## Load Completion Contract

- **Load report:** `docs/research/pages/<page-slug>/load-report.json`
- **Critical selectors:** `<selectors that must be visible before extraction>`
- **Network quiet window:** `<milliseconds and ignored request classes/domains>`
- **DOM stability samples:** `<element count/text length/height samples>`
- **Lazy-load warming:** `<scroll route used>`
- **Fonts readiness:** `<document.fonts.ready | timeout>`
- **Slow/unresolved elements:** `<N/A or selector -> blocker/placeholder plan>`
- **Scrapling fallback:** `<not needed | used with config | unavailable>`

## Static Fidelity Policy

- **Animations:** `<disabled | replaced by static poster | not present>`
- **Videos/canvas/Lottie:** `<localized | placeholder | static frame | not present>`
- **Dynamic widgets:** `<static state selected and why>`

## Global Styles

- **Body font:** `<family, weight, size, line-height>`
- **Heading fonts:** `<family, weights, sizes>`
- **Colors:** `<background, foreground, primary, muted, borders, accents>`
- **Container system:** `<max widths, gutters, breakpoints>`
- **Spacing rhythm:** `<common px values>`

## Section Inventory

Create one entry per visible section in exact top-to-bottom order.

### `<section-id>` - `<visible heading or role>`

- **Order:** `<N>`
- **Component target:** `src/components/sections/<ComponentName>.*`
- **Visual evidence:** `<screenshot path>`
- **DOM evidence:** `<saved html/json path if available>`
- **Layout pattern:** `<hero | card grid | editorial block | pricing | logo strip | footer | ...>`
- **Dimensions:** `<desktop/tablet/mobile width, height, padding, gaps>`
- **Computed CSS:** `<exact values for container and key children>`
- **Text content:** `<verbatim visible text>`
- **Assets:** `<source URL -> local path or placeholder id>`
- **Static replacement:** `<N/A or placeholder/static poster contract>`
- **Responsive behavior:** `<desktop/tablet/mobile changes>`
- **Derived spec:** `docs/research/components/<ComponentName>.spec.md`

## Header/Nav Contract

- **Component target:** `src/components/Header.*`
- **Logo:** `<text/svg/image local path>`
- **Nav items:** `<label -> href>`
- **CTA items:** `<label -> href>`
- **Desktop layout:** `<measurements>`
- **Mobile layout:** `<measurements and static menu treatment>`

## Footer Contract

- **Component target:** `src/components/Footer.*`
- **Groups:** `<heading -> links>`
- **Legal/social/newsletter:** `<content>`
- **Desktop layout:** `<measurements>`
- **Mobile layout:** `<measurements>`

## Asset Manifest

| ID | Source URL | Local Path Or Placeholder | Size | Used By | Status |
|---|---|---|---:|---|---|
| `<asset-id>` | `<url>` | `<public/assets/...>` | `<bytes>` | `<section-id>` | `<localized | placeholder | skipped>` |

## Placeholder Manifest

| ID | Reason | Original URL | Aspect Ratio | Visual Contract | Used By |
|---|---|---|---|---|---|
| `<placeholder-id>` | `<over-budget | blocked | dynamic-only>` | `<url>` | `<w:h>` | `<color, label, occupied area>` | `<section-id>` |

## QA Acceptance Contract

- **Static visual sections:** `<1.0%` pixel mismatch
- **Text-heavy sections:** `<2.0%` pixel mismatch
- **Geometry drift:** `<=3px`
- **Broken localized assets:** `0`
- **Undocumented placeholders:** `0`
- **Duplicated header/footer markup:** `0`

## Readiness Checklist

- [ ] Load-completion report is linked and passing, or blockers are recorded.
- [ ] Desktop and mobile screenshots are linked.
- [ ] Every visible section is listed in order.
- [ ] Header/nav and footer contracts are separate.
- [ ] CSS values come from computed styles, not estimates.
- [ ] Visible text is verbatim.
- [ ] Asset status is localized, placeholder, or skipped with reason.
- [ ] Placeholder contracts preserve visual occupancy.
- [ ] Static treatment for motion/dynamic media is documented.
- [ ] Responsive behavior is recorded.
- [ ] Component specs are linked or scheduled.

## Change Log

- `<timestamp>`: `<evidence or contract change>`

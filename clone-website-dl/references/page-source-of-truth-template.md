# <PageName> Source of Truth

> Canonical reconstruction record for `<URL>`.
> Complete this file before writing code for this page. Derived component specs and implementation must follow it exactly.

## Page Identity
- **URL:** `<https://example.com/path>`
- **Page slug:** `<path-slug>`
- **Captured at:** `<timestamp>`
- **Scope:** `<full page | named section>`
- **Evidence directory:** `docs/research/pages/<page-slug>/`

## Visual References
- **Desktop screenshot (1440px):** `docs/design-references/<page>-desktop-full.png`
- **Tablet screenshot (768px):** `docs/design-references/<page>-tablet-full.png`
- **Mobile screenshot (390px):** `docs/design-references/<page>-mobile-full.png`

## Global Page Contract
- **Body computed style:** `<font-family, background, color, line-height>`
- **Container system:** `<max-width, gutters, breakpoints>`
- **Header/footer variants:** `<exact variant used on this URL>`
- **Interaction model:** `<static | scroll-driven | click-driven | mixed>`
- **Third-party replacements:** `<N/A or explicit static replacement>`

## Section Inventory

Create one entry for every visible section in top-to-bottom order.

### `<section-id>` — `<visible heading>`
- **Order:** `<N>`
- **Layout pattern:** `<hero | sticky-scroll | alternating row | card grid | carousel | footer | ...>`
- **DOM evidence:** `docs/research/pages/<page-slug>/sections/<section-id>.html`
- **Visual evidence:** `docs/design-references/<page>-<section-id>-desktop.png`
- **Dimensions:** `<desktop/tablet/mobile width, height, padding, gap>`
- **Computed styles:** `<exact getComputedStyle values for container and key children>`
- **Text content:** `<verbatim headings, body, labels, CTA text>`
- **Assets:** `<resolved local paths or exact source URLs>`
- **Visual occupancy:** `<which media fills the region, or documented booth fallback when unavailable>`
- **States and triggers:** `<default, hover, click, scroll thresholds, transitions>`
- **Responsive behavior:** `<what changes at each breakpoint>`
- **Derived spec:** `docs/research/components/<component>.spec.md`

## Asset Manifest
- `<asset-id>`: `<source URL>` → `<local public path>` used by `<section-id>`

## Route And Link Contract
- `<visible label>` → `<exact href or route>`

## Animation Contract
- **Audit report:** `docs/research/animations/<page>.animations.json`
- **Animated regions:** `<region → trigger, duration, easing, start/mid/end styles>`
- **Responsive differences:** `<desktop/tablet/mobile>`
- **Reduced motion:** `<stable readable state>`
- **Fallbacks:** `<N/A or evidence-backed poster/static composition>`

## Strict Spacing Contract
- **Audit report:** `docs/research/spacing/<page>.spacing.json`
- **Section boundaries:** `<section → desktop/tablet/mobile top, bottom, height>`
- **Landmark anchors:** `<heading/media/CTA → viewport x, y, width, height>`
- **Sibling gaps and edge insets:** `<exact px values>`
- **Intentional whitespace:** `<region → measured boundaries + reason>`
- **Breakpoint deltas:** `<what changes and by how many px>`

## Known Constraints
- `<N/A or evidence-backed limitation>`

## QA Acceptance Contract
- **QA outputs:** `docs/qa/<page-slug>/`
- **Static-section pixel mismatch:** `<0.5%`
- **Text-heavy-section pixel mismatch:** `<1.5%`
- **Geometry drift:** `<=2px`
- **Dynamic-region masks:** `<N/A or region + reason>`
- **Missing visible assets:** `0`
- **Unexplained blank regions:** `0`
- **Broken network assets:** `0`

## Readiness Checklist
- [ ] Desktop, tablet when relevant, and mobile screenshots are linked.
- [ ] Every visible section is listed in exact top-to-bottom order.
- [ ] Layout pattern and dimensions are recorded for every section.
- [ ] CSS values come from `getComputedStyle()`, not estimates.
- [ ] Visible text is copied verbatim.
- [ ] Assets are resolved and linked to sections.
- [ ] Reachable media assets are visibly rendered, not merely referenced.
- [ ] Unavailable media assets have deliberate booth fallbacks.
- [ ] Large blank regions are confirmed intentional or removed.
- [ ] Responsive changes and interactive states are documented.
- [ ] Animated pages have a pre-freeze audit report, start/mid/end states, and reduced-motion behavior.
- [ ] Spacing audit records section boundaries, landmark anchors, sibling gaps, edge insets, and intentional whitespace.
- [ ] Unresolved conflicts, blanks, and placeholders are removed.
- [ ] Component specs link back to this page and section IDs.
- [ ] Deterministic screenshots, pixel diff reports, and geometry reports pass the QA acceptance contract.

## Change Log
- `<timestamp>`: `<what evidence changed and which derived specs/code need reconciliation>`

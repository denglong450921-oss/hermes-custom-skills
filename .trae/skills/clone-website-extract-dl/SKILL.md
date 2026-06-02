---
name: clone-website-extract-dl
description: >
  Extract the rendered source of truth for a website-cloning workflow. Use when
  reverse-engineering a live page or section before implementation: run
  preflight checks, select an extraction mode, capture screenshots, computed
  CSS, assets, responsive states, motion, spacing, and a canonical per-page
  SOURCE_OF_TRUTH.md. This is the evidence phase used by clone-website-dl.
compatibility: Rendered browser automation, Playwright, Firecrawl, or curl depending on target complexity.
---

# Clone Website Evidence Extraction

Own the evidence required to build a faithful clone. Do not write clone
components in this skill. Produce a canonical page record that a builder can
execute without guessing.

Treat the directory containing this file as `CLONE_EXTRACT_DIR`.

## Input

```json
{
  "url": "https://example.com/page",
  "project_root": "/path/to/clone",
  "scope": "full | partial | multi-page | customized",
  "section": "optional semantic section name"
}
```

## Output

```json
{
  "status": "ready | blocked | partial",
  "page_slug": "home",
  "source_of_truth": "docs/research/pages/home/SOURCE_OF_TRUTH.md",
  "screenshots": [],
  "reports": [],
  "constraints": []
}
```

## Mode Selection

Run the bundled preflight audit first:

```bash
bash "$CLONE_EXTRACT_DIR/scripts/preflight-audit.sh" "$URL"
```

Choose the strongest available capability:

| Capability | Example check | Use |
|---|---|---|
| Interactive browser automation | Browser MCP or Camofox health check | Preferred for rendered CSS and interaction sweeps |
| Headless browser scripting | `python3 -c "import playwright"` | Full rendered fallback for SPAs and SSR pages |
| HTML/content extraction | Firecrawl MCP or `curl` | Fallback for SSR/static content only |

Use Camofox or another interactive browser when available. Use Playwright as the
all-round rendered fallback. Use Firecrawl or curl only when HTML already
contains meaningful content. Stop on a SPA when no rendered-browser capability
is available.

## Scope Routes

- Full clone: capture every section.
- Partial clone: capture only the named section plus enough adjacent context to
  identify it. Capture desktop and mobile screenshots and show them to the user.
- Multi-page clone: repeat the full evidence depth for every URL. A complete
  homepage does not authorize coding a sub-page.
- Customized clone: capture original values before recording overrides.

## Evidence Workflow

### 1. Capture rendered references

Save desktop `1440px`, tablet `768px` when layout changes, and mobile `390px`
screenshots under `docs/design-references/`.

**CRITICAL: Anti-Animation & Force Visibility**
Before taking full-page screenshots, you MUST:
- Inject CSS to force `opacity: 1 !important`, `visibility: visible !important`, and `transform: none !important` on elements with animation classes (e.g., `[class*="animate"]`, `[class*="hpc-"]`).
- Disable all transitions and animations (`animation-duration: 0s !important`).
- Perform a full scroll sweep to trigger lazy-loaded assets and ScrollMagic-style triggers.
- Wait at least 2 seconds after scrolling back to the top to ensure the layout has stabilized.

Use `scripts/extract-playwright.py` when a reusable headless extraction run is
helpful. Read `references/playwright-extraction.md` for the rendered-browser
pattern and `references/firecrawl-mode.md` for HTML-only fallback behavior.

### 2. Capture content, CSS, and assets

Use exact values from `getComputedStyle()`. Never estimate CSS from a
screenshot.

- Run `scripts/discover-assets.js` to enumerate images, video, backgrounds,
  fonts, SVG pressure, and favicons.
- Run `scripts/extract-component-css.js` for per-section computed CSS.
- Run `scripts/extract-svgs.js` when inline SVGs need deduplication.
- Record lazy image placeholders and resolved `currentSrc` values after scroll.
- Record exact visible text, including non-English headings.
- Hand the companion QA skill's `scripts/verify-css.js` to downstream QA for
  original-versus-clone CSS verification.

### 3. Record behavior

Complete a scroll sweep, click sweep, hover sweep, and responsive sweep. Save
the findings in `docs/research/BEHAVIORS.md`.

Identify the interaction model before implementation: static, click-driven,
scroll-driven, or time-driven. Capture every visible state, not just the
default.

### 4. Record animation evidence

When motion markers are present, run:

```bash
node "$CLONE_EXTRACT_DIR/scripts/audit-animations.mjs" \
  --url "$URL" \
  --out docs/research/animations \
  --label "$PAGE_SLUG"
```

Audit animations before injecting animation-disabling CSS or taking
deterministic screenshots. Record start/mid/end styles, timeline values,
responsive differences, and reduced-motion behavior. Reproduce motion with the
simplest faithful route: CSS transitions, `IntersectionObserver`, scroll progress,
explicit state, or reachable media.
Do not default every animated region to a static block.
Read `references/animation-reconstruction.md`.

### 5. Record a strict spacing graph

Run:

```bash
node "$CLONE_EXTRACT_DIR/scripts/audit-spacing.mjs" \
  --url "$URL" \
  --out docs/research/spacing \
  --label "$PAGE_SLUG"
```

Record landmark rectangles, section boundaries, sibling gaps, edge insets,
alignment anchors, and breakpoint-specific deltas. Classify large whitespace as
intentional or unexplained from measured boundaries and visible media.
Do not replace a spacing graph with approximate section heights.

### 6. Enforce visible asset occupancy

If the original exposes media and the asset is reachable, render it. Do not hide available
assets with `display: none`, `visibility: hidden`, `opacity: 0`, off-screen
placement, or oversized empty wrappers.

If media is genuinely unavailable after fallback attempts, specify a deliberate
booth fallback that preserves the section's occupied area, hierarchy, color,
and balance. Record the substitution in the canonical source of truth. Treat
unexplained blank regions as extraction failures.

### 7. Write the canonical page record

Create:

```text
docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md
```

Start from `references/page-source-of-truth-template.md`. It is the unique
canonical authority for screenshots, topology, exact text, computed CSS,
assets, routes, animations, strict spacing, responsive states, QA acceptance,
known constraints, and the Modification Ledger.

Run the source-of-truth gate:

```bash
node "$CLONE_EXTRACT_DIR/scripts/validate-source-of-truth.mjs" \
  "docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md" \
  "$PWD" \
  --stage=extraction
```

Require exit code `0`. If the gate fails, return to extraction. Do not code yet.

Before every later fidelity modification, treat a non-zero validator exit as a
hard stop. Reconcile in this order:

1. Record the new live evidence and reason in the `Modification Ledger`.
2. Update the source of truth first.
3. Reconcile derived component specs.
4. Modify implementation.
5. Re-run the source-of-truth validator, build, occupancy checks, and QA.

## Recovery

| Failure signal | First response | Final fallback |
|---|---|---|
| Preflight script unavailable | Run inline SPA and transport checks | Record unavailable audit and continue only with sufficient evidence |
| Browser navigation blocked | Check headers and alternate rendered mode | Ask for access, screenshots, or assets |
| Lazy media unresolved | Scroll, wait, and inspect `data-src` | Record fallback URL or booth requirement |
| Motion state unclear | Increase samples and inspect trigger points | Record limitation and block unsupported implementation |
| Canonical record incomplete | Re-run focused extraction | Stop before build |

## Verification

Before handing off to `clone-website-build-dl`, confirm:

- The canonical page record passes the extraction validator.
- Screenshots exist for required viewports.
- Every section has exact content, layout pattern, assets, and CSS evidence.
- Behavior, animation, and spacing reports are linked.
- Visible media has either a reachable asset or a documented booth fallback.

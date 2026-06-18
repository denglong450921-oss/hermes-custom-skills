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

> **Field Notes:** For common extraction pitfalls, edge cases, and proven fixes,
> see clone-website-dl's consolidated Field Notes section (GWT/JS apps, lazy-load,
> CDN blocks, email obfuscation, CORS, CSS-illustrated content, logo-strip detection,
> `&nbsp;` traps, `page.evaluate()` gotchas, and more).

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

**GWT / JS-heavy app extraction:** Some pages (e.g. login, checkout, dashboard)
are built with GWT or similar JS frameworks where the HTML `<body>` contains
only script tags and a thin shell. The visible UI is rendered entirely by
client-side JavaScript into auto-generated DOM (opaque class names, deeply
nested divs, no semantic HTML). **Approach:** use Playwright for full JS
rendering. Extract only: (1) visible text via `body.innerText`, (2) visual
layout via screenshots (desktop + mobile), (3) computed CSS of key interactive
elements (buttons, inputs, cards). Do NOT try to extract semantic DOM structure
or section topology — the auto-generated DOM does not reflect the source
layout. The clone will be a visual re-creation, not a structural port.
Document as "GWT/JS-rendered app — visual clone only" in the source of truth.

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

**Mobile screenshot lazy-load trap:** The bundled `extract-playwright.py`
captures the mobile screenshot BEFORE the lazy-image scroll pass. On pages
with heavy lazy-loading (`data-src`, `data-lazy`) or JS-triggered animation
reveals, the mobile screenshot shows blank/placeholder regions.
**Fix:** After the automated script, re-capture with a slow scroll: scroll in
~200px steps with 200-500ms waits to trigger intersection-observers and lazy
bindings, then back to top, wait 2s, take full-page screenshot.

**Force-load unresolved lazy images:** If verification shows `loaded < total`,
run inside `page.evaluate()`:

```javascript
document.querySelectorAll('img[data-src]').forEach(img => {
  if (img.dataset.src) img.src = img.dataset.src;
});
document.querySelectorAll('img[data-lazy]').forEach(img => {
  if (img.dataset.lazy) img.src = img.dataset.lazy;
});
```

Wait 2-3s, then verify. Remaining failures are typically: (a) hidden-viewport
variants for that breakpoint, (b) empty `src` placeholder slots in JS
carousels, or (c) tracking pixels. Document each in the source of truth.

**Verify image load after capture:** Run:

```javascript
const imgs = Array.from(document.querySelectorAll('img')).map(i => ({
  src: i.currentSrc || i.src,
  loaded: i.complete && i.naturalWidth > 0
}));
```

Print `loaded/N`. For unloaded images inspect className, parent, and
visibility via `!i.complete || i.naturalWidth === 0 && i.offsetParent !== null`.

Use `scripts/extract-playwright.py` when a reusable headless extraction run is
helpful. **Pitfall — shared output directory:** This script always writes to
`docs/design-references/`, regardless of page. When cloning multiple pages,
each run **overwrites** the previous page's evidence. Workaround: after each
page's extraction, immediately copy `docs/design-references/*` into
`docs/research/pages/<page-slug>/`, or use the script's second argument
(`output_dir`) to redirect.

Read `references/playwright-extraction.md` for the rendered-browser
pattern and `references/firecrawl-mode.md` for HTML-only fallback behavior.
animation reveals, the mobile screenshot will show blank/placeholder regions.
**Fix:** After the automated script completes, re-capture the mobile screenshot
with a slow scroll pass: scroll in ~200px steps with 200-500ms waits between
each step to trigger intersection-observers and lazy-load bindings. Scroll
back to top, wait 2s, then take the full-page screenshot.

**Force-load unresolved lazy images:** After the scroll pass, some images may
still show as not loaded (especially slider/fade-in images that load only when
made visible by JS). If a verification check shows `loaded < total`, run a
force-load pass inside `page.evaluate()`:

```javascript
document.querySelectorAll('img[data-src]').forEach(img => {
  if (img.dataset.src) img.src = img.dataset.src;
});
document.querySelectorAll('img[data-lazy]').forEach(img => {
  if (img.dataset.lazy) img.src = img.dataset.lazy;
});
```

Wait 2-3s after this, then verify load status again. Remaining failures are
typically: (a) hidden-viewport variants correct for that breakpoint,
(b) empty `src` placeholder slots in JS-driven carousels, or (c) tracking
pixels. Document these in the source of truth.

**Verify image load status after capture:** After each screenshot, run:

```javascript
const imgs = Array.from(document.querySelectorAll('img')).map(i => ({
  src: i.currentSrc || i.src,
  loaded: i.complete && i.naturalWidth > 0
}));
```

Print `loaded/N` to verify. For unloaded images, filter by
`!i.complete || i.naturalWidth === 0` and inspect className, parent element,
and visibility — this distinguishes genuine extraction gaps from expected
hidden/empty slots.

**CloudFront / CDN 403 downloads:** When downloading assets via `curl`, CDNs
like CloudFront may return `AccessDenied` (HTTP 403) for certain image paths.
This usually blocks slider images or dynamic asset paths while letting others
through. **Defense:** (1) try a browser-style `User-Agent` header first;
(2) if still blocked, check which images are actually accessible from the same
CDN origin and use a mobile/alternative variant as fallback (look for a parallel
path under `Mobile/`, `tablet/`, or a different size suffix); (3) if no variant
is accessible, try the path from the `data-src` or `data-lazy` attribute
instead of the `src` attribute; (4) record the substitution as a booth fallback
in the source of truth.

**CDN asset download — SVG screenshot limitation:** When CDN blocks direct
fetch of SVG images (badges, icons), `Playwright` element `.screenshot()`
throws `Unsupported screenshot mime type: image/svg+xml`. SVGs cannot be
extracted via element screenshot. Workaround: (1) try fetching SVG text via
`page.evaluate(fetch)` in the page context (fails if CDN has CORS), (2) create
an inline SVG approximation as a JSX component with matching dimensions and
text, or (3) use a descriptive text link as fallback. Record in Booth Fallback
Ledger.

Use `scripts/extract-playwright.py` when a reusable headless extraction run is
helpful. **Pitfall — shared output directory:** This script always writes to
`docs/design-references/`, regardless of page. When cloning multiple pages, each
run **overwrites** the previous page's evidence files (JSON + PNG). Workaround:
after each page's extraction, immediately copy the contents of
`docs/design-references/` into the page-specific directory under
`docs/research/pages/<page-slug>/`, or redirect the script's output via its
second argument (`output_dir`).

Read `references/playwright-extraction.md` for the rendered-browser
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
- **Cloudflare email obfuscation trap:** When the page uses `data-cfemail`
  attributes or `__cf_email__` spans, the raw HTML contains obfuscated email
  text. The real addresses appear only after the Cloudflare `email-decode.min.js`
  script runs in the browser. Always extract emails from the browser-rendered
  DOM (via `textContent` after JS execution) — do not copy them from the raw
  HTML source.
- **Non-breaking space (`&nbsp;`) extraction trap:** The original page may use
  `&nbsp;` (non-breaking space) between words (common in Chinese text to prevent
  orphaned fragments or to space CJK/Latin mixed phrases). Browser `innerText`
  collapses `&nbsp;` to a regular space, so the extracted text in the page record
  will not match the original's exact HTML. **Fix:** When extracting headings or
  visible text, cross-check against `innerHTML` or `textContent` (not `innerText`)
  for suspicious spaces. Note `&nbsp;` usage explicitly in the source of truth's
  exact-text entries. **In JSX:** render as `{'\u00A0'}` or the HTML entity
  `&nbsp;` (React does not escape HTML entities in JSX text children).
- **CDN-blocked image assets:** Some CDNs (CloudFront S3, Akamai hotlink
  protection) return 403 or `ERR_CONNECTION_CLOSED` when downloading images
  outside the browser. Downloaded file is ~263 bytes (XML error body) or curl
  returns exit code 35. Workflow:

  (1) try browser `User-Agent` header.

  (2) try alternative URL paths (mobile variant, different subdomain).

  (3) try Playwright `page.evaluate(fetch)` + `FileReader` base64 — if the
      CDN allows same-origin requests from the page context.

  (4) **Element screenshot fallback** — if fetch fails (CORS or connection
      closed) but images are visible on the rendered page, use:
      ```
      el = page.locator(f'img[src="{url}"]').first
      await el.screenshot(path=path)
      ```
      This works because the CDN already served the image to the browser's
      rendering engine even though it blocks cross-origin or direct fetch.
      **Pitfall — SVG images:** `.screenshot()` throws
      `Unsupported screenshot mime type: image/svg+xml` for SVG files.
      For SVGs, instead of element screenshot, fetch the SVG text content
      from the page context or use an inline SVG placeholder.

  (5) last resort: substitute a similar image and document in the Booth
      Fallback Ledger. Read `references/cdn-element-screenshot.md`.
- **Cross-origin CSS CORS trap:** When stylesheets are loaded from a CDN or
  different origin, `document.styleSheets[i].cssRules` is silently blocked by
  CORS. The sheets exist but `.cssRules` returns `null`. The bundled
  `scripts/extract-component-css.js` and `scripts/discover-assets.js` may
  return empty results. **Workaround:** Skip stylesheet-rule iteration for
  cross-origin sheets. Use `getComputedStyle()` on specific target elements
  (h1, p, .btn, body) via `page.evaluate()` instead. Fall back to manual
  Playwright extraction for critical CSS values.
- **Nav-detection trap when `<nav>` absent:** Not all sites use a `<nav>`
  element. Some use a `<div>` with header/nav classes. The automated script's
  `document.querySelector('nav')` returns `null` on these sites.
  **Workaround:** After the automated script, probe for sticky/fixed elements
  at `top:0` with multiple children and links: check
  `getComputedStyle(el).position` and `el.querySelectorAll('a').length > 2`.
  Capture the result via a supplemental Playwright script.
- **`page.evaluate()` gotcha — `forEach` + `break` throws at runtime:**
  `SyntaxError: Illegal break statement` occurs when using
  `Array.forEach()` with a `break` inside `page.evaluate()`. Use
  `for (let i = 0; i < arr.length; i++)` instead when the loop may need to
  break early (first-match searches, sticky-header detection).
- **CSS-illustrated content trap (SVG / div mockups):** Marketing pages often
  render important visual content through inline SVGs, CSS-styled divs, and
  container elements rather than `<img>` tags. Examples: device mockups
  (phone/tablet frames), dashboard graphs, animated shields, carrier/payment
  logo strips. Standard extraction that only enumerates `<img>` elements
  (`document.querySelectorAll('img')`) will miss these entirely, leading to a
  clone with prominent blank sections.
  **Detection pass — after image extraction, run:**
  ```javascript
  // Find large inline SVGs (visual illustrations, not icons)
  const svgs = [...document.querySelectorAll('svg')].filter(s =>
    s.getBoundingClientRect().width > 80 && s.getBoundingClientRect().height > 80
  );
  // Find visual divs (device frames, graph containers)
  const visualDivs = [...document.querySelectorAll('div')].filter(d => {
    const r = d.getBoundingClientRect();
    const s = getComputedStyle(d);
    return r.width > 60 && r.height > 60 &&
      (s.backgroundImage !== 'none' || s.backgroundColor !== 'rgba(0, 0, 0, 0)') &&
      d.children.length > 0 &&
      !d.innerText.trim();
  });
  ```
  **Action:** Record each visual SVG/div in the source of truth's section
  inventory with a note on how to reproduce (inline SVG, CSS background-image,
  or simplified approximation). Do not mark a section as "no media" when its
  visual content is CSS-rendered — the clone will look incomplete.
- Hand the companion QA skill's `scripts/verify-css.js` to downstream QA for
  original-versus-clone CSS verification.
- **`page.evaluate()` JavaScript gotcha — `forEach` does not support `break`:**
  When writing inline JS inside `page.evaluate()`, using `Array.forEach()` with
  a `break` statement throws `SyntaxError: Illegal break statement`. Use
  `for (let i = 0; i < arr.length; i++)` instead of `arr.forEach()` whenever
  the loop may need to `break` early (e.g. first-match searches, sticky-header
  detection). This is a runtime error that only surfaces when the evaluate
  call runs — it won't be caught by a linter on the Python/Node side.
- **Logo strips outside container (Ecwid pattern):** Payment and carrier logo
  strips in Ecwid pages are siblings of `.container`, not children. They sit
  directly inside the `<section>` alongside `<div class="container">`. The
  automated section extractor (which traverses `.container > .row > .col-*`)
  will MISS these. After automated extraction, always query:
  ```javascript
  document.querySelectorAll('.hpc-logos--pyments, .hpc-logos--shippings')
  ```
  Capture these as separate section-level children with their own HTML and
  computed styles. Record in the source of truth that the logos strip is
  a top-level sibling of the container, not nested inside it.

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

#### Validator gate — known regex checks

The validator checks with specific patterns. Common causes of failure and fixes:

| Check | What triggers failure | Required to pass |
|---|---|---|
| Missing section entries | No `###` subheadings in Section Inventory | Add at least one `### Section-name` |
| Animation audit report | "Audit report:" missing from Animation Contract | Add `- **Audit report:**` line |
| Spacing audit report | "Audit report:" missing from Strict Spacing Contract | Add `- **Audit report:**` line |
| Booth fallback | "booth" anywhere requires `## Booth Fallback Ledger` | Add the heading (can be empty) |
| Unchecked readiness items | Unchecked `[ ]` items block at extraction stage | Check all extraction-appropriate items |
| Angle-bracket placeholders | Any `<content>` not containing `\n` | Replace `<PageName>`, `<0.5%>`, etc. with real values |
| TODO/TBD/FIXME markers | Any of these keywords in content | Remove stub markers |
| Backtick paths | `` `docs/...` `` paths must exist as real files | Create stub files or remove backticks from future-artifact refs |

**Common friction:**
- Template contains `<PageName>`, `<0.5%>`, `<page-slug>` — replace ALL before first run.
- Text like `Mobile (<768px)` has angle brackets — rewrite as `(under 768px)` or `[br]` for `<br>`.
- `docs/qa/` and `docs/research/components/` refs point to future artifacts. Either create stub dirs or drop backticks from those lines.
- `## Booth Fallback Ledger` must be a top-level heading between Known Constraints and QA Acceptance Contract.

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
| CSS rules inaccessible (CORS) | Skip stylesheet iteration; use `getComputedStyle()` on specific target elements via `page.evaluate()` | Document CSS source as "getComputedStyle per-element" in source of truth |
| Asset download 403 / connection closed (CDN/CloudFront) | Add browser User-Agent header; try alternative variant (e.g. mobile image); check data-src/data-lazy for alternate URLs; use Playwright element screenshot on visible img | Record substitution as booth fallback in source of truth |
| Canonical record incomplete | Re-run focused extraction | Stop before build |

## Verification

Before handing off to `clone-website-build-dl`, confirm:

- The canonical page record passes the extraction validator.
- Screenshots exist for required viewports.
- Every section has exact content, layout pattern, assets, and CSS evidence.
- Behavior, animation, and spacing reports are linked.
- Visible media has either a reachable asset or a documented booth fallback.

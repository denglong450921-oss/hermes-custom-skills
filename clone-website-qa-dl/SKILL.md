---
name: clone-website-qa-dl
description: >
  Measure and converge website-clone fidelity after implementation. Use after
  clone-website-build-dl has produced a compiling clone: capture deterministic
  original and clone screenshots, compare pixels and geometry, verify CSS,
  inspect occupancy and interactions, record discrepancies, and repeat the
  evidence-first repair loop until completion thresholds pass.
compatibility: Playwright for capture and ImageMagick for pixel comparison.
---

# Clone Website Visual QA

Own fidelity measurement. Do not accept "looks close enough" as completion.

> **Field Notes:** For common QA pitfalls and proven fixes, see
> clone-website-dl's consolidated Field Notes section (animation-heavy pages,
> DOM vs CSS repair order, Next.js font fallback, &nbsp; traps, stat font-size
> verification, column gap checks, structural vs CSS pixel diff diagnosis,
> two-number diff reporting, ImageMagick version handling).

Treat the directory containing this file as `CLONE_QA_DIR`. Resolve the loaded
`clone-website-extract-dl/SKILL.md` path once and treat its containing directory
as `CLONE_EXTRACT_DIR`. Do not resolve bundled resources relative to the clone
project's working directory.

## Input

```json
{
  "original_url": "https://example.com",
  "clone_url": "http://localhost:3000",
  "source_of_truth": "docs/research/pages/home/SOURCE_OF_TRUTH.md",
  "dynamic_masks": []
}
```

## Output

```json
{
  "status": "passed | repair_required | blocked",
  "reports": [],
  "mismatches": [],
  "completion_gate_passed": false
}
```

## QA Workflow

### 0. Pre-flight: verify the clone server is serving a fresh build

Before running any capture, confirm the production server is serving the
current build's CSS:

```bash
CSS_URL=$(curl -s "$CLONE_URL" | grep -o '/_next/static/chunks/[^"]*\.css' | head -1)
curl -sL -w "%{http_code}" "$CLONE_URL$CSS_URL" | grep -q 200 || \
  { echo "CSS returns non-200 — server is running a stale build. Kill server, rm -rf .next, rebuild, restart."; exit 1; }
```

**CSS 500 / stale build trap:** When `npm run build` runs while a production
server (`npx next start`) is alive, or when the server is restarted without
rebuilding, the HTML references a new CSS hash that doesn't exist in the old
`.next/` directory, producing `500 Internal Server Error` for the CSS file.
Fix: kill server → `rm -rf .next` → `npm run build` → restart.

### 1. Validate the canonical record

```bash
node "$CLONE_EXTRACT_DIR/scripts/validate-source-of-truth.mjs" \
  "docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md" \
  "$PWD" \
  --stage=completion
```

### 2. Capture deterministic references

```bash
node "$CLONE_QA_DIR/scripts/capture-reference.mjs" --url "$ORIGINAL_URL" --out docs/qa/original
node "$CLONE_QA_DIR/scripts/capture-reference.mjs" --url "$CLONE_URL" --out docs/qa/clone
```

### 3. Compare pixels and geometry

```bash
node "$CLONE_QA_DIR/scripts/visual-diff.mjs" --reference docs/qa/original/home.desktop.png --candidate docs/qa/clone/home.desktop.png --out docs/qa/diff
node "$CLONE_QA_DIR/scripts/compare-geometry.mjs" --reference docs/qa/original/home.desktop.geometry.json --candidate docs/qa/clone/home.desktop.geometry.json --out docs/qa/diff --tolerance 2
```

Use `$CLONE_QA_DIR/scripts/verify-css.js` for critical typography, backgrounds, and CTA values.

### 4. Audit occupancy, interactions, and responsiveness

- No reachable media asset is hidden or broken.
- No unexplained blank region remains.
- Documented booth fallbacks occupy the intended visual region.
- Scroll, click, hover, and responsive states behave like the original.
- Console errors and broken network assets are zero.
- **Full text content verification:** Extract ALL visible text from each section of the original and compare with the clone. Don't just check headings — check numbers, labels, button text, and body paragraphs. The GlobalStats section on Ecwid's sell page has specific numbers (70+, 175, 50) and labels (40+ 支付网关, 175 国家/地区, 50 语言) that are easy to guess wrong. Compare section-by-section `innerText` from the original capture against the clone using Playwright evaluate.
- **Next.js font fallback — expected CSS diff:** Next.js font optimization inserts a `"<FontName> Fallback"` entry in the `fontFamily` computed style (e.g. `Montserrat, "Montserrat Fallback", Montserrat, sans-serif` vs original `Montserrat, sans-serif`). Mark as **expected** — do not count against CSS match.
- **Text fidelity — non-breaking spaces (`&nbsp;`):** The original may use `&nbsp;` in headings (CJK text). Browser `innerText` collapses `&nbsp;` to a regular space. Cross-check against `textContent` or `innerHTML` for CJK sections. In JSX, render as `&nbsp;` or `{'\u00A0'}`.
- **Section spacing check:** After capture, verify the gap between adjacent sections is consistent. Use `getBoundingClientRect()` for each section `id` — if section A's `bottom` equals section B's `top` (0px gap), the sections touch without breathing room. Each section should have explicit vertical padding.
- **Stat / number font-size verification:** Stat numbers (e.g. "70+", "175", "50") are often dramatically larger than expected — original marketing pages commonly use `206px` or similar heroic sizing. Never guess stat font sizes. Always extract via `getComputedStyle(element).fontSize` from the original page. Even a reasonable-looking `56px` is only ~25% of the intended size. The `+`/`%` superscript text also needs proportional sizing (typically ~half the number size).
- **Column layout gap check:** Bootstrap columns have no inherent gap between them (adjacent columns touch at 0px). Tailwind clones using `w-6/12` halves also touch by default. If the original feels cramped, the fix isn't to add gap to the original columns — check the outer HTML structure: image-illustration divs (SVGs, absolute-positioned mockups) are often siblings of the `.container`, not children. Absolute-positioned mockups with `left`/`right` offsets extend beyond their column bounds. Add `lg:gap-12` to the flex row AND reduce image `max-w` so oversized illustration images don't overflow their column.

### 5. Apply the measurable convergence gate

Acceptance thresholds:
- Static sections: `<0.5%` pixel mismatch.
- Text-heavy sections: `<1.5%` pixel mismatch.
- Geometry drift: `<=2px`.
- Missing visible assets: `0`.
- Unexplained blank regions: `0`.
- Broken network assets: `0`.

**When pixel diff exceeds thresholds but CSS values match perfectly:**
High pixel diff (~40-50%+) with close-to-100% CSS match comes from structural differences, not CSS inaccuracy.

| Source | Example | Action |
|--------|---------|--------|
| **Scope omission** | Cookie banner, analytics iframe, country selector, GTM, illustrative SVGs intentionally excluded | Document as expected diff. Exclude from convergence gate. |
| **Grid system difference** | Bootstrap (original) vs Tailwind (clone) — column widths, gutters differ by 1-15px | Geometry drift expected. Accept if under ~5% of page width. |
| **Page height mismatch** | Original taller due to extra illustrations | Compare only overlapping region (crop to min height). Report as primary metric. |
| **CSS value mismatch** | getComputedStyle values differ | Fix in components. Re-run QA. |
| **Different animation/JS behavior** | JS carousel vs static image | Mask as dynamic region or document as intentional simplification. |

**Report two pixel-diff numbers:** (1) Raw full-page, (2) Overlapping (crop to min height).

**Gate passes for structural diffs when:** CSS values match >=95%, overlapping pixel diff under threshold, all scope omissions documented, no blank regions or broken assets, console errors zero.

### 6. Route repairs evidence-first

1. Record stronger live evidence and QA report in source record's Modification Ledger.
2. Update canonical source of truth.
3. Reconcile component specs.
4. Modify implementation.
5. Re-run build, occupancy checks, and QA.

Never silently patch code while leaving the page record stale.

### 7. Optional iterative stability check

```bash
python3 "$CLONE_QA_DIR/references/iterative-qa.py" http://localhost:3459 50
```

## Component Relationship Graph

After acceptance, generate `docs/component-graph.json` and `docs/component-graph.md`.

## Recovery

| Failure signal | First response | Final fallback |
|---|---|---|
| Dynamic mismatch | Add documented mask only for genuinely dynamic regions | Re-extract interaction states |
| Geometry drift | Compare measured landmarks with canonical spacing graph | Return to focused evidence extraction |
| Broken assets | Restore reachable source media | Use documented booth fallback |
| Mixed iterative failures | Increase settle time and add scroll-then-wait | Flag manual review |
| High pixel diff with 100% CSS match | Categorize by source. Report overlapping-region pixel diff as primary metric. | Document expected diffs in QA appendix |
| Screenshot tooling unavailable | Compare manually and run CSS verification | Report blocked gate honestly |
| Stale production server (CSS 500) | Kill server, `rm -rf .next`, build, restart | Verify CSS 200 before re-running QA |

## Best Practices & Experience (Ecwid Project)

1. **Spacer Injection**: Use responsive spacers (`hidden lg:block lg:h-[xxxpx]`) to align vertical rhythm.
2. **Fuzzy Matching**: `compare-geometry.mjs` should use normalized class names for minor DOM variations.
3. **SVG Identity**: Detect SVGs via `<title>` or unique path data to avoid coordinate drift.
4. **Layout Patches**: When `bodyHeightDelta` persists, use `jq` to find the section where cumulative offset begins and apply localized padding.
5. **Stale-build detection**: Always verify CSS returns 200 before capturing references.
6. **ImageMagick command name**: `visual-diff.mjs` uses `magick` (v7). On systems with only `convert` (v6), symlink `magick→convert`.
7. **Column gap & image overflow**: Read `references/tailwind-column-spacing.md` for Bootstrap→Tailwind column spacing fixes and image sizing rules of thumb.
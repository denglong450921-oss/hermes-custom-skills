# Measurable Convergence Harness

Use this harness for every cloned page. Visual QA is a measured repair loop, not an eyeball-only review.

## Capture Contract

Capture the source and clone with identical desktop, tablet, and mobile viewports. The capture script disables animations and caret rendering, hides cookie-consent UI, warms lazy-loaded assets by scrolling, waits for fonts and images, then saves a full-page PNG and a DOM geometry snapshot.

```bash
node scripts/capture-reference.mjs --url https://example.com/path --out docs/qa/path/source --label path
node scripts/capture-reference.mjs --url http://localhost:4173/path --out docs/qa/path/clone --label path
```

## Diff Contract

Run the pixel diff and DOM geometry checks for each viewport. For section-level repair, crop matching source and clone sections before running the image diff.

```bash
node scripts/visual-diff.mjs \
  --reference docs/qa/path/source/path-desktop.png \
  --candidate docs/qa/path/clone/path-desktop.png \
  --out docs/qa/path/diff \
  --label path-desktop \
  --threshold 0.005

node scripts/compare-geometry.mjs \
  --reference docs/qa/path/source/path-desktop.geometry.json \
  --candidate docs/qa/path/clone/path-desktop.geometry.json \
  --out docs/qa/path/diff \
  --label path-desktop \
  --tolerance 2
```

## Acceptance Thresholds

| Check | Required result |
|---|---|
| Static section pixel mismatch | `<0.5%` |
| Text-heavy section pixel mismatch | `<1.5%` |
| DOM geometry drift | `<=2px` |
| Missing visible assets | `0` |
| Unexplained blank regions | `0` |
| Broken network assets | `0` |

Live timestamps, randomized content, video frames, and externally injected widgets must be frozen or explicitly masked. Record every masked region and its reason in the page `SOURCE_OF_TRUTH.md`.

## Repair Loop

1. Capture source and clone with the same viewport contract.
2. Generate pixel heatmaps, overlays, and geometry reports.
3. Rank the worst sections by mismatch ratio and geometry delta.
4. Re-check live evidence and update `SOURCE_OF_TRUTH.md` first.
5. Reconcile derived specs and implementation.
6. Repeat until every report passes or an explicit dynamic-region mask explains the residual difference.

Save all outputs under `docs/qa/<page-slug>/`. Do not claim a 1:1 clone without passing reports.

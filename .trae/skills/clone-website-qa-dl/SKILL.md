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

### 1. Validate the canonical record

Before QA and before accepting a repaired page, run:

```bash
node "$CLONE_EXTRACT_DIR/scripts/validate-source-of-truth.mjs" \
  "docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md" \
  "$PWD" \
  --stage=completion
```

### 2. Capture deterministic references

Capture original and clone pages at desktop `1440px`, tablet `768px`, and mobile
`390px`:

```bash
node "$CLONE_QA_DIR/scripts/capture-reference.mjs" --url "$ORIGINAL_URL" --out docs/qa/original
node "$CLONE_QA_DIR/scripts/capture-reference.mjs" --url "$CLONE_URL" --out docs/qa/clone
```

Record and mask dynamic regions explicitly. Do not freeze animations before the
extraction skill has recorded their runtime contract.

### 3. Compare pixels and geometry

Run:

```bash
node "$CLONE_QA_DIR/scripts/visual-diff.mjs" \
  --reference docs/qa/original/home.desktop.png \
  --candidate docs/qa/clone/home.desktop.png \
  --out docs/qa/diff

node "$CLONE_QA_DIR/scripts/compare-geometry.mjs" \
  --reference docs/qa/original/home.desktop.geometry.json \
  --candidate docs/qa/clone/home.desktop.geometry.json \
  --out docs/qa/diff \
  --tolerance 2
```

Use `$CLONE_QA_DIR/scripts/verify-css.js` on both original and clone for
critical typography, backgrounds, and CTA values. Read
`references/measurable-convergence.md`.

### 4. Audit occupancy, interactions, and responsiveness

Check every section top to bottom:

- No reachable media asset is hidden or broken.
- No unexplained blank region remains.
- Documented booth fallbacks occupy the intended visual region.
- Scroll, click, hover, and responsive states behave like the original.
- Text remains complete and verbatim.
- Console errors and broken network assets are zero.

### 5. Apply the measurable convergence gate

Acceptance thresholds:

- Static sections: `<0.5%` pixel mismatch.
- Text-heavy sections: `<1.5%` pixel mismatch.
- Geometry drift: `<=2px`.
- Missing visible assets: `0`.
- Unexplained blank regions: `0`.
- Broken network assets: `0`.

Do not claim a 1:1 clone without saved reports. Repeat the repair loop until
reports pass.

### 6. Route repairs evidence-first

For each discrepancy:

1. Record stronger live evidence and the QA report in the source record's
   `Modification Ledger`.
2. Update the canonical source of truth.
3. Reconcile component specs.
4. Modify implementation.
5. Re-run build, occupancy checks, and QA.

Never silently patch code while leaving the page record stale.

### 7. Optional iterative stability check

For clone projects that use the compatible fixture assumptions, run:

```bash
python3 "$CLONE_QA_DIR/references/iterative-qa.py" http://localhost:3459 50
```

Interpret `50/50` repeated failures as deterministic bugs and mixed failures as
timing or lazy-load instability.

## Component Relationship Graph

After acceptance, generate `docs/component-graph.json` and
`docs/component-graph.md` from component imports. Include this Component
Relationship graph in delivery so the clone remains maintainable.

## Recovery

| Failure signal | First response | Final fallback |
|---|---|---|
| Dynamic mismatch | Add documented mask only for genuinely dynamic regions | Re-extract interaction states |
| Geometry drift | Compare measured landmarks with the canonical spacing graph | Return to focused evidence extraction |
| Broken assets | Restore reachable source media | Use only documented booth fallback |
| Mixed iterative failures | Increase settle time and add scroll-then-wait | Flag manual review requirement |
| Screenshot tooling unavailable | Compare manually and run CSS verification | Report blocked quantitative gate honestly |

## Best Practices & Experience (Ecwid Project)

1. **Spacer Injection**: Use responsive spacers (`hidden lg:block lg:h-[xxxpx]`) to align vertical rhythm between React and static sources.
2. **Fuzzy Matching**: The `compare-geometry.mjs` script should use normalized class names (sorted) and bucket-based matching to handle minor DOM variations.
3. **SVG Identity**: Detect SVGs using their `<title>` or unique path data to avoid coordinate drift misdetection.
4. **Layout Patches**: When `bodyHeightDelta` persists, use `jq` to identify the specific section where the cumulative offset begins and apply localized padding/margin adjustments.


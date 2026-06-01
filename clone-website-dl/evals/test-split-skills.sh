#!/usr/bin/env bash
set -euo pipefail

ORCH="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_ROOT="$(cd "$ORCH/.." && pwd)"
EXTRACT="$SKILLS_ROOT/clone-website-extract-dl"
BUILD="$SKILLS_ROOT/clone-website-build-dl"
QA="$SKILLS_ROOT/clone-website-qa-dl"

fail() {
  printf 'split-skills assertion failed: %s\n' "$1" >&2
  exit 1
}

for skill in "$ORCH" "$EXTRACT" "$BUILD" "$QA"; do
  test -f "$skill/SKILL.md" || fail "missing $skill/SKILL.md"
done

if find "$ORCH/scripts" "$ORCH/references" -type f 2>/dev/null | grep -q .; then
  fail "orchestrator still owns duplicated implementation resources"
fi

test "$(wc -l < "$ORCH/SKILL.md" | tr -d ' ')" -le 220 ||
  fail "orchestrator exceeds 220 lines"

for companion in clone-website-extract-dl clone-website-build-dl clone-website-qa-dl; do
  grep -q "$companion" "$ORCH/SKILL.md" || fail "orchestrator omits $companion"
done

grep -q 'STOP: wait for user confirmation before implementation' "$ORCH/SKILL.md" ||
  fail "orchestrator omits evidence approval stop"
grep -q 'evidence -> source record -> specs -> implementation -> QA' "$ORCH/SKILL.md" ||
  fail "orchestrator omits evidence-first repair order"

if grep -q 'getComputedStyle()\\|capture-reference.mjs\\|compare-geometry.mjs' "$ORCH/SKILL.md"; then
  fail "orchestrator embeds atomic implementation details"
fi

for file in \
  scripts/preflight-audit.sh \
  scripts/extract-playwright.py \
  scripts/discover-assets.js \
  scripts/extract-component-css.js \
  scripts/extract-svgs.js \
  scripts/audit-animations.mjs \
  scripts/audit-spacing.mjs \
  scripts/validate-source-of-truth.mjs \
  references/page-source-of-truth-template.md; do
  test -f "$EXTRACT/$file" || fail "extract skill missing $file"
done

for file in \
  references/spec-template.md \
  references/checklist.md \
  references/customization.md \
  references/antipatterns.md; do
  test -f "$BUILD/$file" || fail "build skill missing $file"
done

for file in \
  scripts/capture-reference.mjs \
  scripts/visual-diff.mjs \
  scripts/compare-geometry.mjs \
  scripts/verify-css.js \
  references/measurable-convergence.md; do
  test -f "$QA/$file" || fail "QA skill missing $file"
done

grep -q 'getComputedStyle()' "$EXTRACT/SKILL.md" ||
  fail "extract skill omits computed CSS contract"
grep -q 'validate-source-of-truth.mjs' "$EXTRACT/SKILL.md" ||
  fail "extract skill omits canonical evidence gate"
grep -q 'references/spec-template.md' "$BUILD/SKILL.md" ||
  fail "build skill omits component spec contract"
grep -q 'npm run build' "$BUILD/SKILL.md" ||
  fail "build skill omits production build verification"
grep -q 'capture-reference.mjs' "$QA/SKILL.md" ||
  fail "QA skill omits deterministic capture"
grep -q 'compare-geometry.mjs' "$QA/SKILL.md" ||
  fail "QA skill omits geometry comparison"
grep -q '<0.5%' "$QA/SKILL.md" ||
  fail "QA skill omits static-section threshold"
grep -q '<=2px' "$QA/SKILL.md" ||
  fail "QA skill omits geometry threshold"

python3 -m json.tool "$ORCH/evals/split-skills-evals.json" >/dev/null
printf 'split-skills regression assertions passed\n'

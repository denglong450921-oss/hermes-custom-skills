#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/docs/research/animations" "$TMP/docs/research/spacing" "$TMP/docs/qa/page"
touch "$TMP/docs/research/animations/page.animations.json" "$TMP/docs/research/spacing/page.spacing.json"

cat > "$TMP/valid.md" <<'EOF'
## Page Identity
## Visual References
## Global Page Contract
## Section Inventory
### `hero` - `Example`
## Asset Manifest
## Route And Link Contract
## Animation Contract
- **Audit report:** `docs/research/animations/page.animations.json`
## Strict Spacing Contract
- **Audit report:** `docs/research/spacing/page.spacing.json`
## Known Constraints
## QA Acceptance Contract
- **QA outputs:** `docs/qa/page/`
## Readiness Checklist
- [x] complete
- [ ] [completion] pixel diff pending
## Modification Ledger
- recorded
EOF
node "$ROOT/scripts/validate-source-of-truth.mjs" "$TMP/valid.md" "$TMP" >/dev/null
if node "$ROOT/scripts/validate-source-of-truth.mjs" "$TMP/valid.md" "$TMP" --stage=completion >/dev/null 2>&1; then
  echo "expected completion-stage pending item to fail" >&2
  exit 1
fi

sed 's/- \[x\] complete/- [ ] complete/' "$TMP/valid.md" > "$TMP/invalid.md"
if node "$ROOT/scripts/validate-source-of-truth.mjs" "$TMP/invalid.md" "$TMP" >/dev/null 2>&1; then
  echo "expected unchecked readiness item to fail" >&2
  exit 1
fi

echo "source-of-truth gate regression assertions passed"

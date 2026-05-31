#!/bin/bash
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
TMP_DIR=$(mktemp -d)
trap 'kill "${SERVER_PID:-}" 2>/dev/null || true; wait "${SERVER_PID:-}" 2>/dev/null || true; rm -rf "$TMP_DIR"' EXIT

cat > "$TMP_DIR/index.html" <<'HTML'
<!doctype html>
<style>
  body { margin: 0; }
  section { padding: 30px 20px; }
  h1, h2 { margin: 0 0 18px; }
  .breathing { margin-top: 120px; }
</style>
<section><h1>Hero</h1><p>Intro</p></section>
<section class="breathing"><h2>Details</h2><p>Body</p></section>
HTML

python3 -m http.server 8766 --directory "$TMP_DIR" >/dev/null 2>&1 &
SERVER_PID=$!
sleep .4

node "$SKILL_DIR/scripts/audit-spacing.mjs" --url http://localhost:8766/ --out "$TMP_DIR/report" --label fixture >/dev/null
python3 - "$TMP_DIR/report/fixture.spacing.json" <<'PY'
import json
import sys
report = json.load(open(sys.argv[1]))
for viewport in report["viewports"].values():
    assert viewport["bodyHeight"] > 0
    assert len(viewport["landmarks"]) >= 4
    assert viewport["verticalHeadingGaps"][0]["from"] == "Hero"
    assert viewport["verticalHeadingGaps"][0]["to"] == "Details"
    assert viewport["verticalHeadingGaps"][0]["gap"] >= 120
PY
echo "spacing audit regression assertions passed"

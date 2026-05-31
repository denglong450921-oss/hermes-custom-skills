#!/bin/bash
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
TMP_DIR=$(mktemp -d)
trap 'kill "${SERVER_PID:-}" 2>/dev/null || true; wait "${SERVER_PID:-}" 2>/dev/null || true; rm -rf "$TMP_DIR"' EXIT

cat > "$TMP_DIR/index.html" <<'HTML'
<!doctype html>
<style>
  @keyframes pulse { from { opacity: .25; transform: translateX(0); } to { opacity: 1; transform: translateX(40px); } }
  html { scroll-behavior: smooth; }
  body { min-height: 2400px; }
  .animated { animation: pulse 1s infinite alternate; transition: opacity .3s ease; width: 100px; height: 100px; background: #fc0; }
  .scroll-card { margin-top: 1300px; transition: transform .4s ease; transform: translateY(12px); width: 120px; height: 80px; background: #09f; }
</style>
<div class="animated">motion</div>
<canvas width="40" height="40"></canvas>
<video></video>
<div class="scroll-card">scroll</div>
HTML

python3 -m http.server 8765 --directory "$TMP_DIR" >/dev/null 2>&1 &
SERVER_PID=$!
sleep .4

node "$SKILL_DIR/scripts/audit-animations.mjs" \
  --url http://localhost:8765/ \
  --out "$TMP_DIR/report" \
  --label fixture \
  --samples 3 \
  --settle 40 >/dev/null

python3 - "$TMP_DIR/report/fixture.animations.json" <<'PY'
import json
import sys
report = json.load(open(sys.argv[1]))
assert report["libraries"]["videos"] == 1
assert report["libraries"]["canvases"] == 1
assert len(report["states"]) == 3
assert report["states"][0]["scrollY"] == 0
assert report["states"][-1]["scrollY"] == report["bodyHeight"] - report["viewport"]["height"]
assert any(state["animations"] for state in report["states"])
assert any(
    element["style"]["animationName"] == "pulse"
    for state in report["states"]
    for element in state["elements"]
)
PY

set +e
missing_url_output=$(node "$SKILL_DIR/scripts/audit-animations.mjs" 2>&1)
missing_url_status=$?
capture_missing_url_output=$(node "$SKILL_DIR/scripts/capture-reference.mjs" 2>&1)
capture_missing_url_status=$?
set -e

test "$missing_url_status" -eq 1
test "$capture_missing_url_status" -eq 1
printf '%s' "$missing_url_output" | grep -q '^Usage:'
printf '%s' "$capture_missing_url_output" | grep -q '^Usage:'
echo "animation audit regression assertions passed"

#!/bin/bash
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
FIXTURE_DIR=$(mktemp -d)
PORT=${PORT:-18765}
SERVER_PID=

cleanup() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$FIXTURE_DIR"
}
trap cleanup EXIT

{
  printf '%s\n' '<!doctype html><HTML><HEAD>'
  printf '%s\n' "<META NAME='viewport' content='width=device-width'>"
  printf '%s\n' "<LINK HREF='/assets/main.12345678.css?x=1' REL='stylesheet'>"
  printf '%s\n' "<LINK REL='preconnect' HREF='https://fonts.gstatic.com'>"
  printf '%s\n' "<STYLE>.dark { color:red!important } @media (prefers-color-scheme:dark) { body { color:white!important } }</STYLE>"
  printf '%s\n' '</HEAD><BODY data-theme="dark"><SCRIPT SRC="bundle.js"></SCRIPT><div data-aos="fade">'
  i=0
  while [ "$i" -lt 31 ]; do
    printf '<SVG viewBox="0 0 1 1"></SVG>'
    i=$((i + 1))
  done
  printf '%s\n' "<IMG DATA-SRC='hero.webp' LOADING='lazy'><p>fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content fixture content</p></div></BODY></HTML>"
} > "$FIXTURE_DIR/index.html"

python3 -m http.server "$PORT" --directory "$FIXTURE_DIR" > "$FIXTURE_DIR/http.log" 2>&1 &
SERVER_PID=$!
sleep 1

bash "$SKILL_DIR/scripts/preflight-audit.sh" "http://127.0.0.1:$PORT" |
  python3 -c '
import json, sys
checks = json.load(sys.stdin)["checks"]
expected = {
    "fetch_ok": 1,
    "partial_fetch": 0,
    "http_status": "200",
    "css_local": 1,
    "css_hashed": 1,
    "resource_hints": 1,
    "lazy_images": 2,
    "inline_svgs": 31,
    "google_fonts": 1,
    "has_viewport_meta": 1,
    "dark_mode_markers": 3,
    "animation_library_markers": 1,
    "important_rules": 2,
}
for key, value in expected.items():
    assert checks[key] == value, (key, checks[key], value)
'

bash "$SKILL_DIR/scripts/preflight-audit.sh" "http://127.0.0.1:9" |
  python3 -c '
import json, sys
checks = json.load(sys.stdin)["checks"]
assert checks["fetch_ok"] == 0
assert checks["partial_fetch"] == 0
assert not any("viewport" in problem for problem in checks["problems"])
'

printf 'preflight regression assertions passed\n'

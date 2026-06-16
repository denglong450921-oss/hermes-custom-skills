#!/usr/bin/env bash
set -euo pipefail

# Generate a complete WeChat cover package from Markdown.
# Run this from the wechat-cover-generator-dl skill directory.

ARTICLE="${1:-/path/to/article.md}"
OUT_DIR="${2:-/tmp/wechat-cover-output}"
STYLE="${3:-auto}"

mkdir -p "$OUT_DIR"

python3 scripts/run_pipeline.py \
  --input "$ARTICLE" \
  --style "$STYLE" \
  --output "$OUT_DIR/cover.png" \
  --report "$OUT_DIR/report.json"

echo "Cover:  $OUT_DIR/cover.png"
echo "Report: $OUT_DIR/report.json"
echo "Title:  $OUT_DIR/cover-title.md"

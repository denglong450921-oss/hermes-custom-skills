#!/bin/bash
# Usage: bash fetch-command.sh "your query keywords" 1200
QUERY="${1:-tech workspace laptop}"
MIN_WIDTH="${2:-1200}"
python3 scripts/fetch_image.py --query "$QUERY" --min-width "$MIN_WIDTH"

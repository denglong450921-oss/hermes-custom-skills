#!/bin/bash
# Run validation
python3 scripts/validate_image.py \
  --image-url "https://images.unsplash.com/photo-xxxxx" \
  --query "topic keywords" \
  --min-width 1200

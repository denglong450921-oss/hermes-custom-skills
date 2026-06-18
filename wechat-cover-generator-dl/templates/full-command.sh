#!/bin/bash
# Step 1: Generate title
# (run wechat-title-generator-dl manually)

# Step 2: Fetch image
python3 scripts/fetch_image.py --query "topic keywords" --min-width 1200

# Step 3: Validate
python3 scripts/validate_image.py --image-url "<url>" --query "topic" --min-width 1200

# Step 4: Render cover
python3 gen_cover.py \
  --title "Article Title" \
  --subtitle "Subtitle text" \
  --tagline "Tagline text" \
  --label "CATEGORY" \
  --image-url "<validated-url>" \
  --output /path/to/cover.png

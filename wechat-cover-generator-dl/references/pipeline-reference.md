# Pipeline Reference

## Skill composition

```
Input: Markdown article file
  │
  ▼
Step 1: wechat-title-generator-dl
  │  Extract topic + style from Markdown
  │  Output: title.md (title, subtitle, tags, label)
  │
  ▼
Step 2: open-source-image-fetch-dl
  │  Query with 3-5 English keywords from topic
  │  Retry up to 3 times with broader queries
  │  Output: image JSON (URL, author, license, dims)
  │
  ▼
Step 3: image-quality-validator-dl
  │  Validate 6 dimensions (resolution, clarity, etc.)
  │  If FAIL → go back to Step 2 (max 3 retries)
  │  Output: validation report
  │
  ▼
Step 4: wechat_article_cover_image_gen
  │  Render 900×383 PNG with title overlay
  │  Output: final cover PNG
```

## Retry logic

```python
max_attempts = 3
for attempt in range(max_attempts):
    image = fetch_image(query, min_width)
    result = validate_image(image["image_url"], query)
    if result["status"] == "pass":
        break
    query = broaden_keywords(query)  # add more general terms
# If all fail: use solid dark gradient
```

## Quality checklist

- [ ] Title extracted from Markdown h1
- [ ] Tags derived from body keywords
- [ ] Image is landscape (w ≥ h)
- [ ] Image width ≥ 1200px
- [ ] No watermark detected
- [ ] Validation passed or fallback documented
- [ ] Cover is 900×383 PNG
- [ ] Title font ≥ 28px, weight ≥ 600
- [ ] Safe zones ≥ 80px on left/right

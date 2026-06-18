---
name: image-quality-validator-dl
description: >
  REQUIRED validation step between image fetch and cover generation. Checks 6
  quality dimensions: resolution (≥1200px), landscape orientation, watermark
  presence, clarity/blur via Laplacian variance, theme relevance via keyword
  matching, and 900×383 crop suitability. Triggers whenever an image URL is
  available and needs quality verification — ALWAYS run this after
  open-source-image-fetch-dl and before wechat-cover-generator-dl. Built-in
  3-attempt retry: if validation fails, automatically re-fetches with broader
  query. Never skip validation — blurry, watermarked, or low-res images
  produce unprofessional covers. Returns JSON with pass/fail status, detailed
  per-dimension scores, and failure reason.
compatibility: Python 3.10+ with Pillow, numpy
---

# Image Quality Validator

Validate image quality for WeChat Official Account covers across 6 dimensions.
If any check fails, automatically retry with a different image (up to 3 attempts).

## Input

```json
{
  "image_url": "https://images.unsplash.com/photo-xxxxx",
  "query": "AI workspace entrepreneur laptop minimal modern",
  "min_width": 1200
}
```

| Field | Required | Description |
|---|---|---|
| `image_url` | Yes | URL of the image to validate |
| `query` | No | Topic keywords for relevance check |
| `min_width` | No | Minimum width in px (default: 1200) |

## Output

```json
{
  "status": "pass / fail",
  "relevance": 0.91,
  "clarity": 0.95,
  "resolution_px": [2400, 1600],
  "reason_if_fail": "resolution too low"
}
```

## Validation dimensions

### 1. Resolution check
- Minimum short side: 1200px
- Must be landscape (width >= height)
- Full resolution info returned in output

### 2. Landscape orientation
- Must be wider than tall
- Score penalised for portrait images

### 3. Watermark heuristic
- Checks bottom-right corner variance vs rest of image
- Flags abnormal brightness/contrast differences in corners
- Returns confidence score (0–1)

### 4. Theme relevance
- Scores keyword overlap between query and 8 topic categories
- Returns matched category and overlap count
- Minimum threshold: 0.75

### 5. Clarity (blur detection)
- Uses Laplacian variance
- Minimum threshold: variance >= 50
- Rating: sharp (≥200), acceptable (50–200), blurry (<50)

### 6. Crop suitability for 900×383
- Checks aspect ratio proximity to ~2.35
- Wider images preferred (more room to crop)
- Ratings: excellent, good, fair, poor

## Fail retry mechanism (CRITICAL)

If validation status is `fail`, the agent MUST:

1. Call `open-source-image-fetch-dl` to fetch a different image
2. Validate the new image
3. Repeat up to 3 total attempts
4. If all 3 attempts fail, use a solid dark gradient fallback

```python
max_attempts = 3
for attempt in range(max_attempts):
    # fetch new image
    image = fetch_image(query=query, min_width=min_width)
    # validate
    result = validate_image(image_url=image["image_url"], query=query)
    if result["status"] == "pass":
        break
    # else retry with modified query
```

## Workflow

1. Parse input JSON.

🔴 **CHECKPOINT: Verify input parameters are valid before proceeding.** Incorrect or missing parameters will cause script failure. Confirm with the user if ambiguous.


🔴 **CHECKPOINT: Review the output before proceeding.** If results are unexpected, go back and retry with different parameters.

2. Run `python3 <skill_dir>/scripts/validate_image.py` with the image URL.
3. Check the output JSON status.
4. If `pass`, return the validation result.
5. If `fail`, retry with a different image (up to 3 total attempts).
6. Log each attempt's failure reason for transparency.
7. Return final validation result.

### Script usage

```bash
python3 <skill_dir>/scripts/validate_image.py \
  --image-url "https://images.unsplash.com/photo-xxxxx" \
  --query "AI workspace" \
  --min-width 1200
```


🛑 **STOP: Present the final result to the user for confirmation** before using it in any downstream task.

## Failure handling

| Trigger | First-line fix | Still fails → fallback |
|---|---|---|
| Image too small (< 1200px side) | Retry with different image (attempt N+1) | Try alternative approach or fallback |
| Portrait orientation | Retry with landscape-specific query | Try alternative approach or fallback |
| Image blurry (Laplacian < 50) | Retry with different source | Try alternative approach or fallback |
| Watermark detected | Retry with watermarked filtered | Try alternative approach or fallback |
| All 3 attempts fail | Create solid dark gradient background as fallback | Try alternative approach or fallback |
| Script crashes | Return fail with error details | Try alternative approach or fallback |




## Anti-patterns & blacklist

| Anti-pattern | Why it's dangerous | Instead do |
|---|---|---|
| Using random web images | Copyright risk + wrong aspect ratio for covers | Use curated Unsplash fallbacks or CC0 sources |
| Ignoring orientation requirement | Portrait images crop poorly to landscape | Always specify `"orientation": "landscape"` |
| Skipping min_width check | Low-res images pixelate at 900×383 | Validate dimensions ≥ 1200px on short side |
| Blindly trusting low relevance_score | Score < 0.7 means fallback triggered | Re-run with better keywords |
| No retry on failed validation | Single failure means no cover image | Implement 3-attempt retry with broader queries |



## Edge cases

| Scenario | How to handle |
|---|---|
| Image URL returns 404 or connection refused | Return status "fail" with reason "image not accessible" |
| Image dimensions smaller than min_width | Return fail with actual dimensions — do NOT resize automatically |
| Laplacian variance between 30-50 (borderline blurry) | Return fail with clarity_rating "soft" — suggest finding a sharper image |
| Relevance score between 0.70-0.75 (borderline match) | Return pass but warn user that topic match is marginal |
| Image is already exactly 900×383 | Ideal case — mark crop_suitability as "excellent" |
| Watermark check flagging false positives on artistic borders | Note in evidence: "possible artistic border, not standard watermark pattern" |

## Harness (Self-Eval)

The harness validates that `validate_image.py` produces correct quality assessment JSON.

### Cases

| ID | Scenario |
|----|----------|
| `case_001` | Validate image from Unsplash tech photo with "tech AI" query — check all 5 dimensions |
| `case_002` | Validate a business photo with "business meeting" query — check status, clarity, crop |
| `case_003` | Validate with higher min-width (1800px) — check resolution check passes |

### Checks

| Check | What it detects |
|-------|----------------|
| `script_exit_ok` | Script ran without errors |
| `output_is_json` | Output is valid JSON |
| `has_status` | Contains `status` field (pass/fail) |
| `has_relevance_score` | Contains `relevance` score (0–1) |
| `has_clarity_score` | Contains `clarity` score (0–1) |
| `has_resolution` | Contains `resolution_px` with [width, height] |
| `has_crop_check` | Contains `crop_check` sub-object |

### Run

```bash
# Generate output
python3 scripts/validate_image.py --image-url "https://images.unsplash.com/photo-1677442136019-21780ecad995" --query "tech AI" > /tmp/validate-output.json

# Grade
python3 evals/grader.py /tmp/validate-output.json '[{"text":"Status","check":"has_status"},{"text":"Clarity","check":"has_clarity_score"}]'

# Full harness
python3 evals/run_harness.py /tmp/validate-output.json
```

### Honesty & Truthfulness

Report results exactly as they are:
- Validation pass/fail must match actual output, not be guessed
- If image fails validation, report the exact `reason_if_fail`
- All 6 dimension checks must be reported transparently
- No assumed scores — only report what the script actually returned


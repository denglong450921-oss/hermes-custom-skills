---
name: open-source-image-fetch-dl
description: >
  ALWAYS use this skill first when generating any cover image — it fetches
  free-license background images from Unsplash and curated CC0 sources with
  zero API keys needed. Triggers when the user asks for a "background image",
  "封面图", "stock photo", "banner", or needs a landscape image for WeChat
  covers, social media cards, or article banners. Returns structured JSON
  with URL, author, license, dimensions, and relevance score. Must be used
  before image-quality-validator-dl for validation and before
  wechat-cover-generator-dl for the final cover pipeline. Automatically
  handles fallbacks — if one image fails, it tries the next.
compatibility: Python 3.10+ with requests, Pillow, numpy
---

# Open Source Image Fetch

Fetch free-license, high-resolution images from open sources. No API keys
required — uses curated fallback URLs grouped by category.

## Input

JSON object describing the desired image:

```json
{
  "query": "AI workspace entrepreneur laptop minimal modern",
  "license": "CC0 / free commercial use",
  "orientation": "landscape",
  "min_width": 1200
}
```

| Field | Required | Values |
|---|---|---|
| `query` | Yes | Space-separated keywords (English preferred) |
| `license` | No | `CC0 / free commercial use` (default), `CC BY`, `public domain` |
| `orientation` | No | `landscape` (default), `portrait`, `square` |
| `min_width` | No | Minimum width in px (default: 1200) |

## Output

```json
{
  "image_url": "https://images.unsplash.com/photo-xxxxx",
  "author": "Unsplash",
  "license": "Unsplash",
  "width": 2400,
  "height": 1600,
  "relevance_score": 0.92
}
```

## How it works

The script `scripts/fetch_image.py` uses keyword matching against curated
Unsplash photo URLs organised by topic categories. For each query:

1. Parse keywords from the query string
2. Score each pre-curated image category by keyword overlap
3. Pick the highest-scoring category and select a photo from it
4. Try fetching from category-specific Unsplash source URLs
5. On failure, fall back through the general fallback chain
6. Return structured JSON with image metadata

### Pre-curated categories

The script has 8 topic categories with 4 curated photos each:

| Category | Keywords | Photos for |
|---|---|---|
| `tech` | AI, workspace, laptop, computer, software, digital | Tech/business covers |
| `business` | entrepreneur, startup, office, meeting, strategy | Business/finance |
| `nature` | landscape, mountain, forest, ocean, sky, nature | Calm/background |
| `abstract` | abstract, pattern, texture, geometric, gradient | Modern/minimal |
| `education` | book, study, learn, reading, library, knowledge | Cognitive/learning |
| `health` | wellness, health, meditation, nature, calm | Wellness |
| `city` | city, urban, architecture, building, street | Urban/lifestyle |
| `creative` | art, design, creative, drawing, color | Design/creative |

## Workflow

🔴 **CHECKPOINT: Verify input JSON has all required fields before proceeding.** Missing `query` will cause script failure. Confirm with user if ambiguous.

1. Parse input JSON — extract query, license, orientation, min_width.
2. Run `python3 <skill_dir>/scripts/fetch_image.py` with the query.
3. Read the JSON output from the script.

🔴 **CHECKPOINT: Verify output dimensions meet min_width and landscape requirements.** If dimensions are insufficient, inform the user before proceeding.

4. Check dimensions match the min_width and orientation requirements.
5. Return the result to the user.
6. If the script fails, try a second query with broader keywords.
7. If all attempts fail, create a solid dark gradient image as last resort.

🛑 **STOP: Present the final result to the user before using the image in any downstream task (cover generation, design, etc.). The user must confirm the image is acceptable.**

### Script usage

```bash
python3 <skill_dir>/scripts/fetch_image.py \
  --query "AI workspace entrepreneur laptop" \
  --min-width 1200
```

Output:
```json
{
  "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995",
  "author": "Unsplash",
  "license": "Free to use under the Unsplash License",
  "width": 2400,
  "height": 1600,
  "relevance_score": 0.85
}
```

## Failure handling

| Trigger | First-line fix | Still fails → fallback |
|---|---|---|
| All categories miss the query keywords | Widen query keywords or use the first general fallback URL | Try an unrelated category or solid dark gradient |
| Image download returns 404 | Try next fallback URL in the category | Try next category's photos or general fallback chain |
| Downloaded image too small for min_width | Try next image in the same category | Reduce min_width requirement or use fallback image |
| Script crashes with Python error | Log the error, retry with simplified query | Create solid dark gradient as pure fallback |

## Anti-patterns & blacklist

Avoid these common mistakes when fetching cover images:

| Anti-pattern | Why it's dangerous | Instead do |
|---|---|---|
| Using random images from web search | Copyright risk + mismatch with 900×383 cover format | Use Unsplash fallbacks or curated CC0 sources |
| Ignoring orientation requirement | Portrait images crop poorly to landscape covers | Always specify `"orientation": "landscape"` |
| Skipping min_width check | Low-res images look pixelated at 900x383 | Always validate dimensions ≥ 1200px on short side |
| Using min_width ≥ 1200 while script adds crop params | `?w=900&h=383&fit=crop` makes downloaded image 900px wide — min_width check fails even though full-res image is 5120+px. All category photos get skipped → score 0.5 | Script now checks curated dimensions before download. If still hitting this, lower to min_width=800 or use `--min-width 800` which still produces 900px usable cover |
| Blindly trusting relevance_score=0.5 | Score 0.5 means fallback triggered — image may not match topic | Re-run with better keywords if score < 0.7 |
| No query expansion for failed downloads | Narrow keywords (e.g., "quantum computing") may have no category match | Try broader terms (e.g., "tech abstract") |





## Edge cases

| Scenario | How to handle |
|---|---|
| Query returns relevance_score < 0.7 | Retry with broader keywords — add "general" or "abstract" to the query |
| User provides Chinese-only keywords (e.g. "科技办公") | Translate to English before querying: "tech workspace" |
| min_width > 4000 | Clamp to 4000 — available curated photos don't exceed this |
| User requests portrait orientation | Note that landscape is strongly preferred for 900×383 covers, but still try to fetch |
| License field unknown or unreasonable | Default to "CC0 / free commercial use" and use Unsplash fallbacks |
| Network timeout or DNS failure on fetch | Log the timeout and try the next fallback URL immediately |

## Harness (Self-Eval)

The harness validates that `fetch_image.py` produces valid JSON output with all required fields.

### Cases

| ID | Scenario |
|----|----------|
| `case_001` | Fetch a tech/workspace image (keyword: "AI workspace laptop tech") — check URL, author, license, width ≥ 1200 |
| `case_002` | Fetch a business image (keyword: "entrepreneur startup business office") — check URL, width ≥ 1200 |
| `case_003` | Fetch with higher min-width (keyword: "abstract pattern landscape", min-width 1800) — check width ≥ 1800 |

### Checks

| Check | What it detects |
|-------|----------------|
| `script_exit_ok` | Script ran without Traceback/Error |
| `output_is_json` | Output is valid JSON (starts with `{`) |
| `has_image_url` | JSON contains `image_url` field |
| `has_author` | JSON contains `author` field |
| `has_license` | JSON contains `license` field |
| `has_width_ge_1200` | Image width ≥ 1200px |
| `has_width_ge_1800` | Image width ≥ 1800px (case_003 only) |
| `has_relevance_score` | JSON contains `relevance_score` (0–1) |

### Run

```bash
# Generate output
python3 scripts/fetch_image.py --query "AI workspace laptop tech" --min-width 1200 > /tmp/fetch-output.json

# Grade
python3 evals/grader.py /tmp/fetch-output.json '[{"text":"Script ran","check":"script_exit_ok"},{"text":"JSON","check":"output_is_json"},{"text":"Image URL","check":"has_image_url"}]'

# Full harness
python3 evals/run_harness.py /tmp/fetch-output.json
```

### Honesty & Truthfulness

Report results exactly as they are:
- Script failed → state "failed" with the actual error output
- Missing fields in JSON → report exact missing fields
- No defensive disclaimers on correct results
- If width check fails, report actual width value


---
name: wechat-cover-generator-dl
description: >
  Full-pipeline WeChat Official Account cover generator. Orchestrates title
  generation, image fetching, quality validation, and cover rendering into a
  single workflow. Requires a Markdown input file with article metadata. Use
  this skill when the user wants a complete cover image for a WeChat article
  push — from title to final 900x383 PNG. This is the top-level orchestration
  skill that composes wechat-title-generator-dl, open-source-image-fetch-dl,
  image-quality-validator-dl, and wechat_article_cover_image_gen together. Do
  NOT use the individual sub-skills directly unless you only need one specific
  step.
compatibility: Python 3.10+ with Pillow, numpy; requires wechat-title-generator-dl, open-source-image-fetch-dl, image-quality-validator-dl, wechat_article_cover_image_gen
---

# WeChat Cover Generator (Orchestration)

Full-pipeline orchestration that produces a WeChat-ready 900×383 cover image
from a Markdown input file. Composes all sub-skills automatically.

## Input

A Markdown file with article metadata, for example:

```markdown
# OPC：AI时代的个人商业系统

## Prompt
Generate a high-level WeChat article about OPC system.

## Requirements
- Must include MVP framework
- Must include risk analysis
- Must include real-world validation logic
- Must include actionable steps
```

## Input contract

| Element | Source | Example |
|---|---|---|
| Title (h1) | 1st `#` heading in the Markdown input | `OPC：AI时代的个人商业系统` |
| Topic keywords | Extracted from the Markdown body | `OPC, AI, personal business system` |
| Style hint | Section headings like `## Requirements` | `high-level`, `professional` |

## Pipeline

The orchestration runs 4 steps in sequence:

### Step 1: Generate title metadata

1. Load `wechat-title-generator-dl` skill.
2. Extract topic and style from the Markdown input.
3. Generate a structured title file with title, subtitle, tagline, label.

**Input:**
```json
{
  "topic": "extracted from Markdown h1 + body content",
  "style": "professional / high-level / cognitive"
}
```

**Output:** A `.md` file with title, subtitle, tagline, label fields.

### Step 2: Fetch a free-license image

1. Load `open-source-image-fetch-dl` skill.
2. Derive 3-5 English keywords from the article topic.
3. Run the fetch script with the keywords.

**Query:** Extract 3-5 English keywords from the article topic.

**Output:** JSON with image URL, author, license, dimensions.


🔴 **CHECKPOINT: Review the output before proceeding.** If results are unexpected, go back and retry with different parameters.

### Step 3: Validate the image (with retry)

1. Load `image-quality-validator-dl` skill.
2. Validate the fetched image against 6 quality dimensions.

- If `pass` → proceed to Step 4.
- If `fail` → increment attempt counter, go back to Step 2 with modified
  query. Up to 3 attempts total.
- If all 3 fail → proceed with fallback (solid dark gradient).

### Step 4: Generate the cover

1. Load `wechat_article_cover_image_gen` skill.
2. Pass title metadata from Step 1 as `--title`, `--subtitle`, `--tagline`, `--label`.
3. Pass validated image URL from Step 3 as `--image-url`.
4. Run the cover generation script.

```bash
python3 <cover_skill_dir>/scripts/gen_cover.py \
  --title "AI 时代的 OPC" \
  --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
  --tagline "决策者 + AI 工具链  ·  可验证需求  ·  商业闭环" \
  --label "AI ERA  ·  ONE PERSON COMPANY" \
  --image-url "<validated-image-url>" \
  --output /path/to/final-cover.png
```


🛑 **STOP: Present the final result to the user for confirmation** before using it in any downstream task.

## Output

```json
{
  "cover_image_url": "/path/to/final-cover.png",
  "title_md_path": "/path/to/generated-title.md",
  "layout": "center-title-overlay",
  "text_render_quality": "high",
  "validation": "pass",
  "image_source": "Unsplash",
  "image_validation_attempts": 1
}
```

## Quality rules (inherited from sub-skills)

The final cover MUST satisfy:
- **Canvas**: 900×383 px
- **Title font**: ≥ 28px, weight ≥ 600, white high-contrast with text-shadow
- **No blurry text** — outline width ≥ 2px, anti-aliased rendering
- **Dark overlay**: uniform rgba over full canvas for Dark Mode readability
- **Left/right safe zone**: ≥ 80px from edges for WeChat thumbnail crop
- **Central whitespace**: title area centred, no elements near edges
- **Background**: clean, no faces obstructing text, no busy patterns under title

## Failure handling

| Trigger | First-line fix | Still fails → fallback |
|---|---|---|
| Markdown input missing h1 | Use filename as fallback title | Try alternative approach or fallback |
| Step 1 (title gen) fails | Derive title directly from Markdown | Try alternative approach or fallback |
| Step 2 (image fetch) fails after 3 retries | Use solid dark gradient background | Try alternative approach or fallback |
| Step 3 (validation) all fail | Report "fallback mode" and proceed | Try alternative approach or fallback |
| Step 4 (cover gen) fails | Return error with last script output | Try alternative approach or fallback |
| Any step unrecoverable | Return structured error with which step failed | Try alternative approach or fallback |




## Anti-patterns & blacklist

| Anti-pattern | Why it's dangerous | Instead do |
|---|---|---|
| Skipping image validation | Blurry/low-res image makes cover look unprofessional | Always run image-quality-validator-dl before rendering |
| No title metadata step | Cover has no title or wrong title | Always run wechat-title-generator-dl first |
| Ignoring validation retry | First attempt may fail → no fallback image | Allow up to 3 retries with modified queries |
| Not showing user the result | User might disagree with image/title choice | Always present final cover for confirmation |
| Hardcoding image URLs | Same cover for every article, no variety | Let open-source-image-fetch-dl pick per topic |



## Edge cases

| Scenario | How to handle |
|---|---|
| Input Markdown has no h1 heading | Use the filename (without .md) as the fallback title |
| All 3 image fetch attempts fail | Proceed with solid dark gradient — document as "fallback mode" |
| Validation passes but cover script errors | Retry the cover script once. If it fails again, report the Python traceback |
| User provides no Markdown file | Ask user for the article topic directly, use "untitled" as fallback |
| Pipeline interrupted mid-step | Report which step completed and which step failed — do not proceed automatically |
| Title generation produces overly long title (>30 chars) | Auto-truncate to 28 chars for the cover, store full title in metadata |

## Harness (Self-Eval)

The harness validates that the full pipleline completes successfully, producing a cover image with all required metadata.

### Cases

| ID | Scenario |
|----|----------|
| `case_001` | Full pipeline: OPC / AI topic, high-level style — title gen → image fetch → validate → cover render |
| `case_002` | Cognitive learning topic, cognitive style — check all steps execute |
| `case_003` | Wellness topic with retry handling — check pipeline handles validation retries gracefully |

### Checks

| Check | What it detects |
|-------|----------------|
| `pipeline_complete` | Pipeline output contains completion signals (cover_image_url, validation) |
| `cover_generated` | Final PNG cover was produced |
| `title_created` | Title metadata was generated (.md reference found) |
| `image_fetched` | Image source (Unsplash) was fetched |
| `image_validated` | Image validation step ran |
| `honest_reporting` | Pipeline reports status honestly (pass/fail/fallback) |

### Run

```bash
# Run pipeline by loading all 4 sub-skills and following workflow
# Grade the final report:

python3 evals/grader.py /path/to/pipeline-report.json '[{"text":"Pipeline","check":"pipeline_complete"},{"text":"Cover","check":"cover_generated"}]'

# Full harness
python3 evals/run_harness.py /path/to/pipeline-report.json
```

### Honesty & Truthfulness

Report results exactly as they are:
- If any pipeline step fails, report which step and why
- If fallback was used (after 3 retries), state "fallback mode" explicitly
- Do not claim "all passed" when steps were skipped or fell back
- Cover existence must be verified by `ls -la`, not assumed
- Report retry count when applicable


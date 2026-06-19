---
name: wechat-article-write-to-push-dl
description: >
  Choreographed pipeline for WeChat Official Account full-publish workflow.
  Orchestrates 4 skills in sequence: dennon-perspective (write article) →
  wechat-md-to-article-dl (convert to HTML) → wechat-cover-generator-dl
  (generate cover) → wechat_article_push_dl (push to drafts).
  Trigger when the user says "publish", "推文", "推送", "发布公众号",
  "write and push", "coverOK", "封面OK", "推", or finishes a dennon-style
  article and wants it published. Also triggers on any clipping path from
  the Obsidian vault or Auto Article directory when the user wants the
  full write-to-publish flow, not just transcription.
  During the push safety step, the user approves with "confirm", "推", or
  "go ahead" — treat any of these as explicit confirmation to execute.
  This skill is the single entry point — do NOT ask the user to run each
  sub-skill manually.
---

# WeChat Write-to-Push Pipeline

Choreographs 4 existing skills into one end-to-end workflow.
Each step delegates to a dedicated skill — this skill owns sequencing, data
handoff, quality gates, and safety stops.

## Overall pipeline

```
[Input] Article topic or clipping
  ↓
Step 1: dennon-perspective → write article → ~/Downloads/<title>.md
  ↓
Step 2: wechat-md-to-article-dl → convert to HTML → /tmp/<name>.wechat.html
  ↓
Step 3: wechat-cover-generator-dl → generate cover → ~/Downloads/<name>-cover.png
  ↓
Step 4: wechat_article_push_dl → show push command (STOP — user confirms)
  ↓
Step 5: Save outputs → workspace directory + summary.txt
  ↓
[Done] User reviews draft at mp.weixin.qq.com
```

## Before starting

### Resume detection

If the user invokes this skill with the same source file as a previous interrupted run,
check for existing artifacts before re-running Steps 1-3:

```bash
ls -la "/Users/f/Downloads/<title-first-chars>*.md" 2>/dev/null && echo "article exists"
ls /tmp/<short-name>.wechat.html 2>/dev/null && echo "HTML exists"
ls "/Users/f/Downloads/<short-name>-cover.png" 2>/dev/null && echo "cover exists"
```

- **All three exist** → Resume at Step 4 (push). Re-open the cover for user approval first, then show push command.
- **HTML + cover exist, no article** → Start from Step 2.
- **Nothing exists** → Full pipeline from Step 1.
- **Article exists but no cover/HTML** → Likely user wants a different article from same source; re-run from Step 1.

When resuming, open the existing cover and present the pipeline status table showing which
steps are already done, then ask: "Cover was previously generated — still OK, or redo?"

### Assess input type:

| Input | Action |
|-------|--------|
| Clipping path (`Clippings/Auto Article/` or vault path) | Follow dennon-perspective's Auto Article clipping rules |
| Raw transcript path (`.mp4` URL or file) | First transcribe with `video-transcribe` skill, then use the transcript as source |
| Topic phrase ("写一篇关于X的文章") | Go directly to Step 1; dennon-perspective writes from framework alone |
| Existing `.md` file | Skip Step 1, go to Step 2 |
| `--cover-only` flag | Skip Steps 1-2, go directly to Step 3 |
| `--push-only` flag with existing HTML + cover | Skip Steps 1-3, go directly to Step 4 |

## Step 1: Write article

**MUST load and follow `dennon-perspective` skill.** This is NOT optional. Do NOT write the article directly — always invoke dennon-perspective's Agentic Protocol:

1. Load `dennon-perspective` with `thinking-models-dl` (the skill auto-loads it)
2. Follow the full Agentic Protocol (Problem classification → Research → Structure architecture → Writing → Cleanup)
3. Run layout-check.py — exit code 0 required

**Output**: `~/Downloads/<标题前20字>.md`
**Quality gate**: layout-check.py exit code 0 (≥5 layout types, ≤3 consecutive text paragraphs, adjacent chapter diversity).

If layout check fails, fix and re-run before proceeding to Step 2.

### Step 1 in the full pipeline example

```bash
# Step 1: MUST invoke dennon-perspective skill to write the article
# Feed the source (clipping / topic / transcript) to dennon-perspective
# The skill produces: ~/Downloads/<标题前20字>.md
# Then validate:
python3 /Users/f/.hermes/skills/dennon-perspective/scripts/layout-check.py \
  "/Users/f/Downloads/<标题前20字>.md"
# Must exit 0 before proceeding
```

## Step 2: Convert to WeChat HTML

After the article is saved. Load `wechat-md-to-article-dl` skill.

Determine theme based on article domain:

| Article domain | Theme |
|----------------|-------|
| 教育方法论、学习方法、认知科学 | `cognition` |
| 健康、医学、养生 | `health` |
| AI、技术、编程、系统架构 | `tech` |
| 商业、理财、副业、效率 | `wealth` |
| 其他 / 通用 | `cognition` (dennon default) |

```bash
python3 ~/.hermes/skills/wechat-md-to-article-dl/scripts/convert.py \
  "<absolute-path-to-article.md>" \
  --output /tmp/<short-name>.wechat.html \
  --theme <theme> \
  --title "<full-article-title>"
```

**Quality gate**: Read the output JSON report. Verify all 5 scores ≥ 90.
- visual_hierarchy ≥ 90
- readability ≥ 90
- restraint ≥ 90
- consistency ≥ 90
- wechat_compatibility ≥ 90

If any score < 90, re-run with `--quality-threshold 90`. If still failing, report the failed dimensions to the user and ask how to proceed.

No `--official-check` unless the user explicitly requests it.

## Step 3: Generate cover

Use **Direct Mode** — the simplified 2-step approach (not the full pipeline).

### Extract cover title from article

Read the article's first `# ` heading (the full title). The cover needs a short version:

- **Cover title** (`--title`): first ≤14 characters of the article title
- **Cover subtitle** (`--subtitle`): remaining characters (if any)
- If full title is ≤14 chars, use it whole with no subtitle
- **Prefer semantic split at punctuation**: When the title contains `：` (full-width colon), `——` (em dash), or `·` (middle dot), split at that delimiter first regardless of character count. The colon-delimited pair reads naturally as title/subtitle. Example: `"为什么刷手机不是休息：注意力系统的隐性破产"` → title=`"为什么刷手机不是休息"`, subtitle=`"注意力系统的隐性破产"`.
- **Priority when rules conflict**: Semantic split wins over char count. When pre-punctuation text exceeds 14 chars (e.g. `"Context Engineering的噪声陷阱"` = 17 chars), use it anyway — gen_cover.py auto-adjusts font size. The 14-char limit is a safe heuristic for arbitrary cuts, not a hard bound when a natural semantic boundary exists.

### Fetch image

```bash
python3 ~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py \
  --query "<3-5 English keywords from article topic>" \
  --min-width 800
```

Parse the `image_url` from stdout JSON.

### Render cover

```bash
python3 ~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py \
  --title "<cover-title (≤14 chars)>" \
  --subtitle "<subtitle>" \
  --image-url "<image-url>" \
  --template auto \
  --align center \
  --output "~/Downloads/<short-name>-cover.png"
```

**Quality gate**: Visually verify the cover by opening it:
```bash
open ~/Downloads/<short-name>-cover.png
```

**Show the user before continuing.** Wait for user approval of the cover before proceeding to Step 4. If the user wants changes, re-render with adjustments (different image, different title split, different template) until approved.

### Image reuse prevention

Check `~/.hermes/skills/wechat-cover-generator-dl/references/used-images.txt` before fetching. If the fetched image's Unsplash ID is already in the file, fetch again with different keywords. Append new IDs after rendering.

Picsum images (fastly.picsum.photos) have no Unsplash ID — skip the check for those.

## Step 4: Push to drafts

Load `wechat_article_push_dl` skill.

### Safety stop

🔴 **STOP — Show the user the exact command and wait for confirmation.**
Do NOT execute until the user explicitly says "go ahead" or "push it".

**Session acceleration**: After the first push in a session has been seen and confirmed, "confirm" alone is sufficient for subsequent pushes — the user has already approved the pattern. Skip re-displaying the full command.

```bash
cd ~/Documents && md2wechat \
  --html /tmp/<short-name>.wechat.html \
  --author dennon \
  --cover ~/Downloads/<short-name>-cover.png
```

- Do NOT add `--style` — the HTML already has inline styles from Step 2
- Do NOT add `--title` — it's auto-extracted from the HTML H1
- `cd ~/Documents` is REQUIRED — that's where the .env credentials live

### Execute

Only after user confirmation. Check the result:
- `"success": true` + `media_id` → done
- Error code → decode and fix per wechat_article_push_dl's failure table

### Complete

Tell the user:
- Article has been pushed to WeChat 草稿箱 (drafts)
- Review and publish at mp.weixin.qq.com → 草稿箱
- Do NOT claim it was auto-published

## Step 5: Save outputs and generate summary

After Steps 1-4 are complete, consolidate all intermediate and final artifacts into a
single workspace directory for easy review, debugging, and future reference.

### Workspace structure

```
<workspace-dir>/
  ├── article.md                          # original Markdown (Step 1)
  ├── <name>.wechat.html                  # WeChat-formatted HTML (Step 2)
  ├── <name>.wechat.html.report.json      # quality report (Step 2)
  ├── <name>-cover.png                    # 900×383 cover image (Step 3)
  └── summary.txt                         # pipeline summary (this step)
```

### Workspace directory

Use a date-stamped directory so each run gets its own folder and old runs can be revisited:

```bash
SHORT_NAME="<short-name>"  # e.g. context-engineering, education-margin
WORKSPACE="$HOME/.hermes/skills/social-media/wechat-article-write-to-push-dl-workspace/$(date +%Y%m%d)/$SHORT_NAME"
mkdir -p "$WORKSPACE"
```

### Write summary.txt

Generate a plain-text summary documenting:

- Pipeline run date
- Article title
- Each step's status (PASSED / SKIPPED / BLOCKED)
- For Step 2: theme used and all 5 quality scores
- For Step 3: image source (Picsum / Unsplash ID), cover title, subtitle
- For Step 4: the exact push command shown to the user (even if not executed)
- Full paths to all outputs

Copy all intermediate files into the workspace so a future review or re-push
has everything in one place:

```bash
cp <article.md>     "$WORKSPACE/"
cp <wechat.html>    "$WORKSPACE/"
cp <report.json>    "$WORKSPACE/"
cp <cover.png>      "$WORKSPACE/"
cp summary.txt      "$WORKSPACE/"
```

### Rationale

Without consolidation, artifacts scatter across `/tmp/` (ephemeral) and
`~/Downloads/` (hard to find later). A single workspace dir makes it possible
to:
- Re-push without re-running Steps 1-3
- Share the full pipeline state for review
- Debug quality failures by checking the report.json alongside the HTML

## Full pipeline example

A typical publish run — uses absolute paths (not `~`) since Python scripts do not
expand tilde:

```bash
# Step 1: MUST use dennon-perspective skill to write the article (see Step 1 section above)
# Load dennon-perspective → feed source → get ~/Downloads/<标题前20字>.md
# Then validate:
python3 /Users/f/.hermes/skills/dennon-perspective/scripts/layout-check.py \
  "/Users/f/Downloads/<标题前20字>.md"
# Must exit 0 before proceeding

# Step 2:
python3 ~/.hermes/skills/wechat-md-to-article-dl/scripts/convert.py \
  "/Users/f/Downloads/学习系统的三重模型重构.md" \
  --output /tmp/learning-system.wechat.html \
  --theme cognition \
  --title "低维努力的陷阱：学习系统的三重模型重构"

# Step 3:
python3 ~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py \
  --query "learning brain cognition focus" --min-width 800
python3 ~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py \
  --title "低维努力的陷阱" \
  --subtitle "学习系统的三重模型重构" \
  --image-url "https://fastly.picsum.photos/..." \
  --template auto --align center \
  --output "/Users/f/Downloads/学习系统-cover.png"

# Step 4 (after user confirms):
cd ~/Documents && md2wechat --html /tmp/learning-system.wechat.html \
  --author dennon --cover "/Users/f/Downloads/学习系统-cover.png"

# Step 5: Save outputs
WORKSPACE="$HOME/.hermes/skills/social-media/wechat-article-write-to-push-dl-workspace/$(date +%Y%m%d)/outputs"
mkdir -p "$WORKSPACE"
cp "/Users/f/Downloads/学习系统的三重模型重构.md" "$WORKSPACE/article.md"
cp /tmp/learning-system.wechat.html "$WORKSPACE/"
cp /tmp/learning-system.wechat.html.report.json "$WORKSPACE/"
cp "/Users/f/Downloads/学习系统-cover.png" "$WORKSPACE/"
echo "All outputs saved to $WORKSPACE"
```

## Failure handling

| Step | Failure | Response |
|------|---------|---------|
| 1 | layout-check fails | Fix layout diversity, re-run check. If adjective: report to user |
| 2 | Score < 90 | Rerun in strict mode. If still failing, show failed dimensions to user |
| 2 | Unicode filename | Copy to `/tmp/` with ASCII name per wechat-md-to-article-dl's workaround |
| 3 | Image fetch fails | Retry with different keywords (max 3 attempts). Then fallback to gradient with `--no-image` |
| 3 | Cover title truncated | Shorten `--title`, move overflow to `--subtitle` |
| 4 | `40164` IP not whitelisted | Read actual IP from error, tell user to add to mp.weixin.qq.com whitelist |
| 4 | `MISSING_COVER_IMAGE` | Verify cover path exists, re-run with absolute path |
| 4 | CLI not found | `pip3 install md2wechat` |

## Output summary

When the pipeline completes successfully, report:

```json
{
  "article_md": "~/Downloads/<title>.md",
  "wechat_html": "/tmp/<name>.wechat.html",
  "cover_png": "~/Downloads/<name>-cover.png",
  "theme": "<theme>",
  "scores": {"visual_hierarchy": N, "readability": N, "restraint": N, "consistency": N, "wechat_compatibility": N},
  "media_id": "<media_id from push>",
  "draft_url": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=<id>&token=<token>&lang=zh_CN"
}
```

## Verification checklist (before claiming completion)

- [ ] layout-check.py exit code 0 (Step 1)
- [ ] All 5 WeChat HTML scores ≥ 90 (Step 2)
- [ ] Cover opened and user confirmed (Step 3)
- [ ] User confirmed push command (Step 4)
- [ ] Push returned `"success": true` with `media_id`
- [ ] No `--style` flag added to push command
- [ ] No `--title` flag added to push command
- [ ] `cd ~/Documents` executed before push
- [ ] All outputs copied to workspace directory (Step 5)
- [ ] summary.txt written with step-by-step status

## Reference files

- `references/eval-grading-pitfalls.md` — Workarounds for grader field-name bugs, `run-1/` directory requirement, and `passed` polarity errors discovered during this skill's test cycle.

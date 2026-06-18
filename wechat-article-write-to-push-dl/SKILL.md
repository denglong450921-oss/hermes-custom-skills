---
name: wechat-article-write-to-push-dl
description: >
  Choreographed pipeline for WeChat Official Account full-publish workflow.
  Orchestrates 4 skills in sequence: dennon-perspective (write article) →
  wechat_md-to-article-dl (convert to HTML) → wechat-cover-generator-dl
  (generate cover) → wechat_article_push_dl (push to drafts).
  Trigger when the user says "publish", "推文", "推送", "发布公众号",
  "write and push", or finishes a denton-style article and wants it published.
  This skill is the single entry point — do NOT ask the user to run each
  sub-skill manually.
---

# WeChat Write-to-Push Pipeline

Choreographs 4 existing skills into one end-to-end workflow.
Each step delegates to a dedicated skill — this skill owns sequencing, data
handoff, quality gates, and safety stops.

## Pipeline overview

```
[Input] Article topic or clipping
  ↓
Step 1: dennon-perspective → write article → ~/Downloads/<title>.md
  ↓
Step 2: wechat_md-to-article-dl → convert to HTML → /tmp/<name>.wechat.html
  ↓
Step 3: wechat-cover-generator-dl → generate cover → ~/Downloads/<name>-cover.png
  ↓
Step 4: wechat_article_push_dl → push to drafts
  ↓
[Done] User reviews draft at mp.weixin.qq.com
```

## Before starting

Assess input type:

| Input | Action |
|-------|--------|
| Clipping path (`Clippings/Auto Article/` or vault path) | Follow dennon-perspective's Auto Article clipping rules |
| Raw transcript path (`.mp4` URL or file) | First transcribe with `video-transcribe` skill, then use the transcript as source |
| Topic phrase ("写一篇关于X的文章") | Go directly to Step 1; dennon-perspective writes from framework alone |
| Existing `.md` file | Skip Step 1, go to Step 2 |
| `--cover-only` flag | Skip Steps 1-2, go directly to Step 3 |
| `--push-only` flag with existing HTML + cover | Skip Steps 1-3, go directly to Step 4 |

## Step 1: Write article

Load `dennon-perspective` with `thinking-models-dl` (the skill auto-loads it).

Follow the full Agentic Protocol:
1. **Step 1 (Problem classification)** — determine if research is needed
2. **Step 2 (Research)** — only if factual data is required
3. **Step 2.5 (Structure architecture)** — model matching from thinking-models-dl
4. **Step 3 (Writing)** — produce Dennon-style article
5. **Step 4 (Cleanup)** — run layout-check.py, pass all checks

**Output**: `~/Downloads/<标题前20字>.md`
**Quality gate**: layout-check.py exit code 0 (7+ layout types, ≤3 consecutive text paragraphs, adjacent chapter diversity).

If layout check fails, fix and re-run before proceeding to Step 2.

## Step 2: Convert to WeChat HTML

After the article is saved. Load `wechat_md-to-article-dl` skill.

Determine theme based on article domain:

| Article domain | Theme |
|----------------|-------|
| 教育方法论、学习方法、认知科学 | `cognition` |
| 健康、医学、养生 | `health` |
| AI、技术、编程、系统架构 | `tech` |
| 商业、理财、副业、效率 | `wealth` |
| 其他 / 通用 | `cognition` (dennon default) |

```bash
python3 ~/.hermes/skills/wechat_md-to-article-dl/scripts/convert.py \
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

## Full pipeline example

A typical publish run from a vault clipping:

```bash
# Step 1 already ran — article saved
# Step 2:
python3 ~/.hermes/skills/wechat_md-to-article-dl/scripts/convert.py \
  "~/Downloads/学习系统的三重模型重构.md" \
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
  --output "~/Downloads/学习系统-cover.png"

# Step 4 (after user confirms):
cd ~/Documents && md2wechat --html /tmp/learning-system.wechat.html \
  --author dennon --cover ~/Downloads/学习系统-cover.png
```

## Failure handling

| Step | Failure | Response |
|------|---------|---------|
| 1 | layout-check fails | Fix layout diversity, re-run check. If adjective: report to user |
| 2 | Score < 90 | Rerun in strict mode. If still failing, show failed dimensions to user |
| 2 | Unicode filename | Copy to `/tmp/` with ASCII name per wechat_md-to-article-dl's workaround |
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

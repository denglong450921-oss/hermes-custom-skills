---
name: wechat-cover-generator-dl
description: >
  Generate complete WeChat Official Account cover images from a Markdown file,
  article topic, or title. Use when the user asks for a WeChat cover, 公众号封面,
  thumbnail, article banner, 900x383 PNG, cover pipeline, or wants title
  metadata plus a validated cover report. Provides a self-contained Python
  runner that creates a deterministic 900x383 PNG and JSON report, and can also
  orchestrate external title/image/validation/rendering skills when available.
---

# WeChat Cover Generator

Generate a WeChat-ready `900x383` PNG cover and a structured pipeline report.
Default to the bundled runner so the skill works when installed alone.

## Quick Path

Use `scripts/run_pipeline.py` for most requests:

```bash
python3 scripts/run_pipeline.py \
  --input /path/to/article.md \
  --style tech \
  --output /tmp/wechat-cover.png \
  --report /tmp/wechat-cover-report.json
```

The runner needs Pillow to render PNG files. If the active `python3` lacks
Pillow, it automatically retries with the Codex bundled Python runtime when
available; otherwise install it with `python3 -m pip install pillow`.

If the user gives only a topic:

```bash
python3 scripts/run_pipeline.py \
  --topic "OPC / AI / 个人商业系统" \
  --style high-level \
  --output /tmp/opc-cover.png
```

The runner writes:

```json
{
  "cover_image_url": "/tmp/opc-cover.png",
  "title_md_path": "/tmp/opc-cover-title.md",
  "validation": "pass",
  "dimensions": [900, 383],
  "image_source": "deterministic_gradient",
  "image_validation_attempts": 1
}
```

## Input Rules

Accept one of these inputs:

| Input | Use |
|---|---|
| `--input article.md` | Extract first `#` heading as title and body as topic context |
| `--topic "..."` | Generate title metadata from the topic |
| `--title "..."` | Use the exact cover title after length validation |
| `--image-path file` or `--image-url URL` | Use a provided background, then crop and overlay safely |

If title, topic, and Markdown are all missing, ask the user for the article
topic before generating.

## Workflow

1. Parse the article title/topic.
2. Generate compact title metadata: title, subtitle, tagline, label.
3. Choose a style palette: `tech`, `business`, `cognitive`, `health`,
   `professional`, or `auto`.
4. Render the cover with center-safe text and a deterministic gradient or
   provided image.
5. Validate dimensions, title presence, safe area, and report completeness.
6. Return the PNG path and JSON report.

🛑 STOP: Show the generated cover to the user before using it in a downstream
draft, upload, or publication workflow.

## External Skill Mode

Use external skills only when the user explicitly needs live image search,
special title generation, or stricter visual validation:

| Step | Optional external skill | Keep this invariant |
|---|---|---|
| Title metadata | `wechat-title-generator-dl` | Still write `title_md_path` |
| Image sourcing | `open-source-image-fetch-dl` | Keep license and source fields |
| Image validation | `image-quality-validator-dl` | Record pass/fail and attempts |
| Rendering | `wechat_article_cover_image_gen` | Final PNG must be `900x383` |

After external orchestration, normalize the final report to the output contract
above so downstream workflows do not depend on which path was used.

## Quality Gates

| Gate | Pass condition |
|---|---|
| Canvas | Exactly `900x383` PNG |
| Title | Non-empty, readable, max 2 lines |
| Safe area | Main text stays at least 60px from left/right edges |
| Contrast | Dark or light overlay keeps title readable |
| Report | Includes cover path, title metadata path, validation, dimensions, source |

## Failure Handling

| Trigger | Response | Fallback |
|---|---|---|
| Missing title/topic | Ask for topic | Use filename stem only if a Markdown file exists |
| Provided image cannot load | Continue with deterministic gradient | Report `image_source: deterministic_gradient` |
| Title too long | Generate a shorter cover title | Preserve full title in title metadata |
| Output path unwritable | Stop with the exact path error | Use `/tmp/wechat-cover.png` only after telling the user |
| Validation fails | Return `validation: fail` and blocker details | Do not claim the cover is ready |

## Anti-Patterns

| Do not | Why |
|---|---|
| Claim the full live pipeline ran when only the deterministic runner ran | Misleads downstream publishing decisions |
| Skip PNG existence or dimension checks | Broken covers can reach WeChat drafts |
| Hardcode one stock image for every topic | Causes repeated, generic covers |
| Hide fallback mode | Users need to know whether an external image was used |
| Publish or upload without user confirmation | Cover choice is editorial, not just technical |

## References

Read `references/pipeline-reference.md` when a request needs external skill
orchestration, live image fetching, retry strategy, or report normalization.

Use `templates/pipeline-input.md` as the starting Markdown format and
`templates/full-command.sh` as a copyable command example.

## Self-Eval

Run the harness from the skill directory:

```bash
python3 evals/run_harness.py
```

The harness runs the bundled pipeline on three realistic prompts, opens the PNGs
with Pillow, validates dimensions, checks report fields, and writes traces under
`evals/traces/`.

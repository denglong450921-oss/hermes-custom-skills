---
name: wechat-article-cover-image-gen
description: >
  Generate sharp, beautiful 900x383 PNG cover images for WeChat Official
  Account articles. Use when the user asks for a WeChat cover, 公众号封面,
  article thumbnail, banner, social preview image, composite cover, readable
  title overlay, clear text on image, non-blurry text, premium editorial cover,
  or wants article metadata rendered into a PNG with title, subtitle, tagline,
  label, safe-zone validation, and text sharpness reporting.
---

# WeChat Article Cover Image Generator

Generate a **sharp 900x383 PNG** cover for WeChat Official Accounts. The
bundled renderer draws text at high resolution, downsamples with LANCZOS, and
applies a light unsharp mask so text stays clear after compositing.

## Quick Start

Use deterministic gradient mode for reliable local output:

```bash
python3 scripts/gen_cover.py \
  --title "AI 时代的 OPC" \
  --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
  --tagline "决策者 + AI 工具链 · 可验证需求 · 商业闭环系统" \
  --label "AI ERA · ONE PERSON COMPANY" \
  --template business \
  --align left \
  --no-image \
  --output /tmp/cover.png \
  --report /tmp/cover.report.json
```

Use a provided background image:

```bash
python3 scripts/gen_cover.py \
  --title "AI 工作流质量门禁" \
  --subtitle "从提示词到生产系统" \
  --template tech \
  --image-path /path/to/background.jpg \
  --output /tmp/cover.png
```

The output is always a PNG file, even when the background is JPEG or a remote
image.

## Input Rules

| Field | Required | Notes |
|---|---:|---|
| `--title` | Yes | Short cover title; long titles wrap to at most 2 lines |
| `--subtitle` | No | One sentence, usually under 28 Chinese chars |
| `--tagline` | No | Micro copy or concept tags |
| `--label` | No | Top label, default `FEATURED ARTICLE` |
| `--output` | Yes | PNG output path |
| `--report` | No | JSON quality report path |
| `--image-path` | No | Local background, center-cropped |
| `--image-url` | No | Remote background, center-cropped |
| `--no-image` | No | Use deterministic gradient, no network |
| `--stock-fallbacks` | No | Try bundled stock URLs when no image is provided |
| `--template` | No | `auto`, `tech`, `insight`, `business` |
| `--align` | No | `center` or `left` |
| `--render-scale` | No | Internal scale 2-5, default 4 |

## Style Selection

| Template | Best for | Visual direction |
|---|---|---|
| `tech` | AI, software, workflow, systems | dark blue, cool accent, crisp center or left type |
| `insight` | cognition, essays, thinking | warm editorial paper, dark text, calm contrast |
| `business` | strategy, finance, OPC, growth | black/brown gradient, gold accent, premium left layout |
| `auto` | mixed topics | balanced dark editorial cover |

Use `left` alignment for premium magazine/editorial covers. Use `center` for
symmetrical tech and concept covers.

## Text Clarity Rules

- Keep the cover title short enough to read at thumbnail size.
- Prefer one strong title plus one supporting subtitle; avoid paragraphs.
- Render with `--render-scale 4` unless speed matters.
- Keep `--outline-width 2` for dark or mixed backgrounds.
- Do not screenshot HTML text into the cover; render text directly with
  `scripts/gen_cover.py`.
- Treat `text_sharpness_score < 7.0` as a failed cover.

The report includes:

```json
{
  "format": "PNG",
  "canvas": [900, 383],
  "render_scale": 4,
  "downsample_filter": "LANCZOS",
  "unsharp_mask": {"radius": 0.65, "percent": 155, "threshold": 2},
  "text_sharpness_score": 28.52,
  "safe_zone_left_ok": true,
  "safe_zone_right_ok": true
}
```

## Quality Gates

Before claiming the cover is ready, confirm:

- output file opens as PNG;
- dimensions are exactly `900x383`;
- text was rendered at `3x` or higher internal scale;
- `text_sharpness_score >= 7.0`;
- all important text stays at least 60px from left/right edges;
- title has 1-2 lines and main font is at least 38px;
- subtitle and tagline are readable but clearly secondary;
- final cover has one focal idea and no crowded text.

## Failure Handling

| Failure | Response |
|---|---|
| Missing Pillow | Report install command; the script auto-tries Codex bundled Python |
| Image cannot load | Use deterministic gradient and report `image_source` |
| Long title wraps poorly | Shorten the title or use a stronger 2-line version |
| Safe zone fails | Switch to `left` layout, shorten text, or reduce subtitle/tagline |
| Text sharpness fails | Use `--render-scale 4`, avoid screenshot text, keep PNG output |
| Output path invalid | Stop with the exact path error |

## Verification

Run:

```bash
python3 -m unittest discover -s tests
python3 evals/run_harness.py
python3 scripts/gen_cover.py \
  --title "AI 时代的 OPC" \
  --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
  --template business \
  --align left \
  --no-image \
  --output /tmp/wechat-cover.png \
  --report /tmp/wechat-cover.report.json
```

Open the PNG and inspect it at 100% zoom. If the title looks soft or muddy, do
not ship it.

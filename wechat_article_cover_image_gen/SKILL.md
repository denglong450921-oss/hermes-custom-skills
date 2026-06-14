---
name: wechat_article_cover_image_gen
description: >
  Generate a WeChat Official Account cover image (900x383 PNG) from article
  metadata. Downloads a free stock photo, applies a uniform dark overlay, and
  draws centred, outlined text (title + subtitle + tagline) with a gold accent
  bar. Use this skill whenever the user needs a cover image for a WeChat
  article push — they'll mention "cover image", "封面", "cover", or want to
  push an article and need a cover. It handles the full pipeline: stock photo
  download (with multiple fallbacks), Chinese/English font rendering with text
  outline, and automatic vertical/horizontal centering.
---

# WeChat Article Cover Image Generator

Generate a polished **900×383 PNG cover image** for WeChat Official Account
articles. The script handles stock photo download (with auto-fallback), text
layout, and rendering.

## Prerequisites

- **Pillow** (`pip3 install Pillow`)
- **numpy** (`pip3 install numpy`)
- **STHeiti Medium** font — comes pre-installed on macOS at
  `/System/Library/Fonts/STHeiti Medium.ttc`. Falls back to Songti.
- **Internet connection** on first run (stock photo download).

## Workflow

### 1. Gather article metadata

Extract from the article's title, subtitle/summary, and tagline.

| Element | Source | Example |
|---|---|---|
| `--title` (required) | Article title | `"AI 时代的 OPC"` |
| `--subtitle` | Summary / subtitle | `"一个人如何用最小成本跑通自己的商业闭环"` |
| `--tagline` | Key concept / tagline | `"决策者 + AI 工具链 · 可验证需求 · 商业闭环"` |
| `--label` | Top category label | `"AI ERA  ·  ONE PERSON COMPANY"` |

The label is an English descriptive tag. If the user doesn't specify one,
derive it from the article topic.

### 2. Run the script

```bash
python3 <skill_dir>/scripts/gen_cover.py \
  --title "AI 时代的 OPC" \
  --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
  --tagline "决策者 + AI 工具链  ·  可验证需求  ·  商业闭环系统" \
  --label "AI ERA  ·  ONE PERSON COMPANY" \
  --output /path/to/cover.png
```

**Options:**

| Flag | Required | Default | Description |
|---|---|---|---|
| `--title` | **Yes** | — | Main title (supports Chinese/English) |
| `--subtitle` | No | `""` | Subtitle below title |
| `--tagline` | No | `""` | Bottom tagline |
| `--label` | No | `"FEATURED ARTICLE"` | Top label |
| `--output` | **Yes** | — | Output PNG path |
| `--image-url` | No | Auto fallback | Custom stock image URL (900×383 preferred) |
| `--outline-width` | No | `2` | Text outline radius in pixels |

### 3. Present result

Open the generated PNG and show the user where it was saved:

```bash
open /path/to/cover.png
```

Report the cover metadata:
- Output path
- Title font size and width coverage
- Canvas dimensions (900×383)

## Design rules

- **Font**: STHeiti Medium (Chinese sans-serif). Falls to Songti (serif).
- **Overlay**: Uniform `rgba(5,8,15,165)` over the full canvas (Dark Mode safe).
- **Title**: Largest font that fits ~93% width. Pure white + 2px black outline.
- **Subtitle**: 26pt, white + 1px outline.
- **Label/Tagline**: Smaller, gold/warm-gray with outline.
- **Gold accent bar**: 260px centred, gradient fade on edges.
- **Centering**: Both horizontal (pixel-perfect via mask) and vertical (block centre).
- **Stock image**: Auto-downloads from Unsplash with 5 fallback URLs.

## Failure handling

| Failure | Response |
|---|---|
| `STHeiti Medium.ttc` not found | Falls back to Songti, then STHeiti Light |
| Stock image download fails | Tries all 5 fallback Unsplash URLs, then creates a solid dark gradient |
| Invalid output path | Show the error and ask for a valid directory |
| Pillow / numpy missing | `pip3 install Pillow numpy` |

## Verification

Confirm:
- Output file exists (use `ls -la <path>`)
- File is a valid PNG (use `file <path>` or `python3 -c "from PIL import Image; Image.open('<path>')"`)
- Text is centred and readable (open in browser)
- Image is 900×383 pixels

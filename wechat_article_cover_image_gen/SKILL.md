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

**Real article → parameters example:**
```
Article title:  "AI 时代的 OPC"
Article summary: "一个人如何用最小成本跑通自己的商业闭环"
Key concept:   "决策者 + AI 工具链 · 可验证需求 · 商业闭环"
Topic category: "AI · Business"

→ --title "AI 时代的 OPC"
→ --subtitle "一个人如何用最小成本跑通自己的商业闭环"
→ --tagline "决策者 + AI 工具链 · 可验证需求 · 商业闭环"
→ --label "AI ERA  ·  ONE PERSON COMPANY"
```

If no explicit subtitle/tagline exists in the article, derive from the
article's summary and key takeaway. Keep `--label` under 30 chars.

🔴 **CHECKPOINT: Verify you have all 4 metadata fields filled before proceeding.
Missing `--title` or `--output` will cause the script to fail.**

🛑 **STOP: Show the user the exact command before running.**
Present the full `python3 gen_cover.py` command with all arguments and
the expected output path. Wait for explicit confirmation before executing.
This prevents accidentally overwriting an existing file or using wrong text.

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

Open the generated PNG and report the cover metadata to the user:

```bash
open /path/to/cover.png
```

**Output report template:**
```
Cover generated: /path/to/cover.png
  Canvas: 900x383
  Title: AI 时代的 OPC
  Title font: 125px
  Title width coverage: 93%
  Vertical offset: 66px
```

If the cover text appears clipped or off-centre, offer to regenerate with
adjusted parameters (shorter title, different `--outline-width`).

## Design rules

- **Font**: STHeiti Medium (Chinese sans-serif). Falls to Songti (serif).
- **Overlay**: Uniform `rgba(5,8,15,165)` over the full canvas (Dark Mode safe).
- **Title**: Largest font that fits ~93% width. Pure white + 2px black outline.
- **Subtitle**: 26pt, white + 1px outline.
- **Label/Tagline**: Smaller, gold/warm-gray with outline.
- **Gold accent bar**: 260px centred, gradient fade on edges.
- **Centering**: Both horizontal (pixel-perfect via mask) and vertical (block centre).
  See [references/text-centering-technique.md](references/text-centering-technique.md)
  for the algorithm (mask-based centering avoids font-bearing asymmetry).
- **Stock image**: Auto-downloads from Unsplash with 5 fallback URLs.

## Failure handling

| Trigger | First-line fix | Still fails → fallback |
|---|---|---|
| `STHeiti Medium.ttc` not found | Falls back to Songti, then STHeiti Light | Install font: `cp /System/Library/Fonts/Supplemental/Songti.ttc ~/Library/Fonts/` |
| Stock image download fails | Retries with Unsplash fallback URLs (5 total) | Creates a solid dark gradient background |
| Invalid output path | Verify the parent directory exists: `ls -la <parent>` | Use `/tmp/cover.png` as fallback path |
| Pillow / numpy missing | `pip3 install Pillow numpy` | Use system Python with `python3 -m venv venv && source venv/bin/activate && pip install` |
| Title text is extremely long (>25 chars) | Script auto-reduces font size to fit canvas | If still clipped, manually shorten the title or use a 2-line subtitle |
| Output PNG looks dim | Overlay alpha may be too high | No fix needed — uniform `rgba(5,8,15,165)` is intentional for Dark Mode readability |

## Verification

Confirm:
- Output file exists (use `ls -la <path>`)
- File is a valid PNG (use `file <path>` or `python3 -c "from PIL import Image; Image.open('<path>')"`)
- Text is centred and readable (open in browser)
- Image is 900×383 pixels

## 反例与黑名单 (Anti-Patterns)

下列操作不仅无效，还可能造成不良后果。避免使用。

| 反模式 | 为什么危险 | 替代做法 |
|--------|-----------|---------|
| 手动用 Photoshop/Canva 做封面 | 耗时且无法自动化，每次文章更新需重新设计 | 用 `gen_cover.py` 一次生成，改文字只需改参数 |
| 跳过 `--output` 参数不指定路径 | 脚本不知道写到哪里，报错退出 | 始终指定完整路径，如 `--output ~/Desktop/cover.png` |
| 用随机网络图片当封面 | 版权风险 + 图片比例不匹配 900×383 | 使用 Unsplash 免费图片或脚本默认自动下载 |
| 在图片上手动叠加文字 | 文字可能被 WeChat 裁剪或遮挡 | 脚本自动在底部留安全区域 + 居中布局 |
| 封面文字过多（>50 个字符） | 视觉拥挤，在 WeChat 缩略图中看不清 | 标题保持在 20 字符以内，多余信息放 subtitle/tagline |
| 纯英文标题过长 | 英文字符窄，长句在 125px 字重下超长溢出 | 保持在 15 个英文单词以内，或用缩写 |

## Harness (Self-Eval)

The harness validates that `gen_cover.py` produces valid 900×383 PNG covers
with correct text layout.

### Cases

| ID | Scenario |
|----|----------|
| `case_001` | Full Chinese article cover — title, subtitle, tagline, label |
| `case_002` | Minimal English-only cover — title only |
| `case_003` | Long Chinese title — dense content centering |

### Checks

| Check | What it detects |
|-------|----------------|
| `script_exits_ok` | No errors or tracebacks in stdout |
| `output_file_exists` | PNG file was written to the specified path |
| `valid_png` | File is a valid PNG image (Pillow `verify()`) |
| `correct_dimensions` | Image is exactly 900×383 pixels |
| `title_coverage_90plus` | Self-reported title width ≥ 90% of canvas |

### Run

```bash
# Full harness
python3 evals/run_harness.py

# Single check
python3 evals/grader.py <output-file> '<checks-json>'
```

### Honesty & Truthfulness

Report results exactly as they are:
- Test failed → state "failed" with the actual evidence
- Skipped verification → say "not verified", don't imply it passed
- No defensive disclaimers on correct results ("but this might not be correct")
- No false success — if output shows failure, don't claim "all passed"

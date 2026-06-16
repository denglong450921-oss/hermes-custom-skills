---
name: wechat_article_cover_image_gen
description: >
  Generate a high-end, editorial-quality WeChat Official Account cover image
  (900×383 PNG) from article metadata. Downloads a free stock photo, applies a
  uniform overlay, and renders text with professional hierarchy (BIG title →
  SMALL subtitle → MICRO tagline). Supports left-aligned (premium editorial) and
  center-aligned (modern tech) layouts, plus themed style kits (tech, insight,
  business, auto). Use this skill whenever the user needs a cover image for a
  WeChat article push — they'll mention "cover image", "封面", "thumbnail",
  "banner", or want to push an article and need a clickable cover. It handles
  the full pipeline: stock photo download (with fallbacks), Chinese/English font
  rendering with text outline, safe-zone compliance, and TDD-style quality
  checklist. Always prefer this over manual design tools.
---

# WeChat Article Cover Image Generator

Generate a **high-end 900×383 cover image** for WeChat Official Accounts.
Professional editorial design principles: single focal idea, strong contrast,
minimal text, clear hierarchy, breathing space.

## 🔑 First Principle: What a WeChat Cover Really Is

A WeChat cover is NOT decoration, background art, poster, or branding wallpaper.

It IS: **a clickable thumbnail + information signal + attention hook**.

Its job:
```
1. Stop scrolling
2. Communicate topic in 1 second
3. Make user want to click
```

## 📐 Official WeChat Specs (Hard Rules)

| Property | Value |
|---|---|
| Canvas | **900×383 px** (ratio ~2.35:1) |
| Safe zone L/R | ≥ **60px** padding from edges |
| Safe zone T/B | Avoid placing key text at extreme edges |
| Feed crop | Different across feed list, article page, share preview — never put key text at edges |

## 🧱 Design Rules (Visual Hierarchy)

### Rule 1: ONE focal point only
```
✔ "AI entrepreneur working alone"
✔ "minimal workspace laptop"
✗ multiple objects / multiple ideas
```

### Rule 2: Text hierarchy (BIG → SMALL → MICRO)
```
Main title:  28-40px  (BIG)
Subtitle:    14-18px  (SMALL)
Tag / Label: 12-14px  (MICRO)
```

Never equal-weight text. The eye must know where to look first.

### Rule 3: Contrast is mandatory
```
Option A: white text + dark overlay  (rgba(0,0,0,0.35))
Option B: black/dark text + light overlay  (rgba(255,255,255,0.35))
```

### Rule 4: Minimal text principle
```
MAX: 1 main title + 1 subtitle + optional tag
✗ paragraphs, explanations, long sentences
```

### Rule 5: Alignment system
```
Left-aligned  → premium editorial style (magazine feel)
Center-aligned → modern tech style (clean, symmetric)
✗ random positioning, scattered layout, diagonal text
```

### Rule 6: Breathing space = luxury signal
```
Minimum left/right safe zone: 60px
Don't crowd text. Keep padding.
Luxury feeling = empty space.
```

## 🎨 Visual Style Rules

| Rule | Guideline |
|---|---|
| Saturation | Low saturation — black/white/gray, deep blue, muted green, warm beige |
| Images | Real photography preferred (workspace, human+laptop, environment) |
| Avoid | Cartoon style, random AI abstract art, neon colors, rainbow tones |
| Depth | Foreground (text) → middle (subject) → background (blur/depth) |
| Spacing | ≥ 60px safe zone, don't crowd text |

## 🧩 Professional Layout Templates

### Template: tech
```text
[dark overlay bg, center-aligned]

AI时代的OPC
——一个人的商业系统
```
Style: dark + minimal + high contrast. Cool blue accent. No gold bar.

### Template: insight
```text
[light warm overlay, center-aligned]

一个关键认知：
MVP不是产品，而是验证
```
Style: editorial / magazine. Warm brown accent. Gold bar.

### Template: business
```text
[deep dark overlay, left-aligned]

一个人公司的真正边界
```
Style: black + gold accent + minimal text. Gold bar.

### Template: auto
```text
[default — auto-detect based on content]
```
Style: 35% black overlay, gold label, center-aligned.

## ⚠️ Common Mistakes

| Mistake | Problem |
|---|---|
| Too much text | Unreadable at thumbnail size |
| No contrast | Gray on gray = invisible |
| Over-design | Too many gradients/shadows/colors = cheap |
| Random image | Must match topic (AI → laptop workspace, not city skyline) |
| Squeezed layout | No breathing space = cluttered |

## Prerequisites

- **Pillow** (`pip3 install Pillow`)
- **numpy** (`pip3 install numpy`)
- **STHeiti Medium** font — macOS at `/System/Library/Fonts/STHeiti Medium.ttc`. Falls back to Songti.
- **Internet connection** on first run (stock photo download).

## Workflow

### 1. Gather article metadata

| Element | Source | Example |
|---|---|---|
| `--title` (required) | Article title — keep ≤ 20 chars | `"AI 时代的 OPC"` |
| `--subtitle` | Summary / subtitle | `"一个人如何用最小成本跑通自己的商业闭环"` |
| `--tagline` | Key concept tag | `"决策者 + AI 工具链 · 可验证需求 · 商业闭环"` |
| `--label` | Top category label (≤ 30 chars) | `"AI ERA  ·  ONE PERSON COMPANY"` |

**TITLE LENGTH RULE:** Keep `--title` short (≤ 20 Chinese chars or ≤ 10 English words). Long titles get wrapped to 2 lines at smaller font, which reduces impact. If the article title is long, use a shortened version for the cover and keep the full version for the article metadata.

### 2. Choose template + alignment

Match template to article domain:

| Article type | Template | Alignment |
|---|---|---|
| Tech / AI / Systems | `tech` | center |
| Essay / Insight / Thinking | `insight` | center |
| Business / Finance / Wealth | `business` | left |
| Mixed / Unsure | `auto` | center |

### 3. Run the script

```bash
python3 <skill_dir>/scripts/gen_cover.py \
  --title "AI 时代的 OPC" \
  --subtitle "一个人如何用最小成本跑通自己的商业闭环" \
  --tagline "决策者 + AI 工具链  ·  可验证需求  ·  商业闭环" \
  --label "AI ERA  ·  ONE PERSON COMPANY" \
  --template business \
  --align left \
  --image-url "https://images.unsplash.com/photo-xxx?w=900&h=383&fit=crop" \
  --output /path/to/cover.png
```

**Options:**

| Flag | Required | Choices | Default | Description |
|---|---|---|---|---|
| `--title` | **Yes** | — | — | Main title (keep ≤ 20 chars for best results) |
| `--subtitle` | No | — | `""` | Subtitle (14-18px) |
| `--tagline` | No | — | `""` | Bottom tagline (12-14px) |
| `--label` | No | — | `"FEATURED ARTICLE"` | Top label (12-14px, ≤ 30 chars) |
| `--output` | **Yes** | — | — | Output PNG path |
| `--image-url` | No | — | Auto fallback | Stock image URL (900×383 preferred) |
| `--align` | No | `center`, `left` | `center` | Text alignment |
| `--template` | No | `auto`, `tech`, `insight`, `business` | `auto` | Visual style template |
| `--overlay-opacity` | No | 0.0–1.0 | Template default | Override overlay darkness |
| `--outline-width` | No | — | 2 | Text outline radius in px |

### 4. Present result

Open the generated PNG and report:

```bash
open /path/to/cover.png
```

**Output report includes:**
```
Cover generated: /path/to/cover.png
  Canvas: 900x383
  Template: business  Align: left
  Title: AI 时代的 OPC
  Title font: 36px  Lines: 1
  Title width coverage: 78%
  Vertical offset: 52px
  Safe zone L: ✓  R: ✓

  TDD Checklist:
    ✔  Safe zones ≥ 60px on both sides
    ✔  Title font ≤ 40px
    ✔  Title font ≥ 28px
    ✔  Title readable (coverage ≥ 40%)
    ✔  Title ≤ 2 lines
```

If the TDD checklist shows any ✗, regenerate with adjusted parameters.

## Design rules (technical)

### Text sizing
- Title: 28-40px, adaptive based on text length. Longer text → smaller font.
- Subtitle: 16px fixed. White/light fill with 1px outline.
- Label/Tagline: 13px fixed. Colored accent with 1px outline.

### Layout
- **Center alignment**: Text centered via pixel-precise mask (L margin == R margin).
- **Left alignment**: Text starts at 72px from left edge (≥ 60px safe zone).
- Vertical: Content block vertically centered, max 85% of canvas height, min 40px top/bottom padding.

### Overlay
- **tech**: rgba(0,0,0,0.40) — deep for contrast
- **insight**: rgba(255,248,240,0.31) — warm editorial
- **business**: rgba(5,8,15,0.35) — dark blue-black
- **auto**: rgba(0,0,0,0.35) — neutral dark

### Accents
- **Gold bar**: 260px centered (or left-aligned with left mode). Gradient fade on edges. Only shown when template enables it and content includes subtitle or tagline.
- **Label**: Always top-left or top-center per align mode.

## Failure handling

| Trigger | First-line fix | Still fails → fallback |
|---|---|---|
| Font not found | Fall back to Songti, then STHeiti Light | Report exact missing font path |
| Stock image fails | Retry Unsplash fallbacks (5 URLs) | Solid dark gradient background |
| Invalid output path | Check parent directory exists | Use `/tmp/cover.png` |
| Pillow / numpy missing | `pip3 install Pillow numpy` | System venv install |
| Title extremely long (>30 chars) | Auto-wraps to 2 lines at 28px | Offer to shorten title |
| Safe zone test fails | Adjust alignment or shorten text | Widen padding in script |

## TDD-Style Test Checklist

Before publishing, always verify:

```
✔ Can I understand topic in 1 second?
✔ Is there only one focal idea?
✔ Is text readable on mobile?
✔ Is contrast strong enough?
✔ Is image relevant to topic?
✔ Is layout simple and clean?
✔ Does it look like editorial / system thinking content?
```

The script prints a machine-checkable subset. For the subjective checks above, inspect the output image visually.

## Verification

Confirm:
- Output file exists (`ls -la <path>`)
- Valid PNG (`file <path>` or `python3 -c "from PIL import Image; Image.open('<path>').verify()"`)
- Dimensions: exactly 900×383
- Safe zones: L/R ≥ 60px (script reports ✓/✗)
- Font range: title 28-40px, subtitle 14-18px, tag/label 12-14px
- No crowded text, no edge-adjacent elements

## 反例与黑名单 (Anti-Patterns)

| 反模式 | 为什么危险 | 替代做法 |
|---|---|---|
| 手动用 Photoshop/Canva 做封面 | 耗时且无法自动化 | 用 `gen_cover.py` 一次生成 |
| 标题过长（> 20 字） | 在 WeChat 缩略图中无法阅读 | 截取核心概念作为封面标题 |
| 用随机网络图片 | 版权风险 + 比例不匹配 | 使用 Unsplash 或脚本默认图库 |
| 灰底灰字 | 无对比度 = 不可读 | 始终用深色叠层 + 白色文字 |
| 多焦点多颜色 | 看起来廉价 | 一个焦点 + 低饱和度配色 |
| 零留白 | 拥挤 = 低端感 | 保持 ≥ 60px 安全区 |

## Harness (Self-Eval)

The harness validates that `gen_cover.py` produces valid 900×383 PNG covers.

### Cases

| ID | Scenario |
|---|---|
| `case_001` | Full Chinese article cover — title, subtitle, tagline, label, center align |
| `case_002` | Minimal English-only cover — title only, left align, insight template |
| `case_003` | Long Chinese title — dense content, auto-wrapping, safe zone check |

### Checks

| Check | What it detects |
|---|---|
| `script_exits_ok` | No errors or tracebacks |
| `output_file_exists` | PNG file was written |
| `valid_png` | File is a valid PNG image |
| `correct_dimensions` | Image is exactly 900×383 pixels |
| `title_font_in_range` | Title font 28-40px |
| `safe_zones_ok` | L/R safe zones ≥ 60px |

### Run

```bash
# Full harness
python3 evals/run_harness.py

# Single check
python3 evals/grader.py <output-file> '<checks-json>'
```

### Honesty & Truthfulness

Report results exactly as they are:
- Test failed → state "failed" with evidence
- Skipped verification → say "not verified"
- No false success

---
name: "html-output"
description: "编写美观易读的 HTML 输出，用于复杂的 AI 回复。当回复包含比较表格、流程步骤、带指标的卡片、可折叠代码块时使用。触发词: HTML, HTML output, generate HTML, 生成HTML, layout, card, table, steps, highlight, 美观HTML, 网页输出, 富文本"
---

# HTML Output

> 核心原则：HTML 唯一的优势是 **信息密度**。读者能在 10 秒内理解的东西，远超过任何线性 markdown。**如果 10 秒内抓不住重点 → 失败。**

## Quick Navigation

| If you want to... | Go to... |
|---|---|
| Start with the rules | [Core Principles](#core-principles) |
| Build the layout | [Layout System](#layout-system-proven-must-follow) |
| See available CSS | [output.css Reference](#what-outputcss-provides) |
| Verify before shipping | [Pre-Delivery Protocol](#pre-delivery-verification-protocol必须逐条过缺一不可) |
| Self-check your output | [Quality Checklist](#quality-checklist产出前逐条检查) |
| Run automated evaluation | [Harness (Self-Eval)](#harness-self-eval) |
| Avoid common pitfalls | [Common HTML Mistakes](#-common-html-mistakes--what-not-to-do) |

## TL;DR — Experienced User Workflow

1. Wrap everything in `<div class="container">`
2. Lead with an `.insight` card — the thesis in one sentence
3. Use `<table>` for comparisons, `.steps` for sequences, `.callout` for takeaways
4. Wrap code/long references in `<details><summary>`
5. Insert `<hr>` between every major section
6. Walk the 10-element [Pre-Delivery Protocol](#pre-delivery-verification-protocol必须逐条过缺一不可) before claiming completion

## Core Principles

### ① HTML 不是必须的

大部分回复用 markdown 就够了。只在以下情况下启用 HTML output：
- 含 **3+ 项的对比表**（方案/产品/方案比较）
- 含 **量化比较**（评分、涨幅、价格档位）
- 含 **3+ 步骤的流程/演进/历史阶段**
- 涉及流程/架构/关系类空间信息（纯文字讲不清的）

> 🔴 **CHECKPOINT**: Is the response complex enough for HTML? If none of the above conditions are met, output plain markdown. Using HTML for simple answers wastes tokens and reader attention.

## Layout System (PROVEN, must follow)

### Step 1: 元素计划

**2–3 秒**：先规划用哪些 CSS 组件、分几段。通常结构如下：

```
.container                    # 全局容器，始终在最外层
  .insight                    # [必选] 全文核心结论/论点
  <hr>                        # 分隔线

  <p>                         # 正文介绍
  .callout                    # 关键发现/警告/建议

  <table>                     # 对比/筛选/排行（必须有 <thead>）
  <hr>

  <ol class="steps">          # 3+ 步的演进/流程

  <details><summary>          # 代码块/引用/参考表
```

### Step 2: 组件填充

按 <skill-dir>/references/output.css 定义的 class 填充内容。常用组件频次：

**高频（每篇必用）**

| 组件 | CSS class | 用途 |
|------|-----------|------|
| 容器 | `.container` | 所有内容的根容器 |
| 核心结论 | `.insight` | 全文唯一的论点，必须放最前面 |
| 分隔线 | `<hr>` | 分隔每大段，约 3-4 个 |
| 关键引用 | `.callout` | 警示、建议、关键数据 |
| 段落 | `<p>` | 正文 |

**中频（根据内容类型）**

| 组件 | CSS class | 用途 |
|------|-----------|------|
| 步骤列表 | `<ol class="steps">` | 3+ 步的演进/流程 |
| 表格 | `<table>` + `<thead>` | 对比/特征/评分 |
| 高亮 | `.highlight` | 关键指标/数值 |
| 折叠块 | `<details><summary>` | 代码/引用/次要参表 |

**低频（特定场景）**

| 组件 | CSS class | 用途 |
|------|-----------|------|
| 卡片组 | `.card-grid` | 多卡对比 |
| 子弹笔记 | `.highlight-list` | 紧凑要点 |
| 双栏 | `.two-column` | 左右对照 |
| 特殊引用 | `.pullquote` | 名言/高度凝练句 |
| 来源 | `.source`、`.source-inline` | 引用的来源标注 |

### Step 3: 输出

把 `<style>` 复制到开头（就在 `container` 前），然后按计划写 HTML。

> 🔴 **CHECKPOINT**: Before claiming the HTML is complete, you MUST walk the Pre-Delivery Protocol below. Skipping this step is the #1 cause of failed grader checks.

## What output.css provides

The complete CSS is in `<skill-dir>/references/output.css`. It provides:

### Layout
- `.container` — max-width 800px centered, responsive padding
- `.two-column` — CSS grid, 1fr 1fr on desktop, stacked on mobile
- `.card-grid` — auto-fill grid, min 280px cards

### Typography
- Serif body, sans-serif headings, mono for code
- `.callout` — left border accent, bold title + body text
- `.insight` — centered large text with accent bar, for the single key thesis
- `.pullquote` — decorative quote style
- `.source`, `.source-inline` — citation styles

### Data
- `.highlight` — `.num` (large number) + `.label` (description)
- `.highlight-list` — compact bullet list with accent bullets
- `<table>` — clean bordered table with `<thead>` header styling

### Interactive
- `<ol class="steps">` — numbered timeline with `data-step` labels
- `<details><summary>` — expandable sections, styled arrow

No extra inline CSS needed. Just paste the whole file.

> 🔴 **CHECKPOINT**: Before running the Quality Checklist, fix any obvious layout issues first. The checklist catches known patterns — but cannot fix sloppy structure.

Common blind spots from production sessions:
- **`.steps` missing**: Articles with a sequential process (pipeline stages, evolution, how-to steps) look like they have visual flow from the text but lack the actual `<ol class="steps">` element. If the content describes 3+ sequential phases, you MUST use `.steps`.
- **`.highlight` missing**: Articles with concrete stats, metrics, or big numbers (scores, percentages, counts, money) must use `.highlight` to make them scannable. A number in body text is invisible.
- **`<table>` missing**: Any side-by-side comparison (tools, options, features, tiers) needs a `<table>` with `<thead>`. Even 3 rows × 2 columns counts.
- **`<details>` missing**: Code blocks, secondary reference tables, optional drill-down content should be wrapped in `<details>`/`<summary>` to keep the page scannable.

## Quality Checklist（产出前逐条检查）

1. `.container` 包裹所有内容？
2. `.insight` 是否有且仅有一个？（全文核心论点）
3. 每个 `.callout`、表格、步骤是否包含 **无法目视观察到的信息**？**不要为 AI 废话加特效**？
4. 代码有没有少 `/` 闭合？常见问题：`</summary>` 写成 `<summary>`、`<hr>` 写成 `<hr/>`
5. 表格有无 `<thead>`、`<tbody>`、`<th>`？数据大屏是否缺了最后一行导致跨行不对齐？
6. 引号是否正确配对？有没有花式空格？（常见的 copy-paste 污染源）
7. CSS 是否粘贴完整（整个 `<style>` 块，自包含，无外部引用）？
8. CSS 内是否有引入非常用字体（如 `Georgia`、`Merriweather`）？这些在 Claude 沙箱中可能失效。
9. 语言风格是否与 HTML layout 一致？**一句一句读**，不要有机器感。**白话讲复杂事，不讲专业黑话**。
10. **这篇去掉 HTML 特效后是否仍有阅读价值？** 如果内容不值得 markdown，HTML 也救不了。

> **Failure mode:** If the HTML's key insights look the same as body text, the checklist should catch this at lines 2-3. Fix by wrapping in `.callout` or `.insight`.

## ❌ Common HTML Mistakes — What NOT to Do

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|------------------|
| 1 | **Skip `.container` wrapper** | Content floats left, no centering, breaks layout at all breakpoints | Every output wrapped in `<div class="container">` |
| 2 | **Bury key insights in body text** | Readers scan for visual anchors — plain text looks like filler | Use `.callout` (key insight) or `.insight` (punchline) |
| 3 | **Put numbers/stats in plain paragraphs** | Numbers in running text are invisible — readers miss critical data | Use `.highlight` with `.num` + `.label` |
| 4 | **Write `<table>` without `<thead>`** | First row looks like data, no semantic header, accessibility fails | Always include `<thead>` with `<th>` elements |
| 5 | **Use `<ol>` for sequential processes** | Regular numbered lists have no visual timeline, hard to follow for 3+ steps | Use `<ol class="steps">` with `data-step` attributes |
| 6 | **Leave code blocks visible** | Long code sections bloat the page, distract from narrative | Wrap in `<details><summary>` for expand/collapse |
| 7 | **Claim "all classes used correctly" without verifying** | Optimistic reporting hides real layout errors, breaks feedback loop | Walk the 10-element Pre-Delivery Protocol honestly |
| 8 | **Mix inline CSS with output.css classes** | Inline overrides break dark/light auto-switch, creates maintenance debt | Use only output.css classes — no inline styles |
| 9 | **Omit `<hr>` between sections** | Content runs together visually, no breathing room for scanning | Insert `<hr>` between every major section |
| 10 | **Add defensive disclaimers** | "This might not render correctly" undermines confidence, adds noise | Trust the layout system — if it follows the protocol, it renders correctly |

## Harness (Self-Eval)

> 🔴 **CHECKPOINT**: The grader is a structural validator, not a design judge. A "PASS" means all required elements exist — but does not guarantee the output is well organized or pleasant to read. Always manually review after an automated pass.

This skill has a built-in eval harness following the Agent Harness 5-module pattern. It tests whether HTML output meets quality standards.

### Files

- `evals/grader.py` — Main grading logic, outputs `PASS`/`FAIL`
- `evals/run_harness.py` — CLI runner for testing against eval pairs
- `evals/evals.json` — Eval pair definitions

### Quick Test

Run the grader on the last output:
```bash
python3 <skill-dir>/evals/grader.py --mode reason < <last-html-file>
```

Or run the full harness:
```bash
python3 <skill-dir>/evals/run_harness.py
```

### Feedback Loop

- `feedback/distill.py` — Process session logs into training examples
- `feedback/ftpr.py` — Calculates First-Token Pass Rate (how often the first attempt passes)
- `feedback/failures.jsonl` — Collected failure modes from production

### Honesty & Truthfulness

- `references/honesty-grader-patch.md` — Prevents the model from lying about "using all CSS classes correctly"
- `references/feedback-loop.md` — How to incorporate feedback

## References

| File | Purpose |
|------|---------|
| `references/output.css` | The complete CSS stylesheet |
| `references/feedback-loop.md` | How to improve from production failures |
| `references/honesty-grader-patch.md` | Prevents false "all classes correct" claims |
| `references/mermaid-dark-theme.md` | Dark theme for Mermaid diagrams |

## Version History

- **v4.2**: Added `.source` / `.source-inline` for citations. Added honesty-grader-patch rules. Updated output.css with dark mode auto-switch.
- **v4.1**: Added `.pullquote` for decorative quotes. Simplified "MUST / SHOULD / MAY" to plain language. Added blind spots section.
- **v4.0**: Complete rewrite. Added card-grid, tier-list, highlight-list. Removed .toc. Simplified steps. Added Quality Checklist.

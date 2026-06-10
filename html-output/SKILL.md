---
name: "html-output"
description: "将复杂 AI 回复改写为美观、易读、逻辑清晰的 HTML 页面。凡是用户要求 HTML、网页输出、富文本、美化排版，或内容包含多层论证、关键结论、比较表格、流程步骤、指标卡片、架构关系、决策路径时，都应使用此技能。输出必须先总结核心观点，再突出关键点，用合适的图示或结构表达逻辑，展开细节后回到整体结论，形成总—分—总结构。触发词: HTML, HTML output, generate HTML, 生成HTML, layout, card, table, steps, highlight, diagram, flowchart, 美观HTML, 网页输出, 富文本, 总结重点, 逻辑图"
---

# HTML Output

> 核心原则：HTML 唯一的优势是 **信息密度**。读者能在 10 秒内理解的东西，远超过任何线性 markdown。**如果 10 秒内抓不住重点 → 失败。**

## Ultimate Principles

每次修改或生成 HTML，都先把原始内容变成一个可扫读的论证，而不是把段落机械地套进卡片。

1. **先总结核心观点**：开头用 `.executive-summary` 承载标题、一个 `.insight` 核心结论，以及 3–5 个最重要要点。读者先拿到地图，再进入细节。
2. **突出关键点**：重要结论、数字、风险、建议必须成为视觉锚点。用 `.callout`、`.highlight`、`.highlight-list` 或表格，不要把关键内容埋在普通段落里。
3. **让逻辑可见**：用 `.logic-map` 包裹最合适的关系表达。线性过程用 `.steps`，对比用 `<table>`，并列维度用 `.card-grid`，左右关系用 `.two-column`，复杂分支或网络关系才使用 Mermaid。
4. **总—分—总**：开头给全局结论，中间按逻辑拆分并展开证据，结尾用 `.closing-synthesis` 回到整体判断和下一步。结尾不是重复开头，而是把细节重新压缩成行动。

### 10-second reading path

```text
Executive summary
  -> highlighted key points
  -> logic map
  -> detailed sections and evidence
  -> closing synthesis
```

## Quick Navigation

| If you want to... | Go to... |
|---|---|
| Start with the rules | [Core Principles](#core-principles) |
| Build the layout | [Layout System](#layout-system-proven-must-follow) |
| Choose the logic visual | [Logic Visual Selection](#logic-visual-selection) |
| See available CSS | [output.css Reference](#what-outputcss-provides) |
| Recover from a failed review | [Failure Recovery Matrix](#failure-recovery-matrix) |
| Self-check your output | [Quality Checklist](#quality-checklist产出前逐条检查) |
| Run automated evaluation | [Harness (Self-Eval)](#harness-self-eval) |
| Avoid common pitfalls | [Common HTML Mistakes](#-common-html-mistakes--what-not-to-do) |

## TL;DR — Experienced User Workflow

1. Wrap everything in `<div class="container">`
2. Open with `<section class="executive-summary">`: title, one `.insight`, then 3–5 key points
3. Add one `.logic-map` using the simplest visual grammar that makes the reasoning obvious
4. Use `<table>` for comparisons, `.steps` for sequences, `.callout` and `.highlight` for important takeaways
5. Develop the details in logical sections, wrapping secondary material in `<details><summary>`
6. Close with `<section class="closing-synthesis">` that reconnects the details to the overall judgment and next step
7. Insert `<hr>` between every major section
8. Walk the [Quality Checklist](#quality-checklist产出前逐条检查) before claiming completion

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
  .executive-summary          # [必选] 开头总览
    .insight                  # [必选] 全文核心结论/论点
    .highlight-list           # [必选] 3–5 个关键点
  <hr>                        # 分隔线

  .logic-map                  # [必选] 逻辑图：steps/table/cards/two-column/Mermaid
  <hr>

  <section>                   # 分：正文解释、证据、比较和细节
    <p>
    .callout                  # 关键发现/警告/建议
    <table>                   # 对比/筛选/排行（必须有 <thead>）
  <hr>

  .closing-synthesis          # [必选] 总：归纳判断 + 下一步
```

### Step 2: 组件填充

按 <skill-dir>/references/output.css 定义的 class 填充内容。常用组件频次：

**高频（每篇必用）**

| 组件 | CSS class | 用途 |
|------|-----------|------|
| 容器 | `.container` | 所有内容的根容器 |
| 总览 | `.executive-summary` | 开头总览：标题、核心结论、关键要点 |
| 核心结论 | `.insight` | 全文唯一的论点，必须放最前面 |
| 逻辑图 | `.logic-map` | 包裹最合适的关系表达 |
| 结尾归纳 | `.closing-synthesis` | 回到整体判断和下一步 |
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
| Mermaid | `.mermaid` | 复杂分支、依赖网络、架构关系；简单流程不要用 |
| 特殊引用 | `.pullquote` | 名言/高度凝练句 |
| 来源 | `.source`、`.source-inline` | 引用的来源标注 |

### Step 3: 输出

把 `<style>` 复制到开头（就在 `container` 前），然后按计划写 HTML。

#### 输出路径规则

**HTML 文件必须写入 `~/Downloads/`，不是当前项目目录。**

```
path = ~/Downloads/<descriptive-name>.html
```

原因：浏览器直接从 `~/Downloads/` 打开，不需要从项目目录复制。用户习惯在下载目录找渲染好的文件。

例外：只有当用户明确指定项目目录路径时（如"放在 docs/ 下"），才写入指定位置。

#### 写入后自动打开

HTML 文件写入后，**必须立即用 Chrome 打开**：

```
open -a "Google Chrome" ~/Downloads/<filename>.html
```

用当前运行时可用的 shell 或 terminal 工具执行。不要等用户问"打开看看"——直接打开。

> 🔴 **CHECKPOINT**: Before claiming the HTML is complete, you MUST walk the [Quality Checklist](#quality-checklist产出前逐条检查) below. If any item fails, use the [Failure Recovery Matrix](#failure-recovery-matrix) before rechecking.

## Logic Visual Selection

逻辑图不是装饰。它要让读者比阅读段落更快地理解结构。选择最简单、最准确的表达：

| 内容关系 | 优先表达 | 原因 |
|---|---|---|
| 3+ 个连续阶段、操作步骤、演进过程 | `<ol class="steps">` inside `.logic-map` | 最轻量，离线可用 |
| 方案、产品、优缺点、参数差异 | `<table>` inside `.logic-map` | 横向比较最快 |
| 并列的支柱、模块、原因、策略 | `.card-grid` inside `.logic-map` | 让同层概念一眼可见 |
| 输入/输出、现状/目标、问题/解法 | `.two-column` inside `.logic-map` | 强化两侧关系 |
| 分支决策、依赖网络、架构、反馈回路 | Mermaid inside `.logic-map` | 图关系无法用线性列表清楚表达 |

如果使用 Mermaid，先读 `references/mermaid-dark-theme.md`。不要为了“看起来高级”把简单列表升级成 CDN 图。

## General-Specific-General Writing Pattern

### General: opening map

- 用 `.executive-summary` 先说清楚：主题是什么、最重要判断是什么、读者该记住哪 3–5 点。
- `.insight` 只保留一个，写成一句有判断力的话。
- 关键点按重要性排序，不按原文出现顺序排序。

### Specific: structured development

- 每一段只承担一个任务：解释、比较、举证、风险或行动。
- 用标题和 `<hr>` 让阅读层级可见。
- 每个视觉组件必须承载真实信息差：表格用于比较，步骤用于顺序，卡片用于并列，callout 用于提醒。

### General: closing synthesis

- 用 `.closing-synthesis` 收束全文。
- 回答两个问题：细节共同说明了什么？读者下一步应该做什么？
- 不要逐句复述开头，要把分散证据重新压缩成一个可行动的结论。

## What output.css provides

The complete CSS is in `<skill-dir>/references/output.css`. It provides:

### Layout
- `.container` — max-width 800px centered, responsive padding
- `.two-column` — CSS grid, 1fr 1fr on desktop, stacked on mobile
- `.card-grid` — auto-fill grid, min 280px cards
- `.executive-summary` — summary-first opening block
- `.logic-map` — visual reasoning wrapper
- `.closing-synthesis` — concluding synthesis block

### Typography
- Sans-serif body with CJK font stack, mono for code
- `.callout` — white card + gradient left accent border, bold title + body text
- `.insight` — opening quote mark decoration, accent-soft background
- `.pullquote` — decorative quote mark via `::before`, gradient text
- `.source`, `.source-inline` — citation styles
- **CJK content:** The reference `output.css` already includes `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC"` in the body font-family. When copy-pasting the `<style>` block, verify CJK fonts were not stripped — the stack must include at least the above four Chinese fonts. If they were dropped, re-append them after `Arial`.

### Data
- `.highlight` — gradient text `.num` + `.label` (description), soft gradient background
- `.highlight-list` — compact bullet list with gradient accent dots, bottom-separated lines
- `<table>` — clean bordered table with `<thead>` header styling, strip rows, hover highlight

### Interactive
- `<ol class="steps">` — numbered timeline with gradient circle icons and glow shadow
- `<details><summary>` — expandable sections, styled arrow box
- `.closing-item` — flex card with gradient numbered circle, left-aligned title + desc, hover lateral shift

### Extended layout (append to `<style>` when needed)

**Multiple `.highlight` in a row** — when you have 2-3 related metrics that need side-by-side display (e.g., actual vs expected, brand A/B/C):

**Symmetrical stat layouts** — see the full [Symmetrical Layout Patterns](#symmetrical-layout-patterns-for-numbers--graphics) section below for: T-shape, 2×2 Grid, Three-Column, Center + Wings, Cross, and Figure + Stats patterns. Each includes CSS + HTML + responsive rules.
```css
.highlights-row {
  display: flex;
  gap: 1em;
  margin: 1.2em 0;
}
.highlights-row .highlight {
  flex: 1;
  margin: 0;
}
@media (max-width: 640px) {
  .highlights-row { flex-direction: column; }
}
```
Usage: `<div class="highlights-row">` wrapping 2-3 `.highlight` blocks. Do NOT use inline `style=""` attributes on `.highlight` elements to force them side-by-side — use this class instead.

**"T-shape" stat block** — when you have one primary metric and two secondary ones, arrange as a full-width primary above and two side-by-side below:
```html
<div class="stat-block">
  <div class="highlight stat-primary">
    <span class="num" style="font-size: 2.8rem;">280 万</span>
    <span class="label">总价</span>
  </div>
  <div class="highlights-row">
    <div class="highlight">
      <span class="num">140 m²</span>
      <span class="label">面积</span>
    </div>
    <div class="highlight">
      <span class="num">≈2 万/m²</span>
      <span class="label">单价</span>
    </div>
  </div>
</div>
```
The `.stat-primary` block should fill full width (`margin: 0 0 1em 0`). The `.highlights-row` handles the flex row below. Add this CSS to the `<style>` block:
```css
.stat-block { margin: 1.2em 0; }
.stat-primary .num { font-size: 2.8rem; }
```
Apply `.stat-primary` as a class on the `.highlight` wrapper of the primary stat, not extra inline styles.

**When the output.css itself lacks a utility**: append the missing CSS to the `<style>` block rather than using inline `style=""` attributes on elements. This preserves the separation of concerns and keeps dark/light switching intact.

### Symmetrical Layout Patterns for Numbers & Graphics

These patterns ensure **visual symmetry** — equal visual weight, balanced whitespace, and aligned metrics. Choose the simplest pattern that fits your data.

#### Pattern: "2×2 Grid" — four equal metrics in a square

```css
.grid-2x2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1em;
  margin: 1.2em 0;
}
.grid-2x2 .highlight {
  margin: 0;
  padding: 1em 0.8em;
}
@media (max-width: 640px) {
  .grid-2x2 { grid-template-columns: 1fr; }
}
```
```html
<div class="grid-2x2">
  <div class="highlight"><span class="num">98%</span><span class="label">Uptime</span></div>
  <div class="highlight"><span class="num">2.3s</span><span class="label">Avg Latency</span></div>
  <div class="highlight"><span class="num">12K</span><span class="label">Daily Users</span></div>
  <div class="highlight"><span class="num">$4.2M</span><span class="label">Revenue</span></div>
</div>
```

#### Pattern: "Three-Column" — three metrics equally balanced

```css
.cols-3 {
  display: flex;
  gap: 1em;
  margin: 1.2em 0;
}
.cols-3 .highlight {
  flex: 1;
  margin: 0;
}
@media (max-width: 640px) {
  .cols-3 { flex-direction: column; }
}
```
```html
<div class="cols-3">
  <div class="highlight"><span class="num">$280</span><span class="label">Avg Order</span></div>
  <div class="highlight"><span class="num">3.2★</span><span class="label">Rating</span></div>
  <div class="highlight"><span class="num">42%</span><span class="label">Growth</span></div>
</div>
```

#### Pattern: "Center + Wings" — one primary centered, two side mirrors

Use when you have a central figure flanked by two symmetrical companions (left/right mirror).

```css
.center-wings {
  display: flex;
  align-items: stretch;
  gap: 1em;
  margin: 1.2em 0;
}
.center-wings .highlight {
  flex: 1;
  margin: 0;
}
.center-wings .highlight.center-wing-main {
  flex: 1.5;
  padding: 1.5em 1em;
}
.center-wings .highlight.center-wing-main .num {
  font-size: 2.2rem;
}
@media (max-width: 640px) {
  .center-wings { flex-direction: column; }
}
```
```html
<div class="center-wings">
  <div class="highlight"><span class="num">-12%</span><span class="label">Last Year</span></div>
  <div class="highlight center-wing-main"><span class="num">+45%</span><span class="label">Current YoY</span></div>
  <div class="highlight"><span class="num">+8%</span><span class="label">Industry Avg</span></div>
</div>
```

#### Pattern: "Cross" — center + four cardinal points

Use for radar / balanced-scorecard layouts where the central metric summarises four surrounding dimensions.

```css
.stat-cross {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  grid-template-rows: auto auto auto;
  gap: 0.8em;
  justify-items: center;
  align-items: center;
  margin: 1.2em 0;
}
.stat-cross .highlight {
  margin: 0;
  width: 100%;
  text-align: center;
}
.stat-cross .highlight.cross-north  { grid-column: 2; grid-row: 1; }
.stat-cross .highlight.cross-west   { grid-column: 1; grid-row: 2; }
.stat-cross .highlight.cross-center { grid-column: 2; grid-row: 2; }
.stat-cross .highlight.cross-east   { grid-column: 3; grid-row: 2; }
.stat-cross .highlight.cross-south  { grid-column: 2; grid-row: 3; }
.stat-cross .highlight.cross-center .num {
  font-size: 2.8rem;
}
@media (max-width: 640px) {
  .stat-cross { grid-template-columns: 1fr 1fr; grid-template-rows: auto; }
  .stat-cross .highlight { grid-column: auto; grid-row: auto; }
}
```
```html
<div class="stat-cross">
  <div class="highlight cross-north"><span class="num">92</span><span class="label">Satisfaction</span></div>
  <div class="highlight cross-west"><span class="num">87</span><span class="label">Quality</span></div>
  <div class="highlight cross-center"><span class="num">4.5★</span><span class="label">Overall</span></div>
  <div class="highlight cross-east"><span class="num">91</span><span class="label">Delivery</span></div>
  <div class="highlight cross-south"><span class="num">78</span><span class="label">Support</span></div>
</div>
```

#### Pattern: "Figure + Stats" — graphic left, stats right (or vice versa)

Use when you have an icon / small chart / figure that should visually anchor a balanced block of stats.

```css
.figure-stats {
  display: flex;
  gap: 1.5em;
  align-items: center;
  margin: 1.2em 0;
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5em;
  box-shadow: var(--shadow);
}
.figure-stats .figure-area {
  flex: 0 0 100px;
  text-align: center;
  font-size: 2.5rem;
}
.figure-stats .stats-area {
  flex: 1;
  display: flex;
  gap: 1em;
}
.figure-stats .stats-area .highlight {
  flex: 1;
  margin: 0;
  background: var(--bg);
  border: 1px solid var(--border);
}
@media (max-width: 640px) {
  .figure-stats { flex-direction: column; text-align: center; }
  .figure-stats .figure-area { flex-basis: auto; }
  .figure-stats .stats-area { flex-direction: column; width: 100%; }
}
```
```html
<div class="figure-stats">
  <div class="figure-area">📊</div>
  <div class="stats-area">
    <div class="highlight"><span class="num">83%</span><span class="label">Engagement</span></div>
    <div class="highlight"><span class="num">+24%</span><span class="label">vs Last Month</span></div>
  </div>
</div>
```

When combining a graphic with 3+ stats, keep the graphic side at `flex: 0 0 100px` and let the stats wrap using the `cols-3` or `grid-2x2` pattern inside `.stats-area`.

**Choosing the right pattern:**

| Data shape | Pattern |
|---|---|
| One dominant number + two supporters | T-shape (above) |
| Four equal KPIs | 2×2 Grid |
| Three equal numbers | Three-Column |
| Central comparison (us vs them) | Center + Wings |
| Balanced scorecard / 5-dimension | Cross |
| Icon/badge + supporting numbers | Figure + Stats |

No other extra inline CSS needed. Just paste the whole file.

> 🔴 **CHECKPOINT**: Before running the Quality Checklist, fix any obvious layout issues first. The checklist catches known patterns — but cannot fix sloppy structure.

Production remedies are encoded once in the matrix below. Use the first matching row, apply the smallest repair, then rerun the checklist.

## Failure Recovery Matrix

检查失败时不要继续堆组件。先修复最小根因，再重新走 Quality Checklist。只有第一修复仍然不能表达内容时，才使用 fallback。

| If this trigger appears | First repair | Fallback |
|---|---|---|
| 标题后直接进入长段落，10 秒内看不到结论 | 把核心判断移到开头 `.executive-summary`，保留一个 `.insight` 和 3–5 条 `.highlight-list` | 原始材料无法形成可靠结论时，明确写出"已知事实"和"待确认问题"，不要编造总结 |
| 关键数字、风险或建议和正文长得一样 | 将最重要的信息改为 `.highlight`、`.callout` 或比较表格 | 信息过多时只保留影响决策的 3–5 项，其余放入 `<details>` |
| `.logic-map` 只是装饰，不能更快解释关系 | 回到 [Logic Visual Selection](#logic-visual-selection)，替换为最简单准确的 steps / table / cards / two-column | 关系确实包含复杂分支或网络时才使用 Mermaid；外部图加载不可靠时回退到离线 HTML 结构 |
| CSS 显得太简单/不够精致,用户反馈"not beautiful enough" | 使用 v4 premium output.css（渐变 accent、多级 shadow、hover 动效、refined 中文排版），尾部的证据总结改用 `.closing-item` 卡片组件 | 如果仍然不够，退回到纯色干净方案，确保可读性优先 |
| 多个数字指标的排列方式被用户纠正（如"up big one, down left and right"） | 使用 T-shape stat block 模式：主指标全幅在上，两个副指标用 `.highlights-row` 并排在下 | 如果超过 3 个指标，参考 [Symmetrical Layout Patterns](#symmetrical-layout-patterns-for-numbers--graphics) 选择合适的对称布局（2×2 Grid / Three-Column / Center + Wings / Cross） |
| 3+ 个连续阶段或并排方案仍写成长段落 | 连续阶段改为 `<ol class="steps">`；并排方案改为带 `<thead>` 的 `<table>` | 不适合步骤或表格时，使用 `.card-grid` 或 `.two-column` 表达同层关系 |
| 代码、引用或次要参表抢占正文注意力 | 用 `<details><summary>` 收起次要内容 | 仍然过长时，正文只保留结论，将完整材料移到独立附录 |
| 文章停在最后一个细节，没有整体判断 | 添加 `.closing-synthesis`，回答“这些细节共同说明什么”和“下一步做什么” | 无法给出建议时，收束为决策条件和下一步验证动作 |
| 结构检查失败：缺少 wrapper、闭合标签、表头或 `data-step` | 修复最小 HTML 错误，再运行 `python3 <skill-dir>/evals/grader.py <last-html-file>` | 自动检查仍失败时，减少到 `.container` + summary + one logic view + details + synthesis 的最小有效结构 |
| CJK 正文显示为系统回退字体 | 检查 `<style>` 块 body font-family 是否包含 `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`。参考 output.css 已自带，但长 HTML 的 copy-paste 过程可能丢失 | 字体不可用时保留系统 sans-serif，确保可读性优先 |
| 浏览器没有自动打开，或当前环境不能调用 Chrome | 仍然写入 `~/Downloads/<descriptive-name>.html`，然后使用当前运行时可用的打开方式 | 无法打开浏览器时，返回完整文件路径并明确说明预览未自动启动 |

## Quality Checklist（产出前逐条检查）

1. `.container` 包裹所有内容？
2. 开头是否是 `.executive-summary`，并在进入细节前总结核心观点？
3. `.insight` 是否有且仅有一个？（全文核心论点）
4. 是否用 `.highlight-list`、`.callout`、`.highlight` 或表格突出真正关键的点？
5. 是否有 `.logic-map`？其表达方式是否比正文更快地解释关系？
6. 中间细节是否按解释、比较、证据、风险或行动分段，而不是堆砌？
7. 结尾是否有 `.closing-synthesis`，把细节重新归纳为整体判断和下一步？
8. 每个 `.callout`、表格、步骤是否包含 **无法目视观察到的信息**？**不要为 AI 废话加特效**？
9. 代码有没有少 `/` 闭合？常见问题：`</summary>` 写成 `<summary>`、`<hr>` 写成 `<hr/>`
10. 表格有无 `<thead>`、`<tbody>`、`<th>`？数据大屏是否缺了最后一行导致跨行不对齐？
11. 引号是否正确配对？有没有花式空格？（常见的 copy-paste 污染源）
12. CSS 是否粘贴完整（整个 `<style>` 块，自包含，无外部引用）？
13. CSS 内是否有引入非常用字体（如 `Georgia`、`Merriweather`）？这些在 Claude 沙箱中可能失效。
14. 语言风格是否与 HTML layout 一致？**一句一句读**，不要有机器感。**白话讲复杂事，不讲专业黑话**。
15. **这篇去掉 HTML 特效后是否仍有阅读价值？** 如果内容不值得 markdown，HTML 也救不了。
16. **HTML 文件是否写入 `~/Downloads/`？** 不要放到项目目录里。
17. **CJK 字体是否完整？** 参考 output.css 已包含 `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC"`，验证 copy-paste 后未被剥离。如果正文主要是中文但 font-family 缺少这些字体 → 重新追加。

> If any item fails, use the first matching row in the [Failure Recovery Matrix](#failure-recovery-matrix), repair the smallest root cause, then rerun this checklist.

## ❌ Common HTML Mistakes — What NOT to Do

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|------------------|
| 1 | **Skip `.container` wrapper** | Content floats left, no centering, breaks layout at all breakpoints | Every output wrapped in `<div class="container">` |
| 2 | **Bury key insights in body text** | Readers scan for visual anchors — plain text looks like filler | Use `.callout` (key insight) or `.insight` (punchline) |
| 3 | **Put numbers/stats in plain paragraphs** | Numbers in running text are invisible — readers miss critical data | Use `.highlight` with `.num` + `.label` |
| 4 | **Write `<table>` without `<thead>`** | First row looks like data, no semantic header, accessibility fails | Always include `<thead>` with `<th>` elements |
| 5 | **Use `<ol>` for sequential processes** | Regular numbered lists have no visual timeline, hard to follow for 3+ steps | Use `<ol class="steps">` with `data-step` attributes |
| 6 | **Leave code blocks visible** | Long code sections bloat the page, distract from narrative | Wrap in `<details><summary>` for expand/collapse |
| 7 | **Claim "all classes used correctly" without verifying** | Optimistic reporting hides real layout errors, breaks feedback loop | Walk the Quality Checklist honestly and use the Failure Recovery Matrix for any failed item |
| 8 | **Mix inline CSS with output.css classes** | Inline overrides break dark/light auto-switch, creates maintenance debt | Use only output.css classes — no inline styles |
| 9 | **Omit `<hr>` between sections** | Content runs together visually, no breathing room for scanning | Insert `<hr>` between every major section |
| 10 | **Add defensive disclaimers** | "This might not render correctly" undermines confidence, adds noise | Trust the layout system — if it follows the protocol, it renders correctly |
| 11 | **Start with details before summarizing** | Reader must reconstruct the argument before knowing why it matters | Open with `.executive-summary` |
| 12 | **Treat diagrams as decoration** | Adds visual noise without improving comprehension | Put the simplest accurate relationship view inside `.logic-map` |
| 13 | **End after the last detail** | Reader gets information but no integrated judgment or next step | Close with `.closing-synthesis` |
| 14 | **Use `"\\n".join()` to build HTML in Python** | `"\\n".join(list)` produces literal `\n` text in the output file instead of real line breaks — showing as visible `\n` in the browser | Use `"\n".join(list)` (real newline character) when assembling HTML fragments in Python. See `references/python-html-pitfalls.md` |

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
python3 <skill-dir>/evals/grader.py <last-html-file>
```

Or run every eval case against the last output:
```bash
python3 <skill-dir>/evals/run_harness.py <last-html-file>
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

- **v5.5**: Added 6 symmetrical layout patterns for numbers & graphics (T-shape, 2×2 Grid, Three-Column, Center + Wings, Cross, Figure + Stats) with CSS, HTML examples, responsive rules, and a pattern-selection table. Updated output.css reference with all new classes. Updated Failure Recovery Matrix to reference symmetrical patterns for multi-metric layout issues.
- **v5.3**: Upgraded output.css to v4 premium design: gradient accent system (blue-to-purple), soft page background + white cards, refined CJK typography (PingFang SC / Noto Sans SC), multi-level shadows (sm/md/lg), hover animations on cards/steps/closing-items, gradient decorative elements (h2 bars, hr, steps connector, callout border). Added `.closing-item` / `.closing-item-icon` / `.closing-item-title` / `.closing-item-desc` / `.closing-finale` / `.closing-finale-sub` components. Added "CSS not beautiful enough" row to Failure Recovery Matrix.
- **v5.2**: Consolidated repeated production blind spots into the Failure Recovery Matrix and added a direct logic-visual navigation route.
- **v5.1**: Added an explicit trigger → first repair → fallback recovery matrix. Replaced obsolete verification links with the current Quality Checklist and recovery flow.
- **v5.0**: Added summary-first, highlighted-key-point, visible-logic, and general-specific-general editorial contract. Added `.executive-summary`, `.logic-map`, and `.closing-synthesis` structure.
- **v4.3**: Added CJK font guidance — append `PingFang SC` / `Hiragino Sans GB` / `Microsoft YaHei` for Chinese content. Added blind spot + checklist item.
- **v4.1**: Added `.pullquote` for decorative quotes. Simplified "MUST / SHOULD / MAY" to plain language. Added blind spots section.
- **v4.0**: Complete rewrite. Added card-grid, tier-list, highlight-list. Removed .toc. Simplified steps. Added Quality Checklist.

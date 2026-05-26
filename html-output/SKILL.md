---
name: html-output
description: >
  Write beautiful, easy-to-read HTML output for complex AI responses. The key advantage is INFORMATION DENSITY
  — a table/card/diagram browses in 10s vs 2min of linear markdown. USE THIS SKILL whenever the response
  contains 2+ tables, comparison matrices, multi-level checklists, 3+ decision points, multi-dimensional info
  (current+changes+tests+next steps), spatial information (flows, architecture, relationships), or
  multi-chapter analysis. The shared CSS at references/output.css has everything built in — centered container,
  dark/light auto-switch, cards, callout boxes, insight highlights, stats blocks, step lists (timeline/flowchart),
  accordions (details/summary), tables, tags, print styles. Write clean semantic HTML using the classes
  documented in this skill. Do NOT trigger for simple Q&A, single code snippets, or one-glance answers.
---

# HTML Output for AI Responses

## Core Principles

### ① 信息密度是最大优势
一个对比表格、一张架构图、一组并排卡片，10秒钟浏览完。等价的MD内容要花两分钟线性阅读。AI回复动辄上千字，一天看几万字眼睛受不了。HTML让阅读和理解效率大幅提升。

### ② 内容优先 + 易读好看
HTML只做一件事：把信息高效传递给读者。用 `references/output.css` 的预置样式，不在样式上花时间。

**重要：视觉层次不是装饰，是必需品。** "极简"不等于"丑陋"——没有 `.container` 的居中、没有 `.callout`/`.insight` 的重点突出、没有 `line-height:1.8` 的行距，读者会错过关键信息。下面 Layout System 中的每个类（callout, insight, highlight, steps, card-grid, table）的存在目的都是信息密度——让读者10秒扫完核心信息，同时看着舒服不累眼。

如果输出的 HTML 中关键信息和普通段落看起来一样，说明 layout 没做对，需要重做。

### ③ 仅复杂内容才用HTML
简单回答直接在终端输出。以下情况才用HTML：
- 包含 **≥2个** 表格/多层级清单/多个章节
- 包含 **≥3个** 待决策的选项/决策点
- 同时呈现"现状+改动+测试+待决策+下一步"等多维度信息
- 涉及流程/架构/关系类空间信息（纯文字讲不清的）

## Layout System (PROVEN, must follow)

This is the key difference between readable HTML and hard-to-read HTML. **Every page must follow this layout.**

### Step 1: Base template

```html
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>title</title>
<style>
/* paste entire references/output.css here */
</style>
</head><body>
<div class="container">
<!-- ALL content goes inside .container for centering -->
</div>
</body></html>
```

> The `.container` centers everything at 800px max-width with auto margins. Without it, content floats left. Output.css has it built in.

### Step 2: Build visual hierarchy

```
h1          ← Page title (one per page, 2rem bold)
.meta       ← Author, date (subdued gray)
p / .intro  ← Body text (line-height 1.8 for easy scanning)
    ↓
h2          ← Section divider with accent blue bottom border
    → table, card-grid, blockquote, callout
    → hr (between major sections)
    ↓
h3          ← Sub-section
    → p, ul, ol, pre, insight
```

### Step 3: Make important points POP

Content that matters should be VISUALLY DIFFERENT from ordinary paragraphs. Burying key insights in plain text = reader misses them.

| Pattern | Usage |
|---------|-------|
| **`.callout`** | Key insight, core takeaway — blue left border box with accent background |
| **`.insight`** | Punchline, one-liner conclusion — gray bordered highlight paragraph |
| **`.highlight`** | Key metrics / statistics — centered big number display |
| `<blockquote>` | Quotes, soft callouts — left bar, muted text |
| **`.tag`** | Category labels — small rounded pill |

**Callout** (for "the thing to remember"):
```html
<div class="callout">
<strong>核心观点：xxx</strong>
<p>详细说明。</p>
</div>
```

**Insight** (for punchline):
```html
<p class="insight">不是「让 AI 从零生成一切」，而是「人提供约束良好的预制件」。</p>
```

**Step list** (for timeline / process / flowchart):
```html
<ol class="steps">
<li data-step="1"><strong>调研</strong><p>先做调查研究，摸清情况。</p></li>
<li data-step="2"><strong>分析</strong><p>抓住主要矛盾，制定策略。</p></li>
<li data-step="3"><strong>执行</strong><p>集中优势兵力，各个击破。</p></li>
</ol>
```
Renders as: numbered circles connected by a vertical timeline line. Perfect for step-by-step processes, roadmaps, or flowcharts — without drawing a single shape.

**Accordion** (for hiding details until clicked):
```html
<details>
<summary>点击展开详情</summary>
<div>
<p>这里的内容默认隐藏，用户点击才展开。</p>
</div>
</details>
```
Use this to keep the page clean and high-level (like a zoomed-out diagram), letting users expand only the nodes they care about. Pure HTML, zero JavaScript.

**Actual diagrams** (Mermaid.js, optional):
If you *must* have literal flowcharts or mind maps, use Mermaid.js. Add one `<script>` tag and write diagram text:
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<pre class="mermaid">
graph LR
  A[Start] --> B[Process]
  B --> C[End]
</pre>
```
Only use this when the `.steps` list or `.card-grid` truly can't express the relationship. Mermaid adds a CDN dependency and breaks offline.

**Highlight stats** (for numbers that matter):
```html
<div class="highlight">
<span class="num">85,000+</span>
<span class="label">公开 Skill 数量</span>
</div>
```

### Standard content components

| Component | HTML | When |
|-----------|------|------|
| Tables | `<table>` with `<thead>` + `<tbody>` | Data comparison, feature matrices |
| Card grid | `<div class="card-grid">` + `<div class="card">` | Grouping related items |
| Card with number | `.card` + `.card .num` | Numbered item cards |
| Card with tag | `.card` + `<span class="tag">` | Status-labeled cards |
| Code block | `<pre><code>` | Code snippets |
| Metadata | `.meta` | Author, date, tags |

**Table:**
```html
<table>
<thead><tr><th>方案</th><th>成本</th><th>周期</th></tr></thead>
<tbody>
<tr><td>方案A</td><td>低</td><td>1周</td></tr>
<tr><td>方案B</td><td>中</td><td>2周</td></tr>
<tr><td>方案C</td><td>高</td><td>1月</td></tr>
</tbody>
</table>
```

**Card grid:**
```html
<div class="card-grid">
<div class="card">
<div class="num">1</div>
<h3>标题</h3>
<p>内容。</p>
</div>
<div class="card">
<div class="num">2</div>
<h3>标题</h3>
<p>内容。</p>
</div>
</div>
```

## What output.css provides (everything built in)

These are all **pre-built** — just paste the whole CSS file in `<style>` and use the classes:

| Feature | Usage |
|---------|-------|
| **Centered layout** | `.container` — 800px max-width, auto margins |
| **Dark/light mode** | Auto via `prefers-color-scheme` |
| **Line height 1.8** | Default on `body` — easy scanning |
| **Section heading** | `h2` has accent blue bottom border |
| **Cards** | `.card-grid` + `.card` — flex wrap, min 220px |
| **Number badge** | `.card .num` — accent circle |
| **Tag pill** | `.tag` — small rounded label |
| **Callout box** | `.callout` — blue left border box |
| **Insight para** | `.insight` — gray highlight paragraph |
| **Stats block** | `.highlight` + `.num` + `.label` — centered big numbers |
| **Step list** | `.steps` + `li[data-step]` — timeline/flowchart with numbered circles |
| **Accordion** | `<details>` / `<summary>` — expandable section, pure HTML |
| **Meta line** | `.meta` — subdued subtitle |
| **Tables** | Striped rows, uppercase headers, shadow |
| **Code blocks** | Dark bg (respects theme), rounded, monospace |
| **Blockquote** | Left accent bar, muted text |
| **Print styles** | Strips dark, shows link URLs, page-break control |
| **Responsive** | Collapses at 640px |

No extra inline CSS needed. Just paste the whole file.

## Quality Checklist（产出前逐条检查）

- [ ] Wrapped in `<div class="container">` — required for centering
- [ ] Key insights use `.callout` or `.insight` — **not** buried in plain text
- [ ] Key numbers use `.highlight` with `.num` + `.label`
- [ ] Sections separated by `<hr>` for breathing room
- [ ] Tables have `<thead>` with `<th>` elements
- [ ] Card grids use `card-grid` + `card` classes
- [ ] Step lists use `.steps` with `data-step` attributes
- [ ] Accordions use `<details>` + `<summary>` for expandable sections
- [ ] Self-contained — paste entire output.css in `<style>`
- [ ] Dark/light modes both look right
- [ ] Content scannable in 10 seconds

> **Failure mode:** If the HTML's key insights look the same as body text, the checklist should catch this at lines 2-3. Fix by wrapping in `.callout` or `.insight`.

## Harness (Self-Eval)

This skill has a built-in eval harness following the Agent Harness 5-module pattern. It tests whether HTML output meets quality standards.

### Task (what to test)
3 eval cases in `evals/evals.json`:
- **case_001**: Cloud services comparison → must use `.container` + `<table>` + `.callout`
- **case_002**: Deployment steps → must use `.steps` + `.container`
- **case_003**: Methodology comparison → must use `<table>` + `.callout` + `.steps`

Each case is defined with the article's exact format (`id`, `task`, `environment`, `tools`, `grader`).

### Environment (what's available)
- `references/output.css` — all layout classes pre-built
- OS dark/light mode determines render
- Desktop ~/Desktop/ for output files

### Tools (CSS classes available)
`.container` `.card-grid` `.card` `.num` `.tag` `.callout` `.insight` `.highlight` `.steps` `details`/`summary` `table` `blockquote` `.meta`

### Trace (what gets recorded)
Each run produces:
```json
{
  "case_id": "case_001",
  "task": "用户原始任务...",
  "tools_used": ["container", "table", "callout"],
  "answer": "HTML saved to ~/Desktop/xxx.html",
  "grade": {
    "success": true,
    "passed": 3,
    "total": 3,
    "failures": [],
    "details": { "Uses .container": {"passed": true, "evidence": "found"} }
  }
}
```

### Grader (how to check)
Run the harness on any generated HTML:

```bash
# Full harness run (tests all 3 cases against one HTML)
python3 <skill-dir>/evals/run_harness.py ~/Desktop/my-output.html

# Or run individual checks
python3 <skill-dir>/evals/grader.py ~/Desktop/my-output.html \
  '[{"text":"Container","check":"has_class_container"},{"text":"Table","check":"has_table"},{"text":"Callout","check":"has_callout"},{"text":"Steps","check":"has_steps"},{"text":"Accordion","check":"has_details"},{"text":"Highlight","check":"has_highlight"},{"text":"Tag","check":"has_tag"},{"text":"Meta","check":"has_meta"},{"text":"Insight","check":"has_insight"},{"text":"HR","check":"has_hr"}]'
```

### Eval flow
1. Pick a case from `evals/evals.json` (or any user request)
2. Follow Layout System above → produce HTML
3. Save to Desktop
4. Run `run_harness.py` to grade
5. Fix failures, re-output, re-check

### 反馈回灌 (Feedback Loop: Semi-Automatic Distillation)

The harness generates **two types of value**:

| 价值 | 作用对象 | 生效时机 |
|------|---------|---------|
| **把关 (Direct Value)** | 当次生成的 HTML | 立即生效：不合格的 HTML 不交付 |
| **回灌 (Indirect Value)** | 后续所有 HTML 生成 | 下次生成时生效：一次过概率更高 |

Without the feedback loop, the harness catches the same layout errors (missing `.container`, missing `.callout`, etc.) every time. With the feedback loop, each caught error becomes a **weak supervision signal** — abstracted into a rule and injected back into the generator's instructions.

#### The Distillation Loop

```
┌─ You produce HTML following Layout System
│    ↓
│  Harness grader catches failure(s)
│    ↓
│  1. Log the exact failure (assertion + evidence + HTML file)
│  2. Periodically: cluster errors by pattern
│  3. Abstract each cluster into a generalized HTML rule
│  4. Review and approve rules
│  5. Inject rules into your instructions
│    ↓
└── Your first-time pass rate improves
```

#### Run the Distiller

```bash
# Log failures from harness runs
python3 <skill-dir>/feedback/distill.py <skill-dir>/feedback/failures.jsonl

# Track first-time pass rate
python3 <skill-dir>/feedback/ftpr.py <skill-dir>/feedback/failures.jsonl --total-runs <N>
```

Example distilled rules from common HTML errors:

| Pattern | Count | Distilled Rule |
|---------|-------|----------------|
| missing `.container` | 12 | ALL output wrapped in `<div class="container">` — required for centering |
| key insight in plain text | 8 | Key insights use `.callout` or `.insight` — never buried in body text |
| table without `<thead>` | 5 | Tables always include `<thead>` with `<th>` elements |

#### Why This Matters

Without the feedback loop → every harness run catches the same errors, you pay the same fixing cost each time. With it → **FTPR rises**, token costs drop, the system evolves.

### Extended Architecture

```
html-output/
├── SKILL.md              ← layout system + quality checklist
├── references/
│   ├── output.css          ← shared stylesheet
│   └── feedback-loop.md    ← NEW: feedback loop reference
├── evals/                  ← quality gate
│   ├── evals.json
│   ├── grader.py
│   └── run_harness.py
└── feedback/               ← NEW: evolution engine
    ├── failures.jsonl      ← append-only failure log
    ├── distill.py          ← semi-automatic error distiller
    └── ftpr.py             ← first-time pass rate calculator
```

## CSS Reference

The shared stylesheet: `references/output.css`

Paste its entire content into `<style>` in your HTML. That's it.

## Version History

- **v1**: Hand-wrote HTML with inline styles. No shared CSS.
- **v2**: Markdown → pandoc → HTML (removed).
- **v3**: Direct HTML writing with shared CSS. Layout classes had to be added inline separately.
- **v3.1 (current)**: All layout classes built into output.css — container, callout, insight, highlight, tag, meta, step list (`.steps`), accordion (`<details>`/`<summary>`), Mermaid.js note. Zero extra CSS needed.
- **v4.0**: Added feedback loop (distill.py + ftpr.py), two-fold value concept, extended architecture with feedback/ directory.

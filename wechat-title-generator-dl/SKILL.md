---
name: wechat-title-generator-dl
description: >
  ALWAYS use this skill before generating any WeChat article cover or content.
  Takes a JSON input describing topic and style, outputs a structured Markdown
  file with title, subtitle, tagline, and label. Trigger immediately when the
  user mentions "标题", "title", "headline", "article topic", or needs a
  WeChat article title. Use this whenever you need a professional,
  non-clickbait title for Chinese business, tech, or cognitive content —
  before generating covers (wechat-cover-generator-dl), before writing
  articles, or when the user asks for a headline. The output feeds directly
  into the cover pipeline (open-source-image-fetch-dl +
  wechat-cover-generator-dl).
---

# WeChat Title Generator

Generate professional, structured WeChat article titles that follow a
methodology-based format. No clickbait, no emotional manipulation, no hype.

## Input

JSON object describing the article:

```json
{
  "topic": "OPC / AI / 个人商业系统",
  "style": "professional / high-level / cognitive"
}
```

| Field | Required | Values |
|---|---|---|
| `topic` | Yes | Short description of article domain (Chinese or English) |
| `style` | Yes | `professional`, `high-level`, or `cognitive` |

## Output

A Markdown file with this exact structure:

```markdown
# [领域] + [核心概念] + [方法/系统/路径]

## 副标题
[One-line explanation of the article's value]

## 标签
[标签1] · [标签2] · [标签3]

## 原标题
[Column for later use: the original full title idea]
```

## Title rules (MUST follow)

1. **No clickbait** — no "震惊", "全网疯传", "再不XX就晚了", "99%的人都不知道"
2. **No emotional manipulation** — no fear, greed, urgency, or FOMO triggers
3. **Clear structure** — reader should know what the article is about from the title alone
4. **Include keywords** — at least one domain keyword in the title
5. **Show methodology** — the title must hint at a system, framework, path, or method

### Recommended title structure

```
[领域] + [核心概念] + [方法/系统/路径]
```

Examples:
- "AI 时代的 OPC：如何用最小系统跑通一个人的商业闭环"
- "认知写作：从信息输入到结构化表达的系统方法"
- "个人商业系统：从需求验证到 MVP 再到可持续收入的完整路径"

### Style guidance

| Style | Tone | Title length | Language |
|---|---|---|---|
| `professional` | Formal, authoritative | 15–25 chars | Prefer Chinese |
| `high-level` | Strategic, visionary | 18–30 chars | Chinese + English terms OK |
| `cognitive` | Thoughtful, analytical | 15–28 chars | Chinese, conceptual |

## Workflow

1. Parse the input JSON — extract topic and style.

🔴 **CHECKPOINT: Verify input parameters are valid before proceeding.** Incorrect or missing parameters will cause script failure. Confirm with the user if ambiguous.

2. Generate a title following all rules above.
3. Generate a 副标题 (subtitle) — one sentence summarizing the article's value proposition.
4. Generate 3 标签 (tags) — short keywords for categorisation.
5. Save the full output as a `.md` file at the user-specified path.
6. Return the file path and a summary of what was generated.


🛑 **STOP: Present the final result to the user for confirmation** before using it in any downstream task.

## Example

**Input:**
```json
{
  "topic": "OPC / AI / 个人商业系统",
  "style": "high-level"
}
```

**Output file (`/tmp/opc-title.md`):**
```markdown
# AI 时代的 OPC：如何用最小系统跑通一个人的商业闭环

## 副标题
从需求验证到 MVP，再到可持续收入的系统化路径

## 标签
OPC · AI工具链 · 个人商业系统

## 原标题
AI 时代的 OPC：一个人如何用最小成本跑通自己的商业闭环
```

## Failure handling

| Trigger | First-line fix | Still fails → fallback |
|---|---|---|
| Missing `topic` | Return error: "topic is required" | Try alternative approach or fallback |
| Invalid `style` | Default to `professional` with a warning | Try alternative approach or fallback |
| Output path not writable | Use `/tmp/wechat-title-<timestamp>.md` as fallback | Try alternative approach or fallback |




## Anti-patterns & blacklist

| Anti-pattern | Why it's dangerous | Instead do |
|---|---|---|
| Using clickbait titles (震惊, 99%, etc.) | Lowers article credibility, may trigger WeChat content review | Use structured [领域+核心概念+方法] format |
| Overly emotional language | Turns off professional readers, reduces sharing intent | Keep tone professional/cognitive/high-level per style |
| Missing subtitle or tags | Reader can't quickly assess article's value | Always include ## 副标题 and ## 标签 |
| Title too long (>30 chars) | Gets truncated in WeChat chat preview | Keep title 15-25 chars for professional style |
| No methodology in title | Title feels generic, doesn't signal value to reader | Follow [领域+核心概念+方法/系统/路径] structure |



## Edge cases

| Scenario | How to handle |
|---|---|
| Input topic has no clear domain keywords | Use `professional` style and extract nouns from the topic as keywords |
| User provides a very long topic (>50 chars) | Focus on the first 20 chars as the core domain, rest as context |
| Mixed Chinese/English topic (e.g. "OPC / AI / 个人商业系统") | Keep English terms in the title, wrap in Chinese syntax |
| User wants emotional/anxiety-driven title | Push back politely: explain clickbait rules, offer structured alternative |
| Style field is empty or invalid | Default to `professional` with a warning |
| Output Markdown needs to be in English | Still use ## 副标题 / ## 标签 structure but fill with English content |

## Harness (Self-Eval)

The harness validates that title output follows the structured Markdown format with no clickbait patterns.

### Cases

| ID | Scenario |
|----|----------|
| `case_001` | OPC / AI / personal business system, professional style — check title, subtitle, tags, no clickbait |
| `case_002` | Cognitive writing / structured thinking, high-level style — check title structure |
| `case_003` | Learning methods / knowledge management, cognitive style — check structure and no clickbait |

### Checks

| Check | What it detects |
|-------|----------------|
| `has_markdown_title` | Output has `#` heading with title text |
| `has_subtitle` | Contains `## 副标题` section |
| `has_tags` | Contains `## 标签` section |
| `no_clickbait` | No clickbait phrases (震惊, 99%, 再不...就, etc.) |
| `has_structure` | Has all required structure (title + subtitle + tags) |

### Run

```bash
# Run cases manually by loading this skill and applying the prompt
# Then save the output Markdown for grading:

python3 evals/grader.py /path/to/title-output.md '[{"text":"Title","check":"has_markdown_title"},{"text":"Subtitle","check":"has_subtitle"},{"text":"Tags","check":"has_tags"},{"text":"No clickbait","check":"no_clickbait"}]'

# Full harness
python3 evals/run_harness.py /path/to/title-output.md
```

### Honesty & Truthfulness

Report results exactly as they are:
- Missing title sections → report which are missing
- Clickbait detected → list the offending phrases
- No defensive disclaimers ("this might not be correct")
- If output passes all checks, state clearly without hedging


---
name: skill-harness
description: >
  Inject the 5-module Agent Harness (Task → Environment → Tools → Trace → Grader) into any skill.
  USE THIS when the user says "make a harness for X skill", "add evals to Y", "make tests for Z",
  "upgrade X with harness", or asks to add automated quality checking to any skill.
  The harness creates evals/evals.json, grader.py, run_harness.py, and a Harness section in SKILL.md.
  Now also supports the feedback loop concept: audit trail, semi-automatic error distillation,
  first-time pass rate (FTPR) tracking, and prompt rule injection for continuous improvement.
---

# Skill Harness — Inject the 5-Module Agent Harness

> Reference implementation: `html-output` skill's harness (evals/, grader.py, run_harness.py)

## What This Does

Takes any skill and adds a self-eval harness following the Agent Harness 5-module pattern:

```
Task         — 3+ realistic test prompts
Environment  — What files/tools are available
Tools        — What the skill provides (commands, CSS classes, APIs, etc.)
Trace        — JSON record: task → tools called → grade result
Grader       — Automated assertion checker
```

### Trace — what gets recorded

When `run_harness.py` runs, it generates a structured trace for each test case. This is the critical output for debugging:

```json
{
  "case_id": "case_001",
  "task": "分析三款云服务对比，做成HTML",
  "environment": {
    "files_available": ["output.css"],
    "tools_available": ["container", "table", "callout"]
  },
  "tools_used": ["container", "table", "callout"],
  "tools_arguments": {
    "container": {"max_width": "800px", "margin": "auto"},
    "table": {"has_thead": true},
    "callout": {"border_left": "4px accent"}
  },
  "answer": "HTML output saved to ~/Desktop/eval1-cloud.html",
  "grade": {
    "success": true,
    "passed": 3,
    "total": 3,
    "failures": [],
    "details": {
      "Uses .container": {"passed": true, "evidence": "container class found"},
      "Has <table> with <thead>": {"passed": true, "evidence": "<table> with <thead> found"},
      "Has .callout": {"passed": true, "evidence": ".callout found"}
    }
  }
}
```

Each field in the trace helps answer a specific debugging question:
- **tools_used vs tools_available** — did the output use all appropriate tools, or skip some?
- **tools_arguments** — were the tools called with the right parameters?
- **failures** — which assertions failed? tells you exactly what to fix
- **details** — per-assertion evidence shows what the grader actually found

## How to Use

### Step 1: Quick inject (automated)

```bash
python3 <skill-dir>/scripts/inject.py ~/.hermes/skills/<target-skill>
```

This:
1. Creates `evals/` directory with `grader.py` + `run_harness.py` (copied from html-output)
2. Generates `evals/evals.json` from template (needs real tasks filled in)
3. Adds `## Harness` section to target's `SKILL.md`

### Step 2: Fill in real eval cases

Edit `evals/evals.json` — replace `__EVAL_TASK_1__` etc with realistic prompts.

Each case follows the article's format:

```json
{
  "id": "case_001",
  "task": "A real user request this skill should handle",
  "environment": {
    "files": {"some.conf": "config file content"},
    "tools_available": ["tool1", "tool2"]
  },
  "tools": ["tool1", "tool2"],
  "grader": {
    "must_use": ["tool1"],
    "must_have": ["specific result content"],
    "must_not_have": ["common mistakes"]
  }
}
```

**Rules for good cases:**
- Each case tests a distinct capability of the skill
- `must_use` = which tools/classes the output must contain
- `must_have` = content/features the output must include
- `must_not_have` = patterns that indicate failure

**Concrete example** — the `html-output` harness has 3 working cases. Read them as template:
```
~/.hermes/skills/html-output/evals/evals.json
```
Notice how each case maps a specific task → required tools → grader rules. Copy this pattern for your target skill.

### Step 3: Map grader checks

The harness uses these default checks from `grader.py`:

| Check | Detects |
|-------|---------|
| has_class_container | `.container` CSS class |
| has_table | `<table>` with `<thead>` |
| has_callout | `.callout` class |
| has_steps | `.steps` class |
| has_details | `<details>`/`<summary>` elements |
| has_highlight | `.highlight` stat block |
| has_tag | `.tag` pill label |
| has_meta | `.meta` class |
| has_insight | `.insight` class |
| has_hr | `<hr>` element |

**For non-HTML skills**, add custom checks to `grader.py`. Pattern:

```python
elif check["check"] == "has_json_output":
    passed = html.strip().startswith("{")
    evidence = "JSON detected" if passed else "not JSON"
```

### Step 4: Run and iterate

```bash
# Full harness (tests all cases against one output)
python3 evals/run_harness.py <output-file>

# Or individual check
python3 evals/grader.py <output-file> '<checks-json>'
```

## Architecture

```
target-skill/
├── SKILL.md              ← + Harness section (added by inject.py)
└── evals/                ← (created by inject.py)
    ├── evals.json        ← 3+ test cases (fill in real prompts)
    ├── grader.py         ← static output checker
    └── run_harness.py    ← full harness runner
```

## 两重价值 (Two-Fold Value)

A harness generates two distinct types of value. Understanding the difference is critical for designing the feedback loop:

| 价值 | 作用对象 | 生效时机 |
|------|---------|---------|
| **把关 (Direct Value)** | 当次生成的产出 | 立即生效：不合格的产出不交付 |
| **回灌 (Indirect Value)** | 后续所有生成 | 下次生成时生效：生成器"一次过"的概率更高 |

**Direct value** is what the basic harness provides — catch bad outputs before they reach the user. **Indirect value** is the harder, more valuable part: every caught error becomes a learning signal that makes the generator smarter over time.

Only direct value without indirect value → the harness runs forever catching the same mistakes every time. With indirect value, the generator's **first-time pass rate** increases each iteration, and the harness catches fewer errors over time. Token costs decrease as fewer retries are needed.

> 🔑 Core insight from DIPG (蚂蚁保保险快查深度解读系统): The offline pipeline's verify loop never converges without the feedback loop. You pay the same cost for the same fixes every run. Feedback is what makes quality a convergent process.

## 反馈回灌 (Feedback Loop: Semi-Automatic Distillation)

The key architectural insight from the DIPG system: **caught errors must be abstracted into generalized rules and injected back into the generator's prompt**. This transforms the harness from a static quality gate into a self-improving system.

### The Distillation Loop

```
┌─ Generator produces output
│    ↓
│  Verifier/Grader catches error(s)
│    ↓
│  1. Log the exact failure with full context
│  2. Periodically: cluster errors by pattern
│  3. Abstract each cluster into a generalized rule
│  4. Human reviews and approves rules
│  5. Inject approved rules into generator's instructions
│    ↓
└── Generator's first-time pass rate improves
```

### Step-by-Step Implementation

#### Step 1: Create an Audit Trail (the `/audit/` pattern)

Verification is meaningful only when the verifier can compare output against source data. Without the audit trail, the grader can verify format/structure but **cannot verify factual accuracy**.

```
audit/
  ├── tool_call_1_<ts>.json      ← input + output of each tool call
  ├── tool_call_2_<ts>.json
  ├── source_data_<ts>.json      ← raw materials the generator used
  └── ...
```

The audit trail is written by middleware that wraps every tool call the generator makes:

| Component | What it records | Who reads it |
|-----------|----------------|--------------|
| `state["files"]` | Output HTML/report | Verifier Agent extracts report |
| `/audit/` | Every tool call: input, output, timestamp | Verifier Agent reads via `read_file` to compare output vs data source |

**For non-agent skills** (no tool calls), the audit trail is simply the input file(s) the generator received.

#### Step 2: Log Failures with Full Context

When the grader/verifier catches a failure, record the full context. This is the input to the distillation process:

```json
{
  "case_id": "case_003",
  "timestamp": "2026-05-26T08:30:00Z",
  "assertion": "Has.container class",
  "evidence": "missing.container",
  "source_files": ["cloud-data.json"],
  "generator_prompt_section": "layout-system"
}
```

Storage: `feedback/failures.jsonl` — append-only log. Every failure appends one line.

#### Step 3: Run the Distiller

```bash
python3 <skill-dir>/feedback/distill.py <skill-dir>/feedback/failures.jsonl
```

The distiller clusters errors by assertion type and evidence pattern, then abstracts each cluster into a generalized prompt rule:

```json
{
  "distillation_run": "2026-05-26",
  "total_failures": 47,
  "clusters": [
    {
      "count": 12,
      "pattern": "missing .container wrapper",
      "rule": "ALL output must be wrapped in a top-level <div class=\"container\"> element. This is required for centering — without it content floats left. Treat this as a structural requirement, not a styling suggestion.",
      "severity": "high",
      "inject_to": "layout-system"
    },
    {
      "count": 8,
      "pattern": "key insight in plain text instead of .callout",
      "rule": "Key insights, core takeaways, and conclusions MUST NOT be buried in plain paragraph text. Use .callout (blue left border box) to make important points visually distinct from body text.",
      "severity": "medium",
      "inject_to": "step-3"
    }
  ]
}
```

#### Step 4: Human Review + Rule Injection

The developer reviews the clustered rules and selects which to inject. Approved rules go into the generator's instructions as hard constraints:

```markdown
### Hard Constraints (distilled from harness feedback)

The following rules were automatically generated from real failures caught
by the harness. Following them prevents the most common errors.

- **Layout**: ALL output wrapped in `<div class="container">` — missing
  container was the #1 failure (12 occurrences)
- **Emphasis**: Key insights use `.callout` or `.insight` — never buried
  in plain text (8 occurrences)
- **Tables**: Always include `<thead>` with `<th>` — 5 failures from
  missing table headers
```

#### Step 5: Track Metric — First-Time Pass Rate

Track FTPR across harness iterations. This is the single KPI that tells you whether the system is improving:

```
FTPR = (outputs passing all assertions on first try) / (total outputs generated)
```

```bash
python3 <skill-dir>/feedback/ftpr.py <skill-dir>/feedback/failures.jsonl \
  --total-runs 30
```

**FTPR Interpretation:**

| FTPR | State | Action |
|------|-------|--------|
| < 50% | Generator needs major improvement | Run distillation now |
| 50-80% | Reasonable but common failure patterns | Distillation will help |
| 80-95% | Strong generator | Distill for edge cases |
| > 95% | Near-perfect | Consider adding harder assertions |
| 100% | Suspicious | Harness may be too easy (missing important checks) |

### Why Distillation is Necessary

Without the feedback loop, the offline pipeline runs forever catching the **same error types** and making the **same patches** each iteration. Token cost stays flat — you pay full price for every fix every time.

With distillation:
- Every caught error becomes a **weak supervision signal** for the generator's instructions
- **FTPR increases** each cycle → fewer errors need fixing
- **Token costs decrease** as generator improves
- The system **evolves without manual prompt engineering**

## 审计追踪 /audit/ 模式详解

The `/audit/` pattern is the architectural mechanism that enables factual verification and distillation. Here's the concrete setup:

### For Agent-based Skills

```
audit/
  ├── download_insurance_materials_<ts>.json    ← what files were retrieved
  ├── read_disk_file_<ts>.json                 ← what the generator read
  ├── web_search_<ts>.json                     ← external data retrieved
  ├── tool_<name>_<ts>.json                    ← every tool call logged
  └── ...
```

Implementation via middleware:

```python
class AuditMiddleware:
    """Wraps every tool call, logging input+output to state['files']['audit']."""
    
    def on_tool_call(self, tool_name, args, result):
        log_entry = {
            "tool": tool_name,
            "args": args,
            "result_preview": str(result)[:500],
            "timestamp": datetime.now().isoformat()
        }
        path = f"audit/{tool_name}_{timestamp}.json"
        write_file(path, json.dumps(log_entry))
```

The verifier then reads the audit trail to check **factual alignment** — are the facts in the output traceable to the source data?

### For Non-Agent Skills

When the skill is a deterministic script/transform (no agents), the audit trail is simpler — just snapshot the input:

```
audit/
  ├── source_input.json    ← the input file(s) the script received
  └── output.html          ← what was generated
```

### What the Verifier Does With It

The verifier compares two things:
1. **Structural checks** — output format against schema/contract (pure code, no audit needed)
2. **Factual alignment** — output data vs audit trail data (requires audit access)

Factual alignment is where most LLM errors hide. Without the audit trail, the verifier cannot distinguish between "well-formatted truth" and "well-formatted hallucination."

## 扩展架构 (Extended Architecture)

With the feedback loop, the harness evolves from a static quality gate into a self-improving system:

```
target-skill/
├── SKILL.md              ← + Harness section + Hard Constraints section
├── evals/                ← quality gate: test cases + grader
│   ├── evals.json        ← test case definitions
│   ├── grader.py         ← assertion checker
│   └── run_harness.py    ← full harness runner
│
└── feedback/             ← NEW: evolution engine
    ├── failures.jsonl    ← append-only log of every failure (one JSON per line)
    ├── distill.py        ← clusters errors → abstracts into rules
    ├── ftpr.py           ← first-time pass rate calculator
    └── rules.md          ← distilled, human-approved rules ready for injection
```

### File Lifecycle

| File | Written by | Read by | Purpose |
|------|-----------|---------|---------|
| `failures.jsonl` | `run_harness.py` (on each failure) | `distill.py`, `ftpr.py` | Raw data for distillation |
| `rules.md` | Human (after reviewing distillation output) | Generator's instruction prompt | Prevents recurring errors |
| `ftpr.py output` | `ftpr.py` | Developer | KPI to measure improvement |

### Integration with inject.py

The inject script now optionally scaffolds the feedback/ directory:

```bash
# Default (evals only)
python3 scripts/inject.py ~/.hermes/skills/<target-skill>

# With feedback loop
python3 scripts/inject.py ~/.hermes/skills/<target-skill> --with-feedback
```

## Reference

The `html-output` skill has a complete working harness. Study it for patterns:
- `/Users/f/.hermes/skills/html-output/evals/evals.json`
- `/Users/f/.hermes/skills/html-output/evals/grader.py`
- `/Users/f/.hermes/skills/html-output/evals/run_harness.py`

For the full Agent Harness article reference, see `references/harness-pattern.md` in this skill.

For the feedback loop concept reference, see `references/feedback-loop-concept.md` in this skill.

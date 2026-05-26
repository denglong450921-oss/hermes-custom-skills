# Feedback Loop Concept Reference

> From the DIPG system (蚂蚁保保险快查深度解读页面生成系统), published by 晓灰, 阿里云开发者 2026

## Why This Exists

The feedback loop concept emerged from a real engineering problem: LLM-generated content for C-side users that must be factually accurate and structurally sound. The offline verify loop (generator → verifier → fix → re-check) ensures immediate quality, but without feedback, it runs forever catching the **same errors** and making the **same patches** every time.

The core insight: **every caught error is a weak supervision signal** for the generator's prompt. Errors should be abstracted into generalized rules and injected back to prevent future occurrences.

## Key Distinctions

### Direct vs Indirect Value

| Aspect | Direct Value (把关) | Indirect Value (回灌) |
|--------|-------------------|---------------------|
| What it does | Catches bad outputs immediately | Prevents future bad outputs |
| When it works | Per-generation | Over time, across iterations |
| Cost profile | Fixed cost per generation | Decreasing cost over time |
| Without it | Bad outputs reach users | Errors repeat forever |

### First-Time Pass Rate (FTPR)

The single convergence metric for the feedback loop:

```
FTPR = outputs passing all assertions on first try / total outputs generated
```

A rising FTPR means the feedback loop is working — the generator is learning from past errors.

## The Distillation Process

```
┌─────────────────────────────────────────────┐
│              Generator Agent                 │
│  Prompt: [base instructions]                │
│          [hard constraints from feedback]    │
└──────────────┬──────────────────────────────┘
               │ produces output
               ↓
┌─────────────────────────────────────────────┐
│              Verifier Agent                  │
│  structural_check: HTML parser rules        │
│  llm_verify: factual alignment with /audit/ │
└──────────────┬──────────────────────────────┘
               │ returns errors + fix_hints
               ↓
┌─────────────────────────────────────────────┐
│            Distillation Loop                 │
│  1. Log: failures.jsonl (append)            │
│  2. Cluster: by assertion + evidence        │
│  3. Abstract: rule from pattern             │
│  4. Review: human selects rules             │
│  5. Inject: rules → generator prompt        │
└──────────────┬──────────────────────────────┘
               │ hardened rules
               ↓
         Generator improves → FTPR rises
```

## Real-World Example

**Error detected:** Generator wrote "优于市场 85% 同类惠民保产品" ("Better than 85% of similar products") without any supporting data.

**Audit trail:** All source data (insurance clauses, health notices) contained zero market ranking data.

**Distilled rule:** "禁止盲目对比: 没有竞品数据不得使用 '优于市场 XX%' 等市场排名表述" (Prohibit blind comparison: without competitor data, do not use market ranking statements.)

**Result:** Rule injected into Research Agent prompt. FTPR for this error type drops from ~15% to ~2%.

## Architecture Requirements

For the feedback loop to work, the harness needs three components:

1. **Audit Trail** — records all data the generator accessed, so the verifier can check factual alignment
2. **Failure Log** — persistent, append-only record of every verification failure with context
3. **Distillation Script** — clusters failures → abstracts into rules → outputs for human review

## Reference Implementation

See `scripts/distill.py` and `scripts/ftpr.py` in this skill for the concrete implementation.

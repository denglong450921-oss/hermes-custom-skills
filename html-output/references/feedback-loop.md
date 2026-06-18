# Feedback Loop for HTML Output

This skill has been upgraded with the feedback loop concept from skill-harness.

## Two-Fold Value

| 价值 | What it does |
|------|-------------|
| **Direct (把关)** | Harness catches bad HTML before it's delivered |
| **Indirect (回灌)** | Caught errors → distilled into layout rules → injected into generator instructions |

## FTPR (First-Time Pass Rate)

Key metric: what % of generated HTML passes all harness checks on first try?

```
FTPR < 50%  → Generator needs major Layout System rework
FTPR 50-80% → Common failure patterns exist; distillation helps
FTPR 80-95% → Strong; distill for edge cases
FTPR 100%   → Suspicious; harness may be too easy
```

## How to Use

```bash
# 1. Run harness on generated HTML
python3 evals/run_harness.py ~/Desktop/my-output.html

# 2. Distill failures into rules
python3 feedback/distill.py feedback/failures.jsonl

# 3. Check FTPR
python3 feedback/ftpr.py feedback/failures.jsonl --total-runs 30
```

For full concept reference, see `skill-harness` skill's `references/feedback-loop-concept.md`.

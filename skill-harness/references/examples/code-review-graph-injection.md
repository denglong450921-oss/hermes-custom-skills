# code-review-graph — Manual Injection Example

This is a working example of non-HTML manual injection for a CLI tool skill.

## Target Skill

`~/.hermes/skills/software-development/code-review-graph/`

## What was created

```
code-review-graph/
├── SKILL.md              ← instructions + Harness section + Honesty constraints
└── evals/
    ├── evals.json        ← 3 test cases (build, detect-changes, visualize)
    ├── grader.py         ← 7 checks (4 functional + 3 truthfulness)
    └── run_harness.py    ← full harness runner
```

## Eval cases

| Case | What it tests | Checks |
|------|--------------|--------|
| case_001 | `code-review-graph build` + `status` | `graph_built`, `status_shows_nodes` |
| case_002 | `code-review-graph detect-changes --brief` | `detect_changes_ran` |
| case_003 | `code-review-graph visualize` | `visualize_file_created` |

## Grader checks (CLI domain)

Functional checks look for keywords in CLI stdout:

```python
elif c == "graph_built":
    passed = "Nodes:" in output and "Edges:" in output

elif c == "status_shows_nodes":
    passed = bool(re.search(r"Nodes:\s*\d+", output))

elif c == "detect_changes_ran":
    passed = "Token Savings" in output or "impact" in output.lower()
```

Truthfulness checks are identical to the generic pattern (reports_failure_honestly, no_defensive_disclaimers, no_false_success).

## Key design decisions

1. **No HTML checks** — skill produces CLI text output, not HTML. Grader checks stdout content, not CSS classes.
2. **Must create test project first** — evals.json includes environment.files with a small Python fixture.
3. **Checks are content-based** — verify the CLI produced expected keywords, not file existence (tempting but fragile).

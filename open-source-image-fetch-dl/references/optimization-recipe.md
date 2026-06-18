# Optimization Recipe (from Darwin Skill 2.0)

Optimal order for maximum per-round gain:

| Priority | Dimension | Δ | Action |
|----------|-----------|-----------|--------|
| 1 | Dim4 Checkpoint | +6 | Add 🔴🛑 markers |
| 2 | Dim9 Anti-patterns | +5 | Add "## Anti-patterns & blacklist" |
| 3 | Dim3 Failure encoding | +3 | 2-col → 3-col failure table |
| 4 | Dim2 Workflow | +1~4 | Numbered sub-steps |
| 5 | Dim6 Resources | +1~3 | references/ + templates/ dirs |
| 6 | Dim5 Specificity | +1~2 | Edge cases table |
| 7 | Dim1 Frontmatter | +0~1 | Pushier trigger words (regression risk!) |

**Dim2 pitfall:** Check for BOTH `## Workflow` AND `## Pipeline`.
**Dim1 risk:** Test on one skill first — YAML changes can regress.

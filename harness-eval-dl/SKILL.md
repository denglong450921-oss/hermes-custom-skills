---
name: harness-eval-dl
description: Build and run evidence-based "exam" evaluations for Harness workflows, skills, rules, agents, or prompt systems. Use this whenever the user asks whether a skill/harness/rule workflow is actually improving, wants to test a skill's harness, compare workflow revisions, create exam-style eval cases, judge transcripts with evidence, aggregate pass rates and score history, or replace subjective vibes with repeatable regression data.
---

# Harness Eval DL

Use this skill to test whether a Harness-style workflow actually works. The core idea is to treat the harness like an exam system, not a single boolean unit test: design cases, run examinees through realistic interactions, judge from transcript evidence, aggregate score trends, and feed the findings back into the next revision.

## First Principles

- Measure repeatable trends, not one lucky run.
- Prefer attribution over a pretty score. A failure should say whether the issue belongs to `[workflow]`, `[eval]`, or `[capability]`.
- Keep the examinee away from the rubric. The task prompt is visible to the examinee; the scoring guide is visible only to the judge.
- Judge from a complete but compressed record of behavior. Final answers alone are not enough because tool calls, file writes, commands, and skipped gates carry the real evidence.
- A harness run is not complete until it produces evidence-backed scores and next-action insights.

## When Starting

Identify:

- **Target harness:** the skill/rules/agent/workflow being tested.
- **Workflow revision:** git commit, package version, or timestamp for the tested harness.
- **Configurations:** usually `with_skill` vs `without_skill`, `new_harness` vs `old_harness`, or several workflow revisions.
- **Run count:** default to at least 3 runs per case/configuration when cost allows; use 1 only for smoke tests.
- **Scope:** smoke, regression, release gate, or diagnosis of a known failure.

Create the workspace next to the skill or project unless the user gave a path:

```text
<target-name>-harness-eval/
  cases/<case-id>/
  runs/<timestamp-or-iteration>/
  reports/
```

## Exam Case Format

Each case is a small directory with four required files:

```text
cases/<case-id>/
  meta.yaml
  task.md
  rubric.md
  env.yaml
  fixtures/        # optional
```

Use `references/exam-case-format.md` for field details. The compact contract:

- `meta.yaml`: identity, version, category, difficulty, purpose, wave, tags.
- `task.md`: the user-facing task plus examiner script for multi-turn interaction.
- `rubric.md`: hard pass criteria, quality scoring, evidence requirements, common failures.
- `env.yaml`: preflight checks, required files/services, sandbox setup, expected artifacts.

Build the case library in waves:

1. Mainline loop: plan -> execute -> verify -> summarize/archive.
2. Gates and state: scope locking, branch confirmation, hard stop behavior.
3. Knowledge loop: retrieval, citation, write-back, conflict detection.
4. Supporting skills: commit discipline, TDD, release verification.
5. Resilience: failure repair, critical blockers, multi-branch conflict, flaky tools.

## Run Protocol

1. **Prepare the exam room.** Run `env.yaml` preflight checks. Use a sandbox or worktree when file changes are possible.
2. **Run the examinee.** Give the examinee only `task.md` and permitted fixtures.
3. **Simulate realistic interaction.** If an examiner is available, it should follow the `task.md` examiner script: answer clarifying questions, introduce specified twists, and stop when the examinee declares completion.
4. **Record the transcript.** Save raw transcript and tool evidence. Create `transcript.for-judge.txt` by reducing noise while preserving tool calls, commands, file writes, user decisions, and final claims.
5. **Judge independently.** Give the judge only `rubric.md`, `transcript.for-judge.txt`, and output artifacts. Do not reuse the examinee context for judgment.
6. **Write score and review.** Save structured score plus evidence-backed diagnosis.
7. **Aggregate.** Update latest summary, score history by workflow revision, and batch insights.

## Required Run Artifacts

Each run directory should contain:

```text
runs/<iteration>/<case-id>/<configuration>/run-<n>/
  transcript.jsonl              # raw if available
  transcript.for-judge.txt      # compact judge input
  outputs/
  score.yaml
  review.md
  grading.json                  # optional skill-creator compatible grading
  timing.json                   # optional but strongly useful
```

`score.yaml`:

```yaml
result: pass        # pass | fail
compliance: 4       # 0-5 process adherence
execution_quality: 4 # 0-5 delivered result quality
overall: 4          # 0-5 combined score
summary: Short evidence-backed outcome.
```

`review.md` should include:

- reason
- evidence with quoted transcript/output snippets
- improvements grouped as `[workflow]`, `[eval]`, and `[capability]`

## Judging Rules

Use `references/judging-guide.md` when writing rubrics or judge prompts.

- Hard pass criteria require explicit evidence. If the transcript does not show it, mark it failed.
- Quality scoring is separate from pass/fail. A barely usable pass should not receive the same score as a clean, proactive run.
- Cite concrete transcript/output evidence for each important verdict.
- Surface weak evals. If a rubric item is non-discriminating, unverifiable, or easy to game, mark it as an `[eval]` improvement.
- Attribute every recommendation. This prevents vague “improve prompt” advice from hiding the real source of failure.

## Reporting

Produce these batch artifacts:

```text
reports/latest.md
reports/latest-stats.yaml
reports/score-history.yaml
reports/batch-insights.md
```

Report at minimum:

- case/configuration/run count
- pass rate and mean overall score
- variance or per-run spread
- token/time cost when available
- top `[workflow]`, `[eval]`, `[capability]` improvements
- regressions compared with the previous workflow revision, if available

## Bundled Scripts

- `scripts/init_exam_case.py`: create the four-file case scaffold.
- `scripts/make_judge_prompt.py`: combine `rubric.md` and `transcript.for-judge.txt` into a judge prompt.
- `scripts/validate_harness_eval.py`: check exam cases, run artifacts, score/review evidence, and report files.
- `scripts/summarize_scores.py`: aggregate `score.yaml` files into latest reports and score history.

Run a smoke validation:

```bash
python <skill-dir>/scripts/validate_harness_eval.py --root <workspace>
```

## Completion Report

When finished, tell the user:

- what harness/revision was tested
- how many cases/configurations/runs were executed
- pass rates and mean scores
- whether the harness appears to be improving, regressing, or inconclusive
- top evidence-backed fixes, grouped by `[workflow]`, `[eval]`, `[capability]`
- where the review/benchmark artifacts are saved

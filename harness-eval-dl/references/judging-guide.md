# Judging Guide

The judge has an evidence job, not a vibes job.

## Inputs

- `rubric.md`: judge-only scoring standard.
- `transcript.for-judge.txt`: compact behavior record with dialogue, tool calls, file writes, command outputs, and final claims.
- output artifacts, when applicable.

## Process

1. Check each hard pass criterion against the transcript and outputs.
2. Mark missing evidence as failed, even if the final answer sounds confident.
3. Score separately:
   - `compliance`: how well the workflow followed gates and process.
   - `execution_quality`: quality of the delivered result.
   - `overall`: combined judgment.
4. Quote evidence for important pass/fail calls.
5. Classify improvements:
   - `[workflow]`: rules, skills, gates, prompts, state handling.
   - `[eval]`: ambiguous task, weak rubric, missing fixture, non-discriminating assertion.
   - `[capability]`: model/tool limitations, context handling, multi-step reasoning.

## Output Shape

Write `score.yaml` and `review.md`.

`score.yaml` is intentionally small and trend-friendly. `review.md` carries evidence and diagnosis.

# Evaluation Loop

Use this reference only when creating, upgrading, or benchmarking `hermes-delegated-coding`.

## Goal

Measure whether the skill actually preserves the intended work mode:

- Codex spends tokens on planning, architecture judgment, review, verification, and preview.
- Hermes performs implementation, test/fix loops, and local investigation.
- Raw logs, whole-repo dumps, and repeated debugging stay out of Codex responses.

## Test Set

Use `evals/evals.json` as the canonical prompt list. Keep `test-prompts.json` only for Darwin-style scoring compatibility.

Good evals should check:

- Normal delegation: Hermes writes code, Codex reviews.
- Ambiguous delegation: Codex refuses to claim hard global rewiring and offers policy-backed alternatives.
- Failure handling: failed tests, preview mismatch, or out-of-scope edits are sent back to Hermes instead of handed off.

## Benchmark Workspace

Create a sibling workspace next to the skill directory:

```text
hermes-delegated-coding-workspace/
  skill-snapshot/
  iteration-1/
    eval-normal-delegation/
      with_skill/
      old_skill/
      eval_metadata.json
```

Before editing the skill, snapshot the old version:

```bash
cp -R /Users/f/.agents/skills/hermes-delegated-coding \
  /Users/f/.agents/skills/hermes-delegated-coding-workspace/skill-snapshot
```

For each eval, run two comparable agents in the same turn when possible:

- `with_skill`: current skill path.
- `old_skill`: snapshot path from before the edit.

Save outputs under each run's `outputs/` directory. Keep the requested output compact: final response, changed file list, verification summary, and any preview/review notes.

## Assertions

Draft assertions while runs execute. Prefer objective checks:

- Mentions Codex as planner/reviewer, not coding worker.
- Sends implementation/debugging back to Hermes.
- Includes scope, verification command, acceptance criteria, and required return format.
- Rejects unsupported hard global delegation claims.
- Does not paste long logs or ask the user to manually do the obvious next implementation step.

Store assertions in each `eval_metadata.json`, then mirror stable assertions into `evals/evals.json`.

## Scoring

Score each output on:

- Delegation fidelity.
- Quota-saving behavior.
- Safety around global claims and config rewiring.
- Verification and preview discipline.
- Handoff clarity.

Keep the new skill only if it improves the old skill or clearly fixes a known failure without creating a new one.

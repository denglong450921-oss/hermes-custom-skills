---
name: hermes-delegated-coding
description: Routes coding labor through Hermes while Codex plans, reviews, verifies, and previews the result. Use when the user asks to save Codex tokens, delegate coding to Hermes, use Hermes agent to code, or run the "Hermes codes, Codex previews/reviews" workflow.
---

# Hermes Delegated Coding

Use this skill for coding tasks where Codex should avoid doing bulk implementation work.

Default roles:

- Codex: plan, acceptance criteria, risk boundaries, final review, verification, preview.
- Hermes: read files, edit code, run tests, fix failures, return compact summary.

Preferred Hermes command:

```bash
hermes -z "$TASK_PACKAGE" --skills engineering-cybernetics-hermes --yolo
```

If the `hermes` MCP server is available in Codex, prefer that bridge for conversation. Otherwise use the CLI command above from the workspace root.

🔴 CHECKPOINT: before delegation, confirm scope, verification command, and acceptance criteria. If any are missing, ask or inspect; do not delegate a vague build.

## Workflow
1. Observe the workspace with cheap local commands only.
   Use `rg --files`, `git status --short`, and focused file reads. Avoid whole-repo dumps.

2. Create a compact task package for Hermes.
   Include goal, allowed scope, forbidden paths, implementation steps, verification command, acceptance criteria, and required return format.

3. Send coding work to Hermes.
   Keep the prompt small. Tell Hermes to return only changed files, core summary, verification result, key diff notes, and risk notes.

4. Codex reviews the result.
   Check `git status --short`, changed files, focused source snippets, relevant tests or preview checks, and whether Hermes touched anything outside scope.

🔴 CHECKPOINT: after Hermes returns, review scope and acceptance before preview or handoff. If scope, tests, or preview fail, send Hermes a narrow correction package.

5. If review finds a miss, send a narrow fix package back to Hermes.
   Do not patch directly unless the change is tiny config, Hermes setup is broken, or the user explicitly asks Codex to edit.

6. Codex previews or verifies.
   For web UI, start a local server and use the Browser plugin when available. If Browser is unavailable, use HTTP checks and a minimal DOM or command-line verification.

7. Handoff.
   Return the preview URL first when available, then changed files, verification, and remaining risks.

## Failure Branches

| Trigger | First response | If still failing |
|---|---|---|
| Hermes MCP unavailable | Run `hermes acp --check`, then use CLI from the workspace root. | Report setup blocked and ask whether Codex should code directly. |
| Hermes hangs or returns long logs | Stop after timeout and ask Hermes for compact status only. | Kill the stuck process, summarize state, and ask before retrying. |
| Hermes edits outside scope | Do not hand off. Ask Hermes to revert the forbidden files. | If revert is risky, stop and ask before changing those files. |
| Verification fails | Send Hermes the failing command and the smallest relevant error excerpt. | Codex reviews the diff and decides whether to narrow scope or ask the user. |
| Preview mismatch | Send Hermes visible acceptance misses and the exact route or viewport checked. | Keep the preview URL but mark it failed; do not claim completion. |
| User asks for global forced delegation | State that hard-forced global delegation is not verified. Apply MCP plus skill policy instead. | Offer per-workspace `AGENTS.md` policy or a project smoke test. |

## Template
```text
You are the coding worker for a Codex delegation task.

Workspace: {absolute path}
Goal: {one sentence}

Allowed scope:
- {paths Hermes may inspect/edit}

Do not touch:
- {paths outside task scope}

Implementation:
{short numbered steps}

Verification:
- Run: {command}
- If it fails, fix and rerun.

Acceptance criteria:
{short checklist}

Return only:
- Changed files
- Core summary
- Verification result
- Key diff notes
- Risk notes
```

## Rules

- Keep Codex in the planner/reviewer lane whenever practical.
- Do not paste long Hermes logs into the user response.
- Do not let Hermes do product/design decisions that need user approval.
- Do not claim global forced delegation; this is policy-driven unless Codex exposes a verified hard delegation setting.
- Keep preview servers and background processes accounted for in the final response.
- Do not hand off work with failed tests, failed preview, or unexplained out-of-scope edits.

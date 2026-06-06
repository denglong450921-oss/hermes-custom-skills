---
name: goal-dl
description: >
  Writing effective goal prompts for autonomous coding agents (Codex, Claude Code, OpenCode, etc.).
  Use when the user asks about writing goals, crafting agent prompts, setting up autonomous tasks,
  deploying AI coding agents, or wants to improve their goal-writing technique. The 7-principle
  framework covers exit criteria, direction, measurability, environment, visual targets,
  progress tracking, and cleanup.
---

# Goal Writing Framework for Autonomous Coding Agents

Seven principles for writing goal prompts that autonomous coding agents can actually complete — without drifting, faking success, or burning tokens.

🔴 **CHECKPOINT — Scan the 7 principles before writing.** Identify the 2-3 that matter most, apply those. Verify all 7 with the checklist below.

> Walkthrough: [decision tree](references/decision-tree.md) — 11 nodes → 7 principles.

## 1. Clear, Verifiable Exit Criteria

A goal prompt is not just an initial instruction — it IS the exit standard. The agent checks "am I done?" against it after every round. So:

- **Keep it short.** Focus on "when is this done?" — not every detail.
- **Include a specific number whenever possible.** "Reduce build+deploy time by 30%", "Migrate to Rust with 100% test parity", "Ship 3 features from the roadmap."
- **When unsure: talk first, then let the agent define its own goal.** A pre-goal discussion surfaces constraints before the agent commits.

Bad: "Improve the performance of the app."
Good: "Reduce cold-start latency from ~800ms to under 200ms, measured by `benchmark_cold_start.sh`."

## 2. Give Direction — Not Just a Target

A bare target like "reduce by 30%" leaves the agent flailing. Give it:

- **A starting point.** Which module? Which function? What's the current approach?
- **Available tools.** What can it call? What APIs? What test suites?
- **Known pitfalls.** What approaches have been tried and failed? What's off-limits?

Also consider: run in **plan mode** first — let the agent research and produce a `plan.md`, then have the goal reference that plan. This separates exploration from execution.

Bad: "Reduce bundle size by 20%."
Good: "Reduce bundle size by 20%. Start with `apps/web/next.config.js`. Current size: 480KB. webpack-bundle-analyzer report at `bundle-report.html`. Do NOT remove any features — tree-shake and code-split only. Test with `pnpm build && pnpm size-check`."

## 3. Make Progress Measurable

Give the agent tools to measure its own progress — otherwise it can't self-correct:

- Screenshot visual diff tools for UI work
- Test suites and coverage reports
- Performance benchmarks (`hyperfine`, `wrk`, `lighthouse`)
- Custom evals for agent-specific tasks

**Watch out for "fake completion":** Agents will sometimes:
- Crop and inline a design mockup and claim pixel-perfect match
- Remove test cases to inflate coverage to 100%
- Hardcode expected outputs instead of solving the real problem

Build verification into the goal: "Run `./verify.sh` — it must return exit code 0."

### If the agent reports completion but verification fails

| Trigger | Fix | Fallback |
|---------|-----|----------|
| Agent claims "done" but verify.sh fails | Require the agent to show verify.sh output in its response — never accept bare "done" claims | Add a second independent verification step run by a different agent |
| Agent removes tests to inflate coverage | Include "test count must not decrease" in the exit criteria | Run `git diff --stat` to detect deleted test files |
| Agent hardcodes expected outputs | Add a randomized seed to test data so outputs can't be pre-computed | Use a hidden held-out test set the agent doesn't have access to |

## 4. Give a Real Environment

Real progress requires real constraints. Run the agent in an environment close to production:

- **Same stack** (language version, framework, dependencies)
- **Same flags** (feature flags, build flags, env vars)
- **Similar database** (schema, data volume, query patterns)
- **Access to deploy and test environments** (it should be able to actually run the thing)
- **Computer use / browser use** to test real applications end-to-end

A `devcontainer` or Docker Compose setup that mirrors production is worth the upfront cost — it prevents "works on my machine" artifacts.

## 5. Be Careful With Pure Visual Goals

"100% pixel-perfect UI" is seductive but dangerous:

- Agents fixate on individual pixels → token explosions
- They overfit to one screenshot → break on other viewports / states
- Visual diff alone can't judge functional correctness

**Instead:** use screenshots as **context**, not as the final judge. Pair them with:
- Feature checklists ("can the user login? change password? see error states?")
- Written specs and design-system tokens
- Functional test suites

Let the agent use visual references to understand intent, but verify completion with specs and tests.

🔴 **CHECKPOINT — If the goal is purely visual ("pixel-perfect", "looks exactly like X"), stop and reframe.** Add at least one functional verification (checklist, spec, or test suite). A purely visual goal will almost certainly produce false completion or token explosions.

### If the agent gets stuck on visual targets

| Trigger | Fix | Fallback |
|---------|-----|----------|
| Agent loops on single-pixel adjustments | Cap the number of visual refinement rounds (e.g., "max 3 visual passes, then stop") | Switch to functional verification — if all checkboxes pass, accept minor visual differences |
| Agent overfits to one screenshot/viewport | Require screenshots at 3 breakpoints (mobile, tablet, desktop) in the exit criteria | Add a second reference screenshot from a different page for cross-validation |
| Visual diff says "100% match" but page is broken | Always pair visual diff with a functional test (e.g., Playwright script that clicks through the page) | Require a manual human review of one critical user flow |

## 6. Track Progress Across Long Runs

Background agents running for hours or days are easy to lose track of. Build progress signals into the goal:

- **Commit at key milestones** and push draft PRs (visible in GitHub even if the agent is still running)
- **Update a living artifact** — an HTML status page, a markdown log, a chart — that a human can glance at
- **Post progress to Slack / Discord / Teams** so the team sees momentum
- **Use `/side` or side-channels** for quick status checks without interrupting the main run

Example goal snippet: "After each module is done, commit with `[agent]` prefix and push a draft PR. Update `STATUS.md` with what's done and what's next."

### If progress tracking breaks down

| Trigger | Fix | Fallback |
|---------|-----|----------|
| Agent stops updating STATUS.md | Add a heartbeat requirement: "STATUS.md must be updated at least once per hour — if stale > 2h, consider the run failed" | Set up a cron job that checks STATUS.md age and alerts if stale |
| Draft PRs pile up unreviewed | Cap concurrent draft PRs at 3 — agent must wait for review before opening more | Auto-assign PRs to a specific reviewer via CODEOWNERS |

## 7. Clean Up Before Handoff

Don't rush to hand the output to the team. Especially for optimization / refactoring tasks:

1. **`/review` first** — run local review, get another agent or human to look at the diff
2. **Let the agent clean up after itself** — have it walk back through its own changes and remove dead ends, debug prints, commented-out experiments, and temporary files it left behind

Agents explore — they try things that don't work, add logging, create scratch files. Those belong in the commit history as learning artifacts, not in the final PR. A cleanup pass turns a messy exploration into a polished contribution.

Example: "After reaching the goal, run `/review` to identify dead code and debug artifacts. Then do a cleanup pass — remove all logging added during exploration, consolidate scratch files, squash fixup commits."

🛑 **STOP — Verify cleanup ran before handing output to the team.** A goal without cleanup produces messy PRs. For multi-hour/day runs, the cleanup step is mandatory.

---

## Anti-Patterns: What NOT to Do

These are the most common goal-writing mistakes. If your goal matches any of these, rewrite it before deploying.

| # | Anti-Pattern | Why it fails | Fix |
|---|-------------|-------------|-----|
| 1 | **Vague target: "make it better"** | Agent has no exit condition — runs forever or stops arbitrarily | Add a specific number: "reduce X from Y to Z" |
| 2 | **No starting point** | Agent wastes rounds exploring the entire codebase blind | Specify which file/module/service to start from |
| 3 | **Pure visual target** | Agent overfits pixels, ignores function, burns tokens | Pair screenshots with functional checklist |
| 4 | **Long run with no progress signals** | Hours/days of silence — you have no idea if it's working or stuck | Embed commit milestones, STATUS.md updates, or Slack notifications |
| 5 | **Wrong environment** | "Works on my machine" — agent tests in dev, fails in production | Specify same stack, same flags, same DB as production |

## Quick Checklist

🔴 **CHECKPOINT — Stop here before deploying any agent goal.** Verify ALL 7 items. If any item is unchecked, go back and fix the goal — an unchecked box here means the agent will either flail, fake completion, or produce unmaintainable output.

- [ ] Exit criteria: Is there a specific, measurable "done" condition?
- [ ] Direction: Starting point, tools, and pitfalls provided?
- [ ] Measurability: Does the agent have tools to verify its own progress?
- [ ] Environment: Does it run in something close to production?
- [ ] Visual targets: Are screenshots context, not the judge?
- [ ] Tracking: Are progress signals built in?
- [ ] Cleanup: Is there a review and cleanup step at the end?

🛑 **STOP — If all 7 are checked, the goal is ready to deploy.** If any item is unchecked, fix it now. Do not proceed with unchecked items.

## Harness (Self-Eval)

The harness validates that an agent following the goal-dl principles actually exhibits the expected behaviors when crafting goal prompts. 3 test cases cover all 7 principles.

### Cases

| ID | Principles Tested | Scenario |
|----|-------------------|----------|
| `case_001` | Exit Criteria + Give Direction | Vague performance-improvement request — agent must push back for specific metrics and starting points before writing a goal |
| `case_002` | Track Progress + Cleanup | Multi-day refactoring goal — agent must embed progress tracking and a cleanup step |
| `case_003` | Not Visual Only + Real Environment | Pixel-perfect UI clone request — agent must warn about visual-only targets and insist on production-like environment |

### Checks

| Check | What it detects |
|-------|----------------|
| `exit_criteria` | Asks for measurable targets, specific numbers, verifiable "done" conditions |
| `give_direction` | Provides starting point, tools, pitfalls, or suggests plan-mode exploration |
| `measurable_progress` | Suggests verification tools, warns about fake completion, builds self-check into goal |
| `real_environment` | Addresses production-like stack, same flags, containers, deployment access |
| `not_visual_only` | Warns about pixel-perfect risks, pairs visual context with functional specs |
| `track_progress` | Embeds commit milestones, living artifacts, or communication channels for long runs |
| `cleanup` | Includes review pass and dead-end removal before handoff |

### Grading Criteria

Each check passes when the agent's output contains 2+ matching positive patterns (5+ patterns per check). The grader also detects negative patterns — e.g., `exit_criteria` fails if the agent accepts a purely vague request without pushing back. Some checks use combined positive+negative scoring.

**Known calibration gaps** — `measurable_progress` and `real_environment` regex patterns are narrower than the principles they test. Tool-specific names (Lighthouse, DevTools Profiler, webpack-bundle-analyzer) and environment-inquiry language (asking about build tools, React version, deployment targets) may not match. See `references/grader-calibration.md` for the full diagnosis and suggested pattern expansions.

### Run

```bash
# Grade an existing output file
python3 evals/grader.py <output_file> '[{"text":"Exit Criteria","check":"exit_criteria"}]'

# Full harness (prints all cases with checks needed)
python3 evals/run_harness.py <output_file>
```

### Feedback Loop

When the harness catches a failure, log the case + evidence to `feedback/failures.jsonl`. Run `feedback/distill.py` to cluster errors into prompt rules, then inject approved rules as Hard Constraints in this section. Track first-time pass rate (FTPR) with `feedback/ftpr.py`.

### Honesty & Truthfulness

Report results exactly as they are:
- Test failed → state "failed" with the actual evidence
- Skipped verification → say "not verified", don't imply it passed
- No defensive disclaimers on correct results ("but this might not be correct")
- No false success — if output shows failure, don't claim "all passed"

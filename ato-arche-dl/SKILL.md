---
name: ato-arche-dl
description: >
  Design or refactor multi-step agent workflows with the atomic-skill +
  orchestration-skill pattern. Use this whenever a user describes a pipeline,
  reusable workflow, monolithic skill, cross-platform workflow, chain of 3 or
  more maintainable steps, or asks how to split, orchestrate, compose, reuse, or
  migrate skills. Trigger for phrases such as "workflow design", "pipeline",
  "orchestrate", "chain skills", "workflow refactor", "设计工作流", "编排 skill",
  "原子化", "拆 skill", "工作流重构", and "复用 skill". Also trigger when a user
  has a skill that's grown too large, has hidden dependencies between steps,
  needs resume/checkpoint capability, runs steps in parallel, or wants to add
  a new platform to an existing workflow. Produce a concrete architecture:
  atomic boundaries, contracts, orchestration steps, checkpoints, failure
  routes, parallel execution plan, cost budget, reuse analysis, and an
  implementation order.
compatibility: Hermes Agent and Codex-style skill environments.
---

# Atomic + Orchestration Workflow Design

Design maintainable agent workflows by separating capability from coordination:

- An **atomic skill** owns one independently testable capability.
- An **orchestration skill** declares sequence, routing, data flow, checkpoints,
  and fallback choices.
- Business logic belongs in atomic skills or their bundled scripts. Keep it out
  of the orchestrator so each capability can evolve without rewriting the flow.

The aim is not to create the largest possible number of skills. Choose the
smallest set of stable boundaries that makes testing, replacement, and reuse
meaningfully easier.

## Quick Start: Scaffolding Tools

Before writing by hand, use bundled scripts:

```bash
# Scaffold a new atomic skill from template
python3 scripts/scaffold-skill.py atomic --name parse-author --dir ./skills/
# Output: ./skills/parse-author/SKILL.md + references/ + scripts/

# Scaffold a new orchestration skill from template
python3 scripts/scaffold-skill.py orchestration --name content-collection --dir ./skills/
# Output: ./skills/content-collection/SKILL.md with workflow table

# Generate contract docs from a workflow spec (JSON input required)
python3 scripts/generate-contract.py workflow.json --output-dir ./contracts/
# Input: workflow.json — see script docstring for required schema
# Output: ./contracts/<skill-name>.md per atomic skill in spec
```

| Script | Required args | Optional args | Output |
|--------|---------------|---------------|--------|
| `scaffold-skill.py` | `atomic\|orchestration`, `--name` | `--dir` (default `.`) | `<dir>/<name>/SKILL.md` + `references/` + `scripts/` |
| `generate-contract.py` | `workflow.json` path | `--output-dir` (default `./contracts/`) | `<output-dir>/<skill>.md` per atomic skill |

The scaffold produces structured starting points with contract tables, failure handling,
and verification sections already in place. Edit the generated files to fill in
domain-specific details.

## Design Workflow

### 1. Capture the outcome

Summarize:

- The user-visible goal
- Inputs and final deliverables
- External systems, tools, and runtime dependencies
- Human decisions that cannot be automated safely
- Constraints: cost, latency, privacy, partial-result tolerance

Do not start naming skills until the end-to-end outcome is clear.

### 2. Inventory the actions

List the actual operations in execution order. Include setup, validation,
conversion, analysis, persistence, reporting, and cleanup. Mark:

- Conditional branches
- Steps that can run in parallel (see `references/parallel-patterns.md`)
- Repeated operations
- Platform-specific operations
- Human review points
- Failure-prone boundaries (network requests, model calls)

This inventory is a behavior map, not yet a skill list.

### 3. Choose atomic boundaries

Create an atomic skill when a group of actions has one clear responsibility and
can be tested or replaced as a unit.

Good reasons to split:

- It has a distinct input/output contract.
- It is reused by more than one workflow.
- It uses a different runtime, tool, provider, or failure policy.
- It may be tuned, replaced, or tested independently.
- It has a meaningful domain name such as `image-ocr` or `generate-report`.

Good reasons to keep actions together:

- Separating them exposes unstable intermediate data with no reuse value.
- They share one lifecycle and always change together.
- A split would create tiny wrapper skills that only forward parameters.
- The combined unit is still easy to understand and test.

Use a short verb-noun name for each atomic skill, such as `parse-author`,
`collect-works`, `audio-transcribe`, or `generate-report`.

### 4. Separate reusable and specific capabilities

Classify every atomic skill:

| Classification | Meaning | Example |
|---|---|---|
| Reusable | Independent of platform or workflow | `image-ocr`, `audio-transcribe` |
| Domain-specific | Shared within one business domain | `normalize-product-record` |
| Platform-specific | Coupled to an API, site, or provider | `parse-xiaohongshu-author` |
| Workflow-specific | Useful only in this delivery flow | `publish-campaign-summary` |

Look for existing skills before proposing new ones. Reuse is the payoff of this
design pattern.

### Reuse evidence gate

When describing implementation availability, use exactly one status:

- `verified`: an inspected skill path or quoted contract is cited.
- `unverified`: reuse is plausible, but the contract was not inspected.
- `extract`: the behavior exists inside a known monolith and must be separated.
- `create`: no reusable implementation was found within a cited search scope.

Never infer `verified` from naming similarity, a case study, a catalog name, or
a user description alone. Add evidence inline for every `verified`, `extract`,
or `create` claim. For `create`, name the inspected search scope. If inspection
is unavailable, use `unverified` and make contract verification the first
implementation step.

This evidence annotation is additive. Do not remove or simplify safety
invariants, contracts, idempotency keys, immutable digests, fallback routes, or
checkpoints to make room for it.

### 5. Define contracts before implementation

For each atomic skill, specify:

| Field | What to write |
|---|---|
| Responsibility | One sentence describing the single capability |
| Input | Required fields, optional fields, and accepted formats |
| Output | Stable fields, file paths, and result format |
| Preconditions | Required tools, credentials, files, or prior state |
| Failure behavior | Errors, retries, partial results, and fallback output |
| Verification | How to confirm the result is usable |

Prefer structured contracts (JSON objects, documented file layouts).
Avoid implicit handoffs that require downstream skills to guess field names.

#### Contract versioning

Contracts evolve. Plan for backward compatibility:

- **Minor version** (1.0 → 1.1): Add optional fields. Backward compatible.
- **Major version** (1.x → 2.0): Rename or remove fields. Breaking change.
  Provide an adapter skill that converts new format to old format for
  downstream consumers not yet migrated.

Document version in each skill's SKILL.md frontmatter:

```yaml
contract_version: "1.1"
```

Orchestrators should declare which contract version they expect per step.
A mismatch between orchestrator expectation and skill output is a bug, not
a runtime surprise — catch it in testing.

### 6. Design the orchestration skill

The orchestrator should read like an executable map. For every step state:

1. Which atomic skill to call
2. Which previous output supplies its input
3. What result is expected
4. Which route to take on success, partial success, or failure
5. Whether to checkpoint, pause for the user, or continue

The orchestrator may contain routing logic such as:

- If the item is an image, call `image-ocr`.
- If the item is a video, call `audio-transcribe`.
- If a remote GPU is unavailable, route to `transcribe-cpu`.

It should not duplicate implementation details such as selectors, parsing
rules, API payloads, prompts, or shell commands owned by an atomic skill.

#### Parallel execution

When steps have no data dependency, run them in parallel. Three patterns:

**Fan-out / Fan-in:** Multiple items need same processing (batch OCR, parallel
API calls). Each parallel skill gets independent input. Aggregator defines
timeout and partial-result policy.

**Pipeline with buffers:** Streaming data through transformations. Each stage
defines I/O schema. Buffers handle backpressure.

**Competitive execution:** Multiple implementations with different cost/latency
tradeoffs. All produce same output schema. Orchestrator picks first success
and cancels losers.

For detailed patterns, concurrency limits, and examples, see
`references/parallel-patterns.md`.

#### Cost budgeting

Add budget constraints to orchestration contracts:

```json
{
  "max_tokens": 50000,
  "max_api_calls": 100,
  "max_wall_time_seconds": 300,
  "on_budget_exceeded": "stop_and_report"
}
```

Track cumulative cost per `run_id`. Check budget before each step. Route to
cheaper alternatives when approaching limits.

### 7. Make recovery explicit

Workflows become trustworthy when failure is a designed state rather than a
surprise. Define a fallback table:

| Step | Failure signal | First response | Final fallback |
|---|---|---|---|
| `[step]` | `[timeout / empty / invalid]` | `[retry / alternate]` | `[partial / manual / stop]` |

Add run-state fields when a workflow is long-running or expensive:

- `run_id`
- `step_status` (per step: pending / completed / failed / partial)
- `completed_items`
- `failed_items`
- `artifact_paths`
- `resume_from`

Favor idempotent steps so a resumed workflow does not duplicate downloads,
database rows, messages, or charges.

#### Idempotency patterns

- **Idempotency key:** Hash of `(input_params + run_id + step_name)` passed to
  APIs, DBs, or file systems. Server checks if key already processed.
- **Conditional write:** Only write if output doesn't already exist.
- **Upsert:** `INSERT ... ON CONFLICT UPDATE` for database writes.

Non-idempotent steps (email, SMS, payment) must check completion status
before re-executing on resume.

#### Checkpoint strategy

Checkpoint when a step is:
- Expensive (API calls, GPU time)
- Slow (> 1 minute)
- Failure-prone (network requests, model calls)
- Produces partial results with standalone value

On resume, validate checkpoint before trusting it: verify referenced files
still exist, API tokens still valid, data not corrupted. If invalid, restart
from beginning and log warning.

### 8. Verify the architecture

Don't just ask questions — run tests. Execute each procedure from
`references/testing-procedures.md`:

1. **Single responsibility verification:** List all actions, confirm each
   contributes to one responsibility. Fail if skill name contains "and".
2. **Independent testability:** Run each atomic skill in isolation with mock
   input. Verify output matches contract. Fail if it requires another skill
   to run first.
3. **Contract validation:** Check every orchestration step has explicit input
   source (not "previous output"), structured output schema, and documented
   failure behavior.
4. **Failure route verification:** Simulate each failure-prone step's failure
   modes. Verify orchestrator routes to correct fallback.
5. **Platform isolation:** Verify reusable skills contain no platform-specific
   logic. Test with 2+ platform inputs.
6. **Resume safety:** Run to checkpoint, kill process, resume. Verify completed
   steps skipped, no duplicate side effects.
7. **Human decision points:** Verify all STOP points documented, no silent
   auto-approval timeouts.
8. **Cost and time estimation:** Estimate API calls, tokens, wall time per
   step. Sum and compare to budget.

Also run each sub-skill through the 4-node decomposition decision tree in
`references/decomposition-checklist.md`.

## Required Design Output

When answering a workflow-design or workflow-refactor request, provide these
sections. Keep depth proportional to the workflow.

### 1. Workflow summary

Goal, inputs, final deliverables, major constraints.

### 2. Atomic skill map

| Skill | Responsibility | Input | Output | Classification | Reuse status | Evidence |
|---|---|---|---|---|---|---|
| `[name]` | `[responsibility]` | `[contract]` | `[contract]` | `[type]` | `[status]` | `[evidence]` |

### 3. Orchestration flow

| Step | Invoke | Input source | Output | Route, checkpoint, or fallback |
|---|---|---|---|---|
| `0` | `[skill]` | `[source]` | `[result]` | `[next]` |

Mark human review points as `🔴 STOP: wait for user confirmation`.
Do not invent an automatic approval timeout unless the user requests one.

### 4. Parallel execution plan

Which steps run in parallel, which pattern (fan-out, pipeline, competitive),
max concurrency, and partial-failure policy. Omit if all steps are sequential.

### 5. Recovery and resume plan

Fallback table, checkpoint locations, idempotency strategy for non-idempotent
steps.

### 6. Cost budget

Estimated API calls, tokens, wall time per step. Total budget. Action on
budget exceeded.

### 7. Reuse and migration plan

What exists, what to extract, what to create, what stays unchanged when
adding another platform.

### 8. Implementation order

1. Define contracts (run `scripts/generate-contract.py`).
2. Implement and verify atomic skills independently.
3. Test routing, parallel execution, and fallbacks.
4. Add the orchestration skill.
5. Run end-to-end test with checkpoints and resume.

## Common Anti-Patterns

| Anti-pattern | Why it hurts | Better design |
|---|---|---|
| Monolithic skill owns full pipeline | One change disturbs unrelated behavior | Extract capabilities, add orchestrator |
| Orchestrator repeats business logic | Logic diverges across workflows | Keep implementation in atomic skills |
| Atomic skill secretly calls other skills | Dependencies become invisible | Declare cross-skill calls in orchestrator |
| Every tiny helper becomes a skill | Coordination overhead exceeds benefit | Keep inseparable helpers in one skill |
| Contracts are prose-only or implicit | Downstream behavior becomes fragile | Structured inputs, outputs, failure states |
| Configuration is hard-coded | Reuse requires source edits | Pass configuration through contracts |
| Human decisions auto-approve silently | Workflow takes unintended actions | 🔴 Explicit STOP or user-approved policy |
| Recovery is missing | One failure discards useful work | Retry, fallback, partial output, resume |
| Parallel without concurrency limit | Resource exhaustion, rate limits | Max workers, semaphore, backpressure |
| No cost tracking | Budget exceeded silently | Track per step, alert on threshold |
| Checkpoint without validation | Resume from corrupted state | Validate before trusting checkpoint |
| Contract changes without versioning | Downstream skills break silently | Version contracts, adapter skills for breaking changes |

## Real-World Pitfalls

Production deployments surface patterns that design-time reviews miss.
Read `references/pitfalls.md` for 14 documented pitfalls with symptoms,
root causes, and fixes. Two patterns the anti-patterns table above does not
cover in depth:

1. **Retry storms:** No exponential backoff, infinite retry loops hitting
   rate limits. Anti-patterns row 8 covers missing recovery, but storms need
   explicit backoff — add `retry_interval = min(2^attempt, 60)` to contracts.
2. **Implicit state sharing:** Skills share files through hardcoded paths
   instead of explicit contracts (anti-patterns row 5 catches prose-only
   contracts; this is the runtime symptom — always use contract fields,
   never assume file locations).

## Reference Materials

| File | When to read |
|---|---|
| `references/decomposition-checklist.md` | Validating each sub-skill meets the 3 principles |
| `references/parallel-patterns.md` | Designing concurrent execution, cost budgets, checkpoints |
| `references/testing-procedures.md` | Step 8 verification — actionable tests, not questions |
| `references/pitfalls.md` | Learning from 14 production failure patterns |
| `references/cross-domain-cases.md` | Seeing the pattern in SaaS onboarding, ML training, e-commerce, content moderation |
| `references/douyin-case-study.md` | Original content-collection pipeline example |

## Atomic Skill Template

````markdown
---
name: my-atomic-skill
description: Perform one specific capability. Use when [trigger context].
contract_version: "1.0"
---

# My Atomic Skill

## Responsibility
[One capability only.]

## Input
```json
{
  "required_field": "value",
  "optional_field": "value"
}
```

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `required_field` | string | Yes | - |
| `optional_field` | string | No | "default" |

## Preconditions
- [Tools, credentials, files, prior state]

## Process
1. Validate preconditions.
2. Perform the capability.
3. Validate the result.
4. Return structured output or a documented failure state.

## Output
```json
{
  "status": "success",
  "result": {}
}
```

## Failure Handling
| Signal | Response | Fallback |
|--------|----------|----------|
| `[signal]` | `[response]` | `[fallback]` |

## Verification
[How to confirm the result is usable.]
````

## Orchestration Skill Template

```markdown
---
name: my-workflow-orchestrator
description: Orchestrate [workflow outcome] by routing data through atomic skills.
---

# My Workflow Orchestrator

## Inputs
- `[user input]`

## Workflow
| Step | Invoke | Input source | Output | Next route |
|---|---|---|---|---|
| `0` | `health-check` | Runtime context | `health_status` | Continue or fallback |
| `1` | `parse-source` | User input | `source_record` | Step 2 |
| `2` | `collect-items` | `source_record.id` | `items[]` | Step 3 |
| `3a` | `image-ocr` | Image items (parallel) | `text_results[]` | Step 4 |
| `3b` | `audio-transcribe` | Video items (parallel) | `text_results[]` | Step 4 |
| `4` | `generate-report` | All results | Report artifact | Complete |

## Parallel Execution
Steps 3a and 3b run concurrently. Max concurrency: 10 items per skill.
Partial failure policy: continue with successful items if > 90% succeed.

## Recovery
| Step | Failure signal | First response | Final fallback |
|---|---|---|---|
| `[step]` | `[signal]` | `[response]` | `[fallback]` |

## Cost Budget
| Resource | Limit | On exceeded |
|----------|-------|-------------|
| API calls | 100 | Stop and report |
| Model tokens | 50000 | Switch to cheaper model |

## Resume
Persist `run_id`, `step_status`, `failed_items`, and `artifact_paths`.
Validate checkpoint before resuming.
```

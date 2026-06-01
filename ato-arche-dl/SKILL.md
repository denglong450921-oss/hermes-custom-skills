---
name: ato-arche-dl
description: >
  Design or refactor multi-step agent workflows with the atomic-skill +
  orchestration-skill pattern. Use this whenever a user describes a pipeline,
  reusable workflow, monolithic skill, cross-platform workflow, chain of 3 or
  more maintainable steps, or asks how to split, orchestrate, compose, reuse, or
  migrate skills. Trigger for phrases such as "workflow design", "pipeline",
  "orchestrate", "chain skills", "workflow refactor", "设计工作流", "编排 skill",
  "原子化", "拆 skill", "工作流重构", and "复用 skill". Produce a concrete
  architecture: atomic boundaries, contracts, orchestration steps, checkpoints,
  failure routes, reuse analysis, and an implementation order.
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

## Design Workflow

### 1. Capture the outcome

Summarize:

- The user-visible goal
- Inputs and final deliverables
- External systems, tools, and runtime dependencies
- Human decisions that cannot be automated safely
- Constraints such as cost, latency, privacy, and partial-result tolerance

Do not start naming skills until the end-to-end outcome is clear.

### 2. Inventory the actions

List the actual operations in execution order. Include setup, validation,
conversion, analysis, persistence, reporting, and cleanup. Mark:

- Conditional branches
- Steps that can run in parallel
- Repeated operations
- Platform-specific operations
- Human review points
- Failure-prone boundaries such as network requests or model calls

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

Prefer structured contracts such as JSON objects or documented file layouts.
Avoid implicit handoffs that require downstream skills to guess field names.

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

### 7. Make recovery explicit

Workflows become trustworthy when failure is a designed state rather than a
surprise. Define a fallback table:

| Step | Failure signal | First response | Final fallback |
|---|---|---|---|
| `[step]` | `[timeout / empty output / invalid data]` | `[retry / alternate route]` | `[partial result / manual review / stop]` |

Add run-state fields when a workflow is long-running or expensive:

- `run_id`
- `step_status`
- `completed_items`
- `failed_items`
- `artifact_paths`
- `resume_from`

Favor idempotent steps so a resumed workflow does not duplicate downloads,
database rows, messages, or charges.

### 8. Verify the architecture

Before finalizing, ask:

- Does each atomic skill do one coherent job?
- Can each atomic skill be tested without running the full workflow?
- Does the orchestrator contain only coordination logic?
- Are all handoffs explicit and stable?
- Are platform-specific skills isolated?
- Can common capabilities be reused in another workflow?
- Are checkpoints and human decisions clearly marked?
- Does each failure-prone step have a fallback or an intentional stop?
- Can the workflow resume safely after an interruption?

## Required Design Output

When answering a workflow-design or workflow-refactor request, provide the
following sections. Keep the depth proportional to the workflow.

### 1. Workflow summary

State the goal, inputs, final deliverables, and major constraints.

### 2. Atomic skill map

| Skill | Responsibility | Input | Output | Classification | Reuse status | Evidence |
|---|---|---|---|---|---|---|
| `[skill-name]` | `[single responsibility]` | `[contract]` | `[contract]` | `[reusable / domain / platform / workflow]` | `[verified / unverified / extract / create]` | `[inspected path / quoted contract / source monolith / search scope]` |

### 3. Orchestration flow

| Step | Invoke | Input source | Output | Route, checkpoint, or fallback |
|---|---|---|---|---|
| `0` | `[skill-name]` | `[user input or prior output]` | `[result]` | `[next step or fallback]` |

Mark human review points clearly as `STOP: wait for user confirmation`.
Do not invent an automatic approval timeout unless the user requests one.

### 4. Reuse and migration plan

Explain what already exists, what should be extracted from a monolith, what
must be created, and what can remain unchanged when adding another platform.

### 5. Implementation order

Recommend an incremental build sequence:

1. Define contracts.
2. Implement and verify atomic skills independently.
3. Test routing and fallbacks.
4. Add the orchestration skill.
5. Run an end-to-end test with checkpoints.

## Atomic Skill Template

````markdown
---
name: my-atomic-skill
description: Perform one specific capability. Use when [trigger context].
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
|---|---|---|
| `[signal]` | `[response]` | `[fallback]` |
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
| `3a` | `image-ocr` | Image items | `text_results[]` | Step 4 |
| `3b` | `audio-transcribe` | Video items | `text_results[]` | Step 4 |
| `4` | `generate-report` | All results | Report artifact | Complete |

## Recovery
| Step | Failure signal | First response | Final fallback |
|---|---|---|---|
| `[step]` | `[signal]` | `[response]` | `[fallback]` |

## Resume
Persist `run_id`, `step_status`, `failed_items`, and `artifact_paths`.
```

## Common Anti-Patterns

| Anti-pattern | Why it hurts | Better design |
|---|---|---|
| Monolithic skill owns the full pipeline | One change can disturb unrelated behavior | Extract stable capabilities and add an orchestrator |
| Orchestrator repeats business logic | Logic diverges across workflows | Keep implementation in atomic skills |
| Atomic skill secretly calls other skills | Dependencies become invisible | Declare cross-skill calls in the orchestrator |
| Every tiny helper becomes a skill | Coordination overhead exceeds the benefit | Keep inseparable helpers inside one atomic skill |
| Contracts are prose-only or implicit | Downstream behavior becomes fragile | Define structured inputs, outputs, and failure states |
| Configuration is hard-coded | Reuse requires source edits | Pass configuration through contracts |
| Human decisions auto-approve silently | The workflow can take unintended actions | Add an explicit stop or user-approved policy |
| Recovery is missing | One failure discards useful work | Design retry, fallback, partial output, and resume behavior |

## Reference Case

Read `references/douyin-case-study.md` when a concrete example, reuse matrix, or
comparison with a content-collection pipeline would help. Treat it as an
illustration of the pattern, not as a required workflow shape.

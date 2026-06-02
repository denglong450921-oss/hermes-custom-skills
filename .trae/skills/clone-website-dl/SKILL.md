---
name: clone-website-dl
description: >
  Orchestrate high-fidelity website, page, and section cloning from live URLs.
  Use whenever a user asks to clone, copy, replicate, recreate, reverse-engineer,
  or rebuild a website, page, landing page, or individual section, including
  pixel-perfect clones, partial hero or pricing clones, multi-page clones, and
  customized clones. Route work through evidence extraction, implementation,
  and visual QA skills. Do not implement from screenshots alone.
metadata:
  argument-hint: "<url1> [<url2> ...]"
  hermes:
    user-invocable: true
---

# Clone Website Orchestrator

Coordinate a high-fidelity clone without embedding extraction, component-build,
or visual-diff implementation details in this skill.

## Companion Skills

Load the companion skill before entering its phase:

| Skill | Responsibility | Input | Output | Classification | Reuse status | Evidence |
|---|---|---|---|---|---|---|
| `clone-website-extract-dl` | Capture rendered evidence and create a canonical page record. | URL, scope, project root | Completed `SOURCE_OF_TRUTH.md`, screenshots, manifests, behavior reports | reusable | `verified` | Inspected `../clone-website-extract-dl/SKILL.md` |
| `clone-website-build-dl` | Build foundation, component specs, components, and page assembly from approved evidence. | Approved source of truth, project root, customization policy | Compiling clone implementation | reusable | `verified` | Inspected `../clone-website-build-dl/SKILL.md` |
| `clone-website-qa-dl` | Measure fidelity and drive repair until completion gates pass. | Original URL, clone URL, approved source of truth | Saved QA reports and acceptance decision | reusable | `verified` | Inspected `../clone-website-qa-dl/SKILL.md` |

These three skills are the stable atomic boundaries. Keep their internal helper
scripts bundled with their owner. Do not split every browser action, shell
command, or component edit into another skill.

## Scope Defaults

Clone exactly what is visible at the requested URL unless the user says
otherwise.

- Fidelity: high visual fidelity with measured convergence.
- In scope: layout, assets, text, responsive behavior, and visible interactions.
- Out of scope by default: real backend, authentication, analytics trackers,
  and production data connections.
- Customization: none unless requested.

For multiple URLs, process page extraction independently and in parallel where
the runtime permits. Isolate artifacts by page under
`docs/research/pages/<page-slug>/`.

## Run State

Persist enough state to resume safely:

```json
{
  "run_id": "clone-...",
  "targets": [],
  "scope": "full | partial | multi-page | customized",
  "step_status": {},
  "artifact_paths": [],
  "failed_items": [],
  "resume_from": null
}
```

## Agent Pipeline

```text
clone-website-extract-dl
  -> STOP: review canonical source of truth
  -> clone-website-build-dl
  -> clone-website-qa-dl
  -> repair loop: evidence -> source record -> specs -> implementation -> QA
  -> component graph and delivery
```

When delegation is available, dispatch independent component builders only
after their specs are complete. When delegation is unavailable, execute the
same specs sequentially. The architecture does not depend on subagents.

## Orchestration Flow

| Step | Invoke | Input source | Output | Route, checkpoint, or fallback |
|---|---|---|---|---|
| `0` | Parse target and scope | User request | Validated targets and scope | Ask only if full versus partial scope is genuinely ambiguous |
| `1` | `clone-website-extract-dl` | Targets, scope, project root | Canonical evidence bundle per page | Stop on inaccessible SPA without rendered-browser capability |
| `2` | Review evidence | Step 1 | Approved page records | **STOP: wait for user confirmation before implementation** |
| `3` | `clone-website-build-dl` | Approved records and requested customizations | Compiling implementation | Partial clones skip full page assembly |
| `4` | `clone-website-qa-dl` | Original URL, clone URL, records | QA reports and pass/fail decision | On mismatch, enter the repair loop |
| `5` | Reconcile fidelity change | QA discrepancy | Updated record, specs, code | Return to step `4`; never patch code before recording stronger evidence |
| `6` | Generate component graph | Accepted implementation | `docs/component-graph.md` | Deliver clone and QA evidence |

## Partial Clone Route

For a named section such as hero, pricing, or footer:

1. Ask `clone-website-extract-dl` for focused desktop and mobile evidence.
2. Show the target screenshots and confirm the selected section.
3. Ask `clone-website-build-dl` for one independently testable component with
   props and defaults.
4. Skip page assembly.
5. Ask `clone-website-qa-dl` to compare the standalone render.

If the section depends on page-level scrolling, explain that behavior and ask
whether to add a minimal wrapper.

## Customized Clone Route

Extract the original first. Record each requested override in the canonical
page record before implementation. During QA, require non-customized regions to
match the original and verify customized regions against the override contract.

## Recovery

| Step | Failure signal | First response | Final fallback |
|---|---|---|---|
| Extraction | Target blocked or rendered evidence unavailable | Retry through the extraction skill's capability fallback | Ask for an accessible URL or screenshots; do not guess |
| Evidence review | Missing asset, state, or CSS value | Re-run focused extraction | Stop before implementation |
| Build | TypeScript or production build fails | Repair the owning component from its spec | Rebuild the component from the recorded layout pattern |
| QA | Pixel or geometry gate fails | Record discrepancy, update evidence, then repair | Document an intentional limitation only when fidelity is impossible |

## Completion Contract

Do not claim completion until:

- Each page has one approved canonical source of truth.
- The production build passes.
- `clone-website-qa-dl` has saved visual and geometry reports.
- Reachable assets render visibly; unavailable media has a documented fallback.
- Interactive states and responsive layouts have been checked.
- The component graph is saved to `docs/component-graph.md`.

## Common Antipatterns

| Antipattern | Better route |
|---|---|
| Coding before evidence is complete | Return to `clone-website-extract-dl` |
| Implementing directly from a screenshot | Extract DOM, computed CSS, assets, spacing, and states |
| Putting business logic in this orchestrator | Move it into the owning atomic skill |
| Splitting every small command into a skill | Keep helpers bundled with their stable capability |
| Patching a structural layout mismatch | Rebuild from the corrected source record and spec |
| Calling a clone "done" by visual impression alone | Require `clone-website-qa-dl` convergence reports |

## Self-Test

Run:

```bash
bash evals/test-split-skills.sh
python3 evals/run_harness.py SKILL.md
```

The split-skills test validates companion contracts, resource ownership, thin
orchestration, and the existing regression harness.

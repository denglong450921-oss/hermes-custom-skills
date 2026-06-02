---
name: clone-website-build-dl
description: >
  Build a website clone from an approved canonical source of truth. Use after
  clone-website-extract-dl has captured evidence and the user has approved
  implementation: establish the shared foundation, write component specs,
  implement sections, assemble pages, and keep the production build compiling.
  This is the implementation phase used by clone-website-dl.
compatibility: Existing web project scaffold with its normal build and type-check commands.
---

# Clone Website Build

Build only from an approved canonical page record. Do not reinterpret live-site
evidence inside component code.

Treat the directory containing this file as `CLONE_BUILD_DIR`. Resolve the
loaded `clone-website-extract-dl/SKILL.md` path once and treat its containing
directory as `CLONE_EXTRACT_DIR`. Do not resolve bundled resources relative to
the clone project's working directory.

## Input

```json
{
  "project_root": "/path/to/clone",
  "source_of_truth": "docs/research/pages/home/SOURCE_OF_TRUTH.md",
  "scope": "full | partial | multi-page | customized",
  "customizations": []
}
```

## Output

```json
{
  "status": "ready_for_qa | blocked",
  "components": [],
  "routes": [],
  "build_command": "npm run build",
  "build_passed": true
}
```

## Preconditions

Before the first code edit and before every later fidelity modification, run:

```bash
node "$CLONE_EXTRACT_DIR/scripts/validate-source-of-truth.mjs" \
  "docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md" \
  "$PWD" \
  --stage=extraction
```

Require exit code `0`. If implementation evidence changes, update the source of
truth first, then reconcile derived specs, then change code.

## Build Workflow

### 1. Verify scaffold

Run the project's production build before editing. For Next.js with Tailwind v4,
confirm `postcss.config.mjs` exists so utility classes are generated.

### 2. Build shared foundation

Sequentially establish:

1. Fonts and metadata.
2. Global CSS tokens, scroll behavior, and theme variables.
3. TypeScript interfaces under `src/types/`.
4. Shared icons and global assets.
5. Any user-approved customization variables.

Preserve a target site's existing CSS-variable architecture when it is
structured. Prefer reachable self-hosted fonts. Keep third-party trackers out of
the clone.

### 3. Write component specifications

For each section, create:

```text
docs/research/components/<ComponentName>.spec.md
```

Use `references/spec-template.md`. Copy exact values from the approved page
record. Every spec must include:

- Target file and screenshot path.
- Source-of-truth path and section ID.
- Props TypeScript interface.
- DOM hierarchy and exact layout pattern.
- Computed CSS values.
- Text copied verbatim.
- Assets and fallback behavior.
- Static, click, hover, scroll, and responsive states.
- Customization notes and limitations.

Do not estimate missing CSS. Return to `clone-website-extract-dl`.

### 4. Implement components

Build one component per stable visual section. Keep inseparable helpers inside
the component. Split only when a sub-component has an independently useful
contract.

If parallel builders are available, dispatch only after a complete spec exists.
Inline the complete spec, target file, screenshot path, props interface, shared
imports, and type-check command in the builder prompt. If delegation is not
available, implement sequentially from the same spec.

Read `references/checklist.md` before dispatching. Read
`references/antipatterns.md` when a builder is drifting toward approximation.

### 5. Verify each component

Check:

1. Text content exactly matches evidence.
2. Structural pattern matches: sticky scroll, alternating row, hero, grid,
   carousel, modal, or layered composition.
3. Key CSS values match extracted values.
4. Reachable media is visibly rendered.
5. The project's type-check command passes.

If the layout pattern is structurally wrong, rebuild from the corrected spec
instead of patching around it.

### 6. Assemble pages

For full or multi-page clones:

- Wire sections into the route.
- Add page-level scroll containers, sticky layers, and interactions.
- Pass real content through props.
- Update document locale.
- Remove stale clone-target components.
- Run the production build.

For partial clones, skip full page assembly. Deliver one standalone component
with props and sensible defaults, plus a minimal wrapper only when requested.

### 7. Apply customizations

Read `references/customization.md`. Record original values and approved
overrides in the source of truth before changing code. Prefer CSS variables for
colors and typography. Keep non-customized regions faithful to the original.

## Recovery

| Failure signal | First response | Final fallback |
|---|---|---|
| Source-of-truth validator fails | Return to focused extraction | Stop before code edits |
| Production build fails | Isolate the owning component and repair from spec | Temporarily remove only the failing section while diagnosing |
| Builder paraphrases content | Restore verbatim source text | Add exact text to the spec |
| Structural pattern mismatch | Correct evidence and rebuild the section | Implement directly from the corrected spec |
| Missing media | Return to asset evidence | Implement only the documented booth fallback |

## Verification

Hand off to `clone-website-qa-dl` only when:

- Every implemented component has a traceable spec.
- The page record remains current.
- Type checks pass.
- The production build passes.
- Partial clones render independently.

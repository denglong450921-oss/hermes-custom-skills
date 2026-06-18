---
name: clone-website-dl-v2
description: Fast, high-fidelity static website/page cloning from live URLs or supplied HTML, also matching requests that mention clone_website_dl_v2. Use this whenever the user asks to clone, copy, replicate, recreate, reverse-engineer, or rebuild a static web page, landing page, marketing page, docs page, nav/footer, or section and wants localized assets, reusable header/footer components, TDD-style stage gates, explicit load-completion criteria for slow pages, optional Scrapling-assisted extraction, and no animation reconstruction. Prefer this skill over general frontend skills when fidelity, asset localization, and staged detection/checklists matter.
compatibility: Browser automation or Playwright is strongly preferred. Scrapling is optional for slow/dynamic extraction fallback. Works with any web project scaffold that can serve and build static pages.
---

# Static Website Clone DL v2

Replicate static web pages quickly while preserving visual fidelity. This skill is optimized for pages where the user does not need animation behavior. Treat motion, videos, canvases, Lottie, and complex runtime widgets as static visual regions unless the user explicitly asks otherwise.

## Core Contract

Build from evidence, not memory. The workflow advances through stages, and each stage must pass a checklist-driven detection gate before the next stage starts.

Important constraints:

- Prioritize static visual fidelity, responsive layout, real copy, typography, colors, spacing, and media occupancy.
- Build the delivered page from semantic DOM and localized assets. Do not ship a page that hides the real DOM and displays a full-page screenshot/reference capture as the primary visual layer.
- Do not reconstruct animations. Disable CSS/JS animations for deterministic screenshots and implement stable end states or static posters.
- Localize resources. Download reachable images, fonts, SVGs, CSS, and small videos into the project. Rewrite references to local paths.
- Enforce a 500 MB default total resource budget. If localized media would exceed the budget, use documented placeholders for images/videos instead of downloading the large files.
- Create `Header`/navigation and `Footer` as independent reusable components. Page sections must import or compose them rather than duplicating their markup.
- Follow test-driven development: write the stage checklist, expected artifacts, and verification command before implementing that stage.
- For every detection gate, create a fresh detector agent. Do not let the builder self-certify. If fresh delegation is unavailable, stop and tell the user the gate cannot be certified.
- Define and record explicit load-completion criteria before extracting slow pages. Do not rely on a fixed sleep or one `networkidle` event.

## Inputs

Accept any of these:

- One or more URLs.
- A local HTML file or folder.
- A specific page section, plus the URL or HTML source.
- A target project root, or permission to create a minimal static/React/Next/Vite project.

Clarify only when the target, scope, or output project is genuinely ambiguous.

## Output Structure

Use these artifact paths unless the project already has a clearly equivalent convention:

```text
docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md
docs/research/components/<ComponentName>.spec.md
docs/design-references/<page-slug>-<viewport>.png
docs/detection/<stage>/<timestamp>-detector-report.md
docs/qa/<page-slug>/
public/assets/<hostname>/
src/components/Header.*
src/components/Footer.*
src/components/sections/<SectionName>.*
```

For non-React projects, keep the same component boundary in the local framework's idiom.

## Stage Workflow

### Stage 0: Scope And Harness

1. Normalize URL(s), page slug(s), and clone scope.
2. Identify the project type and commands for build, type check, test, and serve.
3. Create a run log at `docs/research/clone-run.md`.
4. Write the Stage 0 detection checklist entry before making code changes.
5. Run the existing build/test command if one exists. If no project exists, create the smallest appropriate scaffold and record that choice.

Detection gate: spawn a fresh detector agent with the Stage 0 checklist. Continue only if it passes.

### Stage 1: Static Evidence Extraction

Capture the source page in a rendered browser when possible.

Before screenshots or DOM extraction, create a load-completion plan and save its report:

```bash
node <skill-dir>/scripts/wait-for-static-load.mjs \
  --url "$URL" \
  --out "docs/research/pages/<page-slug>/load-report.json" \
  --critical-selector "main, body"
```

The page is ready only when the load report shows:

- `domcontentloaded` or stronger reached.
- At least one critical selector is visible.
- The relevant network is quiet for a stable window, ignoring long-lived analytics, websocket, beacon, and telemetry requests.
- DOM element count, visible text length, and page height are stable across repeated samples.
- Fonts are ready or a font timeout is recorded.
- Lazy-loaded sections have been warmed by controlled scrolling.
- Visible images in captured regions are loaded, or are listed as placeholders/fallbacks.
- Skeletons/spinners/cookie overlays are gone, dismissed, or recorded as blockers.

If Playwright/browser extraction cannot reach those conditions within the configured timeout, read `references/load-completion.md` and try the Scrapling fallback route before asking the user for access or screenshots.

Required evidence:

- Full-page screenshots at desktop `1440px`, tablet `768px` when layout changes, and mobile `390px`.
- Load completion report and any slow-element/blocker notes.
- DOM section inventory from top to bottom.
- Exact visible text.
- Computed styles for body, header/nav, footer, major sections, CTAs, cards, forms, and media containers.
- Font sources, font-family stacks, weights, line heights, and letter spacing.
- Color palette and background layers.
- Asset manifest covering images, background images, videos, SVGs, fonts, favicons, and CSS files.
- Stable static state for animated regions. Record what was frozen or replaced.

Use `references/source-of-truth-template.md` for the page record.

Detection gate: spawn a fresh detector agent with the Stage 1 extraction checklist. If text, CSS, screenshots, topology, or asset evidence is incomplete, fix extraction before proceeding.

### Stage 2: Asset Localization And Budgeting

Localize resources before implementation so builders never guess media.

1. Download reachable assets into `public/assets/<hostname>/`.
2. Preserve meaningful filenames where possible; otherwise create stable hashed names.
3. Rewrite project references to local paths.
4. Run:

```bash
node <skill-dir>/scripts/asset-budget-check.mjs --root "$PWD" --budget-mb 500
```

5. For any asset that is unavailable, blocked, or would push the total above 500 MB, create a documented placeholder. The placeholder must preserve aspect ratio, visible occupied area, dominant color, alt text, and source URL in metadata.

Detection gate: spawn a fresh detector agent with the Stage 2 asset checklist. Continue only if every source asset is either localized or explicitly represented by a placeholder.

### Stage 3: Component Architecture And Specs

Write specs before writing components.

Required component boundaries:

- `Header` or `SiteHeader`: all logo, nav links, nav CTAs, and mobile nav shell.
- `Footer` or `SiteFooter`: all footer link groups, legal text, newsletter/social regions.
- One component per visible page section under `src/components/sections/`.
- Shared primitives only when they remove real duplication, such as `Button`, `Logo`, or `ResponsiveImage`.

Use `references/component-spec-template.md` for each component. Specs must link back to the source of truth and screenshot evidence.

Run:

```bash
node <skill-dir>/scripts/check-component-boundaries.mjs --root "$PWD"
```

At Stage 3 this command is a planning check, so it may fail before component files exist. Save the output as the expected pre-implementation boundary baseline and add `docs/research/component-boundary-plan.json` listing the exact Header, Footer, and section component targets that Stage 4/5 must make real. The Stage 3 detector should verify the plan and specs, not require the implementation boundary check to pass yet.

Detection gate: spawn a fresh detector agent with the Stage 3 component/spec checklist. Do not implement sections whose specs are incomplete.

### Stage 4: Foundation And Tests

Create the failing checks before implementing the foundation:

- A build/type-check command.
- A component boundary check for header/footer independence.
- An asset budget/localization check.
- A page render or smoke test if the stack supports it.

Then implement:

- Font loading and metadata.
- Global CSS tokens for colors, spacing, typography, container widths, and responsive breakpoints.
- Local asset helpers or image components.
- Shared `Header` and `Footer` components.

Run all checks. The build can fail before implementation, but must pass before the Stage 4 detection gate.

Detection gate: spawn a fresh detector agent with the Stage 4 foundation checklist.

### Stage 5: Section Implementation Loop

For each section, proceed in top-to-bottom order:

1. Write or confirm the section spec.
2. Add or update a focused test/check for the expected text, assets, and component boundary.
3. Implement the section from the spec.
4. Run type/build/test checks.
5. Run a section screenshot comparison when tooling is available.
6. Spawn a fresh detector agent for that section's checklist.

If a section fails detection, repair that section before starting the next section. This keeps defects local and protects speed.

### Stage 6: Page Assembly

Wire the page together:

- Import `Header`, ordered section components, and `Footer`.
- Preserve top-to-bottom section order from the source of truth.
- Use local assets only.
- Render the semantic component tree visibly. Reference screenshots may be used only as QA inputs, not as CSS backgrounds, pseudo-element overlays, fixed image layers, or hidden-DOM screenshot shells in the delivered page.
- Remove animation libraries, timers, scroll-trigger code, and runtime-only effects unless the user specifically requested them.
- Keep normal links, forms, and simple CSS hover states when they are visible static page behavior.

Run build, tests, boundary checks, and asset checks.

Detection gate: spawn a fresh detector agent with the Stage 6 assembly checklist.

### Stage 7: Static Fidelity QA

Capture original and clone screenshots with the same viewport dimensions and animation-disabling CSS. Compare:

- Pixel diff by viewport and, when needed, by section.
- Geometry drift for section boundaries, headings, CTAs, cards, media boxes, header, and footer.
- Text completeness.
- Missing/broken/localized asset status.
- Header/footer reuse.
- Mobile layout.
- Delivered-page integrity: the clone must not use a full-page source screenshot/reference capture as the visible page. The real header, section components, and footer must be visible and inspectable.

Suggested acceptance thresholds:

- Static visual sections: `<1.0%` pixel mismatch.
- Text-heavy sections: `<2.0%` pixel mismatch.
- Geometry drift: `<=3px` for key landmarks.
- Broken localized asset references: `0`.
- Undocumented placeholder regions: `0`.
- Duplicated header/footer markup inside sections: `0`.
- Screenshot/reference overlay used as delivered page: `0`.

Save results under `docs/qa/<page-slug>/`.

Detection gate: spawn a fresh detector agent with the Stage 7 QA checklist. If it fails, repair from the source of truth/spec first, then code.

## Fresh Detector Agent Rule

At every gate, create a new detector agent whose only job is detection. Give it:

- The stage name.
- The relevant checklist from `references/stage-gates.md`.
- Paths to artifacts it must inspect.
- Commands it may run.
- A required report path under `docs/detection/<stage>/`.

Use the prompt templates in `references/detector-prompts.md`. The detector must not edit implementation files. It may only write its report. A stage passes only when the report says `Decision: PASS`.

In plans, artifact contracts, and completion reports, use the exact phrase `fresh detector agent` for this requirement. That phrase keeps the handoff unambiguous and prevents builders from turning the gate into self-review.

If a detector reports `FAIL`, do not argue with the report. Repair the missing evidence or implementation, then spawn another fresh detector.

## Static Replacement Policy

When the original page uses animation or large media:

- Prefer a real downloaded poster, first frame, thumbnail, or representative static image.
- If no representative asset is available within budget, create a placeholder with the same aspect ratio and visual weight.
- Record every placeholder in the source of truth:
  - source URL
  - reason (`over-budget`, `blocked`, `dynamic-only`, `unsupported`)
  - dimensions/aspect ratio
  - dominant color or gradient
  - alt text or visible label
  - section/component using it

Do not leave blank media boxes unless the original visually has blank space.

Static replacements are allowed only for bounded media regions that correspond to real images, videos, canvases, maps, or animation slots in the source. They must not replace the whole page, the entire viewport, or ordinary text/layout sections. A full-page screenshot can live under `docs/design-references/` or `docs/qa/`, but the delivered `index.html`/route must be assembled from real DOM, CSS, text, and localized assets.

## TDD Rhythm

For each stage:

1. Write the checklist and expected artifacts.
2. Add or select commands that can fail for the right reason.
3. Run them before or during implementation to expose gaps.
4. Implement the smallest change that satisfies the evidence.
5. Run the checks again.
6. Ask a fresh detector agent to certify.

This rhythm matters because clone work otherwise drifts into approximation.

## Completion Report

When finished, report:

- Target URL(s) and scope.
- Components created, especially header/footer.
- Number of sections cloned.
- Asset localization summary and total localized size.
- Placeholder summary, if any.
- Build/test command results.
- Detection reports for each stage.
- Final QA metrics and known limitations.

Do not call the clone complete without a passing Stage 7 detector report.

## Bundled References

Read only what the current stage needs:

- `references/stage-gates.md`: stage checklists and pass/fail criteria.
- `references/load-completion.md`: slow-page readiness criteria, lazy-load warming, and Scrapling fallback guidance.
- `references/source-of-truth-template.md`: canonical evidence record.
- `references/component-spec-template.md`: per-component build contract.
- `references/detector-prompts.md`: prompts for fresh detector agents.
- `references/static-clone-checklist.md`: final delivery checklist.

## Bundled Scripts

- `scripts/asset-budget-check.mjs`: totals localized assets and flags budget breaches.
- `scripts/check-component-boundaries.mjs`: checks for independent header/footer files and reports likely duplicated nav/footer markup.
- `scripts/validate-static-clone-artifacts.mjs`: checks stage artifact presence and unchecked checklist boxes.
- `scripts/wait-for-static-load.mjs`: Playwright helper that records multi-signal page readiness for slow pages.

# Stage Gates

Each stage needs a fresh detector agent. The detector reads the relevant checklist, inspects artifacts, runs allowed commands, and writes a report with exactly one decision line:

```text
Decision: PASS
```

or

```text
Decision: FAIL
```

No stage may proceed on a failing or missing detector report.

## Stage 0: Scope And Harness

Required artifacts:

- `docs/research/clone-run.md`
- Target URL(s) or local source path recorded
- Scope recorded: full page, selected section, or multi-page
- Project build/test/serve commands recorded
- Existing scaffold status recorded

Checklist:

- [ ] Target and scope are unambiguous.
- [ ] Output project root is known.
- [ ] Build/test/serve commands are listed, or absence is explained.
- [ ] Baseline build/test status is recorded.
- [ ] The next stage's source page can be reached or source files exist.

Pass only if all boxes are satisfied.

## Stage 1: Static Evidence Extraction

Required artifacts:

- `docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md`
- `docs/research/pages/<page-slug>/load-report.json`
- Desktop screenshot
- Mobile screenshot
- Tablet screenshot or documented reason it is unnecessary
- Asset manifest
- Section inventory

Checklist:

- [ ] Load-completion criteria are recorded before extraction.
- [ ] Load report passes or explicitly records unresolved blockers.
- [ ] Screenshots cover desktop and mobile viewports.
- [ ] Every visible section appears in top-to-bottom order.
- [ ] Header/nav and footer are separately identified.
- [ ] Visible text is copied verbatim.
- [ ] Key computed CSS values are recorded from the rendered page.
- [ ] Fonts, colors, spacing, and responsive breakpoints are recorded.
- [ ] Asset manifest includes images, backgrounds, video, SVG, fonts, favicons, and CSS.
- [ ] Animated/dynamic regions have a static replacement plan.
- [ ] Slow-loading/lazy elements are warmed, captured, or documented as placeholders/blockers.
- [ ] No section depends on guessed values.

## Stage 2: Asset Localization And Budgeting

Required artifacts:

- Localized asset folder under `public/assets/`
- Asset budget report
- Placeholder manifest when placeholders exist

Checklist:

- [ ] Reachable in-budget assets are downloaded locally.
- [ ] References use local paths or documented placeholders.
- [ ] Total localized asset size is at or below the configured budget.
- [ ] Over-budget or blocked assets have placeholders with aspect ratio, color, alt text, and original URL.
- [ ] No broken local asset paths are known.
- [ ] Favicons and fonts are handled or intentionally excluded with a reason.

## Stage 3: Component Architecture And Specs

Required artifacts:

- Component list in source of truth or `docs/research/component-plan.md`
- Specs under `docs/research/components/`
- Pre-implementation boundary check report
- `docs/research/component-boundary-plan.json`

Checklist:

- [ ] Header/navigation is planned as an independent component.
- [ ] Footer is planned as an independent component.
- [ ] Each visible page section maps to a component.
- [ ] Every component spec links to source evidence and screenshot references.
- [ ] Specs include exact text, assets, layout, CSS, and responsive behavior.
- [ ] Specs describe static replacements for animated or over-budget regions.
- [ ] No section spec duplicates header/footer markup.
- [ ] If the boundary check fails because files are not implemented yet, the failure is recorded as expected and the boundary plan lists the exact files Stage 4/5 must create.

## Stage 4: Foundation And Tests

Required artifacts:

- Build/type/test command results
- Header component file
- Footer component file
- Global styles/tokens
- Asset and component boundary check reports

Checklist:

- [ ] Build or type check passes.
- [ ] Asset budget check passes.
- [ ] Header component exists independently.
- [ ] Footer component exists independently.
- [ ] Global typography, colors, spacing, and breakpoints match evidence.
- [ ] The foundation avoids animation reconstruction code.
- [ ] Tests/checks were written or selected before implementation was accepted.

## Stage 5: Section Implementation

Run this gate per section.

Required artifacts:

- Section spec
- Section component file
- Test/build output
- Optional section screenshot/diff

Checklist:

- [ ] Section component follows its spec.
- [ ] Text is verbatim.
- [ ] Local assets or documented placeholders are used.
- [ ] Layout and responsive behavior match the evidence.
- [ ] Section does not duplicate header/footer.
- [ ] Type/build/test checks pass after the section is added.
- [ ] Static replacements are visually occupied and documented.

## Stage 6: Page Assembly

Required artifacts:

- Page/route file
- Build/test output
- Boundary and asset reports

Checklist:

- [ ] Page imports Header and Footer exactly through reusable components.
- [ ] Sections appear in the source-of-truth order.
- [ ] Page uses local assets only, except documented external links.
- [ ] No animation libraries or runtime motion code were added for static clone fidelity.
- [ ] Build/test checks pass.
- [ ] Desktop and mobile pages render without obvious overflow or missing sections.

## Stage 7: Static Fidelity QA

Required artifacts:

- Original and clone screenshots for matching viewports
- Pixel diff or human-review fallback report
- Geometry report or measured landmark table
- Broken asset report
- Final detector report

Checklist:

- [ ] Desktop visual comparison passes threshold or discrepancies are repaired.
- [ ] Mobile visual comparison passes threshold or discrepancies are repaired.
- [ ] Header/nav geometry and styling match.
- [ ] Footer geometry and styling match.
- [ ] Key landmarks drift no more than the configured tolerance.
- [ ] Broken localized assets: 0.
- [ ] Undocumented placeholders: 0.
- [ ] Header/footer duplicated inside sections: 0.
- [ ] Known limitations are evidence-backed, not excuses for skipped work.

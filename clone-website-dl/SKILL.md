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
- Every structural element (section, div, heading, img, link, input, button) has a unique `id` attribute using the pattern `page-element-purpose` (e.g. `promote-hero-title`, `footer-col-sell`). IDs must be added during the build phase, not as an afterthought.
- Every section uses consistent vertical padding: `py-[80px]` or `py-[88px]` — never `pb-0` or `pt-0` without a deliberate layout reason documented in the source of truth.

## Common Antipatterns

| Antipattern | Better route |
|---|---|
| Coding before evidence is complete | Return to `clone-website-extract-dl` |
| Implementing directly from a screenshot | Extract DOM, computed CSS, assets, spacing, and states |
| Putting business logic in this orchestrator | Move it into the owning atomic skill |
| Splitting every small command into a skill | Keep helpers bundled with their stable capability |
| Patching a structural layout mismatch | Rebuild from the corrected source record and spec |
| Calling a clone "done" by visual impression alone | Require `clone-website-qa-dl` convergence reports |

## Field Notes

Every clone session reveals patterns. These notes are the single source of truth
for pitfalls, edge cases, and proven fixes. Companion skills delegate to this
section — do not duplicate Field Notes across skills.

### Extraction Phase

- **GWT / JS-heavy app extraction:** Pages built with GWT or heavy JS frameworks
  render UI entirely via client-side JavaScript into auto-generated DOM (opaque
  class names, deeply nested divs). Extract only visible text via `body.innerText`,
  visual layout via screenshots, and computed CSS of key elements. Clone is a
  visual re-creation, not a structural port. Document as "JS-rendered — visual
  clone only" in source of truth.

- **Mobile screenshot lazy-load trap:** Automated screenshots capture the
  mobile viewport BEFORE lazy images resolve. Fix: after automated script,
  re-capture with slow scroll (~200px steps, 200-500ms waits) to trigger
  intersection observers. Then back to top, wait 2s, take full-page screenshot.

- **Force-load unresolved lazy images:** When `loaded < total`, run in
  `page.evaluate()`: iterate `img[data-src]` and `img[data-lazy]`, set their
  `src` from the data attribute. Wait 2-3s. Remaining failures are typically
  hidden-viewport variants, empty carousel slots, or tracking pixels.

- **Cloudflare email obfuscation (data-cfemail):** The raw HTML contains
  obfuscated email text in `data-cfemail` attributes or `__cf_email__` spans.
  The real addresses appear only after `email-decode.min.js` runs in the browser.
  Always extract emails from rendered DOM (`textContent` after JS execution),
  never from raw HTML source.

- **Non-breaking space (`&nbsp;`) extraction trap:** Original pages use `&nbsp;`
  between CJK/Latin words. Browser `innerText` collapses `&nbsp;` to a regular
  space. When extracting headings, cross-check against `innerHTML` or
  `textContent` (not `innerText`). In JSX, render as `{'\u00A0'}` or `&nbsp;`.

- **Cross-origin CSS CORS trap:** Stylesheets from CDNs or different origins
  block `document.styleSheets[i].cssRules` (returns null). Skip stylesheet-rule
  iteration. Use `getComputedStyle()` on specific target elements via
  `page.evaluate()` instead.

- **Nav-detection trap (no `<nav>`):** Not all sites use a `<nav>` element.
  Some use `<div>` with header/nav classes. Probe for sticky/fixed elements at
  `top:0` with `getComputedStyle(el).position` and `el.querySelectorAll('a').length > 2`.

- **`page.evaluate()` gotcha — `forEach` + `break`:** `SyntaxError: Illegal break
  statement` occurs when using `Array.forEach()` with a `break` inside
  `page.evaluate()`. Use `for (let i = 0; i < arr.length; i++)` instead.

- **CSS-illustrated content trap (SVG / div mockups):** Marketing pages render
  visual content through inline SVGs and CSS-styled divs, not `<img>` tags.
  After image extraction, scan for large inline SVGs (`getBoundingClientRect`
  width/height > 80px) and visual divs (background-image, no inner text).
  Record each in source of truth or the clone will have blank sections.

- **Logo strips outside `.container` (Ecwid pattern):** Payment and carrier
  logo strips are siblings of `.container`, not children. Query
  `.hpc-logos--pyments, .hpc-logos--shippings` separately. Record as section-level
  children with their own HTML and computed styles.

- **CDN-blocked image extraction:** CDNs (CloudFront, Akamai) return 403 for
  direct downloads. Workflow: (1) try browser `User-Agent` header, (2) try
  alternative path variants, (3) use Playwright element screenshot
  (`page.locator('img[src*="filename"]').first.screenshot(path=path)`).
  **SVG pitfall:** `.screenshot()` throws `Unsupported screenshot mime type:
  image/svg+xml` for SVG images. Use inline SVG approximations instead.

### Build Phase

- **CSS rule invented, not extracted:** Every CSS rule in the clone must trace
  back to original evidence (getComputedStyle or stylesheets). If a rule has no
  origin in the original, remove it and re-extract.

- **Text content fidelity:** Never guess text. Extract ALL verbatim content —
  headings, numbers, labels, CTAs. Cross-check numbers, units, and labels
  against the original screenshot. The GlobalStats section on Ecwid's sell page
  has "70+ / 40+ 支付网关 / 175 国家/地区 / 50 语言" — not "1,500,000+ 商家".

- **Section vertical rhythm:** Every section must have explicit top AND bottom
  padding (`py-[80px]` or `py-[88px]`). Adjacent sections touching (pb-0 + pt-0)
  create zero breathing room. Logo strips in shaded backgrounds need their own
  `py-6` internally, AND the parent section needs `pb-[88px]`.

- **Column gap in split layouts:** Side-by-side text + image columns need
  explicit gap. `w-1/2` columns leave 0px between them by default. Add
  `lg:gap-12` or `lg:gap-8` to the flex row. For device mockups, use
  `lg:w-5/12` for image column, `lg:flex-1` for text column.

- **Absolutely-positioned image sizing:** Device mockup images (tablet + phone)
  must fit within their column after negative offset. Convention: tablet
  `max-w-[420px]`, phone `max-w-[160px]`. Do not default to 580px tablet images.

- **Element ID pattern:** Every structural element needs a unique `id`:
  `page-element-purpose` (lowercase, hyphen-separated). Add during component
  creation, not retroactively. Examples: `promote-hero-title`,
  `manage-bottom-cta-btn`, `footer-col-sell`.

- **Optimize shared components early:** Polish Header, Footer, and layout
  BEFORE building page sections. A bad header makes every page look wrong.
  Add sticky scroll behavior, responsive menu with proper z-index, and match
  original header height exactly.

- **Stale production server:** If CSS returns 500 after rebuild, kill server,
  `rm -rf .next`, `npm run build`, restart. Always verify CSS 200 before QA.

### QA Phase

- **Animation-heavy pages:** QA failures cluster around lazy-loaded media and
  scroll-triggered visibility BEFORE they cluster around CSS. Treat QA as an
  evidence engine: geometry deltas reveal the exact section where cumulative
  spacing drift starts.

- **Fix DOM contract first, then patch spacing:** When a clone is visually
  close but geometry is off, correct the DOM structure before adjusting CSS.
  This reduces noisy `missing` and `svg` mismatch reports.

- **Next.js font fallback — expected CSS diff:** Next.js inserts a
  `"<FontName> Fallback"` entry in computed `fontFamily`. This is expected
  behavior — do not count against CSS match score.

- **Text fidelity in QA — `&nbsp;`:** `innerText` collapses `&nbsp;` to
  regular space. Cross-check against `textContent` or `innerHTML` for CJK
  sections during QA comparison.

- **Stat / number font-size verification:** Stat numbers often use heroic
  sizing (206px) — never guess. Always extract via `getComputedStyle(element).fontSize`
  from the original. Even a reasonable-looking 56px is only ~25% of intended size.

- **Column layout gap check:** Bootstrap columns have no inherent gap (0px).
  Tailwind `w-6/12` halves also touch by default. Add `lg:gap-12` to the flex
  row AND reduce image `max-w` so oversized images don't overflow their column.

- **When pixel diff > threshold but CSS values match:** High pixel diff
  (40-50%+) with 95%+ CSS match comes from structural differences, not CSS
  inaccuracy. Diagnose by source: scope omission, grid system difference,
  page height mismatch, animation/JS behavior, or actual CSS mismatch.

- **Report two pixel-diff numbers:** (1) Raw full-page, (2) Overlapping
  (crop to min height). The overlapping number is the engineering-relevant
  metric. Gate passes for structural diffs when CSS >=95%, overlapping diff
  under threshold, and all omissions documented.

- **ImageMagick command name:** `visual-diff.mjs` uses `magick` (v7). On
  systems with only `convert` (v6), symlink `magick→convert`.

## User Preference: Action-First Mode

This session's user demonstrated a strong **action-first** preference: after
providing the target URL and confirming broad scope, they expected immediate
progress through extraction → build → QA → delivery without intermediate
confirmation stops. Signals included "直接开始构建" and "done? where's the
clip image?" when blocked at the evidence-review gate.

**Apply this heuristic for action-first users:**
- Skip the Step 2 STOP gate when the user has already reviewed comparable
  screenshots from a prior page in the same session and the current page shares
  the same visual system (same font, colors, header/footer pattern).
- Instead, go directly: extract → write source of truth → build → QA.
- If extraction reveals a fundamentally different layout pattern from prior
  pages, do a brief inline summary (1-2 lines) and ask "proceed?" but frame it
  as a confirmation, not a full review gate.
- For new users or first-run clones, always keep the STOP gate active.

## Self-Test

Run:

```bash
bash evals/test-split-skills.sh
python3 evals/run_harness.py SKILL.md
```

The split-skills test validates companion contracts, resource ownership, thin
orchestration, and the existing regression harness.

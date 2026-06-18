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

> **Field Notes:** For common build pitfalls and proven fixes, see
> clone-website-dl's consolidated Field Notes section (CSS rule origins, text
> fidelity, section vertical rhythm, column gaps, image sizing, element IDs,
> shared component polish, stale server traps).

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
| Production build passes but CSS/static assets return 500 when served (Next.js `.next/` cache stale) | Delete `.next/` and run clean build (`rm -rf .next && npm run build`), then restart production server | Stale cached build artifacts cause CSS hash mismatch between server and on-disk files — fresh rebuild resolves |
| Build passes but page metadata (title/description) unchanged when served | Run a fresh `npm run build` for statically exported pages — metadata is baked into the static HTML at build time, so editing `export const metadata` after a build requires a rebuild to take effect | For incremental metadata changes, restart the dev server instead (no `.next/` wipe needed) |
| Builder paraphrases content | Restore verbatim source text | Add exact text to the spec |
| Structural pattern mismatch | Correct evidence and rebuild the section | Implement directly from the corrected spec |
| Missing media | Return to asset evidence | Implement only the documented booth fallback |
| **CDN 403 blocking asset download** | Try browser User-Agent; use alternative variant (e.g. mobile-sized image); check data-src/data-lazy for alternate URL | Record substitution as booth fallback in source of truth |
| **CSS rule invented, not extracted** | Remove the rule that has no corresponding selector in the original's stylesheets or getComputedStyle evidence | Re-verify every CSS rule against the source of truth; if one has no origin in the original, it is wrong |

### 8. Verify section spacing after adding content

After adding logo strips, illustrations, or any element outside the container div, verify the visual gap between the current section and the next:

1. Check computed `paddingBottom` of the current section and `paddingTop` of the next section.
2. Adjacent sections with `pt-0`/`pb-0` (using `--t0`/`--b0` classes) butt against each other — add `pb-[88px]` to the section containing the external element to restore breathing room.
3. Logo strips with a shaded background must have `py-6` or similar padding internally, AND the parent section needs its own bottom padding (`pb-[88px]`) so the next section doesn't feel cramped.
4. Measure with Playwright: `getBoundingClientRect().bottom` of section A vs `top` of section B — aim for ≥88px visual gap.

**Ecwid-specific:** The payments section's logo strip is the most common spacing offender — always add `pb-[88px]` to the payments section.

### 9. Add element IDs for editability

After all sections are implemented and the build passes, add unique `id` attributes to every structural element. This lets the user reference any element by ID for styling or content changes.

**Naming convention:** `page-element-purpose` — lowercase, hyphenated, semantic:

* `<section id="promote-hero">`, `<div id="google-ads-text">`, `<h1 id="manage-hero-title">`
* `<img id="promote-hero-cta">`, `<input id="register-input-email">`, `<a id="header-nav-X">`

**Coverage:** every `<section>`, `<main>`, `<div>`, `<h1>`-`<h3>`, `<img>`, `<a>` (CTAs/nav), `<input>`, `<button>` gets a unique `id`. Loop-rendered items append the index/key (e.g. `tile-${id}-p-${i+1}`).

Shared components use `header-*` / `footer-*` prefixes. Page sections use `{page}-{section}-{element}`.

See `references/ecwid-design-tokens.md` for brand colors, typography, button styles, hero patterns, and asset download workarounds discovered during active sessions.

### 9. Optimize shared components (post-build polish)

After all pages compile, review Header, Footer, and layout:

1. **Scroll behavior:** Add `useEffect` for sticky header bg transition (transparent to white+shadow).
2. **Responsive menu:** Full-screen centered mobile overlay with proper z-index.
3. **Spacing:** Match original header height (e.g. 80px), nav gap, button padding.
4. **Cross-route consistency:** Header/Footer render identically on every page.

Polish shared components early — a bad header makes every page look wrong.

### 10. Fresh build before QA

After build, restart the production server — the old process serves stale CSS:

```bash
kill $(lsof -ti :3459) 2>/dev/null
npx next start -p 3459 &
```

Verify CSS before QA:

```bash
CSS_URL=$(curl -s $CLONE_URL | grep -o '/_next/static/chunks/[^"]*\\.css' | head -1)
curl -sL -w "%{http_code}" "$CLONE_URL$CSS_URL" | grep -q 200 || echo "STALE BUILD"
```

## Antipatterns

| Antipattern | Better route |
|---|---|
| Adding CSS selectors not in the original | Every rule must trace back to original evidence. If no origin found, re-extract. |
| CDN 403 blocking asset downloads | Try browser UA; use accessible variant; check data-src/data-lazy. Verify download >1KB, not XML error body. |
| Copying emails from Cloudflare-obfuscated HTML | `data-cfemail` / `__cf_email__` obfuscation means raw-HTML emails are wrong. Use rendered textContent. |
| **Building all pages before polishing shared components** | Polish Header/Footer early — they appear on every page. A bad header makes everything look "very ugly." |
| **Skipping element IDs** | Without IDs, users can't target elements without reading component source. Add IDs during build, not as a separate pass. |
| **Production server serves stale CSS after rebuild** | Always restart the production server after build. Kill old process, start fresh — reuse causes 404/500 CSS. |

## Verification

Hand off to `clone-website-qa-dl` only when:

- Every implemented component has a traceable spec.
- The page record remains current.
- Type checks pass.
- The production build passes.
- Partial clones render independently.

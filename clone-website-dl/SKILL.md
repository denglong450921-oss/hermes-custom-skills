---
name: clone-website-dl
description: Reverse-engineer and rebuild websites, pages, or individual sections with high visual fidelity by extracting real assets, computed CSS, content, responsive behavior, and interactions before implementation. Use this whenever the user asks to clone, replicate, recreate, copy, reverse-engineer, or rebuild a website from one or more URLs, including partial requests such as "clone just the hero", customized clones such as "copy this site but use our brand colors", and phrases like "make a copy of this site", "rebuild this page", or "pixel-perfect clone".
metadata:
  argument-hint: "<url1> [<url2> ...]"
  hermes:
    user-invocable: true
---

# Clone Website

You are about to reverse-engineer and rebuild **$ARGUMENTS** as pixel-perfect clones.

When multiple URLs are provided, process them independently and in parallel where possible, keeping each site's extraction artifacts isolated in dedicated folders (`docs/research/<hostname>/`).

This is not a two-phase process (inspect then build). You are a **foreman walking the job site** — as you inspect each page, you assemble its page-level source of truth, then derive section specs and hand them to specialist builder agents. Extraction and construction may overlap across pages, but coding for a page cannot start until that page's source of truth is complete.

## Scope Defaults

Clone exactly what's visible at the URL. Unless the user specifies otherwise:

- **Fidelity:** Pixel-perfect — exact match in colors, spacing, typography, animations
- **In scope:** Visual layout, component structure, interactions, responsive design, mock data
- **Out of scope:** Real backend, auth, real-time features, SEO, accessibility audit
- **Customization:** None — pure emulation

If the user provides additional instructions, honor those over defaults.

## Pre-Flight

### Mode Selection

Check which extraction capabilities are available. Tool names vary across runtimes, so route by capability first and use the named tools below as examples.

**Resolve bundled resources first.** Treat the directory containing this `SKILL.md` as `CLONE_SKILL_DIR`. Do not assume a runtime-specific home-directory install path. If the runtime does not expose the skill directory, locate it once:
```bash
CLONE_SKILL_DIR=$(find "$HOME" -path '*/clone-website-dl/SKILL.md' -print -quit | xargs dirname)
test -n "$CLONE_SKILL_DIR" || { echo "clone-website-dl skill directory not found"; exit 1; }
bash "$CLONE_SKILL_DIR/scripts/preflight-audit.sh" "$URL"
```
The preflight audit detects SPA status, third-party embeds, cookie banners, hashed CSS, lazy images, and more — covering all 8 real-world edge cases discovered during 150-site empirical testing.

| Capability | Example availability check | Best for |
|------|--------|----------|
| **Interactive browser automation** | Use any available browser MCP or browser-control tool; Camofox health check: `curl -fsS http://localhost:9377/health` | Full precision extraction with `getComputedStyle()` + interaction sweep |
| **Headless browser scripting** | Check `python3 -c "import playwright"` | Full CSS precision via `page.evaluate(getComputedStyle)`, JS rendering, design token extraction — best all-round fallback when interactive browser automation is unavailable |
| **HTML/content extraction** | Use any available scrape MCP, Firecrawl MCP, or `curl` | Layout + content only when no rendered-browser capability is available |

**Interactive browser automation available (preferred):** Run the full 5-phase pipeline below.
**Headless browser scripting available:** Use the Playwright extraction pattern in `references/playwright-extraction.md`. CSS values are pixel-accurate (`getComputedStyle` via `page.evaluate`). Add manual click/hover calls for multi-state extraction.
**HTML/content extraction only:** Use the Firecrawl/curl adaptation in `references/firecrawl-mode.md`. CSS values will be approximate — only for HTML-rendered sites (no SPAs).
**SPA detection:** Before choosing mode, check if the site is JS-rendered:
```bash
# Quick SPA check: fetch head bytes, count body content vs script tags
HTML=$(curl -sL --max-time 5 "$URL" 2>/dev/null)
BODY_CHARS=$(printf '%s' "$HTML" | grep -Eo '>[^<]{100,}' | wc -l | tr -d ' ')
SCRIPT_COUNT=$(printf '%s' "$HTML" | grep -Eo '<script[^>]*src=' | wc -l | tr -d ' ')
if [ "$BODY_CHARS" -lt 3 ] && [ "$SCRIPT_COUNT" -gt 5 ]; then
  echo "SPA detected ($SCRIPT_COUNT bundles, $BODY_CHARS content blocks)"
  echo "→ Use Camofox or Playwright for full rendering"
fi
```
- **HTML-only (curl) works:** HTML has body content (Notion, GitHub, Next.js sites). Use Firecrawl mode.
- **SPA detected (minimal HTML, many JS):** Must use interactive browser automation or headless browser scripting for extraction. Curl won't work.
- **Rendered browser + HTML extraction both available:** Use the browser for content/styles/interactions and curl for asset discovery.

### Pre-Flight Failure Routing

| Trigger condition | First-line fix | If it still fails |
|---|---|---|
| `CLONE_SKILL_DIR` is empty | Locate the current `SKILL.md` through the runtime's loaded-skill metadata | Ask the user for the installed skill path; do not guess a runtime-specific directory |
| Preflight script is missing or not executable | Confirm `$CLONE_SKILL_DIR/scripts/preflight-audit.sh` exists; invoke it with `bash` | Continue with the inline SPA check and record `preflight script unavailable` in `docs/research/BEHAVIORS.md` |
| Interactive browser automation is unavailable | Check for Playwright with `python3 -c "import playwright"` | Use HTML/content extraction only for SSR/static pages; stop on SPAs |
| Target blocks automated navigation | Check accessibility with `curl -sIL --max-time 8 "$URL"` | Ask the user for an accessible URL, VPN/proxy access, or screenshots/assets |

### Setup

1. Parse `$ARGUMENTS` as one or more URLs. Validate each URL.
2. Verify the base project scaffold (Next.js + shadcn/ui + Tailwind v4) builds: `npm run build`
3. Create output directories: `docs/research/`, `docs/research/components/`, `docs/design-references/`, `scripts/`
4. **Clean stale files** from previous clones:
   - **Single-target re-clone:** Remove old component files (`Hero.tsx`, `CTA.tsx`, etc.), keep only shared infrastructure (`lib/utils.ts`, `components/ui/`, `icons.tsx`)
   - **Multi-page / additive clone (different URLs, same project):** Do NOT clean components — other pages depend on them. Only clean `docs/research/` artifacts and spec files.
   - See `references/pitfalls.md` → "Multi-Page Stale File Cleanup Nuance"

## Common Antipatterns → see `references/antipatterns.md`

## Architecture: Agent Pipeline

> Inspired by Understand-Anything's multi-agent pipeline — each stage is a specialized agent that hands off to the next.

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐
│ Extraction Agent │───▶│   Spec Agent     │───▶│  Builder Agents  │───▶│   QA Agent    │
│ (Camofox/Firecrawl)│  │ (writes .spec.md)│    │ (parallel × N)   │    │ (visual diff) │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └───────────────┘
         │                      │                       │                      │
         ▼                      ▼                       ▼                      ▼
  docs/research/         docs/research/           src/components/        docs/qa/
  PAGE_TOPOLOGY.md       components/*.spec.md     *.tsx                  diff.png
```

**Your role:** Orchestrator. You run Extraction Agent yourself, hand specs to Builder Agents when delegation is available, verify their output, integrate changes, then run QA.

### Execution Strategy

- If parallel subagents and isolated worktrees are available, dispatch builders by component and integrate their changes as they finish.
- If subagents are unavailable, build the same specs sequentially yourself. Do not skip extraction, specs, or QA.
- If the project is not a Git repository, write directly into the project and verify after each component. Do not attempt worktree commands.

## Guiding Principles

These are the truths that separate a successful clone from a "close enough" mess. Internalize them.

### 1. Completeness Beats Speed
Every builder receives **everything** it needs: screenshot, exact CSS values, downloaded assets, real text, component structure.
⚠️ Never dispatch a builder without a spec file. Never reference docs from builder prompts — inline every value.

### 2. Small Tasks, Perfect Results
One agent per distinct design pattern. If a builder prompt exceeds ~150 lines of spec content, split it.
⚠️ Never bundle unrelated sections (CTA + footer) into one agent.

### 3. Real Content, Real Assets
Extract actual text, images, SVGs from the live site. Download every `<img>`. Extract inline `<svg>` as React components.
⚠️ Check for `<video>`, Lottie, or canvas before building HTML mockups. Missing assets make the clone look fake.

### 3A. Never Leave an Unexplained Visual Hole
If the original page exposes an image, video, illustration, or layered composition and the asset is reachable, render it. Do not hide available media with `display: none`, `visibility: hidden`, `opacity: 0`, off-screen placement, or an oversized empty wrapper.

If the original media is genuinely unavailable after extraction and fallback attempts, build a deliberate booth layout: a styled placeholder composition that preserves the section's occupied area, hierarchy, color, and visual balance. Record the substitution in the page source of truth. A booth is an explicit fidelity fallback, not an excuse to skip extraction.

During visual QA, treat unexplained blank regions as failures. Compare each large empty area with the original screenshot and prove it is intentional. If it is not intentional, restore the source media or add the documented booth layout.

### 4. Foundation First
Global CSS with design tokens, TypeScript types, global assets — this is sequential, non-negotiable. Everything after is parallel.

### 5. Extract How It Looks AND How It Behaves
A website is not a screenshot — elements move, change, appear, disappear. Use `getComputedStyle()` for exact values. Document triggers, before/after states, and transitions.
⚠️ Never approximate CSS values. Always use `getComputedStyle()`.

See references/extraction-scripts.md for the per-component extraction script.

### 6. Identify the Interaction Model Before Building
The single most expensive mistake: building click-based UI when the original is scroll-driven.
1. Scroll first — observe what changes
2. Then click/hover to test for click-driven interactivity
3. Document explicitly: "INTERACTION MODEL: scroll-driven" or "click-driven"

⚠️ Don't build click-based tabs when original is scroll-driven — requires complete rewrite.

### 7. Extract Every State, Not Just the Default
Click each tab, scroll past each threshold, hover over each element. Capture ALL states.
⚠️ Missing a state means rebuilding the component later.

### 8. Page Source of Truth Controls Fidelity
Every page gets one canonical `docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md` BEFORE coding starts. Every component then gets a `.spec.md` file derived from it BEFORE any builder is dispatched. The page source of truth controls fidelity; the component spec is the implementation handoff.
See `references/spec-template.md` for the full template.

### 9. Build Must Always Compile
Every builder verifies `npx tsc --noEmit` before finishing. After merging, verify `npm run build`.

### 10. One Canonical Record Per Page
Create each page record with `references/page-source-of-truth-template.md`. It is the unique authority for screenshots, section order, dimensions, computed CSS, exact text, assets, responsive states, interactions, and known constraints.

Do not code a page while its record has blanks, guesses, or unresolved conflicts. If later extraction contradicts it, update the source of truth first, then update derived specs and code. This prevents implementation from drifting into a second, unofficial interpretation of the live page.

## Phase 1: Reconnaissance (Extraction Agent)

You run this phase yourself.

### Determine Scope
- **Full clone:** Run all 5 phases. Default.
- **Partial clone:** "Clone just the hero/pricing/footer" — scope extraction to named sections
- **Multi-page:** Run Phase 1 for each URL, share Phase 2 foundation across all pages

  **⚠️ Sub-page extraction depth trap:** The first (home) page usually gets thorough extraction — screenshots, section HTML, design tokens, interaction sweep. Sub-pages (e.g. `/sell`, `/pricing`, `/about`) often get skimped: just a text dump and a single screenshot. This is the #1 cause of "the sub-page doesn't look like the original".
  
  **Each sub-page needs the same extraction depth as the main page:**
  - Take desktop AND mobile full-page screenshots
  - Save `section.outerHTML` for every section (text-only extraction misses layout patterns like sticky-scroll, parallax, alternating rows)
  - Extract the layout pattern per section (step 12 below) — do not pass text content alone to a builder
  - Save all headings verbatim — the first text-extraction pass often truncates or misreads Chinese/Japanese/Korean headings
  - Document alternating layout direction between adjacent sections (many sites use zigzag: section 1 text-left, section 2 text-right, section 3 text-left...)
  
  **Verify extraction quality before dispatching any sub-page builder:** read the saved `.html` or `.json` files for one section and confirm the heading text matches the live site screenshot. If you can't explain the section's layout pattern in one sentence ("sticky scroll, image left, ~800px"), you haven't extracted enough.

  **Per-page source-of-truth gate:** Finish `docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md` for each URL independently. A complete homepage record does not authorize coding a subpage.

- **Clone with customizations:** "Clone [URL] but change X to Y" — extract originals, apply overrides (see `references/customization.md`)

**🛑 STOP:** If unsure about scope, ask user before proceeding.

### Partial Clone Mode

When the user says "clone just the hero/pricing/footer/section-name" without specifying a full-page clone:

**Use this condensed path:** identify section → capture desktop and mobile section screenshots → show the screenshots to the user → extract section CSS, content, assets, responsive behavior, and interactions → build the shared foundation → write one component spec → implement the standalone component → run visual QA against the standalone render → deliver the component.

1. **Identify the section** — by semantic role:
   - Hero = first major section after header (full-width with heading + CTA)
   - Pricing = section containing price cards/tables
   - Footer = bottom section with links/branding
   - If ambiguous, ask: "Describe the section or share a screenshot."
2. **Scaffold requirement** — `npm run build` must still pass, but skip:
   - Full page topology (`PAGE_TOPOLOGY.md` not needed)
   - Phase 4 page assembly
3. **Extraction scope:**
   - Phase 1: only the target section + header area (for visual context)
   - Phase 2: **run fully** (fonts, globals.css, icons, types, assets — components depend on them)
   - Phase 3: only the target component spec + builder dispatch
4. **Output:** `src/components/<SectionName>.tsx` only (not `src/app/page.tsx`)
5. **The component must be independently testable** — accept props with defaults

**🛑 STOP:** If the section has scroll-driven animations that depend on page-level scroll (IntersectionObserver, viewport triggers), flag: "This section has scroll-driven animations. A standalone component won't animate until assembled into a full page. Continue with standalone or create a minimal wrapper?"

### Customization Mode

When the user says "clone [URL] but change X to Y" — apply customizations while keeping the rest pixel-perfect:

1. **Identify what's changing:** Color? Typography? Layout? Content? Section order?
   - **Color:** Use the CSS variable override pattern in `references/customization.md`
     - If the target uses CSS variables (`--color-*`, `--primary`, etc.): create override block in globals.css
     - If the target uses hardcoded hex colors (no CSS variable system): do a global find-and-replace of the original hex with the new one. Use `grep -rn '#FF5733' src/ --include='*.tsx' --include='*.css'` to find all occurrences. Replace with `var(--color-primary)` and define `--color-primary: #3B82F6` in globals.css. This handles inline styles, Tailwind arbitrary values, and SVG fills.
     - **Gradient handling:** If the original color appears in gradients, replace the specific color stop, not the entire gradient. CSS variable overrides work inside gradients natively.
     - **Dark mode:** If the target has `.dark` or `[data-theme="dark"]` rules, apply the color change in BOTH the light (`:root`) and dark (`.dark`) blocks. Search for the original color in both contexts.
   - **Typography:** Update the chosen font integration (`<link>`, self-hosted file, or `next/font`) and adjust `font-family` in globals.css. Font size/spacing may shift — check at both desktop and mobile.
   - **Layout:** Document changes in each spec file's "Implementation Notes." If changing from single-column to grid, update the container's `gridTemplateColumns`.
   - **Content substitution:** Put original content in comments (`{/* Original: "..." */}`), replace with user's content. Match character counts where possible to preserve layout.
   - **Section reordering:** Update `PAGE_TOPOLOGY.md` first, then reorder imports in `page.tsx`.
2. **Extract originals first** — always capture original values before overriding. The spec file documents both: "Original: #FF5733 → Custom: #3B82F6."
3. **Override strategy:** Use CSS variables for colors/fonts. Modify component code for layout. Use prop defaults with new text for content.
4. **Verification:** Re-run Visual QA after customizations. Compare clone vs original — only customized elements should differ. Everything else must match pixel-perfect.

**🛑 STOP:** If layout changes affect responsive behavior (e.g., single column → multi-column), flag: "Layout changes affect mobile/tablet breakpoints. Manual adjustment may be needed. Proceed?"

### Screenshots
- **Full clone:** Take **full-page screenshots** at desktop (1440px) and mobile (390px) viewports
- **Partial clone:** Screenshot **only the target section** at both viewports. Include enough adjacent header/nav context to identify the section without turning the capture into a full-page screenshot.
- Save to `docs/design-references/` with descriptive names

**🔴 CHECKPOINT (partial mode):** After screenshot, attach or render the saved screenshot using the current platform's supported image-display mechanism. Confirm: "Does this look like the right section? (y/n)" — if no, ask user to describe or share a screenshot.
- If Camofox unavailable, use Playwright screenshot.py

### Global Extraction
- **Fonts:** Inspect `<link>` tags, self-hosted files, and computed `font-family`. Choose the reliable integration strategy in Phase 2.
- **Colors:** Extract palette from computed styles. Map to shadcn CSS variables in globals.css
- **Favicons & Meta:** Download to `public/seo/`, update `layout.tsx` metadata
  - **Viewport meta:** If HTML lacks `<meta name="viewport">`, the site may set it via JS. Still add `<meta name="viewport" content="width=device-width, initial-scale=1">` to clone layout.tsx — safe default for any site.
- **Resource hints:** Scan for `<link rel="preconnect">`, `<link rel="preload">`, `<link rel="dns-prefetch">`. In the clone: keep first-party ones, remove third-party trackers, and preserve only the hints required by the chosen font integration.
- **Global UI patterns:** Custom scrollbar, scroll-snap, keyframe animations, smooth scroll libraries (Lenis, Locomotive Scroll)

### Mandatory Interaction Sweep
**Full clone:** Complete **Scroll sweep** → **Click sweep** → **Hover sweep** → **Responsive sweep** (1440px / 768px / 390px). Save all findings to `docs/research/BEHAVIORS.md`.
**Partial clone:** Sweep only the target section + adjacent header. Check desktop (1440px) and mobile (390px); add tablet (768px) when the layout changes between them. Save to `docs/research/BEHAVIORS.md` (still useful for component-level behaviors).
**Animation library detection:** Check for GSAP, Framer Motion, Lottie, Three.js, AOS (scan HTML for library-specific patterns: `data-aos`, `gsap`, `framer-motion`, `lottie`). If detected:
- Run `scripts/audit-animations.mjs` before injecting animation-disabling CSS or taking deterministic reference screenshots. Follow `references/animation-reconstruction.md`.
- Record triggers, timeline values, start/mid/end styles, responsive differences, and reduced-motion behavior in `BEHAVIORS.md` and the page source of truth.
- Reproduce behavior with the simplest faithful mechanism: CSS transitions, `IntersectionObserver`, scroll progress, explicit React state, or the reachable media player. Do not default every animated region to a static block.
- For Three.js / Canvas content: take a screenshot and use as a static image placeholder

### Page Topology
Map every section from top to bottom. Document visual order, sticky overlays, scroll container, column structure, z-index layers, interaction model per section. Save as `docs/research/PAGE_TOPOLOGY.md`.

### Per-Page Source of Truth
For every URL, consolidate the extracted evidence into `docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md`. Use `references/page-source-of-truth-template.md` and complete its readiness checklist. Link raw screenshots, section HTML/JSON, and asset manifests instead of leaving evidence implicit.

**🔴 CHECKPOINT (source-of-truth gate):** Before writing page or component code for a URL, verify its `SOURCE_OF_TRUTH.md` is complete: no placeholders, no guessed CSS values, exact text captured, desktop/mobile screenshots linked, every section mapped, assets resolved, and interactions documented. If the gate fails, continue extraction. Do not code yet.

**🔴 CHECKPOINT (visual occupancy gate):** For every section, confirm reachable source media is rendered and visually occupies the expected region. If a source asset is unavailable, the source of truth must name the booth fallback. Do not accept unexplained blank space.

**🔴 CHECKPOINT:** For a full clone, review the per-page `SOURCE_OF_TRUTH.md`, `PAGE_TOPOLOGY.md`, and `BEHAVIORS.md` with the user: "Ready to build foundation?" For a partial clone, review the target screenshots, focused `SOURCE_OF_TRUTH.md`, and `BEHAVIORS.md`; `PAGE_TOPOLOGY.md` is intentionally skipped.

## Phase 2: Foundation Build

Sequential. Do it yourself — it touches many files:

1. **Update fonts** in layout.tsx
   - Check if the site uses `next/font` (look for `__<font>_<hash>` class names in the HTML), Google Fonts `<link>` tags, self-hosted fonts, or a system stack.
   - Prefer self-hosted font files when the target exposes them. They preserve fidelity without build-time network access.
   - For Google Fonts, prefer a `<link>` tag in `<head>` plus a CSS font stack because restricted build environments can make `next/font/google` fail. Use `next/font/google` only when the build environment can fetch font files reliably.
   - Mirror the target's `font-display` strategy. `swap` is the safe default for demo clones.
2. **Update globals.css** with the target's color tokens, spacing values, keyframe animations, utility classes, and any **global scroll behaviors** (Lenis, smooth scroll CSS, scroll-snap on body)
   - **Google Font choice:** See `references/pitfalls.md` → "Google Fonts + Turbopack Build Failure" for the reliable `<link>` pattern.
   - **CSS variable architecture detection:** If the target uses an existing CSS variable system (e.g., `--dsw-*`, `--ds-*`, `--venice-*`), preserve the architecture. Map their variables to shadcn tokens where they overlap, keep custom variables as-is. Don't flatten a well-structured design token system.
   - **Dark/light mode handling:** If the target has dark mode (detect `prefers-color-scheme`, `.dark` class, `data-theme="dark"`):
     - Create **BOTH** `:root` and `.dark` (or `[data-theme="dark"]`) CSS variable blocks in globals.css
     - Map light colors to shadcn's `:root`, dark colors to `.dark`
     - If the target uses `prefers-color-scheme` media query, convert to CSS class toggle for Next.js (Next.js doesn't support media-query-based dark mode well with SSR). Add a `ThemeProvider` or `<script>` to apply the class.
     - See `references/customization.md` for variable mapping examples
   - **CSS-variable-heavy sites (100+ vars):** Some design systems (Mantine, Railway) define 100-300 CSS variables. Extract to `globals.css` in a dedicated `:root` block. Use `grep -Eo -- '--[[:alnum:]_-]+:[[:space:]]*[^;]+'` from downloaded CSS to get the full set. Don't manually list each var — automate.
   - **Tailwind variable mapping:** If target uses `--tw-*` variables (Tailwind), compare Tailwind version. If both clone and target use Tailwind, many values can be mapped directly: `--tw-*` → Tailwind utilities, avoiding px-by-px rebuild for standard spacing/colors.
3. **Create TypeScript interfaces** in `src/types/`
4. **Extract SVG icons** — deduplicate and save as React components in `src/components/icons.tsx`
5. **Download global assets** — write `scripts/download-assets.mjs` (batched parallel, 4 at a time)
6. **Extraction scripts:** Pre-built at `scripts/discover-assets.js`, `scripts/extract-component-css.js`, `scripts/verify-css.js`
7. **Verify:** `npm run build` passes

See `references/extraction-scripts.md` for the JS scripts to run in browser console.

## Phase 3: Component Specification & Dispatch

The core loop. For a full clone, process each section in the page's completed `SOURCE_OF_TRUTH.md` from top to bottom. For a partial clone, run the loop once for the selected section.

### Step 1: Extract (yourself)
1. **Screenshot** the section → `docs/design-references/`
2. **Extract CSS** via `getComputedStyle()` — run the bundled `scripts/extract-component-css.js` in the browser console
3. **Extract multi-state styles** — capture both states, diff them
4. **Extract real content** — `element.textContent` verbatim
5. **Identify assets** — which images, videos, icons from Phase 2
6. **Check for lazy-loaded images** — if `<img>` has `data-src` or `data-lazy` attribute, use that (not `src`) for the real image URL. Extract both the placeholder and the real URL.
   - Verify each recovered asset is actually visible in the clone. A valid URL in code is not enough if CSS hides it.
   - When the asset cannot be recovered, specify the booth fallback layout: occupied dimensions, background, borders, decorative blocks, and responsive behavior.
7. **Identify external dependencies** — social widgets (Facebook, Twitter), analytics (GA, Umami), CDN fonts. Flag these as "third-party — skip or replace with static alternatives."
   - Known third-party patterns: `facebook.com`, `twitter.com`, `google-analytics`, `gtag`, `googletagmanager`, `cloudflare`, `cdn.*`, `unpkg.com`, `cdnjs`
   - For analytics: skip entirely (not needed in clone)
   - For social widgets: replace with static links/buttons
   - For CDN fonts: self-host the exposed files when practical; otherwise use the reliable Google Fonts `<link>` pattern described in `references/pitfalls.md`
   - **Cookie consent banners:** Detect and skip. Common patterns: `cookie-consent`, `gdpr`, `ccpa`, `cookie-banner`, `CookieNotice`, `#cookies`. These are irrelevant for demo/development clones. Do NOT include cookie banner HTML in the clone. Document as "removed cookie consent banner (not needed for development clone)."
8. **Detect component library patterns** — if repeated class prefixes suggest a known design system (e.g., `ds-*`, `venice-*`, `Mui*`, `chakra-*`), note it. This speeds up builder dispatch.
9. **Deduplicate inline SVGs** — if the page contains many inline SVGs (Squarespace, Supabase patterns with 50+ SVGs):
   - Group SVGs by visual function (icons, logos, illustrations)
   - Extract unique SVGs to `src/components/icons.tsx` as named React components
   - Avoid creating 50 separate icon files — merge into one icons module
10. **Handle inline Style blocks** — if the HTML has multiple `<style>` blocks:
   - Extract and merge all inline styles into one `inline-styles.css` in `docs/research/`
   - Deduplicate conflicting rules (last rule wins, matching browser behavior)
   - **Extract media queries:** Scan for `@media` blocks inside inline `<style>`. These contain responsive breakpoints. Save them separately as `responsive-breakpoints.md` for builder reference.
   - **Handle `!important`:** If the target uses heavy `!important` (10+ occurrences), the clone must match specificity. When converting to Tailwind, use `!important` on the utility class: `class="text-[#333]! font-bold!"`. Note in builder prompts: "Target used !important for these properties — mirror with Tailwind's `!` modifier."
   - Reference extracted styles in builder prompts: "Use these inline styles as base, convert to Tailwind utilities where possible."
11. **Handle data-attrs and Web Components:**
    - **data-attrs (custom data attributes):** Sites like Sentry, SAP, Astro use 30-200+ `data-*` attributes for JS hooks, state, and styling. In the clone: preserve structural `data-*` attrs that affect layout, drop implementation-specific ones (JS event bindings, internal state). Use judgment — if unsure, keep them (safe to have extra attributes in DOM).
    - **Web Components / Shadow DOM:** If the site uses `customElements`, `attachShadow`, or `<*-*>` custom tags (Cloudflare docs, Astro): these are native Web Components. In the clone, you can either: (a) bundle the same WC JavaScript, or (b) reverse-engineer the visual output and rebuild as regular React components. Option (b) is preferred for clone fidelity — WCs render to regular HTML that can be extracted via `getComputedStyle()` just like any other element.
12. **Identify the structural layout pattern** — this is the single most important thing to get right before dispatching a builder. A builder given "text left, image right" will produce a generic flex row — but the real section might be:
    - **Sticky scroll section** — full-height (800px+) section using `position: sticky` as the user scrolls past; alternating backgrounds; only appears at certain scroll positions
    - **Card grid** — 2/3/4 column grid of equal cards
    - **Full-width hero** — centered text with decorative background
    - **Overlay / modal / popover** — positioned above other content
    - **Carousel / slider** — horizontal scroll container with dots/arrows
    - **Parallax stack** — layered images moving at different speeds
    - **Alternating row** — text left/right swap between adjacent sections
    
    **How to extract:** Evaluate `getComputedStyle(section).position` — if `sticky`, document the `top`, `bottom`, and z-index. Take note of adjacent sections: do they alternate direction? Same background or different? Cross-check section class names for clues (e.g. `sticky-promo`, `slick-slider`, `parallax__layer`).
    
    **Document in the spec as:**
    ```
    LAYOUT PATTERN: sticky-scroll
    Behavior: alternates left/right layout per section (even sections reversed)
    Scroll depth: ~800px per section (4 sections = 3200px scroll)
    ```
    
    ⚠️ Builders default to card-grid or simple column layouts when given vague layout descriptions. You must give them the exact pattern name AND a structural description of the HTML to produce.
    
    **Recovery if builder gets pattern wrong:** Do NOT patch the builder's output — the wrong layout pattern is structural. Rebuild the section from scratch, using either a direct write or a new builder with the correct pattern specification.
13. **Assess complexity** — how many sub-components?

### Step 2: Write the Component Spec File
Create `docs/research/components/<name>.spec.md` using the template at `references/spec-template.md`.
Fill every section. If a section doesn't apply, write "N/A" — but think twice.
Copy values from the page's `SOURCE_OF_TRUTH.md`; do not reinterpret or estimate them. Add the page source-of-truth path and section ID to the spec so discrepancies can be traced back to one authority.

### Step 3: Dispatch Builder Agents
Based on complexity:
- **Simple** (1-2 sub-components): One builder agent
- **Complex** (3+ sub-components): One agent per sub-component + one for the wrapper

**Concurrency note:** If `delegate_task` is available, respect its concurrency limit. For 6+ components, split builders into supported-size batches. Dispatch the first batch, then immediately move to extracting the next section while builders run. If delegation is unavailable, implement from the same specs sequentially.

**Every builder prompt receives inline:**
- Full spec file contents
- Explicit props TypeScript interface
- Screenshot path
- Shared components to import
- Target file path
- `"Use export default function ComponentName — do NOT use export function"`
- Verify with `npx tsc --noEmit`

**🛑 STOP:** Before dispatching, verify the Pre-Dispatch Checklist (`references/checklist.md`).

**Don't wait.** Dispatch builders and immediately move to extracting the next section.

### Step 4: Integrate
As builders complete: integrate the component → verify build → fix type errors. Merge worktrees only when the environment actually provides them.

**🔴 CHECKPOINT (Builder Output Verification):** Before declaring a component ready, read the built file and check THREE things:
1. **Text content** — compare every heading, paragraph, and link against extracted originals. Builders frequently paraphrase non-English text. Fix with patch.
2. **Structural layout pattern** — does the component use the same section type (sticky scroll, card grid, full-width hero, carousel) as the original? A sticky-scroll section rebuilt as a card grid passes text/CSS checks but looks completely wrong. If the pattern mismatches, rebuild from scratch instead of patching.
3. **CSS values** — verify key values (bg, color, padding) match extracted getComputedStyle() output.

If implementation, component spec, and live evidence disagree, update the page `SOURCE_OF_TRUTH.md` first. Then reconcile the derived spec and code in that order.

**🔴 CHECKPOINT (Partial clone complete):** If this is a partial clone, run Phase 5 visual QA against the standalone component. Skip Phase 4 — the component is the deliverable. Confirm with user: "Component built and verified. Ready to deliver?"

## Phase 4: Page Assembly

After all sections built and merged:
- Wire everything in `src/app/page.tsx`
- Implement page-level layout (scroll containers, sticky positioning, z-index)
- Connect real content to component props
- Implement page-level behaviors (scroll snap, IntersectionObserver, smooth scroll)
- **Fix layout.tsx locale** — update `<html lang="XX">` to match original
- Verify: `npm run build` passes

**🔴 CHECKPOINT:** Start dev server, verify every section's text matches the original. Check for stale content from a previous clone target.

## Phase 5: Visual QA Diff

1. Take side-by-side screenshots of original and clone at 1440px and 390px
2. Compare section by section, top to bottom
3. For each discrepancy: check spec → re-extract → fix component
4. Test all interactive behaviors (scroll, click, hover)
5. Audit visual occupancy: flag large blank regions, confirm every reachable media asset is displayed, and confirm every unavailable asset has a documented booth fallback

### Measurable Convergence Gate
Run `scripts/capture-reference.mjs`, `scripts/visual-diff.mjs`, and `scripts/compare-geometry.mjs` using `references/measurable-convergence.md`. Acceptance thresholds are: static sections `<0.5%` pixel mismatch, text-heavy sections `<1.5%`, geometry drift `<=2px`, missing visible assets `0`, unexplained blank regions `0`, and broken network assets `0`. Explicitly mask and document dynamic regions. Repeat the repair loop until reports pass. Do not claim a 1:1 clone without the saved reports.

### CSS Verification
Run `scripts/verify-css.js` on BOTH original and clone. Compare key values:
- h1 fontSize/fontWeight
- h2 sizes across sections
- Body fontFamily and backgroundColor
- CTA button bg, color, padding, borderRadius

Only after this pass is the clone complete.

## Post-Clone: Component Relationship Graph (NEW)

After the clone is built, generate a visual map of how all components relate:

```bash
# Analyze component imports within src/components/
grep -rn "import.*from" src/components/*.tsx | \
  python3 -c "
import sys, json
edges = []
for line in sys.stdin:
    parts = line.strip().split(':import')
    if len(parts) == 2:
        source = parts[0].strip().split('/')[-1].replace('.tsx','')
        target = parts[1].strip()
        edges.append({'source': source, 'target': target})
print(json.dumps(edges, indent=2))
" > docs/component-graph.json
```

This produces a dependency graph showing:
- Which components import shared primitives (Button, Card, etc.)
- Which sections depend on which data types
- The overall architecture of the cloned page

Save the visual as `docs/component-graph.md` for the user to inspect.

## Quick Reference

| Topic | File |
|-------|------|
| Full antipatterns table | `references/antipatterns.md` |
| Spec file template | `references/spec-template.md` |
| Per-page source-of-truth template | `references/page-source-of-truth-template.md` |
| Common pitfalls | `references/pitfalls.md` |
| Fallback decision table | `references/fallback-table.md` |
| Pre-dispatch checklist | `references/checklist.md` |
| Extraction scripts | `references/extraction-scripts.md` |
| Customization example | `references/customization.md` |
| Batch extraction testing | `references/batch-extraction-testing.md` |
| Firecrawl mode | `references/firecrawl-mode.md` |
| Playwright extraction mode | `references/playwright-extraction.md` |
| Animation reconstruction | `references/animation-reconstruction.md` |
| Measurable convergence harness | `references/measurable-convergence.md` |
| Preflight audit script | `scripts/preflight-audit.sh` |

## Harness (Self-Eval)

9 eval cases in `evals/evals.json`:

| Case | What it tests | Key assertions |
|------|---------------|----------------|
| `case_001` | Spec template completeness | spec_has_all_sections, spec_has_css_values, spec_has_states, spec_has_assets |
| `case_002` | CSS extraction accuracy | has_get_computed_style, has_extraction_script, has_css_verification |
| `case_003` | Antipatterns + checkpoints | has_antipatterns_section, has_checkpoint_count, has_fallback_table |
| `case_004` | Firecrawl fallback mode | firecrawl_mentioned, dual_mode_documented, fallback_scenario |
| `case_005` | Agent pipeline + component graph | agent_pipeline_documented, component_graph_mentioned |
| `case_006` | Per-page source-of-truth gate | page_source_truth_documented, source_truth_gate_enforced |
| `case_007` | Visual occupancy and booth fallback | asset_visibility_enforced, booth_fallback_documented |
| `case_008` | Measurable convergence gate | measurable_diff_harness_documented, acceptance_thresholds_enforced |
| `case_009` | Animation reconstruction | animation_audit_documented, animation_contract_enforced |

Run `bash evals/test-preflight-audit.sh` after changing the preflight auditor. It covers HTTP localhost preservation, transport failures, valid JSON output, attribute-order variations, uppercase/single-quoted markup, SVG pressure, viewport detection, dark mode, animation markers, and `!important` counts.

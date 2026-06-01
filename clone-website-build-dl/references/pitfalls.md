## Common Pitfalls

## Google Fonts + Turbopack Build Failure (next/font/google)

**Failure mode:** Build fails during `npm run build` with errors like:
```
Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'
```
This happens when `fonts.gstatic.com` is unreachable from the build environment (no egress, corporate proxy, intermittent DNS, or CI sandbox). The `next/font/google` import tries to download `.woff2` files at build time.

**Fix — use `<link>` tag approach instead:**
1. Remove `next/font/google` imports from `layout.tsx`
2. Add Google Fonts via `<link>` tag in `<head>`:
```tsx
// layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="XX">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=FontName:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-fontname">{children}</body>
    </html>
  );
}
```
3. Add the CSS class in `globals.css`:
```css
.font-fontname {
  font-family: 'FontName', sans-serif;
}
```
4. Change all existing styles from `font-family: 'FontName', sans-serif` to use the `.font-fontname` class.

**Note:** This only affects sites using Google Fonts. Self-hosted fonts or system font stacks don't have this issue. The `<link>` approach also avoids the font preload optimization that `next/font` provides, but for demo clones this is acceptable.

## Multi-Page Stale File Cleanup Nuance

**Failure mode:** The skill says "remove old component files (`Hero.tsx`, `CTA.tsx`, etc.), keep only shared infrastructure" before Phase 2. In multi-page mode (when you are ADDING new pages to an existing clone project), this DESTROYS shared components that other pages depend on.

**Fix — scope the cleanup correctly:**
- **Single-target re-clone (same URL):** Clean ALL old component files. The new clone replaces the entire site.
- **Multi-page / additive clone (different URLs, shared project):** Do NOT clean shared components. Only remove spec files and research artifacts (`docs/research/`). Keep all `src/components/` files intact.
- **Multi-page / second pass on same domain:** If cloning additional pages of the same domain, clean `src/app/<locale>/` sub-pages but keep `src/components/`.

Before cleaning, check the project: does it already have pages under `src/app/` other than the root? If yes, assume multi-page mode and do NOT remove shared components.

## Old Dev Server Still Running Causes Port Conflicts

**Failure mode:** Starting a new `next dev` instance fails with "Another next dev server is already running" because a previous session's server (e.g. on port 3001 or 3456) was left running as a background process.

**Fix:** Before starting a dev server for QA, check for existing processes:
```bash
lsof -ti:3001 -ti:3456 -ti:3457 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1
```
Then start the new server. Or use the already-running server instead of starting a new one.

**Alternative:** Use the static build output directly:
```bash
npx serve out -p 3456
```
This does not clash with `next dev` instances.

## PNG→SVG→HTML Is Not a Viable Clone Path
**Why:** Converting a screenshot PNG to SVG (vector tracing) turns all text into unselectable bezier paths, removes all interactivity (hover, click, scroll), loses responsive behavior, and inflates file size 10–50x. The SVG→HTML step is meaningless — the result is a flat image embedded in HTML. No SEO, no accessibility, no interactivity.
**Correct approach:** Browser automation with `getComputedStyle()` for exact CSS values → Tailwind pixel-perfect rebuild → behavior cloning → visual diff QA. The screenshot is useful only as a reference layer for QA overlay, not as a source format for the clone.

## CJK Characters in Project Path Break Turbopack
**Fix:** Copy/symlink to ASCII-only path (`/tmp/project-clone/`), build there, rsync back.

## Montserrat / Google Fonts Lack Arabic Subset
**Fix:** Use `subsets: ["latin"]` only. Arabic glyphs fall back to system fonts.

## Lazy-Loaded Images Appear Broken During QA
**Fix:** Scroll full page before checking broken images to trigger lazy loads.

## Stale Component Files From Previous Clones
**Fix:** Clean stale files before starting Phase 2 on a new target.

## Sub-Page Builder Dispatch Without Full Phase 1 (Multi-Page Mode)

**Failure mode:** In multi-page mode, you run Phase 1 only on the first URL (homepage), then dispatch builders for sub-pages with brief notes grabbed from a quick scan. The builder guesses the layout — and gets it wrong because sub-pages often have different section structures than the homepage.

**Real example:** Cloning ecwid.com/zh-CN/sell. The homepage uses card grids for features, but the /sell page uses **sticky scroll sections** (4 full-height alternating sections, each 800px, with position:sticky). The builder created a card grid that looked nothing like the original. Heading structure also differed: sub-page had `h4` tagline + `h1` instead of single `h1`.

**Fix — Phase 1 is per-URL, not per-project:** Each sub-page in multi-page mode needs its own full Phase 1 extraction:
1. Navigate to the URL and take full-page screenshots (desktop + mobile)
2. Extract the page structure — identify every section and its layout pattern
3. Extract ALL text content verbatim (headings, descriptions, CTAs, stats)
4. Check for unique section types not seen on other pages (e.g. sticky scroll, logo walls, testimonial carousels)
5. Extract design tokens again — confirm fonts, colors, and spacing match the homepage
6. **ONLY then** write spec files and dispatch builders

**Signs you skipped Phase 1:** The builder's output uses a layout pattern that _doesn't exist_ on the actual page (e.g. card grid instead of sticky scroll sections), or the heading text is wrong.

**Recovery workflow when builder output is wrong:**
1. Go back to Phase 1 for that specific URL — full extraction (screenshots, section dimensions, position values, heading hierarchy)
2. Rebuild the page completely from scratch (do NOT patch the builder's output — the wrong layout is structural; patching a card-grid file to become sticky-scroll sections is more work than rewriting)
3. Write the full page content yourself, or dispatch a new builder with the correct layout pattern explicitly named in the spec
4. Verify with a fresh screenshot comparison against the original

**Telltale signs your builder got the layout wrong:**
- Builder created `<div class="grid grid-cols-2">` but original uses full-width alternating sections with position:sticky
- Builder created `<div class="card">` components but original uses full-height single-section layouts (~800px each)
- The builder's output has a different heading hierarchy than what you see on the live page (e.g. extra/missing tagline `h4`/`h5` elements)
- All feature sections use the same layout direction but the original alternates (zigzag pattern)

### Layout Direction Detection (Zigzag Pattern)

Many marketing sites alternate feature section layouts (text-left/image-right → image-left/text-right) for visual variety. This is usually controlled by a CSS class like `calypso-promo--xl-swap` or similar.

**Check every section individually** — do NOT assume they're all the same layout. Extract the full HTML of each section to see if it has the "swap" class or not. In Tailwind clones:
- Sections without swap → `flex-row` (text left, image right)
- Sections with swap → `flex-row-reverse` (image left, text right)

The pattern is typically: **Hero(no swap) → F1(swap) → F2(no swap) → F3(swap) → F4(no swap)** etc.

### Full HTML Extraction Requirement

For pixel-perfect clones, extracting text content and CSS values is NOT enough. The **HTML structure** reveals:
- Which wrapper divs exist and their class names (revealing layout intent)
- The exact heading hierarchy (`h4` tagline + `h1` vs bare `h1`, or `h5` tag + `h2`)
- Layout-direction classes (`--xl-swap`, `flex-row-reverse` equivalents)
- Image positioning (inside what container, with what classes)
- Whether content is centered (`.text-center`) or left-aligned with offsets (`.offset-xl-*`)

**Minimum extraction for each section before dispatching a builder:**
```javascript
// Full outerHTML of each section (not innerHTML — we need the section wrapper too)
sections.forEach(s => {
  result.push({
    class: s.className,           // ← reveals layout direction, background, modifiers
    height: s.offsetHeight,       // ← reveals if it's a sticky scroll section (800px+)
    html: s.outerHTML.slice(0, 2000), // ← the actual DOM structure
    text: s.textContent.trim()     // ← for content verification
  });
});
```

**Check for h5/h4 tagline elements** that prefix h2/h1 headings. These are easy to miss on a quick scan but critical for pixel accuracy.

### Builder Over-Simplification Pattern

Builder agents (via delegate_task) consistently **simplify** complex layouts:
- Sticky scroll sections → card grids
- Full-width image sections → smaller image containers
- Multi-layer illustrations (tab + phone + notification) → single element
- Parallax / scroll-driven animation areas → static blocks
- Logo walls (9+ logos) → abbreviated logo lists (3-4 logos)

**Mitigation:** When the original has 800px+ tall sections with position:sticky, complex multi-layer image areas, or 9+ repeated elements (logos, testimonials), write the component yourself rather than dispatching a builder. These are structural patterns builders get wrong.

**Structural pattern mismatch is the most expensive mistake** because it's invisible at the text/CSS value level — texts match, colors match, but the visual arrangement is completely different. Always check the **section layout pattern** (sticky scroll vs card grid vs hero vs carousel) when doing builder output verification.

## Subagent-Modified Files Stale in Parent Context
**Fix:** Re-read files before patching after a subagent has touched them.

## PNG → SVG → HTML Is Not a Viable Clone Strategy
Converting a screenshot to SVG (vector tracing) then to HTML is fundamentally wrong for website cloning:
- Text becomes unselectable vector paths — no copy/paste, no SEO, no accessibility
- Interactive elements (buttons, links, hover states) are irreversibly lost
- File size explodes (200KB PNG → 50MB+ SVG)
- No responsive behavior — fixed pixel positions only

**Why people think it might work:** AI vision models (GPT-4o, Claude Vision) can generate HTML from a screenshot, but they're ~85% accurate. The correct approach: getComputedStyle() extraction → exact pixel rebuild → behavior cloning → visual diff QA.

## Client Components Missing "use client" Directive
**Fix:** Include `"use client"` in every builder prompt for interactive components.

## Cross-Subdomain Pages Use Different Design Systems
**Fix:** Check font-family on body — if different from prior pages, don't reuse global font config.

## Builders Create Hardcoded Components Without Props
**Fix:** Every spec MUST include a Props Interface. Tell builders to accept props.

## Builder Export Inconsistency Breaks Phase 4 Assembly
**Fix:** Every builder prompt must say: "Use export default function — do NOT use export function".

## Partial Read Causes Patch Failures in Parent
**Fix:** Always use `read_file(path)` without offset/limit when you plan to edit.

## Shared Components Need Route Updates for Multi-Page Clones
**Fix:** After Phase 3, update HeaderNav nav items from `href="#"` to real routes.

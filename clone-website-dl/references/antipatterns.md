# Common Antipatterns (What NOT to Do)

Every guiding principle has a corresponding antipattern. If you find yourself doing any of these, stop and re-read the matching principle.

| # | Antipattern | Why harmful | Correct approach |
|---|---|---|---|
| 1 | Dispatching builders without a spec file | Builder guesses colors/spacing/fonts — clone looks "close enough" not pixel-perfect | Write full spec file first. Builder prompt gets spec content inline |
| 2 | Referencing docs from builder prompts ("see DESIGN_TOKENS.md for colors") | Builder must read another file — if it doesn't, colors are wrong | Inline every value: "color: #1A1A2E" not "see globals.css" |
| 3 | Bundling unrelated sections into one builder (CTA + footer) | Different designs break when combined; agent approximates everything | One builder per distinct design pattern. If spec > 150 lines, split further |
| 4 | Building HTML mockups for video/animations | Looks static and fake — missing motion is obvious | Check for `<video>`, Lottie, canvas first. Extract real media assets |
| 5 | Skipping asset extraction ("we'll add images later") | Clone always looks fake without real images/fonts/icons | Download every `<img>`, `<video>`, inline `<svg>`. No placeholders |
| 6 | Approximating CSS ("looks like text-lg") | Computed value may differ — 18px/24px ≠ Tailwind's 18px/28px | Always use `getComputedStyle()`. Never estimate |
| 7 | Building click-based tabs when original is scroll-driven | Complete rewrite needed, not a CSS fix | Identify interaction model FIRST (Phase 1 interaction sweep). Scroll before clicking |
| 8 | Extracting only default state of tabbed/stateful components | Missing states = rebuild later | Click every tab, extract content + styles for each state |
| 9 | Building everything in one monolithic change | Can't isolate failures; integration becomes hard to debug | Integrate one component at a time. Use worktree commits when Git worktrees are available; otherwise verify `npm run build` after each component |
| 10 | Using generic placeholder text instead of verbatim content | Layout breaks with different text lengths; looks inauthentic | Extract `element.textContent` verbatim. Only generate for per-session data |
| 11 | PNG→SVG→HTML pipeline (screenshot → vector trace → embed) | Text becomes unselectable vector paths, no interactive elements, no responsive layout, file size 50× larger, zero SEO/accessibility | Extract DOM and computed CSS directly via browser MCP or Firecrawl. PNG→SVG is only suitable for static illustrations/posters, never for interactive website clones |
| 12 | Coding a page before its `SOURCE_OF_TRUTH.md` is complete | Implementation becomes an unofficial interpretation and pixel-level drift compounds across sections | Finish the per-page readiness checklist first. When evidence changes, update source of truth → derived specs → code |
| 13 | Hiding reachable media or leaving oversized empty wrappers | The clone looks unfinished even though the original assets were available | Render recovered media visibly. If recovery truly fails, use a documented booth fallback that preserves visual occupancy |
| 14 | Claiming a 1:1 clone from eyeball-only QA | Small spacing, typography, and media drift survives subjective review | Save deterministic captures, pixel diffs, and geometry reports. Repeat the repair loop until the acceptance thresholds pass |
| 15 | Freezing animation before recording runtime states | GSAP, ScrollMagic, and reveal layers can disappear from the reference, producing false blank regions and a static clone | Run `scripts/audit-animations.mjs` first. Record triggers and start/mid/end styles, then freeze for deterministic static QA |
| 16 | Recording approximate section heights without a spacing graph | Headings, media, and CTAs drift even when the total page height looks plausible | Run `scripts/audit-spacing.mjs`. Record landmark rectangles, sibling gaps, edge insets, breakpoint deltas, and intentional whitespace boundaries |

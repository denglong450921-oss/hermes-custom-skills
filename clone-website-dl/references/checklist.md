# Pre-Dispatch Checklist

Before dispatching ANY builder agent, verify every box:

- [ ] Page source of truth exists at `docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md`
- [ ] Page source-of-truth readiness checklist is complete with no placeholders or guesses
- [ ] Spec links to the page source of truth and exact section ID
- [ ] Spec file written with ALL sections filled (including Props Interface)
- [ ] Every CSS value is from getComputedStyle(), not estimated
- [ ] Interaction model identified and documented
- [ ] For stateful components: every state's content and styles captured
- [ ] For scroll-driven components: trigger threshold, before/after styles, transition recorded
- [ ] Animation audit ran before deterministic capture; start/mid/end states and reduced-motion behavior are documented
- [ ] Spacing audit ran before coding; landmark rectangles, sibling gaps, edge insets, alignment anchors, and breakpoint deltas are recorded
- [ ] Every large whitespace interval is classified as intentional or unexplained from measured boundaries
- [ ] All images identified (including overlays and layered compositions)
- [ ] Image paths match actual files in public/
- [ ] Every reachable source image is visibly rendered; CSS does not suppress it
- [ ] Every unavailable source image has a documented booth fallback layout
- [ ] No unexplained blank region remains in desktop or mobile screenshots
- [ ] Deterministic source and clone capture artifacts are saved under `docs/qa/<page-slug>/`
- [ ] Pixel diff reports pass: static sections `<0.5%`, text-heavy sections `<1.5%`
- [ ] Geometry comparison reports pass with `<=2px` drift
- [ ] Dynamic-region masks are documented with reasons
- [ ] Broken network assets, missing visible assets, and unexplained blank regions are all `0`
- [ ] Responsive behavior documented for desktop and mobile
- [ ] Text content is verbatim, not paraphrased
- [ ] Builder prompt under ~150 lines of spec
- [ ] Builder prompt includes explicit props interface
- [ ] Builder prompt says "export default function" (not export function)
- [ ] Interactive components start with "use client"

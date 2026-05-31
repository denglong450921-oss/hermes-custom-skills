# Pre-Dispatch Checklist

Before dispatching ANY builder agent, verify every box:

- [ ] Spec file written with ALL sections filled (including Props Interface)
- [ ] Every CSS value is from getComputedStyle(), not estimated
- [ ] Interaction model identified and documented
- [ ] For stateful components: every state's content and styles captured
- [ ] For scroll-driven components: trigger threshold, before/after styles, transition recorded
- [ ] All images identified (including overlays and layered compositions)
- [ ] Image paths match actual files in public/
- [ ] Responsive behavior documented for desktop and mobile
- [ ] Text content is verbatim, not paraphrased
- [ ] Builder prompt under ~150 lines of spec
- [ ] Builder prompt includes explicit props interface
- [ ] Builder prompt says "export default function" (not export function)
- [ ] Interactive components start with "use client"

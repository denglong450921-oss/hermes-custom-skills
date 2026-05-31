# Animation Reconstruction

Use a two-pass workflow. Audit motion before deterministic screenshots freeze it.

## 1. Inventory And Sample

```bash
node scripts/audit-animations.mjs --url https://example.com/path --out docs/research/animations --label path
```

The report records detected libraries, videos, canvases, active Web Animations, transition-bearing elements, and runtime styles across scroll positions. For hover, click, carousel, and modal states, trigger the interaction in the browser and save additional screenshots plus computed styles.

## 2. Classify Motion

| Source behavior | Clone approach |
|---|---|
| Hover, focus, button feedback | CSS `transition` |
| Entrance reveal | `IntersectionObserver` plus CSS class |
| Scroll progress, sticky parallax | scroll listener or CSS `animation-timeline` when supported |
| Carousel or tab state | explicit React state and timer only when the original auto-advances |
| CSS keyframes | reproduce the extracted keyframes |
| Video, GIF, Lottie | reuse the reachable asset; use the matching player only when required |
| Canvas, WebGL, Three.js | reproduce only when interaction matters; otherwise use an evidence-backed poster fallback |

Do not replace a meaningful animated composition with blank space. Keep recovered media visible before, during, and after motion.

## 3. Record The Contract

For each animated region, add to the page `SOURCE_OF_TRUTH.md`:

- trigger: load, hover, click, intersection threshold, or scroll range
- timeline: duration, delay, easing, repeat, direction
- key states: start, midpoint when relevant, end
- animated properties: transform, opacity, position, clip path, color, or media frame
- responsive differences and reduced-motion behavior
- implementation choice and any documented fallback

## 4. Verify Both Modes

Run motion QA before static convergence QA:

1. Capture or inspect start, active, and end states.
2. Confirm recovered media remains visibly occupied.
3. Confirm `prefers-reduced-motion: reduce` produces a readable stable state.
4. Run deterministic screenshots only after the motion contract is recorded.

Never inject global animation-disabling CSS before the motion audit. It can suppress GSAP, ScrollMagic, and reveal layers and produce a misleading reference screenshot.

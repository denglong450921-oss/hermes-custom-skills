# Cartoon interactive visual system

Build a lively course shell that feels like a coherent cartoon world, not a collection of unrelated decorated worksheets. Visual energy should direct attention toward the current task and celebrate effort without obscuring answer choices.

## Art direction

- Use a vibrant five-color system: sunshine yellow, coral red, sky blue, grape purple, and mint green.
- Pair bright surfaces with dark navy text so contrast remains readable.
- Use rounded cards, thick friendly outlines, sticker-like badges, soft offset shadows, and simple geometric or SVG illustrations.
- Give the course one mascot, map, or story motif that persists across all days.
- Keep content illustrations semantically accurate. Decorative characters may frame a task but must not reveal the answer.
- Avoid photorealistic stock-art mixtures, random emoji collections, tiny text, and a different visual genre on every page.

## Recommended tokens

```css
:root {
  --navy: #24304a;
  --sun: #ffd84d;
  --coral: #ff6b6b;
  --sky: #59c8ff;
  --grape: #8c6ff7;
  --mint: #62d6a7;
  --cream: #fffaf0;
  --card: #ffffff;
  --outline: 3px solid var(--navy);
  --pop-shadow: 0 8px 0 rgba(36, 48, 74, .16);
}
```

Use color as a redundant cue:

- yellow or blue for learning;
- purple or coral for testing;
- mint plus a check icon and text for correct feedback;
- coral plus a retry icon and explanatory text for correction.

Do not use color as the only state signal.

## Dynamic graphical elements

Prefer response-linked motion over continuous ambient motion:

- fill a progress path after a completed response;
- let the mascot react after feedback;
- bounce, combine, trace, or transform the exact concept being learned;
- press game cards down on click and lift them on release;
- animate stars or confetti only after a testing block, never while the learner chooses;
- provide a visible motion toggle and honor `prefers-reduced-motion`.

Keep answer choices stationary during thinking. Avoid flashing, rapid parallax, autoplay sound, and infinite decorative motion. Default decorative motion to paused or subtle; begin richer motion through a deliberate learner action.

## Daily page anatomy

Desktop:

1. persistent left course map;
2. right content area with a daily mission header;
3. visible 30% learning / 70% testing meter;
4. six sequential mission cards;
5. sticky or clearly reachable previous/next navigation.

Mobile:

1. compact drawer or horizontal day picker;
2. one-column mission cards;
3. touch targets of at least about 44 px;
4. no horizontal overflow at 390 px.

Give learning and testing blocks distinct labels rather than relying on background color. Show progress by completed response opportunities, not time spent watching.

## Interactive minimum

Every delivered HTML course should contain:

- clickable or keyboard-operable game controls;
- immediate feedback in an `aria-live` region;
- local progress persistence;
- replay and activity reset;
- semantic animation or graphical response;
- visible current, completed, and retry states;
- a useful non-drag alternative for drag interactions.

Static cards that only describe a future game do not count as a functional interactive course.

## Visual QA

Verify in a real browser:

- the palette and cartoon system are consistent across the outline and daily pages;
- dynamic elements respond to learner actions;
- reduced motion disables nonessential movement;
- focus indicators remain visible over every color;
- testing illustrations contain no answer labels;
- feedback does not shift or resize the answer grid;
- 390 px and wide desktop layouts remain within bounds.

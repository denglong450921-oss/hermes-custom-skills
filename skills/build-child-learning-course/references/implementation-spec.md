# Offline interactive implementation

## Recommended folder structure

```text
course-slug/
├── index.html
├── day01.html
├── day02.html
├── ...
├── assets/
│   ├── app.js
│   ├── course-data.js
│   ├── styles.css
│   ├── audio/
│   └── images/
├── tools/
│   └── generate_assets.py
└── 使用说明.txt
```

Keep course content in one structured data source. Each page should load the same local JavaScript and select content using `data-day`.

## Unified Paradigm UI template

Start compatible projects by copying the complete `assets/unified-paradigm-ui/` folder from the skill. It is a working offline reference project with an index, 15 dedicated day pages, shared renderers, escalating flip cards, responsive styling, local image atlases, Edge TTS MP3s, and a deterministic validator.

Do not link a delivered project back to the skill installation. Copy the resource, run `node tools/validate_template.js`, replace its curriculum and asset mappings, change the storage key, and rerun the validator. Keep the architecture; replace sample subject matter that does not match the request.

## `file://` compatibility

- Do not depend on `fetch()` for local JSON; many browsers block it under `file://`.
- Assign data directly, for example `window.COURSE_DATA = {...}`.
- Use relative paths for every local asset.
- Do not use CDN scripts, web fonts, analytics, or remote images.
- Declare `<meta charset="utf-8">`.

## Content record

Use one record as the source of truth for visual, audio, answer, and feedback mappings:

```js
{
  key: "A-apple",
  prompt: "apple",
  meaning: "苹果",
  image: "assets/images/a-apple.svg",
  audio: "assets/audio/a-apple-word.mp3",
  answer: "A-apple",
  previouslyTaught: true
}
```

Never derive correctness from grid position or visible text.

## Image rendering contract

An existing image file does not prove that the learner can see it. Give every empty semantic image surface a measurable layout box:

```css
.atlas-art {
  display: block;
  width: 100%;
  aspect-ratio: var(--art-ratio, 1);
  background-image: url("assets/images/day01-atlas.png");
  background-position: var(--x) var(--y);
  background-size: 400% 200%;
}
```

Do not leave a background image on an empty inline `<span>`; its width, height, and aspect ratio can collapse. Prefer a direct local `background-image` declaration. If a URL passes through a CSS variable, inspect the computed style rather than assuming substitution worked.

Preserve the source or atlas-cell ratio. Set one dimension plus `aspect-ratio`; do not set both `width: 100%` and `height: 100%` on mixed-ratio art. If a fixed frame is necessary, crop without distortion using `object-fit: cover` or equivalent. For four image answers, prefer four columns on wide screens and two on mobile instead of flattening every source into a short two-column card.

After CSS or renderer changes, version the local stylesheet and script URLs. In browser QA, assert `getBoundingClientRect().width` and `.height` are positive, compare the rendered ratio with the source/cell ratio unless cropping is intentional, and confirm either `naturalWidth > 0` for `<img>` or `getComputedStyle(element).backgroundImage !== "none"` for a background. Reload the actual daily HTML page, not a retired hash URL.

## Game plan record

Store game identity separately from its visual theme. Define four to six course-level core engines, then give each day one or two records with a progression stage:

```js
{
  coreGames: ["G01", "G02", "G03", "G06", "G08", "G15"],
  games: [
    {
      id: "G02",
      name: "听音侦探",
      stage: "consolidation",
      adaptation: "听算式，选择对应数量模型。"
    },
    {
      id: "G15",
      name: "小老师挑战",
      stage: "transfer",
      adaptation: "向家长解释为什么答案是 8。"
    }
  ]
}
```

Use `onboarding`, `consolidation`, and `transfer` as stable stage values. Use the stable IDs in `game-patterns.md`. Do not rename a matching activity and count it as a new mechanic. Avoid games that appear only once. For courses of 10 or more days, validate the continuity with:

```bash
python scripts/validate_game_diversity.py \
  --course-data path/to/course/assets/course-data.js
```

## Daily 30/70 record

Make the ratio machine-checkable. Every day should contain a six-block plan:

```js
{
  reviewSourceDay: 4,
  timePlan: [
    { id: "previous-review", mode: "testing", percent: 15 },
    { id: "micro-lesson", mode: "learning", percent: 20 },
    { id: "worked-example", mode: "learning", percent: 10 },
    { id: "game-round-a", mode: "testing", percent: 20 },
    { id: "game-round-b", mode: "testing", percent: 20 },
    { id: "exit-challenge", mode: "testing", percent: 15 }
  ]
}
```

Use `"prerequisites"` as `reviewSourceDay` on Day 1. From Day 2 onward, set it to the immediately previous day number.

## Non-game block content (CRITICAL)

The four non-game blocks (①②③⑥) must contain structured interactive content — NOT text descriptions. Each block type needs a dedicated renderer in `app.js`:

### ① Previous-day review renderer

Renders a real quiz using previous day's vocabulary items. One question at a time, 4 choices, immediate feedback, score counter:

```js
// course-data.js daily field:
"review": {
  "type": "quiz",
  "items": ["letter-A","letter-B","letter-C","letter-D","letter-E","letter-F"],
  "questionCount": 4,
  "questionType": "sound-to-image"  // play audio, pick image
}
```

The renderer: shuffles items, picks `questionCount` questions, for each plays audio / shows prompt, renders 4 image choices (from items, one correct + 3 distractors), checks answer, shows feedback, advances. Track score. Must NOT be a `<div class="placeholder">` with static text.

### ② Micro-lesson renderer

Renders a step-by-step visual slideshow. 3-5 slides, each with image + short instruction + audio button + optional interaction:

```js
// course-data.js daily field:
"model": {
  "type": "slideshow",
  "slides": [
    { "image": "assets/images/letter-g.svg", "text": "This is the letter G", "audio": "assets/audio/letter-g-name.mp3", "interaction": "tap-to-hear" },
    { "image": "assets/images/goat.svg", "text": "G says /g/ like goat", "audio": "assets/audio/letter-g-word.mp3", "interaction": null },
    { "image": "assets/images/goat.svg", "text": "Can you say 'goat'?", "audio": "assets/audio/letter-g-word.mp3", "interaction": "say-it" }
  ]
}
```

Renders: large image, text below, play button, Next/Previous arrows, progress dots. For `tap-to-hear` interaction: clicking the image plays audio. For `say-it` interaction: renders "I said it!" button then reveals answer. Never renders as passive text.

### ③ Worked example renderer (fading prompt)

Renders 3 steps with decreasing support:

```js
// course-data.js daily field:
"guidedPractice": {
  "type": "fading",
  "steps": [
    { "prompt": "full", "item": "letter-G", "showAnswer": true },
    { "prompt": "partial", "item": "letter-H", "showAnswer": false, "hint": "Starts with H..." },
    { "prompt": "independent", "item": "letter-I", "showAnswer": false }
  ]
}
```

Step "full": shows image + answer text + audio. Step "partial": shows image + hint, child types or selects, then reveals. Step "independent": shows image only, child responds, then checks. The prompt fades from full support to no support across the 3 steps.

### ⑥ Exit challenge renderer

Renders a scored assessment:

```js
// course-data.js daily field:
"exitCheck": {
  "type": "quiz",
  "items": ["letter-G","letter-H","letter-I","letter-J","letter-K","letter-L"],
  "questionCount": 6,
  "passThreshold": 0.8,
  "mixQuestionTypes": true
}
```

Renders: sequential questions (mix of sound-to-image, image-to-text, and fill-blank), score counter, pass/fail celebration at end. Score saved to progress. Child answers independently before seeing results. Not a description of what the parent should do.

## Cartoon interaction shell

**Design foundation:** Before writing styles, load `frontend-design` via `skill_view(name='openclaw-imports/frontend-design')`. Choose a bold aesthetic direction for the course and execute it with precision. The interaction patterns below are pedagogical constraints; the visual expression comes from frontend-design's principles.

Follow `visual-design.md` and keep the visual system local:

- define vibrant palette variables in local CSS **plus a distinctive typography system** (display font + body font, not Arial/Inter/system defaults);
- keep one course mascot or map motif across pages;
- render rounded outlined mission cards and large touch controls;
- attach graphical feedback and progress animation to learner actions — **use staggered reveals, scroll-triggered entrances, and hover states that surprise**;
- provide a motion toggle and reduced-motion fallback;
- keep answer options stationary during response;
- persist block completion and attempts with `localStorage`.

Static descriptions of future games do not satisfy the interactive requirement. Provide working buttons, choices, rearrangement, or other response controls appropriate to the selected engine.

## Randomization

Use Fisher–Yates on every page load and replay:

```js
function shuffle(items) {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
```

Use deterministic selection only when stable daily sampling is desired. Do not use a fixed seed for a memory game that claims to reshuffle.

## Matching game behavior

- Begin with every card covered unless restored progress is intentionally displayed.
- Reveal the selected face without relying exclusively on 3D CSS transforms.
- Play the record’s local audio on open when sound is relevant.
- Keep the first card visible while the second is selected.
- Keep successful pairs visible and mark them clearly.
- Cover an incorrect pair after readable feedback.
- Let the learner cover a completed pair again.
- Provide a dedicated “restart matching” control that clears only matching state and reshuffles.

## Listening choices

- Use exactly one correct record and unique distractor records.
- Draw distractors from taught content.
- Render clean pictures without labels.
- Use `grid-template-columns: repeat(3, minmax(0, 1fr))`.
- Set question cards and choices to `min-width: 0`.
- Limit the outer listening grid to two columns on wide screens and one column on narrow screens.
- Reveal the correct word in feedback after the response.

## Audio

Pre-generate local MP3 files. For Microsoft Edge TTS:

```python
import edge_tts
await edge_tts.Communicate(text, voice, rate="-5%").save(output_path)
```

Good starting voices include `en-US-AnaNeural` for young English learners. Select an appropriate installed voice for other languages and test a sample with the user when voice quality matters.

Provide:

- playback rates: 0.6×, 0.7×, 0.8×, 0.9×, 1.0×, 1.1× as selectable speed buttons;
- **repetition control**: a visible selector for audio repeat count — options 1×, 2×, 3×. When set to >1, the `play()` function replays automatically with 400ms gap between repetitions. Persists in localStorage alongside speed setting;
- visible playing status;
- clean cancellation when a new sound starts;
- a specific error when a local file is missing.

### Repetition implementation

```js
function play(src, cb){
  if (currentAudio) { currentAudio.pause(); currentAudio = null; }
  if (!src) return;
  const repeats = state.settings.audioRepeats || 1;
  let count = 0;
  function playOnce(){
    if (count >= repeats) { if (cb) cb(); return; }
    const a = new Audio(src);
    a.playbackRate = state.settings.audioRate || 0.8;
    a.onended = () => { count++; setTimeout(playOnce, 400); };
    currentAudio = a;
    a.play().catch(()=>{});
  }
  playOnce();
}
```

The repetition UI must sit alongside the speed control in the hero section of every daily page:

```html
<div class="repeat-control">
  <span class="repeat-label">🔁 重复:</span>
  <button class="repeat-btn active" data-repeat="1">1×</button>
  <button class="repeat-btn" data-repeat="2">2×</button>
  <button class="repeat-btn" data-repeat="3">3×</button>
</div>
```

## Progress state

Store compact state in `localStorage`:

```js
{
  settings: { rate: 0.7, repeats: 2 },
  days: {
    1: {
      blocks: {},
      games: {},
      review: {},
      exit: {},
      completed: false,
      stars: 0
    }
  }
}
```

Version the storage key when the state schema changes. Include activity-level replay and day-level reset.

## Responsive layout

- Desktop: persistent left table of contents and right content.
- Mobile: hidden drawer or compact menu.
- Use `minmax(0, 1fr)` for grids containing buttons or long text.
- Test at a wide desktop size and at 390 px.
- Give controls visible keyboard focus and touch targets of about 44 px.
- Honor `prefers-reduced-motion`.

## Packaging

Validate every expected local file, decode all audio, scan for external URLs, then build the ZIP from a clean source folder. Verify ZIP entry counts and CRC before delivery.

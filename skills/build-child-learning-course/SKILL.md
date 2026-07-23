---
name: build-child-learning-course
description: Build, revise, and validate child-friendly interactive HTML courses for English, mathematics, Chinese, and other subjects. Use whenever Codex needs a multi-day children's curriculum with a coherent cartoon style, vibrant colors, responsive animation, practical game-based learning, a 30% instruction and 70% testing balance, previous-day retrieval, local audio and images, progress tracking, dedicated daily pages, offline packaging, or mastery assessment.
---

# Build Child Learning Course

Create a complete learning system, not a collection of decorated lesson pages. Make every activity serve an observable learning objective and preserve a short loop of instruction, recall, feedback, and review.

## 0. The Content Rule — no placeholder text, ever

**This is the cardinal rule.** Every block on every daily page must contain real, interactive, executable educational content. The learner must be able to DO something — click, choose, speak, type, match, sort, or build — in every single block. A block that only displays descriptive text about what the learner *should* do or what *will* be taught is a failure.

When building the course, never render a block as a `<div class="placeholder">` containing only a description string from course-data. Instead, build concrete interactive content for every block:

| Block | Must contain |
|---|---|
| ① Previous-day retrieval | Actual quiz questions with clickable answer choices, immediate feedback, and score tracking. Large images (≥200px) as answer choices — the image IS the choice, text is secondary. |
| ② Micro-lesson | Animated or click-to-reveal teaching content. A single large image (≥280px, filling ≥60% of the block width) dominates each slide, with minimal text below. The image IS the lesson. |
| ③ Worked example | A step-by-step walkthrough where the child participates in the final step. Large central image (≥240px) with the answer revealed alongside. |
| ④ Game A | Full interactive game engine (see game-patterns.md). Working buttons, choices, feedback. Images in game cards must be large (≥120px, filling most of the card). |
| ⑤ Game B | Second interactive game engine. Same image-size requirements as Game A. |
| ⑥ Exit challenge | A real assessment task. Large image choices (≥180px), the child answers before seeing the result. Score recorded. |

**The test:** Open any daily page. Can a child complete every block by clicking/touching/speaking, receiving feedback, and seeing their progress? If any block requires the child (or parent) to read a description and imagine what to do, the course fails the content rule.

The `app.js` `missionCard()` function must call dedicated renderers for every block type — not just game blocks. See the upgraded [references/implementation-spec.md](references/implementation-spec.md) for the non-game block renderer specifications.

## Route the references

- Always read [references/learning-science.md](references/learning-science.md) before designing the learning loop.
- Always read [references/game-patterns.md](references/game-patterns.md) before selecting a practical cross-day game spine.
- **MANDATORY: Load the `frontend-design` skill with `skill_view(name='openclaw-imports/frontend-design')` before writing any HTML/CSS for the course.** This skill provides the aesthetic direction system — distinctive typography, bold color themes, memorable motion, and spatial composition — that prevents the course from looking like generic AI-generated slop. The course must have a clear, intentional visual identity (not just the five-color palette from visual-design.md). Apply the frontend-design skill's Design Thinking process: pick a bold aesthetic direction (playful/toy-like for young children, storybook/whimsical, cosmic/space, underwater/ocean, etc.), commit to it, and execute with precision across every page.
- Read [references/visual-design.md](references/visual-design.md) for the course-specific interaction patterns, cartoon system, and accessibility rules. The frontend-design skill supplies the aesthetic vision; visual-design.md supplies the pedagogical interaction constraints.
- Read [references/subject-patterns.md](references/subject-patterns.md) for English, mathematics, Chinese, or another subject adaptation.
- Read [references/implementation-spec.md](references/implementation-spec.md) before building interactive offline HTML — **this now includes non-game block specifications.**
- Read [references/qa-checklist.md](references/qa-checklist.md) before final validation.
- Use `scripts/scaffold_course.py` when a new multi-page HTML course needs a consistent starting structure. **WARNING: The scaffold's `app.js` and `course-data.js` contain placeholder text for non-game blocks. You MUST replace every placeholder with real interactive renderers and structured content data before considering the course complete. A scaffold that passes validation checks but still has placeholder text in daily blocks is NOT a finished course.** See Section 4 for the required renderer specifications.

## 1. Establish the learner contract

Determine or reasonably infer:

- learner age and developmental stage;
- prior knowledge and language background;
- subject, scope, duration, and daily study time;
- learning environment, including offline or device constraints;
- parent or teacher involvement;
- required output language and accessibility needs;
- observable mastery target.

Ask only for information that would materially change the curriculum. State important assumptions in the delivered course guide.

## 2. Design backward from mastery

1. Write one measurable final outcome.
2. Decompose it into small prerequisite skills.
3. Sequence those skills from concrete and familiar to abstract and independent.
4. Assign each day one primary objective, the previous day's retrieval set, and a small spaced-review set.
5. Define an exit task that proves the objective without showing the answer.
6. Schedule cumulative review rather than placing all revision on the final day.

Keep daily volume challenging but achievable. Count actual response opportunities, not just items displayed on screen.

## 3. Enforce the 30% learning / 70% testing loop

Budget daily time and response opportunities by mode:

| Order | Daily block | Mode | Share |
|---|---|---:|---:|
| 1 | Previous-day retrieval; use prerequisite retrieval on Day 1 | Testing | 15% |
| 2 | One concise visual, audio, movement, or concrete micro-lesson | Learning | 20% |
| 3 | One worked example with a fading prompt | Learning | 10% |
| 4 | Core game testing round A | Testing | 20% |
| 5 | Core game testing round B with transfer or production | Testing | 20% |
| 6 | Exit challenge, correction, and mastery decision | Testing | 15% |

Count a block as testing only when the child must respond before seeing the answer. Feedback and retries remain part of the testing loop; watching an explanation or replay does not. Record attempts, accuracy, hints, and production evidence separately. Every day after Day 1 must retrieve content from the immediately previous day before introducing new material; add older spaced items only after that requirement is satisfied.

Do not let animation replace thinking. Pause ambient motion by default and animate the item currently being learned or tested.

### Build a coherent game spine

For a course of 10 or more days:

- select four to six core game engines from the larger library in [references/game-patterns.md](references/game-patterns.md);
- use each core engine at least three times across **onboarding → consolidation → transfer**;
- keep a primary engine for a two- or three-session arc when continuity helps;
- use one or two focused games per day and make both produce observable evidence;
- include recognition and production without introducing a new genre merely to appear varied;
- vary content, representation, scaffolding, difficulty, and transfer context inside familiar mechanics;
- avoid one-off games, cosmetic reskins, and a disconnected “new game every day” schedule.

Validate the course rotation with `scripts/validate_game_diversity.py`. Game variety must increase meaningful retrieval opportunities without raising irrelevant interface complexity.

## 4. Build the course system

### 4a. Interactive content in every block (non-negotiable)

Every daily block must contain a real interactive widget. The `app.js` must include renderer functions for ALL six block types, not just game blocks. Build these as first-class interactive components:

- **`renderPreviousReview(block, d, container)`** — renders actual quiz questions from the previous day's content. Shows one question at a time (e.g., "Which picture matches the letter B?" with 4 clickable image choices). Tracks score. Shows feedback after each answer. Uses the same Fisher-Yates shuffle as game blocks.
- **`renderMicroLesson(block, d, container)`** — renders a step-by-step visual lesson. The child clicks "Next" to advance through 3-5 slides. Each slide has a large image, a short instruction, an audio play button, and an optional interactive element (tap the letter to hear it, drag to trace, click to reveal). Progress bar shows position. No passive paragraphs of text.
- **`renderWorkedExample(block, d, container)`** — renders a 3-step fading prompt. Step 1: "Watch" — the full answer is shown with animation. Step 2: "Try with help" — partial answer shown, child fills one gap. Step 3: "Your turn" — child completes independently. Uses the same content item types as games (image + audio + answer).
- **`renderExitChallenge(block, d, container)`** — renders a real assessment. Mix of question types (multiple choice, yes/no, fill-in). The child answers each question before seeing the result. Final score displayed with celebration animation for ≥80% and gentle retry prompt for lower scores. Score saved to progress state.

These renderers must be called from `missionCard()` exactly like game renderers are — not replaced with placeholder `<div>` elements.

### 4b. Content data requirements

The `course-data.js` must include structured data that these renderers can use. Each daily plan's non-game fields must go beyond descriptive strings:

```js
{
  "day": 2,
  "review": {
    "type": "quiz",           // not a text description
    "items": ["letter-A", "letter-B", "letter-C"],
    "questionCount": 4,
    "questionType": "sound-to-image"  // or "image-to-text", "fill-blank"
  },
  "model": {
    "type": "slideshow",      // not a text description
    "slides": [
      { "image": "assets/images/letter-g.svg", "text": "This is G", "audio": "assets/audio/letter-g-name.mp3" },
      { "image": "assets/images/goat.svg", "text": "G says /g/ like goat", "audio": "assets/audio/letter-g-word.mp3" }
    ]
  },
  "guidedPractice": {
    "type": "fading",         // not a text description
    "steps": [
      { "prompt": "full", "item": "letter-G" },
      { "prompt": "partial", "item": "letter-H" },
      { "prompt": "independent", "item": "letter-I" }
    ]
  },
  "exitCheck": {
    "type": "quiz",           // not a text description
    "items": ["letter-G", "letter-H", "letter-I", "letter-J", "letter-K", "letter-L"],
    "questionCount": 6,
    "passThreshold": 0.8
  }
}
```

### 4c. Visual and technical deliverables

**Design requirement:** The course must have a distinctive aesthetic identity, not generic cartoon clip-art. Before writing any HTML/CSS, load `frontend-design` via `skill_view(name='openclaw-imports/frontend-design')` and commit to a bold direction: storybook-whimsical, cosmic-adventure, underwater-explorer, jungle-safari, toy-blocks, etc. The direction must be visible in typography (distinctive display font for headings), color (a dominant theme color + sharp accents, not timid even distribution), spatial composition (unexpected layouts, generous whitespace, asymmetry where appropriate), and motion (staggered reveals, scroll-triggered animations, hover surprises). The five-color palette from visual-design.md becomes a *minimum accessibility baseline*, not the ceiling.

**Image-first layout (mandatory):** The course is for young children who cannot read fluently. Images are the primary communication medium — they must dominate every block. Apply these image-sizing rules across ALL blocks (review, lesson, example, games, exit):

- Slide/lesson images: minimum 280px, fill ≥60% of the block's content width
- Choice/question images: minimum 180px for answer choices, minimum 120px for game cards
- Hero/day-card images: prominent decorative illustration (≥200px)
- Text labels: always secondary to the image, placed below or beside at ≤60% of image size
- Never constrain images to small thumbnails (e.g., 60px) — they must be large enough for a child to recognize without reading
- Image-to-text ratio: the image area must be ≥2× the text area in every block

**Repetition control (mandatory):** Every daily page must include a visible repetition count selector alongside the playback speed control. Audio repetition count options: 1×, 2×, 3×. When set to 2× or 3×, each `play()` call automatically replays the audio the specified number of times with a 400ms gap between repetitions. The setting persists in localStorage and applies to all audio in the course — quizzes, slideshows, games, and challenges equally.

For HTML courses, deliver:

- one outline page and one dedicated page per day;
- a left table of contents and right learning area on desktop;
- a compact mobile navigation pattern;
- a coherent cartoon art direction and vibrant high-contrast palette;
- responsive graphical feedback, semantic animation, and a motion toggle;
- a visible 30/70 learning-testing meter on every daily page;
- local images, audio, fonts, data, CSS, and JavaScript;
- playback speed and repeat controls when audio is pedagogically relevant;
- progress saved locally with clear replay and reset controls;
- randomized practice on every new attempt;
- tests whose visuals never reveal the textual answer;
- immediate, specific, child-safe feedback;
- interactive game controls rather than cards that merely describe a game;
- a complete offline folder and optional ZIP archive.

Generate English and Chinese speech as local Microsoft Neural TTS MP3 files when the user requests recorded pronunciation. Test the chosen voice with a sample before generating the full set.

## 5. Protect interaction integrity

Apply these non-negotiable rules:

- Shuffle with Fisher–Yates on page load and every replay; do not use a fixed seed for a memory game.
- Keep a matched pair visible, but let the learner cover that pair again or restart the activity.
- Play the corresponding local word or prompt audio when an audio-enabled card is opened.
- Draw distractors from content the learner has already encountered unless the task explicitly assesses transfer.
- Keep each option inside its question card at every viewport.
- Store question identity independently from visual position.
- Map each audio path, picture, answer key, and feedback label from the same content record.
- Stop or supersede prior audio cleanly when a new item is played.

## 6. Validate in a real browser

Do not finish after static inspection. Verify:

- every daily page loads under `file://`;
- no network request is required;
- each day totals exactly 30% learning and 70% testing;
- Day 2 onward explicitly retrieves the immediately previous day's content;
- the course reuses four to six core engines across onboarding, consolidation, and transfer;
- interactive controls update feedback and saved progress;
- the cartoon visual system is coherent across all pages;
- card order changes across reloads and replay;
- the opened card reveals the correct face and plays the matching audio;
- every listening question contains exactly one correct option;
- answer pictures contain no answer text;
- saved progress can be replayed without clearing unrelated work;
- desktop and narrow mobile viewports have no horizontal overflow;
- console logs contain no severe errors;
- reduced-motion behavior, keyboard focus, and readable contrast remain usable.

Run the complete checklist in [references/qa-checklist.md](references/qa-checklist.md).
Run `scripts/validate_game_diversity.py --course-data <course>/assets/course-data.js` for generated courses that use the standard data structure.
Run `scripts/validate_course_balance.py <course-folder>` to verify the 30/70 split, previous-day review chain, interactive HTML markers, and offline structure.

## 7. Deliver for reuse

Provide:

- the course entry file;
- the complete offline course folder;
- a ZIP when portability matters;
- a concise Chinese handoff when the learner or parent is Chinese-speaking;
- a short description of learning objectives, daily rhythm, and reset behavior;
- validation results and any remaining limitations.

Open the main HTML file after successful validation when working on a local desktop.

## Optional adjacent demo

If a sibling folder named `15-day-english-adventure` is available, inspect it as a functional reference for local Microsoft TTS, multi-page navigation, matching games, and progress tracking. Reuse the framework, not its English-specific content.

# IELTS Assessment Workflow

Use this reference when creating a quiz, assessment, or interactive HTML learning page for `analyze-ielts-sentence`. It adapts the article structure and English-text display language of `draft-to-high-quality-prose` into a complete learning cycle.

## Table of Contents

- [Learning Cycle](#learning-cycle)
- [Question Blueprint](#question-blueprint)
- [Item Writing Rules](#item-writing-rules)
- [Answer and Scoring Rules](#answer-and-scoring-rules)
- [Result Analysis](#result-analysis)
- [HTML Information Architecture](#html-information-architecture)
- [Visual Contract](#visual-contract)
- [Interaction and Accessibility](#interaction-and-accessibility)
- [Acceptance Checklist](#acceptance-checklist)

## Learning Cycle

Build one connected workflow:

1. **Orientation**: Show the source sentence, Chinese core meaning, learning goals, and a content-specific reading prompt.
2. **Study**: Teach the sentence from simple meaning to structure, vocabulary, upgrade, paragraph use, and transfer.
3. **Compact review**: Restate only the few patterns and collocations that will be retrieved in the test.
4. **Test**: Mix recognition and recall. Do not reveal answers or explanations yet.
5. **Feedback**: Score only after explicit submission and explain every item.
6. **Diagnosis**: Aggregate errors by learning dimension and recommend the next review action.
7. **Retry**: Let the learner retake wrong items or reset the entire lesson.

Do not assess knowledge that was never taught on the page. Do not repeat the answer verbatim immediately above a test item unless the task intentionally measures recognition rather than recall.

## Question Blueprint

Use this standard eight-item blueprint unless the source material requires a justified adjustment.

| Order | Format | Primary dimension | Cognitive action | Typical target |
|---|---|---|---|---|
| 1 | Multiple choice | meaning | identify | overall Chinese meaning |
| 2 | Multiple choice | meaning or structure | distinguish | writing function or logical relation |
| 3 | Multiple choice | structure | analyze | sentence trunk, modifier, or reference |
| 4 | Multiple choice | vocabulary | choose | natural collocation or IELTS-safe upgrade |
| 5 | Fill in the blank | structure | recall | reusable frame or connector |
| 6 | Fill in the blank | vocabulary | recall | high-frequency collocation |
| 7 | Fill in the blank | structure or vocabulary | reconstruct | grammatically complete sentence chunk |
| 8 | Fill in the blank | transfer | apply | taught pattern in a new IELTS topic |

Recommended balance:

- `meaning`: 20-30%
- `structure`: 25-30%
- `vocabulary`: 20-30%
- `transfer`: 20-30%

Use easy-to-difficult order. Keep one primary construct per item so an error has a useful interpretation. A transfer item may combine learned elements, but its required answer must remain constrained enough to score fairly.

## Item Writing Rules

### Multiple choice

- Use four options when possible.
- Write one clearly best answer.
- Base distractors on common errors: literal translation, wrong logical function, collocation mismatch, excessive certainty, or a grammatically possible but contextually wrong choice.
- Keep options parallel in grammar and similar in length.
- Avoid `all of the above`, `none of the above`, unnecessary negatives, and trivia.
- Do not reveal the correct answer through bolding, color, option order patterns, or wording copied uniquely from nearby hints.

### Fill in the blank

- Ask for a word, collocation, or short taught frame, not an unconstrained paragraph.
- Show enough context to make the intended answer identifiable.
- State the expected number of words when that improves fairness.
- Accept a small explicit set of equivalent answers only when each is grammatical and preserves the tested meaning.
- For open production, use human reflection rather than binary automated scoring. Do not pretend a free-form IELTS sentence has one exact correct answer.

### Explanations

For each item, prepare:

- the correct answer
- a one- or two-sentence rationale
- the misconception behind the strongest distractor when useful
- the dimension tag
- one review pointer tied to the study section

Do not show these fields before submission.

## Answer and Scoring Rules

Normalize fill-in responses before comparison:

1. Unicode-normalize with `NFKC` when available.
2. Convert curly apostrophes and quotation marks to plain equivalents.
3. Lowercase.
4. Trim leading and trailing whitespace.
5. Collapse repeated internal spaces.
6. Ignore terminal sentence punctuation when punctuation is not the construct being tested.

Do not remove meaningful word boundaries, prepositions, or inflections. List accepted answers explicitly rather than using fuzzy similarity that may mark a wrong phrase as correct.

Use equal item weights by default. If weighting is necessary, display it before the test. Compute:

```text
mastery percentage = earned item points / available item points * 100
dimension percentage = correct items in dimension / items in dimension * 100
```

Recommended mastery labels:

| Score | Label | Interpretation |
|---:|---|---|
| 90-100 | 熟练掌握 | Can retrieve and transfer the taught pattern reliably. |
| 75-89 | 基本掌握 | Core understanding is sound; review isolated weak points. |
| 60-74 | 需要巩固 | Some recognition exists, but recall or transfer is unstable. |
| 0-59 | 建议重学 | Return to the weakest study dimension before retrying. |

These labels describe this page only. Never convert them to IELTS bands.

## Result Analysis

Reveal results only after the form is complete and submitted.

Show, in this order:

1. Total correct count and mastery percentage.
2. A plain-language mastery label.
3. Four dimension rows with counts and progress bars.
4. A targeted summary naming the strongest and weakest dimensions.
5. One concrete next action for each weak dimension.
6. Item-level feedback beside each question: learner response, correct answer, and rationale.
7. `错题重测` and `重新开始` actions.

Use these review mappings as defaults:

- `meaning`: reread the Chinese core meaning and identify the sentence's writing function.
- `structure`: rebuild the sentence from trunk to modifiers and connector.
- `vocabulary`: retrieve the collocation aloud, then write one short example.
- `transfer`: substitute a new topic into the reusable frame without adding extra clause complexity.

If all dimensions are strong, recommend delayed retrieval later rather than more immediate repetition.

## HTML Information Architecture

Use a self-contained page with this semantic outline:

```html
<body>
  <a class="skip-link" href="#study">跳到学习内容</a>
  <header class="lesson-header"></header>
  <nav class="table-of-contents" aria-label="课程目录"></nav>
  <aside class="reading-tip" aria-labelledby="reading-tip-title"></aside>
  <main>
    <section id="study"></section>
    <section id="review"></section>
    <section id="test">
      <form id="quiz-form"></form>
    </section>
    <section id="results" hidden aria-live="polite" tabindex="-1"></section>
  </main>
  <footer></footer>
</body>
```

The study section may condense the ten teaching sections into grouped modules, but preserve the learning progression. For example:

- `理解`: sections 1-2
- `表达`: sections 3-5
- `运用`: sections 6-8
- `提升`: sections 9-10

Keep the test below the study material. Use real anchor links. Keep result content in the document flow so revealing it does not cover the quiz.

## Visual Contract

Follow the quiet reading-page language used by `draft-to-high-quality-prose`:

- neutral paper and white surfaces
- high-contrast dark text
- blue for structure and focus
- warm color for reading prompts or study emphasis
- green and red only for submitted correctness states
- border radius at or below `8px`
- no ornamental gradients, decorative blobs, heavy shadows, or nested cards

Use repeated cards only for individual quiz questions and result items. Keep page sections unframed with generous vertical separation.

Desktop rails:

- Place the table of contents in a fixed left rail only when it fits outside the article column.
- Place `阅读提示` in a dedicated fixed right rail on sufficiently wide screens.
- At smaller widths, move both elements into normal flow; never hide the reading prompt.
- Verify both rails at the top and after scrolling.

English text:

```css
.english-text,
[lang="en"] {
  max-width: 100%;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: normal;
  hyphens: none;
}

.grid-child,
.question,
fieldset {
  min-width: 0;
}
```

Do not use horizontal sentence scrolling, clipping, ellipsis, fixed text heights, or `white-space: nowrap` for material the learner must read.

## Interaction and Accessibility

- Use a real `<form>` and `<fieldset><legend>` for each multiple-choice question.
- Pair every fill input with a visible `<label>`.
- Give all required controls the `required` attribute and call `reportValidity()` before scoring.
- Keep touch targets at least `44px` high.
- Use visible `:focus-visible` outlines.
- Update answer progress without announcing correctness.
- Put validation and submission status in an `aria-live` region.
- On successful submission, reveal results, update question feedback, and focus the result heading or region.
- Use text plus color for correct and incorrect states.
- Disable or hide score controls only when their purpose is unavailable; never trap keyboard focus.
- Honor `prefers-reduced-motion`.
- Keep all core study, test, scoring, and retry behavior available without network access.

Answers are "initially hidden" only when the learner cannot see or focus answer text, rationales, correctness classes, dimension scores, or recommendations before submission. Storing keys in local JavaScript is acceptable for a learning aid; this is not a secure examination platform.

## Acceptance Checklist

Before delivering the page, verify:

- The source sentence and all English examples wrap fully at desktop and mobile widths.
- The page has no horizontal document scroll.
- The reading prompt is visible in the right rail on wide screens and in normal flow below the breakpoint.
- The left TOC, right prompt, article, quiz, and results never overlap at the top or after scrolling.
- The quiz contains both multiple-choice and fill-in-the-blank items.
- No answer, rationale, correctness state, score, or recommendation is visible before submission.
- Incomplete submission produces a clear validation message and no score.
- A fully correct response produces 100% and accurate dimension totals.
- A mixed response produces correct per-item feedback and targeted weak-dimension advice.
- Fill normalization accepts intended capitalization, spacing, punctuation, and apostrophe variants but rejects meaningfully wrong phrases.
- `错题重测` clears only wrong responses and hides their feedback again.
- `重新开始` restores the original unanswered state.
- The result is labeled as lesson mastery, not an IELTS band estimate.
- Keyboard navigation, focus states, and mobile touch targets work.

Use `../assets/ielts-assessment-workflow-example.html` as the implementation reference for these checks.

# Learning Experience Design

Build an interactive lesson that makes the next learning action obvious.

## Five-stage memory loop

### Notice 观察

Ask for a prediction before explaining. Let the learner commit to a gist or
relationship, then revisit it after study. This uses generation rather than
passive exposure.

### Build 搭建

Reveal the sentence in 3–7 meaningful chunks. Start from the main clause, then
add modifiers. Pair each chunk with Chinese and a short “why it matters” note.

For sentences over 25 words or with 2+ clauses, this must be an actual
progressive interaction, not a visually segmented article:

- use a `.progressive-reveal` container;
- leave only the main clause visible initially;
- mark the reveal control with `data-reveal-next`;
- reveal exactly one functional layer per action;
- update an `aria-live` status with the newly revealed role;
- let the learner restart the reveal sequence.

### Recall 提取

Provide a cover-and-recall control. Hiding Chinese or keywords must change the
task from rereading to retrieval. Offer a hint only after an attempt and count
hints separately from mastery.

### Transfer 迁移

Give a reusable frame and require the learner to replace content while
preserving relationship, register, and qualifiers.

### Review 复习

Use final assessment evidence and confidence to select the next drill and
schedule later retrieval.

## Page anatomy

Use this information architecture:

```text
header: sentence + session progress
stage navigation: Notice → Build → Recall → Transfer → Review
main:
  learning workspace: one dominant active task
  memory coach: strategy, hint budget, next action
practice strip: game progress, separate from mastery
assessment: sealed until the learner reaches Review
```

On wide screens, the stage navigation may be sticky and the memory coach may
sit beside the workspace. At 760px and below, use normal document flow. Never
hide essential content behind hover.

## Visual system

Recommended qualities:

- warm off-white canvas with high-contrast ink;
- indigo or deep blue for structure;
- jade for completed learning actions;
- amber for retrieval cues and uncertainty;
- rounded but not pill-heavy cards;
- a visible chunk map or memory-loop motif;
- calm motion under 240ms, disabled with reduced-motion.

The UI should look authored for language learning. Avoid generic KPI cards,
meaningless gradients, trophy clutter, and excessive shadows.

## Interaction rules

- Give an instruction, expected action, and feedback area for every activity.
- For long sentences, do not expose the complete clause analysis on initial
  render; require the progressive build contract above.
- Use buttons to move chunks up/down or left/right; dragging may be an
  enhancement, never the only method.
- Memory matching must support click/tap and keyboard activation.
- Do not reveal an answer until the learner commits or requests a hint.
- Explain *why* after correctness feedback.
- Keep each interaction resettable.
- Announce state changes in `aria-live` regions.
- Restore focus sensibly after submit, retry, reveal, and reset actions.

## Memory strategies

Label each game with a real strategy:

- **retrieval practice** — produce before seeing;
- **chunking** — compress a long sentence into meaningful units;
- **generation effect** — commit to a prediction or completion;
- **elaboration** — explain why a chunk plays its role;
- **dual coding** — align language with a structural map;
- **interleaving** — alternate meaning, structure, vocabulary, and transfer;
- **spaced retrieval** — revisit after increasing delays;
- **metacognitive calibration** — compare confidence with correctness.

Do not claim that a decorative game automatically improves memory. The game
must rehearse the exact knowledge the learner later needs.

## Recommended games

### Sentence Forge

Purpose: rebuild clause order from chunks.

- Shuffle 3–7 chunks.
- Let learners select a chunk and move it earlier/later with buttons.
- Check only after a complete order is present.
- Explain the main clause and attachment points.
- On replay, reshuffle.

### Collocation Pairs

Purpose: retrieve English collocations from Chinese functions or examples.

- Present 3–5 English and Chinese/function cards.
- Select one from each set to attempt a match.
- Keep unmatched cards available.
- Explain register or a common error after a match.
- Do not rely on color to indicate pairs.

### Cloze Ladder

Purpose: move from cued to independent recall.

- First attempt has no hint.
- Hint 1 reveals Chinese function.
- Hint 2 reveals first letters or chunk boundaries.
- Final reveal appears only after an attempt.
- Record hints for coaching, not mastery.

## Assessment integration

Games create formative signals such as `structureNeedsReview` or
`vocabNeedsReview`. The final assessment remains the sole source of mastery.
Use game signals to order the review drills, not to add or remove test points.

## Accessibility

- Meet WCAG AA contrast for text and controls.
- Use real buttons, labels, fieldsets, legends, and headings.
- Provide a skip link and visible focus ring.
- Ensure 44px target size where practical.
- Respect browser zoom and text expansion.
- Support 320px width without horizontal page scrolling.
- Add `aria-pressed`, `aria-expanded`, or status text where visual state alone
  would be ambiguous.
- Do not autoplay audio.

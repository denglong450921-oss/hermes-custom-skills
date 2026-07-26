# Assessment Workflow

Use this reference for every interactive IELTS sentence lesson.

## What the assessment measures

Measure whether the learner can:

1. recover the sentence’s intended meaning;
2. reconstruct its clause and modifier structure;
3. retrieve useful vocabulary and collocations;
4. transfer the pattern to a new topic.

The page reports **lesson mastery**, never an IELTS band estimate.

## Evidence sequence

### 1. Diagnostic prediction

Before teaching, ask one or two unscored questions:

- a gist prediction;
- a quick choice about what modifies what.

Record the choice for comparison after learning, but do not label it with a
score. This activates prior knowledge and creates a reason to read.

### 2. Formative micro-checks

Insert at least three checks between teaching blocks. Use immediate feedback
that states:

- what the learner noticed correctly;
- what the evidence in the sentence is;
- what to try next.

These checks may update the memory coach or weak-skill flags, but must not
inflate the final mastery score.

### 3. Summative assessment

Use exactly eight scored items, two per dimension:

| Dimension | Item A | Item B |
|---|---|---|
| Meaning | gist or inference | qualifier/relationship |
| Structure | clause role | rebuild or order |
| Vocabulary | collocation recognition | controlled recall |
| Transfer | frame completion | constrained production |

Use at least three response formats, such as choice, fill, ordering,
matching, or constrained production. Keep generated tasks objectively
checkable. For a genuinely open sentence, provide a self-check rubric and do
not silently convert it to a binary machine score.

## Confidence and calibration

Before the learner checks each final item, require:

- **不确定** — guessing or cannot explain;
- **有点把握** — likely correct but not fully explainable;
- **很有把握** — can justify the answer.

Map these to low, medium, and high confidence. After submission calculate:

- **confident-correct**: high confidence and correct;
- **unsure-correct**: low/medium confidence and correct;
- **confident-wrong**: high confidence and wrong.

Confident-wrong items are the priority for review because they reveal a
misconception, not just missing recall. Do not add confidence points to mastery.

## Scoring

Score each of the eight items equally unless a transparent partial-credit
rubric is displayed before submission.

```text
overall mastery = correct items / 8 × 100
dimension mastery = correct items in dimension / 2 × 100
```

Suggested labels:

- 90–100: 熟练掌握
- 75–89: 基本掌握
- 60–74: 需要巩固
- below 60: 建议重学

## Answer security

Before submission:

- keep result panels and explanations hidden;
- do not place correct answers in visible labels, CSS class names, or
  `data-*` attributes;
- store answer keys inside a script closure or load them only on submission;
- do not mark options correct as the learner clicks;
- keep `form` submission controlled with `preventDefault()`.

Formative checks may reveal their own feedback immediately, but final-test
answers must remain sealed until final submission.

## Results dashboard

After submission show:

1. overall mastery and plain-language label;
2. four dimension scores;
3. confidence calibration summary;
4. per-item response, correct answer, and short rationale;
5. strongest dimension and priority weakness;
6. a targeted micro-drill for each weak dimension;
7. retry-wrong and restart controls;
8. spaced retrieval plan.

Game score, streak, elapsed time, and hint count may appear in a separate
“practice energy” area. Never merge them into mastery.

## Adaptive review

Create one actionable drill for each dimension below 75%:

- **Meaning**: cover the translation, say the gist, then uncover and compare.
- **Structure**: rebuild from the main clause outward with chunk buttons.
- **Vocabulary**: complete a collocation from a Chinese cue, then use it once.
- **Transfer**: replace X/Y/Z in the reusable frame with a new topic.

If confidence was high on a wrong item, precede the drill with a contrast
example that exposes the misconception.

On “retry wrong answers”:

- preserve correct items;
- clear only wrong responses;
- hide correct answers and explanations again;
- move focus to the first wrong item;
- update the question progress count.

## Spaced retrieval

Always recommend:

- **10 minutes**: retrieve the main clause and two chunks without looking;
- **1 day**: rebuild the full sentence or reusable frame from shuffled chunks;
- **3 days**: write one new-topic sentence and self-check the qualifier,
  collocation, and clause logic.

Keep the plan short enough to perform. Do not promise notifications unless the
environment actually creates them.

## Acceptance checks

- [ ] 1–2 diagnostic predictions are unscored.
- [ ] 3+ formative micro-checks give explanatory feedback.
- [ ] Final assessment has exactly 8 items.
- [ ] Each of four dimensions has exactly 2 scored items.
- [ ] At least 3 response formats are used.
- [ ] Confidence is required before final checking.
- [ ] Final answers remain hidden before submission.
- [ ] Calibration distinguishes confident-wrong.
- [ ] Weak dimensions generate targeted drills.
- [ ] Retry clears only wrong items and reseals answers.
- [ ] The 10-minute, 1-day, 3-day plan is present.
- [ ] Practice/game metrics are separate from mastery.

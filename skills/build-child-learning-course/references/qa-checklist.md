# Course validation checklist

Run applicable checks before delivery.

## Content quality (CRITICAL — runs before all other checks)

- [ ] No block on any daily page is a static `<div class="placeholder">` containing only descriptive text.
- [ ] ① Previous-day review block renders actual clickable quiz questions with answer checking and score.
- [ ] ② Micro-lesson block renders a step-by-step slideshow with images, audio, and Next/Previous controls.
- [ ] ③ Worked example block renders 3-step fading prompts (full → partial → independent).
- [ ] ⑥ Exit challenge block renders a real scored quiz, not a description of what the parent should do.
- [ ] Every block the child sees is something they can DO — click, choose, speak, match, sort, or build.
- [ ] `app.js` contains `renderPreviousReview()`, `renderMicroLesson()`, `renderWorkedExample()`, and `renderExitChallenge()` functions that are called from `missionCard()`.
- [ ] The `course-data.js` daily fields for review/model/guidedPractice/exitCheck use structured objects (`{type: "quiz", items: [...], ...}`) not plain text strings.

## Curriculum

- [ ] Final mastery outcome is observable.
- [ ] Every day has one primary objective.
- [ ] Prerequisites appear before dependent skills.
- [ ] Daily volume matches age and study time.
- [ ] Day 2 onward begins with retrieval from the immediately previous day.
- [ ] Older review is spaced after the previous-day requirement.
- [ ] Every daily plan totals 30% learning and 70% testing.
- [ ] Testing requires a response before revealing an answer.
- [ ] Recognition and production are both assessed.
- [ ] Distractors represent plausible confusions.

## Learning integrity

- [ ] Tests hide answer labels.
- [ ] Animation represents meaning or process.
- [ ] Support fades before the independent check.
- [ ] Feedback names the correct idea and next action.
- [ ] Stars reward completion without replacing mastery evidence.
- [ ] The learner can retry an activity without losing unrelated progress.

## Game coherence

- [ ] A course of 10 or more days selects four to six core game IDs.
- [ ] Every core engine appears at least three times.
- [ ] Core engines progress through onboarding, consolidation, and transfer.
- [ ] Recognition and production games are both present.
- [ ] Each daily page contains only one or two focused games.
- [ ] No game is a one-off novelty or cosmetic reskin.
- [ ] Short cross-day arcs deepen familiar game mechanics.
- [ ] Every selected game produces evidence for that day's objective.
- [ ] Previous-day content returns in the first testing block.
- [ ] `scripts/validate_game_diversity.py` passes for the course plan.

## Visual and interactive system

- [ ] Outline and daily pages share one coherent cartoon world.
- [ ] The palette is vibrant and text contrast remains readable.
- [ ] Daily pages visibly distinguish 30% learning from 70% testing.
- [ ] Dynamic graphics respond to progress, feedback, or semantic actions.
- [ ] A motion toggle and reduced-motion behavior are present.
- [ ] Game controls accept real learner responses; they are not static descriptions.
- [ ] Completed, retry, and current states are visually and textually clear.
- [ ] Local progress restores after reload.
- [ ] Every visible learning image has a positive rendered width and height.
- [ ] Every `<img>` decodes with `naturalWidth > 0`; every background/sprite has a computed `backgroundImage` other than `none`.
- [ ] Empty background-image elements use block, grid, or flex layout with an explicit width and height/aspect ratio.
- [ ] The rendered image ratio matches the source or atlas-cell ratio unless an intentional `cover` crop is documented; no image is stretched or squashed.
- [ ] A fresh reload of the versioned CSS/JavaScript shows the corrected UI on the actual daily page.

## Content mappings

- [ ] Every item has a unique stable key.
- [ ] Image, audio, prompt, answer, and feedback come from the same record.
- [ ] Every listening question has exactly one correct option.
- [ ] Choices are unique within a question.
- [ ] Distractors come from taught content unless transfer is intended.
- [ ] Every audio file exists and decodes.

## Matching game

- [ ] Order changes across at least three reloads.
- [ ] Replay reshuffles again.
- [ ] Opening a card reveals its face.
- [ ] Opening a card plays its corresponding local audio when enabled.
- [ ] Re-clicking an open card can replay audio.
- [ ] Incorrect pairs cover again.
- [ ] Correct pairs remain visible.
- [ ] A completed pair can be covered and replayed.
- [ ] A dedicated reset affects only the matching activity.

## Layout and accessibility

- [ ] Desktop table of contents and content remain readable.
- [ ] 390 px viewport has no horizontal overflow.
- [ ] Every choice stays inside its question card.
- [ ] Controls have visible focus.
- [ ] Images have useful alternative text or accessible labels.
- [ ] Feedback uses an `aria-live` region where appropriate.
- [ ] Reduced-motion preference disables nonessential animation.
- [ ] Color is not the only correctness signal.
- [ ] Answer options stay stationary while the learner is deciding.

## Offline behavior

- [ ] All pages work from `file://`.
- [ ] No CDN, remote font, analytics, remote image, or runtime TTS request exists.
- [ ] Data loads without local `fetch()` restrictions.
- [ ] All links use relative local paths.
- [ ] UTF-8 Chinese text renders correctly.

## Browser regression

For every daily page, assert:

- expected learning-item count;
- expected test and matching-card count;
- calculated learning share equals 30%;
- calculated testing share equals 70%;
- review source is the previous day;
- correct answer appears among choices;
- no duplicate choice key;
- no severe console error.

Test representative interactions in a real browser:

1. complete and restore a matched pair;
2. reset and reshuffle;
3. intercept or inspect the audio path on card click;
4. answer a listening question correctly and incorrectly;
5. reload saved progress;
6. verify desktop and mobile bounding boxes.
7. complete a block, reload, and verify saved progress.
8. enable and disable responsive motion.
9. inspect a learning image in review, micro-lesson, flip-card, and exit views; confirm each has visible pixels and natural proportions, not only a mapped file.

## Delivery

- [ ] Entry HTML opens successfully.
- [ ] `scripts/validate_course_balance.py` passes.
- [ ] Offline folder contains all assets.
- [ ] ZIP integrity test passes.
- [ ] Usage instructions explain progress storage and reset.
- [ ] Final handoff links to the entry file and ZIP.

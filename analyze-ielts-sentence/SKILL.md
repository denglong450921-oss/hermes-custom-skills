---
name: analyze-ielts-sentence
description: >-
  Analyze difficult IELTS English sentences for Chinese-speaking learners and
  create interactive bilingual learning pages. Use when the user asks for
  IELTS sentence analysis, grammar/structure breakdown, clause mapping,
  vocabulary and collocations, translation, paraphrasing, writing transfer,
  an interactive HTML lesson, a learning assessment, memory games, or
  bilingual slow-speed audio. Especially suitable for long or complex IELTS
  reading and writing sentences.
---

# Analyze IELTS Sentence

Turn one difficult IELTS sentence into a learning experience that helps a
Chinese-speaking learner understand it, retrieve it from memory, and transfer
its structure to new topics.

Use Simplified Chinese as the teaching language unless the user requests
otherwise. Keep terminology accurate but explain it in plain language.

## Choose the output mode

Use the smallest mode that satisfies the request:

- **Chat analysis**: provide the ten-part analysis below.
- **Interactive HTML**: create a polished, self-contained learning page and
  follow all linked learning, assessment, accessibility, and audio contracts.
- **Both**: give a concise chat summary and save the complete page.

If the user asks for a page, quiz, UI, demo, audio, interactive practice, game,
or assessment, use Interactive HTML mode.

## 🔴 CHECKPOINT · 🛑 STOP — ambiguous HTML brief

Before Interactive HTML production, resolve this brief: exact target sentence,
output mode, output path, and whether local audio is required.

- If the sentence and requested mode are explicit, continue immediately. When
  no output path is given, use a new descriptive folder under `outputs/`; this
  default alone does not require confirmation.
- If the sentence is missing, multiple candidate sentences remain, or the
  resolved path would overwrite an existing artifact, **STOP**. Show the
  resolved brief, identify the unresolved choice, and wait for confirmation.
- After confirmation, keep the approved brief fixed unless the user changes it.

## Required analysis

Analyze the sentence in this order:

1. **一句话总览** — natural Chinese meaning and communicative purpose.
2. **主干定位** — subject, predicate, object/complement.
3. **分层拆解** — clauses and modifiers from outer frame to inner detail.
4. **结构图** — compact bracket, tree, or dependency-style view.
5. **逐块对照** — each English chunk immediately paired with Chinese.
6. **关键词与搭配** — meaning, register, collocation, and common misuse.
7. **语法难点** — only grammar that materially unlocks the sentence.
8. **同义改写** — at least one easier version and one formal alternative.
9. **写作迁移** — reusable frame plus a new-topic example.
10. **记忆钩子** — a short chunking or image-based cue for later retrieval.

Do not merely label grammar. Explain how each part contributes to meaning.
Preserve qualifiers such as *largely*, *may*, and *in some cases*.

## Interactive learning workflow

For every HTML lesson, read and follow:

- [`references/learning-experience-design.md`](references/learning-experience-design.md)
- [`references/assessment-workflow.md`](references/assessment-workflow.md)
- [`references/bilingual-audio-workflow.md`](references/bilingual-audio-workflow.md)

Build the lesson as a five-stage memory loop:

1. **Notice 观察** — predict meaning before explanation.
2. **Build 搭建** — reveal the sentence in meaningful chunks.
3. **Recall 提取** — hide supports and retrieve from memory.
4. **Transfer 迁移** — rebuild the pattern with a new topic.
5. **Review 复习** — diagnose weaknesses and schedule later retrieval.

Do not dump all content into one long article. Keep one active task visually
dominant and expose detail progressively.

For a sentence longer than 25 words or containing two or more clauses,
progressive reveal is mandatory: show the main clause first, keep dependent
clauses/modifiers initially hidden, and reveal one functional layer at a time
with a keyboard-operable control. Mark the container `.progressive-reveal` and
the control `data-reveal-next`. A full ten-part analysis rendered all at once
does not satisfy Interactive HTML mode.

## Learning Studio UI contract

Every HTML lesson must include:

- a visible stage/progress navigator;
- a central active workspace;
- a compact “memory coach” area showing the current strategy or next action;
- a `.progressive-reveal` sentence build with a `data-reveal-next` control;
- bilingual English units with audio controls;
- at least three formative micro-checks before the final assessment;
- at least two pedagogical memory games;
- an eight-item final assessment and a mastery dashboard;
- adaptive wrong-answer review and a spaced-review plan;
- responsive behavior with no required horizontal scrolling at 320px width.

Use semantic landmarks, logical heading order, visible focus styles, keyboard
operation, meaningful status messages, and `prefers-reduced-motion`. Never make
dragging, color, sound, or animation the only way to understand or operate a
task.

### Visual direction

Aim for a calm, distinctive learning studio rather than a generic dashboard.
Use strong information hierarchy, generous reading width, consistent tokens,
and one restrained accent system. A subtle grid, paper texture, memory-loop
motif, or chunk map may provide character. Avoid decorative clutter and
gamification that competes with reading.

## Interactive-method selection

Choose interactions that match the learning objective:

| Objective | Preferred interaction |
|---|---|
| Notice main meaning | prediction poll, gist choice |
| See clause hierarchy | progressive chunk reveal, sentence map |
| Learn sequence | chunk-order game with move buttons |
| Learn collocations | memory match, contrast sort |
| Strengthen recall | cover-and-recall, cloze ladder |
| Transfer structure | constrained rewrite, frame builder |
| Monitor certainty | confidence-before-check control |

### Memory game requirements

Include at least two `.memory-game` sections, normally:

1. a **structure game** such as chunk ordering; and
2. a **meaning/vocabulary game** such as collocation matching or a cloze
   ladder.

Each game must:

- name its memory strategy with `data-memory-strategy`;
- include short instructions and a keyboard/touch alternative;
- provide immediate explanatory feedback, not only “correct/incorrect”;
- allow replay without reloading;
- feed a weak-skill signal into review;
- keep points, streaks, and speed bonuses separate from mastery.

Prefer retrieval practice, chunking, generation, elaboration, dual coding,
interleaving, and spaced retrieval. Avoid unsupported claims about “learning
styles.”

## Assessment standard

Use three layers:

- **Diagnostic**: 1–2 unscored predictions before teaching.
- **Formative**: micro-checks during learning with immediate coaching.
- **Summative**: exactly 8 scored items after study.

The final assessment must cover four dimensions with two items each:

- meaning;
- structure;
- vocabulary/collocation;
- transfer.

Use at least three response formats across the eight items. Four-choice and
fill-in items are acceptable, but include one structure or transfer task that
requires generation rather than recognition.

Before checking each final item, collect confidence on a three-point scale.
After submission, report:

- overall mastery (not an IELTS band estimate);
- four dimension scores;
- calibration: confident-correct, unsure-correct, and confident-wrong;
- concise rationale for each item;
- strongest dimension and priority weakness;
- one targeted micro-drill for each weak dimension;
- **retry wrong answers** with correct answers hidden again;
- a 10-minute, 1-day, and 3-day retrieval plan.

Never expose correct answers, answer-bearing classes, explanations, or
mastery results before submission. Do not auto-score free production as fully
correct with a fragile string match; use a constrained task or a transparent
self-check rubric.

## Bilingual and audio contract

Every learner-facing English unit must place, in the same `.english-unit`:

1. the English text;
2. its Chinese translation;
3. a visible English highlight with `<mark>`;
4. a Chinese explanation of the highlight;
5. a play button whose `data-audio-src` points to local Edge TTS audio.

Use the shared audio player and offer `0.6x`, `0.7x`, `0.8x`, and `0.9x`.
Default to `0.7x`. The spoken transcript must exactly match the visible English
for that unit. Do not use browser speech synthesis.

Generate audio with:

```bash
python scripts/generate_edge_tts.py \
  --text "Exact visible English" \
  --output assets/audio/example.mp3 \
  --rate=-30%
```

Audit the finished page:

```bash
python scripts/audit_bilingual_audio.py path/to/page.html
python scripts/audit_learning_experience.py path/to/page.html
```

Both audits must pass before delivery.

## Failure recovery

Use these branches exactly; never report a failed check as complete.

| Trigger | First repair | If it still fails |
|---|---|---|
| Target sentence is missing or multiple sentences compete | Apply the ambiguous-brief checkpoint and request one exact sentence | Stop HTML production; do not invent the learning content |
| Edge TTS generation fails | Retry once with the exact visible transcript and `en-US-AriaNeural`; verify the MP3 is non-empty | Preserve bilingual text, mark audio as unavailable, show the exact retry command, and ask approval before delivering a text-only page |
| Bilingual/audio audit fails | Repair every reported `.english-unit`, audio path, highlight, or speed-control violation, then rerun the audit | Do not deliver the page; report the failing lines and required corrections |
| Learning-experience audit fails | Restore the reported stage, game, assessment, confidence, retry, or progressive-reveal contract, then rerun | Do not deliver the page; report the unmet contract and keep results sealed |
| Inline JavaScript does not parse | Fix quoting/template interpolation and run a syntax check again | Deliver no interactive artifact; provide the exact syntax error and file path |
| Resolved output path already exists | Apply the overwrite checkpoint and choose a new path or obtain explicit approval | Preserve the existing artifact unchanged |

## Canonical UI demo

Use [`assets/ielts-learning-studio-demo.html`](assets/ielts-learning-studio-demo.html)
as the reference implementation. It demonstrates the stage layout, progressive
reveal, cover-and-recall, chunk ordering, memory matching, confidence
calibration, adaptive review, spaced retrieval, accessible audio, and mobile
layout. Adapt its content; do not copy sentence-specific answers into a new
lesson.

## Red lights — anti-pattern blacklist

If any red light is present, repair it before delivery.

| Red light | Why it fails | Required replacement |
|---|---|---|
| Grammar labels without explaining their contribution to meaning | The learner can name a structure but cannot interpret or transfer it | Explain function, meaning effect, and one reusable use |
| Full long-sentence analysis visible on initial render | Encourages passive rereading and overload | Main-clause-first progressive reveal |
| Decorative games, points, or streaks counted as mastery | Confuses engagement with learning evidence | Keep practice metrics separate; mastery comes only from the 8-item test |
| Correct answers encoded in visible text, classes, or `data-*` attributes | Leaks the sealed assessment | Keep answer keys inside a script closure and reveal only after submit |
| Open production auto-scored by one fragile string match | Rejects valid language and overstates accuracy | Use constrained production or a visible self-check rubric |
| Learner-facing English outside audited bilingual units, or browser speech synthesis | Breaks alignment, exact transcript, and offline guarantees | Use `.english-unit` plus verified local Edge TTS |
| Dragging, color, sound, or animation as the only operating cue | Excludes keyboard, low-vision, and reduced-motion users | Add buttons, text status, focus behavior, and semantic state |
| Failed audit, missing audio, or JavaScript error reported as completed | Delivers a knowingly broken lesson | Follow Failure recovery and state the unresolved blocker |

## Delivery checklist

Before completing the task, verify:

- analysis follows the ten-part sequence;
- instruction precedes testing;
- final assessment has 8 items, 2 per dimension, and 3+ response formats;
- answers and results are hidden before submission;
- confidence is collected before checking;
- 2+ accessible memory games are present;
- game performance is separate from mastery;
- weak dimensions create targeted review;
- wrong-answer retry hides answers again;
- spaced review includes 10 minutes, 1 day, and 3 days;
- every learner-facing English unit passes the bilingual/audio audit;
- the page is readable and operable at 320px and with reduced motion;
- all template-generated strings use safe JavaScript quoting.

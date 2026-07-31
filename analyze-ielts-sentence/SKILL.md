---
name: analyze-ielts-sentence
description: >-
  Analyze difficult IELTS English sentences for Chinese-speaking learners and
  create polished interactive bilingual HTML learning pages by default. Use
  whenever the user supplies an English sentence to study or asks for
  IELTS sentence analysis, grammar/structure breakdown, clause mapping,
  vocabulary and collocations, translation, paraphrasing, writing transfer,
  an interactive HTML lesson, a learning assessment, memory games, or
  bilingual slow-speed audio. Teach high-value keywords through practical
  daily-life examples and an easy-to-moderate difficulty ladder. Especially
  suitable for long or complex IELTS reading and writing sentences.
---

# Analyze IELTS Sentence

Turn one difficult IELTS sentence into a learning experience that helps a
Chinese-speaking learner understand it, retrieve it from memory, and transfer
its structure to new topics.

Use Simplified Chinese as the teaching language unless the user requests
otherwise. Keep terminology accurate but explain it in plain language.

## Default output mode

Create **Interactive HTML by default** when the user supplies one exact target
sentence, even if they only say “analyze,” “explain,” or “help me learn this.”
The default deliverable is a polished self-contained page saved in a new
descriptive folder under `outputs/`, plus a short chat handoff linking to it.

Use another mode only when the user explicitly requests it:

- **Chat only**: provide the ten-part analysis in the conversation and do not
  create a file.
- **Both**: give a concise chat summary and save the complete HTML page.
- **HTML without audio**: only when the user explicitly declines audio or the
  audio failure-recovery branch requires permission for a text-only page.

Do not ask the learner to choose a display mode when an exact sentence is
already present. HTML is the resolved default.

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
6. **关键词与搭配** — select 4–6 high-utility words or collocations and teach
   meaning, register, pronunciation cue, common partners, misuse, and a natural
   daily-life example.
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
- a visually distinct `.keyword-lab` containing 4–6 `.keyword-card` units;
- an easy-to-moderate `.difficulty-ladder` for practical keyword transfer;
- bilingual English units with audio controls;
- one dedicated local MP3 for every English learning unit, with no shared MP3
  paths and no multi-sentence audio bundles;
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

Make the page feel like an inviting language-learning studio rather than a
generic dashboard or a long worksheet. Establish a coherent visual concept
from the sentence topic, then express it through a restrained accent palette,
a purposeful display/body type pairing, a visible sentence/chunk motif, and
small moments of useful delight such as a progress trail, flip/reveal cue, or
animated connection between a keyword and its example. Keep the active task
dominant, the reading column comfortable, and motion calm and optional.

Use layered surfaces, spacing, icons or small illustrations, and feedback
states to make learning feel rewarding, but never let decoration obscure the
sentence. Avoid template-like KPI cards, arbitrary gradients, trophy clutter,
excessive shadows, or points presented as learning evidence. At 320px, all
content must remain readable without horizontal scrolling.

## Keyword Lab and practical transfer

Every HTML lesson must teach **4–6 key words or collocations** chosen for
usefulness, transfer value, and relevance to the sentence. Prefer language the
learner can reuse in conversation, work, study, travel, family life, and
IELTS-safe writing. Do not fill the panel with rare words merely because they
look advanced.

Mark the section `.keyword-lab`. Each `.keyword-card` must include:

- the word or collocation and a simple pronunciation/stress cue;
- plain Chinese meaning and the meaning it carries in this sentence;
- register and 1–2 common partners;
- one frequent learner mistake or unnatural combination;
- one short, natural daily-life example relevant to an adult learner;
- a “Use it today” prompt that asks for a small personal response.

Place English examples inside the existing audited `.english-unit` contract.
Use progressive disclosure so cards remain scannable; definitions may be
visible while examples, mistakes, or prompts expand with keyboard-operable
controls.

### Difficulty ladder

Mark the practice sequence `.difficulty-ladder` and provide these three rungs:

1. **Easy · Notice** (`data-difficulty="easy-notice"`) — choose or match the
   keyword with its plain meaning or natural partner.
2. **Easy · Use today** (`data-difficulty="easy-use"`) — complete a short
   first-person sentence about the learner's day, work, family, or plans.
3. **Moderate · Transfer** (`data-difficulty="moderate-transfer"`) — adapt a
   supplied frame to one familiar topic with constraints and a model answer
   hidden until the learner commits.

Keep the first two rungs low-pressure and highly scaffolded. The moderate rung
may combine two learned items, but it should not demand an unsupported essay,
abstract debate, or advanced free production. Do not add a hard tier unless the
user explicitly asks for one. Give specific explanatory feedback and a retry
path at every rung.

## Interactive-method selection

Choose interactions that match the learning objective:

| Objective | Preferred interaction |
|---|---|
| Notice main meaning | prediction poll, gist choice |
| See clause hierarchy | progressive chunk reveal, sentence map |
| Learn sequence | chunk-order game with move buttons |
| Learn collocations | memory match, contrast sort |
| Apply keywords to daily life | personal cloze, guided micro-journal |
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

### Iron rule: one English unit, one MP3

Treat audio as required learning content, not an optional enhancement. Every
learner-facing English sentence, example, model, question stem, answer option,
keyword, or collocation must live in its own `.english-unit` and own exactly
one dedicated local MP3. Never combine two sentences into one MP3. Never point
two units at the same MP3, even when their wording repeats.

Each unit must declare:

- `data-audio-transcript="..."` containing the exact plain-text English heard;
- exactly one `.tts-play` button;
- one unique relative `data-audio-src` ending in `.mp3`;
- one `[lang="en"]` transcript whose normalized text exactly matches
  `data-audio-transcript`.

The page may use one shared `<audio>` player for playback controls, but each
unit's MP3 file remains unique. Generate all MP3 files before delivery and
verify that every referenced file exists and is non-empty. If any required MP3
cannot be generated, follow the audio failure branch and do not call the HTML
lesson complete.

Every learner-facing English unit must place, in the same `.english-unit`:

1. the English text;
2. its Chinese translation;
3. a visible English highlight with `<mark>`;
4. a Chinese explanation of the highlight;
5. exactly one play button whose unique `data-audio-src` points to its own
   local Edge TTS MP3.

Use the shared audio player and offer `0.6x`, `0.7x`, `0.8x`, and `0.9x`.
Default to `0.7x`. The spoken transcript must exactly match the visible English
for that unit. Do not use browser speech synthesis or a multi-sentence
compilation track.

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
| Inline JavaScript does not parse | Fix quoting/template interpolation and run `node --check` on the extracted script block. Common root cause: bare `\u201c`/`\u201d` (Chinese curly quotes) inside `"..."` JS strings — replace with `\u201c`/`\u201d` escapes. | Deliver no interactive artifact; provide the exact syntax error and file path |
| Resolved output path already exists | Apply the overwrite checkpoint and choose a new path or obtain explicit approval | Preserve the existing artifact unchanged |

## Canonical UI demo

Start every lesson from
[`assets/ielts-learning-template.html`](assets/ielts-learning-template.html).
Treat its visual tokens, reading width, type scale, card language, audio row,
responsive behavior, and interaction states as the stable house style so
another AI agent produces a recognizably consistent lesson. Adapt the topic
motif and content, but do not replace the template with a generic dashboard or
plain article.

Use [`assets/ielts-learning-studio-demo.html`](assets/ielts-learning-studio-demo.html)
as the full interaction reference for progressive reveal, memory games,
confidence calibration, adaptive review, and spaced retrieval. Do not copy
sentence-specific answers into a new lesson.

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
| One MP3 reused by multiple English units, one unit with multiple play buttons, or one MP3 containing multiple sentences | Audio and visible text can drift; learners cannot repeat one item precisely | Give every unit one exact transcript, one play control, and one unique local MP3 |
| Dragging, color, sound, or animation as the only operating cue | Excludes keyboard, low-vision, and reduced-motion users | Add buttons, text status, focus behavior, and semantic state |
| Failed audit, missing audio, or JavaScript error reported as completed | Delivers a knowingly broken lesson | Follow Failure recovery and state the unresolved blocker |
| Chinese-style quotes (U+201C/U+201D) or other non-ASCII quotes used inside JS double-quoted strings without escaping | JS parser treats them as string terminators, breaking all event listeners | Use `\u201c`/`\u201d` Unicode escapes in JS strings, or switch to backtick template literals `\u0060...\u0060` for strings containing Chinese punctuation |

## Delivery checklist

Before completing the task, verify:

- analysis follows the ten-part sequence;
- HTML was produced by default unless the user explicitly requested chat only;
- Keyword Lab contains 4–6 practical keyword cards with daily-life examples;
- the difficulty ladder contains easy-notice, easy-use, and moderate-transfer,
  with no unrequested hard tier;
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
- every English unit has one exact `data-audio-transcript`, one play button,
  and one unique, existing, non-empty MP3; no audio bundle contains multiple
  sentences;
- the page is readable and operable at 320px and with reduced motion;
- all template-generated strings use safe JavaScript quoting;
- inline JavaScript passes `node --check` before delivery (Chinese quotes in JS strings are the most common silent breakage).

---
name: build-child-learning-course
description: Build, revise, and validate complete ready-to-teach interactive courseware for children across English, mathematics, Chinese, and other subjects. Use whenever a user asks to create, make, design, or deliver a child learning course, multi-day curriculum, lesson pages, educational games, pronunciation practice, mastery checks, or a playful learning website—even when they describe it as a plan. Unless the user explicitly asks for concepts only, deliver a working offline HTML course with real content, functional games, feedback, progress, dedicated daily pages for long courses, responsive UI, and validation; treat a visually appealing child-facing UI as the primary design principle, not final polish. Start from the bundled, agent-copyable Unified Paradigm UI project when it fits, then adapt it rather than copying it rigidly.
---

# Build Child Learning Course

Deliver **可直接上课的互动课件**: a child must be able to open the entry page and begin a complete lesson without imagining missing content or waiting for later implementation.

## Completion standard

The course is not complete until:

- the first viewport presents a cohesive, distinctive story world that a child can understand and wants to enter;
- the entry HTML and every promised lesson page open successfully;
- every lesson contains the actual teaching content, questions, answers, and feedback;
- every described game is a working interaction rather than a card explaining future gameplay;
- audio, images, data, styles, and scripts are available locally when they are part of the request;
- every pronunciation or listening course uses pre-generated local MP3 as its primary audio; browser or system speech synthesis is never the delivered audio source;
- progress, replay, reset, difficulty, responsive layout, and accessibility behavior work;
- the course runs offline under `file://` with no runtime network dependency;
- representative learning paths pass real-browser validation.

If the user explicitly requests only a philosophy, concept, proposal, or method, provide that narrower output. Otherwise build the courseware and its files.

## Route the references and resources

- Read [references/learning-science.md](references/learning-science.md) before defining the learning loop.
- Read [references/game-patterns.md](references/game-patterns.md) before choosing the course-level game spine.
- Read the relevant section of [references/subject-patterns.md](references/subject-patterns.md) for the requested subject.
- Read [references/visual-design.md](references/visual-design.md) before creating the learner-facing UI.
- Read [references/unified-paradigm-ui.md](references/unified-paradigm-ui.md) before copying or styling the bundled template for another course or AI agent.
- Read [references/implementation-spec.md](references/implementation-spec.md) before writing the course files.
- Read [references/qa-checklist.md](references/qa-checklist.md) before final validation.
- Copy [assets/unified-paradigm-ui](assets/unified-paradigm-ui) as the preferred working project for a multi-day offline HTML course. Treat its `ui-style.json` as the machine-readable design contract and run `node tools/validate_template.js` before and after adaptation.
- Inspect [demo.html](demo.html) for visual rhythm, hierarchy, color discipline, accessibility, and responsive behavior. Adapt its design principles to the child-facing course; do not reuse its adult proposal layout unchanged.
- Use `scripts/scaffold_course.py` when a multi-page course needs a consistent starting structure, then replace every scaffold placeholder with real structured content and renderers.
- Use `scripts/validate_game_diversity.py` and `scripts/validate_course_balance.py` for compatible generated courses.

When an applicable frontend-design skill is available, use it to choose and execute one distinctive visual direction before styling. The bundled visual reference supplies a quality floor, not a ceiling.

## 1. Establish the learner contract

Determine or reasonably infer:

- learner age and developmental stage;
- prior knowledge, language, reading level, and likely confusions;
- subject, scope, duration, daily study time, and mastery target;
- learning environment, offline or device constraints, and adult support;
- output language, pronunciation model, accessibility needs, and delivery folder;
- whether the user needs a ZIP; treat recorded local audio as required whenever pronunciation or listening is a learning objective.

Ask only when an unknown would materially change the curriculum or assets. Otherwise state the assumption and continue building.

## 2. Design backward from observable mastery

1. Write a measurable final outcome.
2. Decompose it into small prerequisite skills and content units.
3. Sequence them from concrete and familiar to independent transfer.
4. Assign each day one primary objective and a manageable new-content load.
5. Start Day 2 onward with retrieval from the immediately previous day.
6. Revisit older material after roughly three and seven days.
7. Define an exit task in which the child responds before seeing the answer.
8. Include both recognition and production evidence.

Keep daily volume appropriate for the age. Count real response opportunities, not merely content displayed on screen.

## 3. Build the daily learning loop

Use the 30% learning / 70% testing ratio as a working design budget:

| Order | Daily block | Mode | Share |
|---|---|---:|---:|
| 1 | Previous-day retrieval; prerequisites on Day 1 | Testing | 15% |
| 2 | Concise visual, audio, movement, or concrete micro-lesson | Learning | 20% |
| 3 | Worked example with fading support | Learning | 10% |
| 4 | Core game round A | Testing | 20% |
| 5 | Core game round B with production or transfer | Testing | 20% |
| 6 | Exit challenge, correction, and mastery decision | Testing | 15% |

A testing block begins with an unanswered prompt and includes the response, feedback, and optional retry. Watching an explanation does not count as testing.

Implement all six blocks:

- **Previous-day retrieval:** a real scored quiz drawn from prior content.
- **Micro-lesson:** a short interactive sequence with relevant visual or audio models and learner-controlled navigation.
- **Worked example:** full support → partial support → independent response.
- **Game A and Game B:** working controls, answer checking, and observable evidence.
- **Exit challenge:** an independent scored check saved to progress.

Do not render any block as placeholder prose telling the learner or parent what they could do.

## 4. Build a coherent game system

For a course of 10 or more days:

- select four to six core game engines from [references/game-patterns.md](references/game-patterns.md);
- use each selected engine at least three times across onboarding → consolidation → transfer;
- use only one or two focused games per day;
- include both recognition and production actions;
- vary content, representation, support, difficulty, and transfer context inside familiar rules;
- avoid disconnected one-off games and cosmetic reskins.

Every game must produce evidence for the current objective. A reward animation after an unrelated quiz is not an integrated learning game.

### Flip-card game quality and difficulty

Treat flip-card matching as a first-class learning engine rather than generic decoration.

Interaction requirements:

- start with cards covered and reshuffle on page load and every replay;
- use stable content keys for matching, never grid positions;
- keep the first card visible while the second is selected;
- play the matching local audio when an audio-enabled card opens;
- cover an incorrect pair after readable corrective feedback;
- keep a successful pair visible while allowing it to be covered and practised again;
- provide a matching-only reset that reshuffles without clearing unrelated course progress;
- keep cards keyboard operable, touch friendly, and understandable without relying on 3D transforms;
- ensure picture, word, phrase, audio, answer, and feedback all come from the same content record.

Scale the game by changing one main difficulty dimension at a time:

| Stage | Typical load | Pair relationship | Support |
|---|---:|---|---|
| Onboarding | 2–3 pairs | picture ↔ picture or picture ↔ spoken word | playable demonstration; generous reveal time |
| Early consolidation | 4 pairs | picture ↔ printed word | replayable audio; one optional location hint |
| Retrieval | 5 pairs | sound ↔ picture or picture ↔ hidden word | no fixed zones; hints appear only after repeated mismatch |
| Interleaving | 6 pairs | new and spaced-review items | similar but already-taught items; no answer labels on pictures |
| Transfer | 6–8 pairs | word ↔ short phrase, sound ↔ scene, or cross-representation pair | child predicts or speaks before locking a match |
| Mastery | 8 pairs by default | mixed cumulative relationships | independent round followed by a supported retry option |

Do not use time pressure as the default difficulty control for six-year-olds. If performance falls below the chosen mastery threshold, reduce pair count or restore one useful cue. If performance is secure across repeated rounds, increase only one of pair count, representational distance, distractor similarity, delay, or production demand.

## 5. Create real curriculum content

Store one structured source of truth for every learning item. Include fields appropriate to the subject, such as:

- stable key;
- target word, symbol, character, or concept;
- child-facing meaning;
- short example or phrase;
- pronunciation or audio path when relevant;
- semantic picture or visual model;
- mastery answer and plausible confusions;
- first-taught day and review schedule.

For English:

- connect sound, print, meaning, and use;
- pair each word with a clean picture that does not print the answer;
- provide a short memorable phrase when requested;
- generate separate local Edge TTS MP3 files for every word and every phrase;
- store the word-audio and phrase-audio paths on the same content record as the text, image, answer, and feedback;
- use familiar vocabulary rather than obscure words chosen only to satisfy a pattern;
- test listening, picture recognition, spoken recall, and short-phrase use.

Populate every promised day with its complete content. Verify requested totals programmatically when the user specifies an exact number of words, questions, lessons, or phrases.

## 6. Build the offline course system

For a multi-day HTML course, normally deliver:

- `index.html` with the course map, objectives, progress, and entry links;
- one dedicated `dayNN.html` page per day for courses of 10 or more days; use a single-page router only when the user explicitly asks for it;
- local shared CSS, JavaScript, structured course data, images, fonts, and audio;
- a consistent learner-facing navigation pattern on desktop and mobile;
- actual renderers for review, micro-lesson, fading example, games, and exit challenge;
- immediate, specific, encouraging feedback in an `aria-live` region;
- local progress persistence with activity replay, day reset, and course reset;
- randomized practice on every new attempt;
- audio speed, repeat, playing-state, and cancellation controls when pronunciation matters;
- a visible motion toggle and reduced-motion fallback;
- usage instructions for the parent or teacher;
- an optional ZIP after validation.

Avoid local `fetch()` dependencies. Load course data from a local script such as `window.COURSE_DATA`. Do not use CDNs, analytics, remote images, remote fonts, or runtime TTS requests.

### Start from the Unified Paradigm UI

Use the bundled [assets/unified-paradigm-ui](assets/unified-paradigm-ui) project as the default implementation starting point when the request needs a multi-day, game-based offline course:

- copy the complete folder into the delivery workspace; never make the delivered course depend on paths inside the installed skill;
- preserve its separate index and daily pages, six-stage 30/70 loop, responsive navigation, progress/reset behavior, audio controls, and escalating flip-card architecture unless the learner contract requires a change;
- replace the sample curriculum, visual world, asset mappings, storage key, title, and instructions with the requested course;
- reuse sample images or audio only when they are semantically correct and their usage rights fit; the template is an implementation paradigm, not mandatory subject matter;
- keep `template.json` and `tools/validate_template.js` synchronized with structural changes, and run the validator before packaging.

### Treat pronunciation audio as a build artifact

Whenever pronunciation, listening, phonics, spoken vocabulary, or oral language is part of the course:

- use Microsoft Edge TTS during the build to pre-generate local MP3 files;
- default English child-facing content to `en-US-AnaNeural` unless the requested accent or learner context requires another appropriate Microsoft Neural voice;
- generate one deterministic `<key>-word.mp3` and one `<key>-phrase.mp3` for every English learning item;
- test a short sample before the full batch, then generate the full set with `scripts/generate_edge_tts_audio.py`;
- keep generation-time network use separate from the delivered course: the finished HTML must play local files and remain fully offline;
- implement speed, repeat, cancellation, replay, and playing-state controls with `HTMLAudioElement`;
- use browser `speechSynthesis` only as an explicitly labeled emergency fallback for a missing or undecodable file, never as the primary audio implementation;
- fail validation when any expected MP3 is absent, empty, undecodable, or mapped to the wrong item.

Do not silently omit recorded audio or substitute system speech. If Edge TTS generation is blocked, report the blocker before claiming the course is complete.

## 7. Lead with a visually appealing, copyable UI system

Choose one coherent world, mascot, map, or story motif that persists across all days.

- Treat visual appeal as the primary learner-facing design principle and a completion criterion, while keeping pedagogy, accessibility, offline reliability, and legibility non-negotiable.
- Choose a subject-grounded palette, type system, layout concept, and one memorable signature element before coding; reject any choice that could belong unchanged to a generic dashboard.
- Hand another AI agent the complete template folder, [references/unified-paradigm-ui.md](references/unified-paradigm-ui.md), and `ui-style.json` together. Never ask it to recreate the UI from prose or screenshots.
- Make the learner-facing UI unmistakably playful and age-appropriate. An adult dashboard, proposal page, or generic component gallery is a visual QA failure even when it is technically functional.
- Use an asset-reuse-first workflow: prefer suitable bundled or local assets, then free/openly licensed cartoon illustration or high-quality cartoon-emoji image sets, and generate custom images only when no suitable resource exists or the user explicitly requests original art.
- Treat simple, clear, consistent pictures as sufficient. For large vocabularies, a coherent ready-made PNG/SVG/WebP set is usually better than generating every item from scratch.
- High-quality cartoon emoji-style image assets may serve as primary semantic visuals when they remain unambiguous at card size. Avoid raw platform-dependent Unicode emoji as the only learning image because their appearance changes across devices.
- Download or copy selected resources into the course for offline use. Record the source and license when attribution is required; never depend on remote image URLs at runtime.
- Map every learning item to a deliberate image or visual model from the same content record. Keep assessment images free of printed answer labels and crop them so the intended subject remains clear at card size.
- Keep one illustration language across the course instead of mixing unrelated libraries. For atlases, sprites, or individual files, verify every item mapping, source dimension, crop position, and decoded local file before delivery.
- Use large touch targets, short instructions, readable contrast, and low reading burden.
- Let the first successful action teach the interaction instead of front-loading instructions.
- Make learning progress visibly change something meaningful in the course world.
- Animate semantic actions and response consequences, not answer choices during thinking.
- Keep decorative motion subtle until the learner acts.
- Provide visible current, correct, retry, completed, and locked states with both text and graphical cues.
- Offer non-drag alternatives for drag interactions.
- Preserve dignity: no punitive scoring, forced countdowns, public rankings, shame, or manipulative reward loops.
- Test at a wide desktop viewport and at 390px without horizontal overflow.

Use [demo.html](demo.html) as a reference for polish and hierarchy, then reshape it into a simpler child-facing interface with age-appropriate navigation and content.

## 8. Enhance reference designs without copying them

When the user supplies a reference, read it completely and separate:

1. intent and success conditions;
2. useful learning and play mechanisms;
3. surface expression such as theme, characters, palette, rewards, and layout;
4. assumptions, gaps, and risks.

Retain, adapt, replace, or add elements according to the actual learner and objective. Preserve strong reasoning, not distinctive names or arbitrary details. The delivered courseware must be complete even when the reference is only a proposal.

## 9. Validate before delivery

Run [references/qa-checklist.md](references/qa-checklist.md) and verify in a real browser:

- every page and asset loads under `file://`;
- every promised lesson contains real interactive content;
- exact content totals and phrase limits match the request;
- Day 2 onward retrieves the immediately previous day;
- the 30/70 balance is represented by real response opportunities;
- the selected game engines recur and deepen across the course;
- flip-card order changes across reloads and replay;
- opened flip cards reveal and play the correct mapped content;
- every listening question has exactly one correct option;
- the expected Edge TTS MP3 count matches the audio-bearing content records, every MP3 decodes, and the page references local audio paths;
- feedback, retries, scoring, progress restore, and reset work;
- the file count includes the promised dedicated daily HTML pages, and every page contains the complete shared teaching loop rather than a placeholder;
- every learning item has a valid local image mapping, every image decodes at its intended dimensions, ready-made resources have compatible usage rights, and no core learning item relies only on a platform-dependent Unicode glyph;
- every visible learning-image surface has a nonzero rendered rectangle and either a decoded `<img>` (`naturalWidth > 0`) or a computed background image other than `none`; file existence alone does not prove that an image is visible;
- every empty element used as a background or sprite surface is `display: block`, grid, or flex with explicit width and height/aspect ratio; prefer a direct local image URL and verify any CSS-variable indirection in computed styles;
- every image preserves its source or atlas-cell aspect ratio unless it uses an intentional nondistorting crop such as `object-fit: cover`; never force both width and height to `100%` on mixed-ratio learning art;
- version local CSS and JavaScript URLs after renderer fixes, reload the actual daily page rather than a retired hash route, and reject results produced by stale cached assets;
- no answer label leaks through testing images;
- desktop and 390px mobile layouts stay within bounds;
- keyboard focus, contrast, reduced motion, and `aria-live` feedback remain usable;
- the console has no severe errors and the course makes no runtime network request.

For compatible courses, run:

```bash
python scripts/validate_game_diversity.py --course-data <course>/assets/course-data.js
python scripts/validate_course_balance.py <course-folder>
```

Do not claim a check passed unless it was actually run.

## 10. Deliver for immediate teaching

Provide:

- a direct link to the course entry file;
- the complete offline course folder;
- a ZIP when portability matters;
- Chinese usage instructions when the learner, parent, or teacher is Chinese-speaking;
- a concise summary of objectives, daily rhythm, progress, replay, reset, and audio controls;
- validation results and any remaining limitations.

Open the entry page after successful validation when working on a local desktop. The handoff should make it obvious how a parent or teacher can start the first lesson immediately.

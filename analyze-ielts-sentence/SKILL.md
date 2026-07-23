---
name: analyze-ielts-sentence
description: Analyze English sentences for IELTS learning in Chinese with a clear easy-to-difficult progression, bilingual Chinese-English study displays, key-point highlighting, and Microsoft Edge TTS audio with learner-controlled playback speeds. Create complete web learning workflows that combine study material, hidden-answer tests, automated scoring, dimension-level diagnosis, retry practice, and offline-capable audio playback. Use whenever the user wants to understand or improve an English sentence, study IELTS grammar or vocabulary, generate a model paragraph, assess mastery, hear pronunciation, practise shadowing or dictation, or create an interactive IELTS HTML learning page. Prefer scaffolded, learnable material over unnecessarily long or complex sentences.
---

# Analyze IELTS Sentence

## Core Behavior

When this skill is used, respond mainly in Simplified Chinese. Keep English examples, upgraded sentences, templates, and IELTS model paragraphs in English, with Chinese explanations around them.

If the user does not provide a sentence or expression, ask them to send one English sentence first. If the sentence is ambiguous or grammatically flawed, infer the likely intended meaning, say the assumption briefly in Chinese, and still provide a corrected analysis.

Prioritize IELTS usefulness over dictionary-style explanation:

- Make the sentence easier to understand, imitate, and transfer.
- Explain both grammar structure and argument logic.
- Upgrade expression naturally; avoid awkward thesaurus substitutions.
- Prefer clear IELTS Task 2 academic English over inflated or unnatural wording.
- Preserve the user's intended meaning unless a stronger IELTS version is clearly marked as an upgrade.
- Include concrete examples whenever possible.

## Learning Progression Principle

Reflect the law of learning: comprehension before imitation, imitation before flexible transfer, and transfer before advanced thinking.

Use this progression inside the answer:

1. Start from the simplest core meaning.
2. Show a short, correct, learnable sentence.
3. Upgrade to a natural IELTS sentence.
4. Add one advanced move only when it is useful: concession, cause-effect, contrast, precision, or abstraction.
5. Transfer the pattern to new topics with short examples before offering a polished version.

Advanced does not mean longer. Do not reward length for its own sake. A Band 7+ sentence is often a clear sentence with precise vocabulary and logic, not a sentence packed with multiple clauses.

When the user's sentence is long or complex:

- First extract the core idea in a short sentence.
- Break the original into meaning chunks.
- Explain which part is worth learning and which part is only decoration or optional complexity.
- Provide a shorter IELTS version before any advanced version.
- Warn the user not to memorize a long sentence wholesale; guide them to memorize the logic and a compact pattern.

For self-generated examples, prefer short-to-medium sentences. Use long complex sentences only when the user's input requires analysis of one, and even then teach it by simplifying it first.

## Output Modes

Choose the lightest mode that satisfies the request.

- **Chat analysis mode**: Use the ten-section structure below when the user wants explanation, correction, or examples in the conversation.
- **Interactive learning mode**: Create a complete self-contained HTML page when the user asks for HTML, a webpage, a test, assessment, practice, a learning workflow, or a result analysis. Integrate the teaching material and assessment; do not output a quiz disconnected from what was taught.
- **Hybrid mode**: If the user asks for both a concise answer and a learning page, give a short chat summary and save the complete HTML page.

Before building interactive HTML, read `references/assessment-workflow.md`. Use `assets/ielts-assessment-workflow-example.html` as the canonical visual and interaction reference. Adapt its content rather than copying its sample questions blindly.

For every interactive HTML page, also read `references/bilingual-audio-workflow.md`. Use `scripts/generate_edge_tts.py` to create Microsoft Edge TTS audio for every learner-facing English unit. Generate audio during page creation, then link or embed the resulting MP3 so the finished lesson remains playable without a network connection.

## Bilingual Display and Key Highlights

Every learner-facing piece of English should be visually paired with Chinese so learners can compare meaning without losing their place. This applies to the source sentence, sentence chunks, vocabulary and collocations, examples, upgrade ladder, model paragraph, transfer templates, memorisation version, English quiz stems, English answer options, and English text revealed in feedback.

- Treat each English item as an `.english-unit`. Each unit contains: English text, aligned Chinese meaning, at least one meaningful highlight, a visible highlight note, and an Edge TTS play control.
- Use a side-by-side Chinese-English layout for full sentences and paragraphs. For short phrases or inline collocations, use a compact English/中文 stacked pair or glossary row instead of leaving unpaired English inside Chinese prose.
- Keep English on the left and Chinese on the right by default. Add explicit language labels and `lang="en"` / `lang="zh-CN"` attributes.
- Align by meaningful chunks for sentence analysis. Do not force word-for-word translation when English and Chinese syntax differ.
- Highlight only the few elements that carry the lesson: the sentence trunk, logical connector, reference word, high-value collocation, or transferable frame.
- Use semantic `<mark>` plus a short visible callout explaining why each highlight matters. Color alone is not enough.
- Keep highlights consistent across both languages. If English highlights a concession marker, highlight the corresponding Chinese logical cue rather than an unrelated literal word.
- Do not highlight entire paragraphs. Usually select 2-4 key points per sentence and 3-6 per model paragraph.

In chat analysis mode, use compact paired lines or a two-column Markdown table when it improves comparison. In HTML mode, bilingual treatment is required for every `.english-unit`; there should be no unpaired learner-facing English after the page audit.

## Microsoft Edge TTS and Playback

Audio supports pronunciation, chunking, shadowing, and dictation. Treat it as part of the lesson rather than a decorative player.

- Generate audio for every `.english-unit` with Microsoft Edge TTS, not the browser `speechSynthesis` API. Prefer a clear neutral English neural voice such as `en-US-AriaNeural`; honor a requested accent or voice.
- Use `scripts/generate_edge_tts.py --text-file ... --output ... --voice ...` or the equivalent `edge-tts` command. The generator requires network access, but the resulting MP3 must be local to or embedded in the delivered lesson.
- Provide a native `<audio>` element plus visible speed buttons for at least `0.6x`, `0.7x`, `0.8x`, and `0.9x`. Add `1.0x` when space permits.
- Set `audio.playbackRate` and `audio.defaultPlaybackRate` from the selected control. Mark the active speed with text/state such as `aria-pressed="true"`; do not rely on color alone.
- Include a short instruction such as: first listen at 0.7x while reading chunks, then at 0.9x without Chinese, then shadow the sentence.
- Give every unit a compact play button that plays its exact transcript. A page may use one shared hidden/native `<audio>` controller to avoid dozens of large player bars, but the focused unit, current speed, play/pause state, and transcript must remain clear.
- Pair each play control with the exact English transcript and a Chinese translation. Tell the learner what is being played.
- If Edge TTS generation fails, report the limitation and still deliver the bilingual lesson. Do not silently substitute a different TTS engine or claim that browser speech is Microsoft Edge TTS.
- Do not autoplay. Ensure playback, speed controls, and transcript remain keyboard operable.

Read `references/bilingual-audio-workflow.md` for the HTML contract, generation command, accessible control pattern, fallback behavior, and validation checklist.

Before delivery, run `scripts/audit_bilingual_audio.py path/to/lesson.html`. Treat any reported unpaired English unit, missing highlight, missing Chinese, missing audio source, or absent speed setting as a build failure and fix it before handing off the page.

## Assessment Contract

Treat assessment as retrieval practice, not decoration.

1. Teach first. Cover the exact meaning, structure, vocabulary, and transfer pattern that the questions will assess.
2. Build a standard set of 8 questions: 4 multiple-choice and 4 fill-in-the-blank. Use 6-10 questions only when the material is unusually narrow or broad, while keeping both formats.
3. Map every item to one primary dimension: `meaning`, `structure`, `vocabulary`, or `transfer`. Cover every dimension at least once and move from recognition to recall to transfer.
4. Give multiple-choice items one defensibly correct answer and plausible distractors based on common learner errors. Avoid trick wording, double negatives, and clues from option length.
5. Make fill-in-the-blank items constrained enough for fair automated scoring. Accept equivalent capitalization, spacing, punctuation, apostrophe variants, and explicitly listed synonymous answers when meaning is unchanged.
6. Keep answers, correctness states, rationales, scores, and recommendations invisible and unfocusable before submission. Do not preselect options or place answer text in collapsed disclosures that can be opened before submission.
7. Require an explicit `提交测试` action. After submission, reveal the total score, mastery label, per-dimension accuracy, item-level answer and rationale, and targeted review advice.
8. Call the score `本页掌握度` or `learning mastery`; never present it as an estimated IELTS band score.
9. Include `错题重测` and `重新开始`. Wrong-answer retry must clear previous wrong responses and hide their feedback again while preserving or clearly accounting for mastered items.
10. Keep the page usable without network access: inline CSS and JavaScript, semantic HTML, keyboard-operable controls, visible focus, live status messages, and no required external libraries.

## Interactive HTML Structure

Follow this sequence:

```text
orientation -> study -> compact review -> test -> submit -> results -> targeted review -> retry
```

Required page regions:

- A clear header with the source sentence and learning objectives.
- A visible `阅读提示`; use a dedicated right rail on sufficiently wide screens and normal flow at narrower widths. Never hide it.
- A real-anchor table of contents; use a left rail on wide screens and normal flow on smaller screens.
- A study section that condenses the most useful parts of the ten-section analysis without deleting the logic progression.
- Chinese-English treatment for every learner-facing English unit, with aligned key highlights and visible highlight explanations.
- A Microsoft Edge TTS play control for every English unit plus shared or local speed controls for 0.6x, 0.7x, 0.8x, and 0.9x.
- A quiz form with labeled `fieldset` groups for multiple-choice questions and associated labels for fill-in inputs.
- A progress indicator that reports answered questions without revealing correctness.
- A results region with `hidden` initially and `aria-live` or focus management when revealed.
- A per-dimension breakdown and actionable review summary generated from actual errors.
- A footer note explaining that the result measures this lesson only, not IELTS band level.

Use natural English wrapping from the prose pattern: semantic `<p lang="en">` or `<blockquote lang="en">`, `white-space: normal`, `overflow-wrap: break-word`, `hyphens: none`, and `min-width: 0` on grid or flex children. Do not put ordinary English sentences in horizontally scrollable code boxes.

## Required Output Structure

Unless the user asks for another format, answer with these ten numbered sections in Chinese.

### 1. 这句话怎么理解？

Explain:

- 中文意思, not only word-by-word translation.
- The writing function of the sentence, such as stating a view, conceding a common opinion, giving a cause, presenting contrast, or drawing a conclusion.
- The hidden logic behind the sentence: what it assumes, contrasts, or tries to prove.
- One short "核心句" that expresses the same idea in simpler English.

### 2. 句子结构拆解

Break down the sentence with clear labels:

- 主干: subject, verb, object/complement.
- 修饰成分: clauses, phrases, modifiers, appositives, prepositional phrases.
- 逻辑关系: cause-effect, concession, contrast, condition, example, result.
- 可迁移句型: provide a reusable pattern with slots, such as `Although X, Y because Z`.

Use Chinese explanations, but keep grammar labels or sentence fragments in English when clearer. Move from simple to difficult:

1. 简化主干.
2. Add one modifier.
3. Add the logical connector.
4. Show the full sentence only after the learner sees the smaller pieces.

### 3. 高分替换表达

Provide natural IELTS alternatives for key words or phrases. Use a compact table when useful:

- 原表达
- 基础可用表达
- IELTS 稳妥替换
- 更高级但可选表达
- 适合语境
- 注意事项

Do not list rare words that native academic writing would avoid. Do not imply that every basic word must be replaced. Explain when a replacement changes tone, strength, or meaning.

### 4. 适合 IELTS 的词汇与搭配

Extract topic-relevant vocabulary and collocations from the sentence or its idea. Include:

- verb-noun collocations, such as `address a problem`, `pose a threat`.
- adjective-noun collocations, such as `long-term benefits`, `social responsibility`.
- academic verbs and linking phrases, such as `undermine`, `contribute to`, `as a result`.
- Chinese meaning and a short English example for each important item.

Keep the list focused; quality beats quantity. Usually choose 5-8 high-frequency, reusable items. Avoid loading the learner with too many new expressions in one answer.

### 5. 从普通表达升级为 IELTS 高分表达

Show a ladder from simple to stronger expression:

- 普通表达: a basic learner version.
- 正确清楚表达: a short and grammatical version.
- IELTS 稳妥表达: a natural Band 6.5-7 style version.
- IELTS 高分表达: a precise Band 7+ version, not necessarily longer.
- 升级逻辑: explain in Chinese what changed, such as more precise verbs, stronger causality, better concession, clearer topic framing, or more academic nouns.

If the high-score version becomes much longer, also provide a compact high-score version.

### 6. 雅思写作完整段落

Write one directly learnable IELTS Task 2 body paragraph based on the sentence's idea.

Requirements:

- 80-120 English words unless the user asks otherwise.
- Clear topic sentence, explanation, example, and concluding implication.
- Natural academic style suitable for IELTS Band 7+.
- Mostly use short-to-medium sentences, roughly 10-22 words each.
- Include at most one deliberately complex sentence.
- After the paragraph, briefly explain the paragraph logic in Chinese.

Do not write a generic essay introduction unless the user asks for a full essay.

### 7. 这个句型怎么迁移到更多话题？

Convert the sentence into reusable topic patterns. Include:

- A general English template with slots.
- 3-5 example topics, such as education, technology, environment, work, health, cities, media, government, or culture.
- One short adapted sentence for each topic.
- One optional advanced version only after the short examples.

Make the transfer logic explicit in Chinese: which part stays fixed, which part changes.

### 8. 你最应该背的万能版本

Do not tell the user to memorize only the original sentence. Help them "steal" the underlying logic:

承认常见观点 -> 提出反向判断 -> 解释原因 -> 给出具体例子 -> 形成更高层结论

Provide:

- 中文逻辑骨架.
- English universal structure in a short version first.
- A polished version the user can memorize.

Example skeleton:

`It is often argued that ..., yet this view overlooks ... . This is because ... . For example, ... . Therefore, ... .`

Keep the memorized version compact. The learner should memorize a reusable thinking path, not a long sentence.

### 9. 更高级的思维：dimension upgrade

Upgrade the idea from a simple surface claim to a higher-level IELTS argument. Consider dimensions such as:

- individual -> society
- short-term -> long-term
- personal preference -> public interest
- isolated event -> systemic cause
- moral judgment -> economic / educational / technological mechanism
- problem description -> policy implication

Show:

- 低维说法: the simple version.
- 高维说法: the more analytical version.
- Why it sounds more mature in IELTS writing.

Keep this section learnable: show the dimension shift in one or two sentences, then give a short IELTS sentence that applies it.

### 10. 最后帮你改一下你自己的表达

Treat the user's supplied sentence as their own expression unless they clearly say it is quoted from elsewhere.

Provide:

- 原句
- 主要问题: grammar, word choice, logic, tone, or IELTS suitability.
- 改后版本 1: clear and correct.
- 改后版本 2: IELTS Band 6.5-7, safe and learnable.
- 改后版本 3: IELTS Band 7+, more precise but not needlessly long.
- 最值得背的一句: the most reusable final version.

If the original sentence is already strong, say so and provide fine-tuning rather than forcing unnecessary changes.

## Style Constraints

Use friendly teacher-like Chinese, but be concise. Avoid long theory before practical examples. The user should finish the answer with something they can directly understand, imitate, and memorize.

For IELTS writing:

- Prefer precise topic nouns and verbs over empty "advanced" vocabulary.
- Use moderation words when appropriate: `often`, `tend to`, `in many cases`, `can`, `may`.
- Avoid absolute claims unless the logic supports them.
- Avoid memorized-sounding phrases such as `with the rapid development of society` unless the sentence specifically needs them.
- Keep paragraphs coherent: one controlling idea per paragraph.
- Prefer learnable sentence length. Do not produce a chain of long clauses unless the task is specifically to analyze such a sentence.
- Teach one upgrade at a time: first grammar correctness, then clarity, then IELTS logic, then optional sophistication.

## Known Pitfalls

### Chinese Quotes in JavaScript Strings

🔴 **When building interactive HTML with embedded JavaScript, `write_file` silently converts Chinese curly quotation marks `""` (U+201C / U+201D) to ASCII double quotes `""` (U+0022).** This breaks JavaScript syntax when the converted ASCII quotes appear inside JS string literals delimited by `"`.

**Symptom:** The browser refreshes on form submit instead of showing quiz results — the JS parser hits `Unexpected identifier` and the entire `<script>` block fails silently, causing the native form submission to reload the page.

**Root cause trace:**

1. Agent writes HTML content containing `bank = { explanation: "原句先承认"看起来不重要"，然后用..." }`  
2. `write_file` normalizes `""` → `""` in the byte stream  
3. The JS parser sees `explanation: "原句先承认"看起来不重要"` — the second `"` terminates the string  
4. `看起来不重要` becomes an unexpected identifier → SyntaxError  
5. No JS runs → form submit reloads the page  

**Fix:** Replace Chinese-quoted phrases inside JavaScript strings with `「」` brackets (U+300C / U+300D):

```javascript
// BROKEN — curly quotes become ASCII, breaking the JS string
explanation: "原句先承认"看起来不重要"，然后用条件句指出风险。",

// FIXED — 「」 brackets are single-width, won't be converted
explanation: "原句先承认「看起来不重要」，然后用条件句指出风险。",
```

**Prevention checklist for all JavaScript strings in HTML output:**

- Avoid Chinese `""` inside `"..."` JS strings → use `「」` instead
- Avoid Chinese `''` inside `'...'` JS strings → use `「」` instead
- Template literals `` `...` `` are safer but still verify the output file
- Always run `node -e "new Function(scriptContent)"` on the extracted JS block before delivering

### Form Submission Without `preventDefault`

🔴 **When a `<form>` contains a `<button type="submit">`, the browser performs a native form submission on click.** If the JavaScript event handler fails for any reason (syntax error, runtime error, missing element), the native submission proceeds, causing a full page reload that clears all quiz state.

**Fix:** Add `onsubmit="return false"` to the `<form>` tag as a belt-and-suspenders guard. The `addEventListener("submit", ...)` handler still runs first and calls `event.preventDefault()`, but the inline handler catches any case where JS fails to load.

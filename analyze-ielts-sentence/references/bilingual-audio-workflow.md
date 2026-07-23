# Bilingual Display and Microsoft Edge TTS Workflow

Use this reference for every interactive HTML lesson created by `analyze-ielts-sentence`. The coverage rule is universal: every learner-facing English item needs Chinese alignment, a meaningful highlight, a visible explanation, and Microsoft Edge TTS playback.

## Coverage rule

Mark every learner-facing English container with `class="english-unit"`. This includes:

- header/source sentence
- sentence chunks and grammar fragments
- vocabulary, collocations, and their examples
- every rung of an upgrade ladder
- model paragraphs and transfer examples
- reusable templates and memorisation sentences
- English quiz stems, cloze sentences, answer options, and submitted English feedback

UI-only text such as `English`, `IELTS`, voice names, file names, and speed labels does not need a separate unit. Everything the learner is expected to understand, imitate, choose, complete, or remember does.

Each `.english-unit` must include or reference:

- an English transcript (`[lang="en"]`)
- an aligned Chinese rendering (`[lang="zh-CN"]`)
- at least one `<mark>` in the English and the corresponding Chinese emphasis when meaningful
- a visible `.highlight-note`
- a `.tts-play` control with `data-audio-src` pointing to a non-empty Edge TTS MP3

Use one shared audio controller for compactness. Clicking a unit's play button loads its `data-audio-src`, announces the unit label, and plays at the currently selected rate. This gives every English item audio without repeating a full native player in every row.

## Learning purpose

The bilingual view should reduce lookup friction while preserving English processing. Audio should train perception and production in three passes:

1. Listen at `0.7x` while following highlighted chunks.
2. Listen at `0.9x` while hiding or ignoring Chinese.
3. Replay and shadow the full English sentence.

## Bilingual HTML contract

Pair English and Chinese in the same semantic component:

```html
<section class="bilingual-pair english-unit" aria-labelledby="source-pair-title">
  <h3 id="source-pair-title">原句对照</h3>
  <div class="bilingual-grid">
    <div class="language-panel" lang="en">
      <span class="language-label">English</span>
      <p><mark>Although</mark> X, Y <mark>because</mark> Z.</p>
    </div>
    <div class="language-panel" lang="zh-CN">
      <span class="language-label">中文</span>
      <p><mark>尽管</mark> X，Y，<mark>因为</mark> Z。</p>
    </div>
  </div>
  <ul class="highlight-notes" aria-label="重点说明">
    <li><strong>让步：</strong><span lang="en">Although</span> 先承认背景。</li>
    <li><strong>原因：</strong><span lang="en">because</span> 引出论据。</li>
  </ul>
  <button class="tts-play" type="button"
          data-audio-src="audio/source.mp3"
          data-audio-label="原句">播放英语</button>
</section>
```

Use this responsive foundation:

```css
.bilingual-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.language-panel { min-width: 0; padding: 1rem; background: var(--surface); }
mark {
  padding: 0 .12em;
  color: inherit;
  background: #fff0a8;
  border-bottom: 2px solid #a76b00;
}
@media (max-width: 700px) {
  .bilingual-grid { grid-template-columns: 1fr; }
}
```

Keep English on the left and Chinese on the right. Stack naturally on mobile. Use meaningful phrase alignment rather than literal word alignment.

## What to highlight

Select only information that changes comprehension or transfer:

- sentence trunk
- logical connector
- pronoun or reference target
- high-frequency IELTS collocation
- reusable frame
- one sentence in the model paragraph that performs the key argumentative move

Use at least one highlight in every English unit, normally 2-4 in a sentence. For a single-word vocabulary unit, the word itself may be marked and the note can identify pronunciation, meaning, register, or collocation. Every highlight needs a nearby text explanation. Do not encode different categories with color alone; add labels such as `让步`, `主干`, `因果`, or `搭配`.

## Generate Microsoft Edge TTS audio

Create a UTF-8 text file containing only the English transcript, then run:

```bash
python scripts/generate_edge_tts.py \
  --text-file transcript.txt \
  --output lesson-audio.mp3 \
  --voice en-US-AriaNeural
```

The helper validates the input and writes the MP3 atomically. Audio generation requires network access. Playback does not, provided the MP3 is delivered beside the HTML or embedded as a data URL.

Generate at a natural base rate. Learners change speed in the browser; this avoids storing four duplicate audio files. Generate one MP3 for each unique English transcript and reuse it when the exact same text appears more than once.

## Accessible player and speed controls

```html
<section class="audio-practice" aria-labelledby="audio-title">
  <h3 id="audio-title">听读训练</h3>
  <p>播放内容：原句。先用 0.7x 跟读分块，再用 0.9x 脱离中文复述。</p>
  <audio id="source-audio" controls preload="metadata">
    <source src="lesson-audio.mp3" type="audio/mpeg">
    你的浏览器不支持音频播放，请阅读下方英文文本。
  </audio>
  <div class="speed-controls" role="group" aria-label="播放速度">
    <button type="button" data-speed="0.6" aria-pressed="false">0.6x</button>
    <button type="button" data-speed="0.7" aria-pressed="true">0.7x</button>
    <button type="button" data-speed="0.8" aria-pressed="false">0.8x</button>
    <button type="button" data-speed="0.9" aria-pressed="false">0.9x</button>
    <button type="button" data-speed="1" aria-pressed="false">1.0x</button>
  </div>
  <p class="audio-status" aria-live="polite">当前速度：0.7x</p>
</section>
```

```javascript
const audio = document.querySelector("#source-audio");
const speedButtons = document.querySelectorAll("[data-speed]");
const speedStatus = document.querySelector(".audio-status");

function setSpeed(speed) {
  audio.playbackRate = speed;
  audio.defaultPlaybackRate = speed;
  speedButtons.forEach(button => {
    button.setAttribute("aria-pressed", String(Number(button.dataset.speed) === speed));
  });
  speedStatus.textContent = `当前速度：${speed.toFixed(1)}x`;
}

speedButtons.forEach(button => {
  button.addEventListener("click", () => setSpeed(Number(button.dataset.speed)));
});
setSpeed(0.7);
```

For a shared-player page, keep one native `<audio>` element and one global speed group. Each `.tts-play` button supplies its own `data-audio-src`; the selected global speed persists as the learner moves between units. Update an `aria-live` status with the unit label, current rate, and play/pause state.

## Offline and fallback behavior

- Inline CSS and JavaScript as before.
- Store MP3 files beside the HTML using relative paths, or embed them when the user requires one-file delivery.
- Do not call an online TTS endpoint from the browser page.
- Do not use `speechSynthesis` as a silent fallback. It is platform-dependent and is not proof of Microsoft Edge TTS.
- If generation fails, keep the transcript, translation, and highlights. State clearly that audio was not generated and provide the exact retry command.

## Validation checklist

- Run `scripts/audit_bilingual_audio.py lesson.html` and require a clean result.
- Confirm every `.english-unit` has English, Chinese, a mark, a highlight note, and a TTS play control.
- Confirm no learner-facing English remains outside an `.english-unit` except the documented UI-only exclusions.
- Confirm the source sentence and key upgraded sentence have explicit key-point highlights.
- Confirm each highlight has a visible explanation and does not rely on color alone.
- Confirm the MP3 exists and is non-empty; check its path matches the `<source src>` value.
- Confirm speed buttons include `0.6`, `0.7`, `0.8`, and `0.9`.
- Confirm clicking each button changes both `playbackRate` and `aria-pressed`.
- Confirm there is no autoplay and all controls are keyboard operable.
- Confirm mobile layout stacks without horizontal overflow.
- Confirm the final HTML remains usable when disconnected from the network.
- Parse every inline script before delivery.

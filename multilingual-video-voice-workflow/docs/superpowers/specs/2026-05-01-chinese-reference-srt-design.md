# Chinese Reference SRT Design

## Goal

Add an independent Chinese reference SRT file for each generated target-language SRT so video editing can be done with side-by-side timing alignment.

The Chinese reference SRT should:

- reuse the exact same subtitle indices as the target-language SRT
- reuse the exact same timestamps as the target-language SRT
- translate only the subtitle body text into Chinese
- be written as a separate file next to the target-language SRT

## Chosen Approach

Use the generated target-language segments as the source for Chinese reference translation, then write a Chinese SRT with the same per-segment timing already computed from the final MP3 durations.

This is the smallest and safest change because the time axis already belongs to the spoken target-language audio. Reusing that timing guarantees that the Chinese reference SRT stays aligned with the actual audio and does not require any extra segmentation reconciliation.

## Non-Goals

- changing the target-language SRT format or naming
- merging target-language and Chinese text into one bilingual SRT
- recomputing timestamps for Chinese content
- translating directly from source text to Chinese for this feature

## Output Behavior

For every generated voice variant:

- keep the existing target-language SRT unchanged
- add a new Chinese reference SRT file with the same cue count and timing

Recommended naming:

- target-language SRT: `*_BanuNeural.srt`
- Chinese reference SRT: `*_BanuNeural_zh-CN.srt`

## Data Flow

1. Clean and segment the source text.
2. Translate source segments into the target locale.
3. Generate MP3 files and compute final cue timings from the target-language audio.
4. Reuse the target-language segments and translate them into Chinese.
5. Write a separate Chinese SRT using:
   - the same cue indices
   - the same start and end timestamps
   - the translated Chinese subtitle text

## Integration Point

The cleanest integration point is inside or immediately after `generate_tts_and_srt(...)`.

That function already has:

- the ordered target-language segment list
- the exact timestamp progression derived from audio durations
- the output voice-specific file naming context

The change should capture cue timing in a structured form once, then reuse it to write:

- the target-language SRT
- the Chinese reference SRT

## Translation Rules

- Translate from target-language segment text to `zh-CN`
- Preserve protected brand names when possible using the existing protected-term masking approach
- Do not alter subtitle numbering or timing
- If the target locale is already Chinese, skip generating the extra Chinese reference SRT

## Manifest Changes

Each voice entry in the manifest should gain a Chinese reference SRT path, for example:

- `reference_srt_path`

This allows downstream automation to discover both the spoken-language SRT and the Chinese reference SRT without filename guessing.

## Error Handling

- If Chinese translation fails, stop the workflow with a readable error
- Do not silently skip the Chinese reference SRT if the feature is enabled
- If the target locale is `zh-CN` or `zh-TW`, skip the extra file and record an empty or omitted reference path

## Testing

Add tests for:

- writing a Chinese reference SRT with the same cue numbers and timestamps
- translating target-language text into Chinese reference text
- manifest voice entries including the Chinese reference SRT path
- skipping Chinese reference SRT generation when the target locale is already Chinese

## Recommended Implementation Shape

Keep the feature in the existing script and add focused helpers:

- `translate_segments_to_reference_chinese(...)`
- `write_srt_from_cues(...)`
- `build_reference_srt_path(...)`

Represent SRT cues as structured records during generation so both SRT outputs can be written from the same timing data.

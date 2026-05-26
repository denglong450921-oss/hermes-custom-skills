# Multilingual Video Voice Workflow Enhancements Design

Date: 2026-05-01
Scope: `multilingual-video-voice-workflow`
Status: Draft for user review

## Summary

This design upgrades the current multilingual video voice workflow to solve four problems discovered in real use:

1. Protected brand names are preserved, but cannot be spoken using target-language-friendly phonetics.
2. Long-running steps do not print usable progress, which makes it hard to know whether the workflow is healthy.
3. Supported language labels are incomplete and reject valid user input such as Azerbaijani.
4. Cleaning decisions are not recorded, which allows repeated mistakes such as carrying source numbering into translated speech text.

The implementation keeps the current single-script entrypoint so existing skill calls do not break.

## Goals

- Support explicit pronunciation dictionaries for brand names, acronyms, and cultural terms.
- Print visible stage and item progress during cleaning, translation, TTS generation, and subtitle writing.
- Expand language resolution so common English labels, Chinese labels, ISO codes, and locale codes work consistently.
- Record cleaning and resolution decisions in a machine-readable manifest for later review.
- Prevent source numbering from leaking into translated segments, subtitle content, and spoken audio.

## Non-Goals

- Building a GUI or progress bar outside the terminal.
- Replacing the translation engine.
- Replacing Edge TTS.
- Solving perfect transliteration automatically for unknown terms without a dictionary entry.

## Current Problems

### Pronunciation Gap

The current workflow only supports `protected_terms`, which prevents translation but does not control speech output. Terms such as `WFM` can remain unchanged in text while still being spoken unnaturally by the target voice.

### Progress Visibility Gap

The script prints only the final manifest. Users cannot tell whether the run is stalled in translation, TTS, or audio duration analysis.

### Language Resolution Gap

The script uses a small hand-maintained alias map. Valid labels such as `Azerbaijani`, `阿塞拜疆语`, or `az-AZ` are not handled consistently.

### Cleaning Audit Gap

The current markdown normalization removes only numbering patterns like `1. ` with a trailing space. Inputs such as `1.WFM` survive cleaning and leak into translated output and subtitles. The workflow also does not record which cleaning rules were applied.

## Recommended Approach

Keep one main script, but introduce focused internal helpers and structured result objects. This preserves the current invocation model while making behavior explicit and auditable.

## Architecture

The script remains `scripts/multilingual_video_workflow.py`, but is reorganized into these logical stages:

1. Input resolution
2. Cleaning and normalization
3. Language resolution
4. Term protection and pronunciation planning
5. Translation
6. Voice selection
7. TTS generation
8. Subtitle generation
9. Manifest and review artifact output

Each stage returns structured data instead of only plain strings. The manifest is built from these results.

## Data Model Additions

### Cleaning Report

Add a structure similar to:

```json
{
  "input_file": "...",
  "cleaned_file": "...",
  "rules_applied": [
    "removed_markdown_heading",
    "removed_list_marker",
    "removed_leading_number_token"
  ],
  "numbering_detected": true,
  "numbering_removed_line_count": 18,
  "empty_lines_preserved": 17
}
```

### Language Resolution Report

Add a structure similar to:

```json
{
  "requested_label": "阿塞拜疆语",
  "resolved_locale": "az-AZ",
  "resolution_source": "alias_map",
  "translator_code": "az",
  "available_voice_locales": ["az-AZ"]
}
```

### Pronunciation Entry

Add a configurable dictionary entry shape:

```json
{
  "term": "WFM",
  "display_text": "WFM",
  "tts_text_by_locale": {
    "az-AZ": "double-u ef em",
    "en-US": "double-u ef em"
  }
}
```

`display_text` is used in review markdown and subtitles. `tts_text_by_locale` is used only for speech generation.

## Cleaning Design

### Input Numbering Rules

The cleaning stage must remove common source numbering forms before segmentation:

- `1.`
- `1. `
- `01.`
- `01)`
- `1)`
- `1 -`

The rule must target only leading numbering tokens at the beginning of a line so real content is not damaged.

### Cleaning Output

The workflow should save a cleaned intermediate file next to the final output artifacts. This file is an audit artifact, not a replacement for the user source file.

Recommended naming:

- `*_cleaned_input.md`

### Output Numbering Rule

Output numbering becomes an explicit workflow setting:

- Review markdown files may keep generated numbering.
- Subtitle body text and TTS input text must never include source numbering.
- The manifest records whether generated numbering was added to review files.

## Pronunciation Design

### Behavior

The workflow applies pronunciation handling in two layers:

1. Protected terms: do not translate.
2. Pronunciation dictionary: replace the term with locale-specific TTS text only for speech generation.

This gives the following behavior:

- Review markdown shows `WFM`
- Subtitle text shows `WFM`
- TTS input for `az-AZ` uses `double-u ef em` or another configured phonetic spelling

### Matching Rules

- Exact term match first.
- Longer terms win before shorter terms to avoid partial overlap.
- Dictionary application happens after translation masking logic is restored, so display text remains stable.

### Fallback Rules

- If a term has no pronunciation entry for the target locale, keep the original display text for TTS input.
- Do not auto-guess phonetics in this phase.
- The manifest records unresolved pronunciation terms so the user can add them later.

## Progress Reporting Design

### Terminal Format

Use human-readable fixed-format messages:

```text
[1/6] Cleaning input
[1/6] Cleaning input: removed numbering on 18 lines
[2/6] Resolving language: 阿塞拜疆语 -> az-AZ
[3/6] Translating: 7/25
[4/6] Generating TTS (az-AZ-BanuNeural): 12/25
[5/6] Writing subtitles: 1/1
[6/6] Writing manifest
```

### Reporting Rules

- Print stage start and stage completion.
- Print item counters for translation and TTS loops.
- Print selected output directory and chosen voices before TTS begins.
- Print actionable errors with stage context.

This format is intentionally simple and terminal-friendly. It avoids fancy progress bars that break logs or remote shells.

## Language Resolution Design

### Resolution Sources

Language resolution uses this order:

1. Exact locale code such as `az-AZ`
2. Built-in alias map for common English and Chinese labels
3. ISO code aliases such as `az`
4. Runtime-discovered locales from `edge-tts --list-voices`
5. Base-language fallback only when the resolved locale is still valid for translation and voice selection

### Built-In Additions

The built-in alias map should add at least:

- `azerbaijani`
- `azeri`
- `az`
- `阿塞拜疆语`
- `阿塞拜疆文`

The alias layer should remain easy to extend without editing multiple maps by hand.

### Voice Selection Rules

- Prefer female voices for the exact target locale.
- If the locale has fewer voices than requested, report the shortfall clearly.
- Do not silently fall back to a different language locale for speech generation.
- Allow explicit voice override to bypass automatic selection.

## Manifest Design

The final manifest expands from a file index into an audit record. New top-level keys:

```json
{
  "source_file": "...",
  "cleaned_input_path": "...",
  "target_locale": "az-AZ",
  "language_resolution": {},
  "cleaning_report": {},
  "pronunciation_report": {
    "matched_terms": [],
    "unresolved_terms": []
  },
  "output_numbering": {
    "review_files_numbered": true,
    "tts_contains_source_numbers": false,
    "subtitle_contains_source_numbers": false
  },
  "voices": []
}
```

## Skill Documentation Updates

`SKILL.md` should be updated to explain:

- language labels can be provided as locale, English name, Chinese name, or ISO code
- pronunciation dictionaries are supported for brand names and acronyms
- terminal progress is printed during execution
- cleaned intermediate files and manifest audit records are produced
- review markdown may be numbered, but spoken text and subtitles are cleaned of source numbering

## Testing Strategy

Add focused coverage for the most failure-prone logic:

1. Cleaning strips `1.WFM` and `01)` forms correctly.
2. Cleaning does not remove legitimate content in the middle of a line.
3. Language resolution accepts `Azerbaijani`, `阿塞拜疆语`, `az`, and `az-AZ`.
4. Pronunciation dictionary keeps subtitle text unchanged while TTS text changes.
5. Voice selection reports insufficient native female voices clearly.
6. Manifest contains cleaning and pronunciation audit fields.

If formal automated tests are too heavy for the current skill layout, provide at minimum a documented manual verification recipe.

## Rollout Plan

1. Refactor script into internal helper functions without changing CLI shape.
2. Add cleaning audit and cleaned input artifact.
3. Add language resolution expansion and runtime locale discovery.
4. Add pronunciation dictionary support for TTS-only text conversion.
5. Add progress reporting across all stages.
6. Update manifest schema and `SKILL.md`.
7. Run one regression check using the existing WFM script example.

## Open Decisions Already Resolved

- Pronunciation policy: explicit dictionary wins over automatic guessing.
- Progress style: stage plus item counts in terminal output.
- Audit style: write persistent manifest records instead of relying only on terminal output.

## Risks

- Runtime locale discovery can expose voices unsupported by the translation backend, so locale-to-translator mapping must remain validated.
- Pronunciation dictionaries can become hard to manage if stored inline only; they should be easy to externalize later.
- More manifest data increases output size, but the gain in traceability is worth it.

## Acceptance Criteria

- The workflow accepts `Azerbaijani`, `阿塞拜疆语`, `az`, and `az-AZ` without failure.
- Source numbering such as `1.WFM` is removed before translation and never appears in TTS or subtitle body text.
- A run prints visible progress throughout translation and TTS loops.
- `WFM` can stay visible in text artifacts while using locale-specific speech text during TTS.
- The manifest explains how input was cleaned and how the target language was resolved.

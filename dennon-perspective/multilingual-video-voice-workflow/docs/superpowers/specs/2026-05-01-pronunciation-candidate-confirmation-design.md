# Pronunciation Candidate Confirmation Design

## Goal

Add a user-confirmed pronunciation workflow so brand names and acronyms do not need to be pre-authored in a static dictionary before every run.

The workflow should:

- scan cleaned input text for high-confidence pronunciation candidates
- pause before translation and TTS when review is required
- write a reviewable candidate file for the user to confirm or edit
- generate a run-specific pronunciation dictionary from the confirmed file
- keep global defaults intact unless explicitly reused

## Non-Goals

- fully automatic phonetic guessing for all brands without user review
- replacing the existing global default pronunciation dictionary
- building a GUI or browser-based editor for confirmation

## User Experience

### First Pass

The user runs the workflow as usual. After input cleaning, the script extracts conservative candidate terms and writes a pending review file into the output directory. The script then exits with a clear message telling the user to review the generated file and rerun with confirmation enabled.

### Review File

The review file is markdown so it can be opened and edited easily in the IDE. Each candidate appears as a structured block with:

- `term`: the original detected term
- `status`: `pending`, `confirmed`, or `ignore`
- `display_text`: what should remain visible in subtitles
- `tts_text_by_locale.<locale>`: what TTS should speak for the current target locale
- `notes`: optional human comments

### Second Pass

The user updates the review file, setting a candidate to:

- `confirmed` and filling in a phonetic TTS value
- `ignore` if the default reading is acceptable

On rerun, the script validates that no `pending` entries remain, converts confirmed entries into a run-specific JSON dictionary, and continues with translation and TTS.

## Candidate Extraction

The default mode is conservative to reduce false positives. A term is considered a candidate if it matches one of these patterns:

- uppercase acronyms of length 2 to 10, such as `WFM` or `MENA`
- title-case or camel-case words that look like branded names, such as `Nexora`
- mixed alphanumeric brand-like tokens, such as `QBX360`
- repeated proper-looking Latin tokens that appear more than once

The extractor excludes:

- pure numbers
- common sentence-start capitalization that appears only once
- obvious file extensions and URLs
- placeholders already used internally by the workflow

## File Outputs

The workflow adds these run-specific artifacts:

- `*_pronunciation_candidates.md`: editable candidate review file
- `*_pronunciation_dictionary.json`: generated from confirmed entries only

The existing manifest gains:

- `pronunciation_candidates_path`
- `generated_pronunciation_dictionary_path`
- `pronunciation_candidate_report`
  - `detected_terms`
  - `confirmed_terms`
  - `ignored_terms`
  - `pending_terms`
  - `requires_user_review`

## Control Flow

1. Read and clean input.
2. Extract pronunciation candidates from cleaned paragraphs and source segments.
3. If candidate review is enabled and no confirmed review file exists:
   - write the candidate markdown file
   - write manifest metadata indicating review is required
   - stop before translation/TTS with a clear instruction
4. If a candidate file exists:
   - parse user decisions
   - fail fast if any entries are still `pending`
   - generate the run-specific JSON pronunciation dictionary
5. Continue with translation, TTS, subtitles, and final manifest output.

## CLI Changes

Add these flags:

- `--pronunciation-review-mode` with values `auto`, `off`, `require`
- `--pronunciation-candidates-file` to explicitly point at an edited review file

Defaults:

- `auto`: extract candidates and require review only if candidates were found
- `off`: skip candidate extraction and use only the default dictionary
- `require`: always create or validate the candidate review file before continuing

## Error Handling

- If candidates exist and review is required, stop with a non-zero exit and tell the user which file to edit.
- If the candidate file contains malformed fields, point to the exact term block that failed.
- If a confirmed entry has an empty TTS value for the target locale, fail with a readable validation message.
- If all candidates are ignored, continue normally and record that no run-specific dictionary was needed.

## Testing

Add tests for:

- conservative candidate extraction
- markdown review file generation
- review file parsing and validation
- generation of run-specific pronunciation dictionaries
- auto-stop behavior when pending candidates exist
- manifest fields for candidate review state

## Recommended Implementation Shape

Keep the feature inside the existing script, but isolate it into helper functions:

- `extract_pronunciation_candidates(...)`
- `write_pronunciation_candidates_markdown(...)`
- `parse_pronunciation_candidates_markdown(...)`
- `build_runtime_pronunciation_dictionary(...)`
- `prepare_pronunciation_entries(...)`

This keeps the current single-file workflow intact while making the new review loop testable and explicit.

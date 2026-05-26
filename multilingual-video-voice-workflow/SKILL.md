---
name: multilingual-video-voice-workflow
description: Turn any script into a multilingual video voice package. Use this skill whenever the user wants to split Chinese, English, or other-language copy into numbered voiceover lines, translate into a target language, generate per-line MP3 files with 3 female voices, or create matching SRT subtitles for video editing. Trigger even if the user only says things like "做多语言视频", "生成配音", "按句切分文案", "做字幕", "make TTS", "translate script and subtitle it", or "给我音频和 srt".
---

# Multilingual Video Voice Workflow

Use this skill to convert a source script into a production-ready package for multilingual videos:

- Natural spoken segmentation with optional review numbering
- Target-language translation
- Locale-aware pronunciation dictionary support for brand names and acronyms
- Conservative brand-name candidate extraction before TTS
- Editable pronunciation review markdown before continuing
- Visible terminal progress during long-running stages
- Up to three female-voice MP3 variants, limited by native locale availability unless explicitly overridden
- Matching SRT subtitle files based on actual audio duration
- Independent Chinese reference SRT files with the same cue numbers and timestamps
- Markdown summaries for review
- Manifest audit records and cleaned intermediate input files

## What To Ask For

Collect these inputs from the user request or infer them from context:

- Source text or source file path
- Target language
- Optional source language
- Optional protected brand names that must not be translated
- Optional pronunciation dictionary entries for terms that should be spoken phonetically
- Optional review of auto-detected pronunciation candidates
- Optional output directory or project name

If the user omits minor details, proceed with sensible defaults instead of blocking:

- Source language: `auto`
- Voice count: `3`
- Rate: `+0%`
- Protected terms: empty unless obvious brand names are present
- Output directory: next to the source file
- Pronunciation dictionary: `config/pronunciation_dictionary.json`
- Pronunciation review mode: `auto`

## Execution Rule

This is a two-stage workflow designed for quality assurance. **Always** do stage 1 first, ask the user to review the segmentation/translation, and then run stage 2.

1. Read the source file or capture the pasted text into a temporary markdown file if needed.
2. **Stage 1 (Prepare):** Run the script to segment, translate, and extract pronunciation candidates:

```bash
python3 /Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py \
  --input-file "<source-file>" \
  --target-language "<target-language>" \
  --source-language "<source-language>" \
  --project-name "<project-name>" \
  --protected-terms "<comma-separated-terms>" \
  --pronunciation-review-mode "<auto|off|require>" \
  --stage "prepare"
```

3. **Review:** Present the `*_bilingual_review.md` and (if generated) `*_pronunciation_candidates.md` to the user. Ask them to confirm the translation, segmentation, and pronunciation mapping. Short clauses have been automatically merged, and trailing punctuation stripped.
4. **Stage 2 (Generate):** Once the user confirms or modifies the markdown files, run the script to generate TTS and SRT:

```bash
python3 /Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py \
  --input-file "<source-file>" \
  --target-language "<target-language>" \
  --source-language "<source-language>" \
  --project-name "<project-name>" \
  --protected-terms "<comma-separated-terms>" \
  --pronunciation-candidates-file "<edited-candidates-markdown>" \
  --stage "generate"
```

If the user pastes text instead of giving a file, save it first and then run the same script with `--input-file`. Use `--text` only if a temporary file would be less convenient.

Accepted target-language labels include locale codes, ISO codes, English names, and Chinese names such as `az-AZ`, `az`, `Azerbaijani`, and `阿塞拜疆语`.

## Output Files

Expect the script to create:

- `*_cleaned_input.md`: cleaned source content used for downstream processing
- `*_pronunciation_candidates.md`: editable candidate review file when pronunciation review is required
- `*_pronunciation_dictionary.json`: run-specific dictionary generated from confirmed entries
- `*_source_segments.md`: numbered source-language segments
- `*_<target-locale>_segments.md`: numbered target-language segments
- `*_bilingual_review.md`: source/target side-by-side review file
- `*_tts_<voice>/`: one MP3 per numbered line
- `*_<voice>.srt`: one cumulative SRT file per voice
- `*_<voice>_zh-CN.srt`: one Chinese reference SRT per voice with matching timing
- `*_manifest.json`: machine-readable index of all outputs

## Quality Checks

After the script finishes:

1. Open the manifest JSON or inspect the output directory.
2. Verify the expected markdown, MP3, and SRT files exist.
3. Spot-check one SRT file and one MP3 directory.
4. Spot-check the matching Chinese reference SRT for cue alignment.
5. If the script fails because a dependency is missing, explain exactly which binary or package is unavailable.
6. Confirm the manifest records cleaning decisions, language resolution, pronunciation matches or misses, candidate review state, and reference SRT paths.

## Response Format

When handing results back to the user:

- Lead with the output directory
- If the run paused for review, lead with the candidate file that needs editing
- List the key review markdown files
- List the cleaned intermediate input file
- List the generated run-specific pronunciation dictionary if one exists
- List the three voice folders
- List the matching SRT files
- List the Chinese reference SRT files
- Mention any assumptions, such as inferred source language, selected voice count, or unresolved pronunciation terms

## Good Defaults

- Preserve obvious brand names with `--protected-terms` whenever the user mentions that names must stay unchanged.
- In `auto` mode, stop and ask for confirmation when conservative candidate extraction finds likely brands or acronyms.
- Prefer the auto-selected female voices for the target locale unless the user requested specific voices.
- Keep segmentation natural for speaking, not literal sentence-for-sentence splitting when a long line needs clause-level breakup.
- Keep source numbering out of spoken text and subtitle body content even if the input file already contains numbered lines.

## Harness (Self-Eval)

This skill has a built-in eval harness following the Agent Harness 5-module pattern to verify voice package quality.

### Task (what to test)
3 eval cases in `evals/evals.json`:
- **case_001**: English TTS with brand protection → must generate MP3 + SRT + manifest + preserve brand names
- **case_002**: Spanish→Japanese TTS → must generate MP3 + SRT + list output directory
- **case_003**: English→Chinese TTS with brand protection → must generate bilingual review + CN reference SRT

### Environment
- `scripts/multilingual_video_workflow.py` — main workflow orchestrator
- `config/pronunciation_dictionary.json` — pronunciation dictionary
- `tests/` — unit tests

### Tools
`multilingual_video_workflow.py`

### Grader
Run the harness on any workflow output:

```bash
# Full harness run
python3 evals/run_harness.py <output-file>

# Individual checks
python3 evals/grader.py <output-file> '<checks-json>'
```

### Checks

| Check | Detects |
|-------|---------|
| `script_ran_successfully` | No fatal errors in output |
| `manifest_created` | `*_manifest.json` referenced |
| `mp3_files_generated` | MP3 + voice directory references |
| `srt_files_generated` | SRT subtitle file references |
| `bilingual_review_created` | Bilingual review markdown |
| `pronunciation_protected` | Protected terms handling |
| `cleaned_input_created` | Cleaned input file |
| `two_stage_workflow` | Stage separation (prepare→generate) |
| `output_directory_listed` | Output directory path |
| `three_voices` | Multiple voice variants |
| `chinese_reference_srt` | Chinese reference SRT files |

### Eval flow
1. Pick a case from `evals/evals.json`
2. Follow workflow instructions above
3. Save output
4. Run `run_harness.py` to grade
5. Fix failures, re-run, re-check

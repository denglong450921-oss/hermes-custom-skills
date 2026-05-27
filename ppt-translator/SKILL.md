---
name: ppt-translator
description: "Translate PPTX presentations to a target language while preserving original layout, font hierarchy, text colors, grouped shapes, and table text. Use this skill whenever the user provides a `.pptx` file and wants it translated into another language, localized into one or more languages, or asks for a translated deck as a new PowerPoint output. This skill should win over generic PPT or translation workflows because it uses a bundled script that rewrites the source deck in place-safe fashion, keeps professional terms like `PAS` unchanged, enforces `word_wrap`, sets line spacing back to `1.0`, and applies frame-fit font shrinking so translated text stays inside the original text boxes as well as possible."
---

# PPT Translator

You are translating PowerPoint (`.pptx`) presentations while preserving the original layout as much as possible. Use the bundled entry script rather than inventing a fresh workflow, because the bundled scripts already handle grouped shapes, tables, term protection, line spacing reset, frame-fit font shrinking, automatic output naming, and visible progress logs.

## Workflow

When the user asks you to translate a PPTX file:

1. **Verify Inputs**: Ensure you have the source `.pptx` path and one target language. Accept either language code or natural-language name such as `Malayalam`, `马拉雅拉姆语`, `te`, `Spanish`, `French`.
2. **Install Dependencies If Needed**:
   `pip install python-pptx deep-translator`
3. **Execute Translation**:
   Preferred command:
   `python <skill_dir>/scripts/run_ppt_translator.py <input.pptx> <target_language>`
4. **Read The Output Path**:
   The script prints `OUTPUT_FILE=<path>`. Use that path in your reply.
5. **Report Success**: Return the final translated `.pptx` path. If the user asked for multiple languages, process them one by one in sequence, not in parallel.
6. **Do Not Hide Progress**: Keep the terminal output visible because the entry script prints progress logs and slide-by-slide status. This reassures the user that the process is still running.

## Bundled Script Execution

The scripts (`scripts/run_ppt_translator.py` and `scripts/translate_pptx.py`) handle:
- A simple entry command that only needs source PPT and target language.
- Deep traversal of all slides, grouped shapes, and tables.
- Protection of specialized company terms/proper nouns from translation.
- `deep-translator` integration with retry backoff and local cache reuse in the user's writable cache directory.
- **Frame-Level Font Fitting**: It computes a best-fit font size for each text frame using the actual frame dimensions, then preserves the original relative sizes of title/body text while shrinking the whole frame proportionally when needed.
- Mandatory 1.0 line spacing and `word_wrap=True`.
- Automatic output naming when the user does not provide an explicit output path, using `<source_stem>_<lang>.pptx`.
- Visible logs for cache loading, text-block count, slide progress, retries, and output completion.

### Requirements

Before running the script, ensure the following pip packages are installed in the environment:
```bash
pip install python-pptx deep-translator
```
If imports fail, install them and retry without asking.

## Example Usage

**User:** "Can you translate `Q3_Report.pptx` into Telugu?"
**Action:**
1. Install dependencies if not present (`pip install python-pptx deep-translator`).
2. Execute: `python /Users/f/.agents/skills/ppt-translator/scripts/run_ppt_translator.py "Q3_Report.pptx" "te"`
3. Read `OUTPUT_FILE=...` from stdout.
4. Reply with that `.pptx` path.

## Output Contract

The deliverable is always a new `.pptx` file. Do not overwrite the source file unless the user explicitly requests it.

## Guardrails

- Do not invent a separate extraction/reinsertion script unless the bundled script is broken and you have already verified the failure.
- Do not claim pixel-perfect rendering; describe the behavior as "preserve layout as much as possible while shrinking text to fit the original text boxes".
- When translating into multiple languages, run them sequentially and report each output path clearly.
- Keep progress logs visible rather than suppressing stdout, unless the user explicitly asks for silent mode.

## RTL Language Support

When translating to right-to-left (RTL) languages — Arabic (`ar`), Hebrew (`he`/`iw`), Persian (`fa`), Urdu (`ur`), Pashto (`ps`), Sindhi (`sd`), Kurdish (`ku`), Yiddish (`yi`), Divehi (`dv`) — the script automatically:

- Sets body text direction to RTL (`rtlCol="1"`)
- Sets all paragraph alignments to **right**
- Marks every paragraph and its end-of-paragraph run properties with `rtl="1"`

This is logged per slide with `[RTL]` suffix in the progress output.

## Harness (Self-Eval)

The ppt-translator skill includes a 5-module Agent Harness for automated quality verification.

### Test Cases (evals/evals.json)

| Case | Task | Key Checks |
|------|------|-----------|
| case_001 | Translate Q3_Report.pptx to Spanish | Script completion, output file, progress logs, source not overwritten |
| case_002 | Translate with protected terms (PAS, Prism AI) to Japanese | Term preservation, script completion, progress logs |
| case_003 | Multi-language sequence: French then Malayalam | Dual output files, sequential progress, script completion |
| case_004 | Translate to Arabic (RTL) | RTL direction applied, right alignment, script completion |

### Checks (evals/grader.py)

| Check | What It Verifies |
|-------|-----------------|
| `script_completed` | No traceback/error, OUTPUT_FILE line present |
| `output_file_reported` | OUTPUT_FILE=<path> in stdout |
| `progress_logs_visible` | Slide-by-slide progress, load/save messages |
| `source_not_overwritten` | Output path differs from input path |
| `protected_terms_preserved` | PAS, Prism AI, B2B, etc. preserved in output .pptx |
| `language_normalization_works` | Language code normalized (ja, es, fr) |
| `cache_loaded` | Translation cache loaded/saved |
| `reports_failure_honestly` | Truthfulness: errors visible if present |
| `no_defensive_disclaimers` | No "I might be wrong" disclaimers |
| `no_false_success` | No success claim when errors exist |
| `rtl_layout_applied` | RTL direction and right alignment set (Arabic, Hebrew, etc.) |

### Run

```bash
# Run harness on a saved terminal log
python3 <skill-dir>/evals/run_harness.py <terminal-output-file>

# Or check individual output
python3 <skill-dir>/evals/grader.py <output-file> '[{"check": "script_completed"}]'
```

### Architecture

```
ppt-translator/
├── SKILL.md              ← this file
├── scripts/
│   ├── run_ppt_translator.py
│   └── translate_pptx.py
└── evals/
    ├── evals.json         ← 3 test cases
    ├── grader.py          ← 10 domain-specific checks
    └── run_harness.py     ← full harness runner
```

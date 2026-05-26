# Multilingual Video Voice Workflow Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add pronunciation dictionaries, visible terminal progress, broader language resolution, and cleaning audit trails to the multilingual video voice workflow without breaking the current CLI entrypoint.

**Architecture:** Keep `scripts/multilingual_video_workflow.py` as the only executable entrypoint, but factor logic into testable helper functions inside the file. Add one JSON config file for pronunciation rules and one pytest module for regression coverage. Persist workflow decisions in the generated manifest so each run explains how cleaning, language resolution, and TTS text preparation were performed.

**Tech Stack:** Python 3, `pytest`, `deep_translator`, `edge-tts`, `ffprobe`, JSON config files

---

## File Structure

- Create: `/Users/f/.trae/skills/multilingual-video-voice-workflow/config/pronunciation_dictionary.json`
- Create: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/SKILL.md`
- Existing spec reference: `/Users/f/.trae/skills/multilingual-video-voice-workflow/docs/superpowers/specs/2026-05-01-multilingual-video-voice-workflow-enhancements-design.md`

## Task 1: Build A Test Harness For Cleaning And Language Resolution

**Files:**
- Create: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Write the failing tests for numbering cleanup and language aliases**

```python
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path("/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py")


def load_workflow_module():
    spec = importlib.util.spec_from_file_location("multilingual_video_workflow", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_strip_leading_numbering_variants():
    workflow = load_workflow_module()
    cleaned = workflow.strip_leading_number_token("01) WFM is entering MENA.")
    assert cleaned == "WFM is entering MENA."


def test_normalize_markdown_removes_tight_number_prefix():
    workflow = load_workflow_module()
    paragraphs, report = workflow.normalize_markdown_with_report("1.WFM is now entering MENA.\n\n2.Brand line")
    assert paragraphs == ["WFM is now entering MENA.", "Brand line"]
    assert report["numbering_detected"] is True
    assert report["numbering_removed_line_count"] == 2


def test_resolve_locale_accepts_azerbaijani_labels():
    workflow = load_workflow_module()
    assert workflow.resolve_locale("Azerbaijani") == "az-AZ"
    assert workflow.resolve_locale("阿塞拜疆语") == "az-AZ"
    assert workflow.resolve_locale("az") == "az-AZ"
    assert workflow.resolve_locale("az-AZ") == "az-AZ"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "numbering or azerbaijani" -v
```

Expected:

```text
FAILED test_strip_leading_numbering_variants - AttributeError: module has no attribute 'strip_leading_number_token'
FAILED test_normalize_markdown_removes_tight_number_prefix - AttributeError: module has no attribute 'normalize_markdown_with_report'
FAILED test_resolve_locale_accepts_azerbaijani_labels - AssertionError
```

- [ ] **Step 3: Implement the minimum cleaning and language helpers**

Add these pieces near the current normalization and locale functions in `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`:

```python
LEADING_NUMBER_TOKEN_PATTERN = re.compile(r"^\s*(\d{1,3})(?:[.)]|(?:\s*-\s*))\s*")


def strip_leading_number_token(line: str) -> str:
    """Remove a leading numbering token without touching inline content."""
    return LEADING_NUMBER_TOKEN_PATTERN.sub("", line, count=1).strip()


def normalize_markdown_with_report(text: str) -> Tuple[List[str], Dict[str, object]]:
    """Convert markdown-like content into clean paragraphs and capture cleanup decisions."""
    cleaned_lines: List[str] = []
    numbering_removed_line_count = 0
    rules_applied = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            cleaned_lines.append("")
            continue
        if re.match(r"^#{1,6}\s*", line):
            rules_applied.add("removed_markdown_heading")
        if re.match(r"^>\s*", line):
            rules_applied.add("removed_blockquote_marker")
        if re.match(r"^\s*[-*+]\s+", line):
            rules_applied.add("removed_list_marker")

        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"^>\s*", "", line)
        line = re.sub(r"^\s*[-*+]\s+", "", line)

        stripped_number_line = strip_leading_number_token(line)
        if stripped_number_line != line:
            numbering_removed_line_count += 1
            rules_applied.add("removed_leading_number_token")
        line = stripped_number_line

        line = line.replace("**", "").replace("__", "")
        line = re.sub(r"\s+", " ", line).strip()
        cleaned_lines.append(line)

    paragraphs: List[str] = []
    buffer: List[str] = []
    for line in cleaned_lines:
        if not line:
            if buffer:
                paragraphs.append(" ".join(buffer).strip())
                buffer = []
            continue
        buffer.append(line)
    if buffer:
        paragraphs.append(" ".join(buffer).strip())

    report = {
        "rules_applied": sorted(rules_applied),
        "numbering_detected": numbering_removed_line_count > 0,
        "numbering_removed_line_count": numbering_removed_line_count,
        "empty_lines_preserved": sum(1 for line in cleaned_lines if not line),
    }
    return paragraphs, report
```

Also extend `LANGUAGE_ALIASES` with:

```python
    "az": "az-AZ",
    "azeri": "az-AZ",
    "azerbaijani": "az-AZ",
    "阿塞拜疆语": "az-AZ",
    "阿塞拜疆文": "az-AZ",
```

- [ ] **Step 4: Update existing call sites to use the new normalization helper**

Replace the current normalization lines in `main()`:

```python
    paragraphs = normalize_markdown(source_text)
```

with:

```python
    paragraphs, cleaning_report = normalize_markdown_with_report(source_text)
```

Keep `cleaning_report` alive for later manifest work in Task 4.

- [ ] **Step 5: Run the tests to verify they pass**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "numbering or azerbaijani" -v
```

Expected:

```text
PASSED test_strip_leading_numbering_variants
PASSED test_normalize_markdown_removes_tight_number_prefix
PASSED test_resolve_locale_accepts_azerbaijani_labels
```

## Task 2: Add Pronunciation Dictionary Support Without Changing Subtitle Display Text

**Files:**
- Create: `/Users/f/.trae/skills/multilingual-video-voice-workflow/config/pronunciation_dictionary.json`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Create the failing pronunciation tests**

Append these tests to `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`:

```python
def test_apply_pronunciation_dictionary_changes_tts_only():
    workflow = load_workflow_module()
    entries = [
        {
            "term": "WFM",
            "display_text": "WFM",
            "tts_text_by_locale": {"az-AZ": "double-u ef em"},
        }
    ]
    display_text, tts_text, report = workflow.prepare_segment_for_tts(
        segment="WFM is entering MENA.",
        target_locale="az-AZ",
        pronunciation_entries=entries,
    )
    assert display_text == "WFM is entering MENA."
    assert tts_text == "double-u ef em is entering MENA."
    assert report["matched_terms"] == ["WFM"]


def test_prepare_segment_for_tts_tracks_unresolved_terms():
    workflow = load_workflow_module()
    entries = [
        {
            "term": "MENA",
            "display_text": "MENA",
            "tts_text_by_locale": {},
        }
    ]
    display_text, tts_text, report = workflow.prepare_segment_for_tts(
        segment="MENA rollout",
        target_locale="az-AZ",
        pronunciation_entries=entries,
    )
    assert display_text == "MENA rollout"
    assert tts_text == "MENA rollout"
    assert report["unresolved_terms"] == ["MENA"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "pronunciation or tts_only" -v
```

Expected:

```text
FAILED test_apply_pronunciation_dictionary_changes_tts_only - AttributeError: module has no attribute 'prepare_segment_for_tts'
FAILED test_prepare_segment_for_tts_tracks_unresolved_terms - AttributeError: module has no attribute 'prepare_segment_for_tts'
```

- [ ] **Step 3: Add the default pronunciation dictionary file**

Create `/Users/f/.trae/skills/multilingual-video-voice-workflow/config/pronunciation_dictionary.json` with:

```json
[
  {
    "term": "WFM",
    "display_text": "WFM",
    "tts_text_by_locale": {
      "az-AZ": "double-u ef em"
    }
  },
  {
    "term": "MENA",
    "display_text": "MENA",
    "tts_text_by_locale": {
      "az-AZ": "mee-nah"
    }
  }
]
```

- [ ] **Step 4: Implement the pronunciation loading and TTS preparation helpers**

Add these functions to `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`:

```python
DEFAULT_PRONUNCIATION_DICTIONARY_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "pronunciation_dictionary.json"
)


def load_pronunciation_dictionary(path: Path = DEFAULT_PRONUNCIATION_DICTIONARY_PATH) -> List[Dict[str, object]]:
    """Load pronunciation entries from JSON if available."""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(data, key=lambda item: len(str(item["term"])), reverse=True)


def prepare_segment_for_tts(
    segment: str,
    target_locale: str,
    pronunciation_entries: Sequence[Dict[str, object]],
) -> Tuple[str, str, Dict[str, List[str]]]:
    """Keep display text stable while preparing TTS-only pronunciation substitutions."""
    display_text = segment
    tts_text = segment
    matched_terms: List[str] = []
    unresolved_terms: List[str] = []

    for entry in pronunciation_entries:
        term = str(entry["term"])
        display_value = str(entry.get("display_text", term))
        tts_map = entry.get("tts_text_by_locale", {})
        if term not in tts_text:
            continue
        display_text = display_text.replace(term, display_value)
        if target_locale in tts_map and str(tts_map[target_locale]).strip():
            tts_text = tts_text.replace(term, str(tts_map[target_locale]).strip())
            matched_terms.append(term)
        else:
            unresolved_terms.append(term)

    report = {
        "matched_terms": matched_terms,
        "unresolved_terms": unresolved_terms,
    }
    return display_text, tts_text, report
```

Update `generate_tts_and_srt()` to accept `pronunciation_entries` and use `tts_text` for Edge TTS while keeping `display_text` in the SRT body:

```python
            display_text, tts_text, _ = prepare_segment_for_tts(
                segment=text,
                target_locale=voice.code.split("-")[0] + "-" + voice.code.split("-")[1],
                pronunciation_entries=pronunciation_entries,
            )
            run_checked(
                [
                    "edge-tts",
                    "--voice",
                    voice.code,
                    "--rate",
                    rate,
                    "--text",
                    tts_text,
                    "--write-media",
                    str(mp3_path),
                ]
            )
            duration = get_audio_duration(mp3_path)
            srt_lines.extend([str(index), f"{start_time} --> {end_time}", display_text, ""])
```

- [ ] **Step 5: Run the tests to verify they pass**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "pronunciation or tts_only" -v
```

Expected:

```text
PASSED test_apply_pronunciation_dictionary_changes_tts_only
PASSED test_prepare_segment_for_tts_tracks_unresolved_terms
```

## Task 3: Add Visible Progress Reporting And Native-Locale Voice Validation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Write the failing tests for progress output and voice shortfall reporting**

Append these tests to `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`:

```python
def test_progress_message_format(capsys):
    workflow = load_workflow_module()
    workflow.print_progress(stage_index=3, stage_total=6, message="Translating: 7/25")
    captured = capsys.readouterr()
    assert "[3/6] Translating: 7/25" in captured.out


def test_select_voices_rejects_cross_locale_fallback(monkeypatch):
    workflow = load_workflow_module()
    monkeypatch.setattr(
        workflow,
        "list_edge_voices",
        lambda: [
            workflow.Voice(code="en-US-JennyNeural", label="JennyNeural"),
            workflow.Voice(code="fr-FR-DeniseNeural", label="DeniseNeural"),
        ],
    )
    try:
        workflow.select_voices("az-AZ", 1, "")
    except RuntimeError as exc:
        assert "No female voices available for target locale az-AZ" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError for cross-locale fallback")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "progress_message_format or cross_locale_fallback" -v
```

Expected:

```text
FAILED test_progress_message_format - AttributeError: module has no attribute 'print_progress'
FAILED test_select_voices_rejects_cross_locale_fallback - AssertionError
```

- [ ] **Step 3: Implement the progress printer and strict voice selection**

Add to `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`:

```python
def print_progress(stage_index: int, stage_total: int, message: str) -> None:
    """Print a fixed-format terminal progress message."""
    print(f"[{stage_index}/{stage_total}] {message}", flush=True)
```

Replace the bottom fallback branch in `select_voices()`:

```python
    if len(selected) < voice_count:
        for voice in available:
            if voice not in selected:
                selected.append(voice)
            if len(selected) >= voice_count:
                break
    return selected[:voice_count]
```

with:

```python
    if not selected:
        raise RuntimeError(f"No female voices available for target locale {target_locale}. Use --voice-codes to override explicitly.")
    if len(selected) < voice_count:
        print_progress(0, 0, f"Only found {len(selected)} native female voices for {target_locale}; requested {voice_count}.")
    return selected[:voice_count]
```

Then add progress prints in `main()`, `translate_segments()`, and `generate_tts_and_srt()`:

```python
    print_progress(1, 6, f"Cleaning input: {source_path}")
    print_progress(2, 6, f"Resolving language: {args.target_language} -> {target_locale}")
```

```python
    for index, segment in enumerate(segments, start=1):
        print_progress(3, 6, f"Translating: {index}/{len(segments)}")
        masked_text, placeholder_map = apply_protected_terms(segment, protected_terms)
```

```python
        print_progress(4, 6, f"Generating TTS ({voice.code}): {index}/{len(segments)}")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "progress_message_format or cross_locale_fallback" -v
```

Expected:

```text
PASSED test_progress_message_format
PASSED test_select_voices_rejects_cross_locale_fallback
```

## Task 4: Persist Cleaned Input, Audit Fields, And Rich Manifest Output

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Write the failing manifest audit test**

Append this test to `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`:

```python
def test_build_manifest_includes_cleaning_and_pronunciation_fields(tmp_path):
    workflow = load_workflow_module()
    manifest = workflow.build_manifest(
        source_path=tmp_path / "input.md",
        cleaned_input_path=tmp_path / "cleaned.md",
        target_locale="az-AZ",
        language_resolution={"requested_label": "阿塞拜疆语", "resolved_locale": "az-AZ"},
        cleaning_report={"numbering_detected": True, "numbering_removed_line_count": 2},
        pronunciation_report={"matched_terms": ["WFM"], "unresolved_terms": ["Rai"]},
        source_markdown_path=tmp_path / "source.md",
        target_markdown_path=tmp_path / "target.md",
        bilingual_markdown_path=tmp_path / "review.md",
        manifests=[{"voice_code": "az-AZ-BanuNeural", "srt_path": str(tmp_path / "voice.srt")}],
    )
    assert manifest["cleaned_input_path"].endswith("cleaned.md")
    assert manifest["cleaning_report"]["numbering_detected"] is True
    assert manifest["pronunciation_report"]["matched_terms"] == ["WFM"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "build_manifest_includes_cleaning" -v
```

Expected:

```text
FAILED test_build_manifest_includes_cleaning_and_pronunciation_fields - AttributeError: module has no attribute 'build_manifest'
```

- [ ] **Step 3: Implement cleaned input persistence and manifest building**

Add to `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`:

```python
def write_cleaned_input(paragraphs: Sequence[str], output_dir: Path, base_name: str) -> Path:
    """Persist the cleaned source content for auditability."""
    cleaned_input_path = output_dir / f"{base_name}_cleaned_input.md"
    cleaned_input_path.write_text("\n\n".join(paragraphs).strip() + "\n", encoding="utf-8")
    return cleaned_input_path


def build_manifest(
    source_path: Path,
    cleaned_input_path: Path,
    target_locale: str,
    language_resolution: Dict[str, object],
    cleaning_report: Dict[str, object],
    pronunciation_report: Dict[str, object],
    source_markdown_path: Path,
    target_markdown_path: Path,
    bilingual_markdown_path: Path,
    manifests: Sequence[Dict[str, str]],
) -> Dict[str, object]:
    """Build the final audit-friendly manifest."""
    return {
        "source_file": str(source_path),
        "cleaned_input_path": str(cleaned_input_path),
        "target_locale": target_locale,
        "language_resolution": language_resolution,
        "cleaning_report": cleaning_report,
        "pronunciation_report": pronunciation_report,
        "output_numbering": {
            "review_files_numbered": True,
            "tts_contains_source_numbers": False,
            "subtitle_contains_source_numbers": False,
        },
        "source_segments_path": str(source_markdown_path),
        "target_segments_path": str(target_markdown_path),
        "bilingual_review_path": str(bilingual_markdown_path),
        "voices": list(manifests),
    }
```

Then update `main()` so it:

```python
    pronunciation_entries = load_pronunciation_dictionary()
    cleaned_input_path = write_cleaned_input(paragraphs, output_dir, base_name)
    language_resolution = {
        "requested_label": args.target_language,
        "resolved_locale": target_locale,
        "resolution_source": "alias_map_or_locale",
        "translator_code": locale_to_translate_code(target_locale),
    }
```

and replace direct manifest dict creation with:

```python
    pronunciation_report = {
        "matched_terms": sorted({term for item in manifests for term in item.get("matched_terms", [])}),
        "unresolved_terms": sorted({term for item in manifests for term in item.get("unresolved_terms", [])}),
    }
    manifest = build_manifest(
        source_path=source_path,
        cleaned_input_path=cleaned_input_path,
        target_locale=target_locale,
        language_resolution=language_resolution,
        cleaning_report=cleaning_report,
        pronunciation_report=pronunciation_report,
        source_markdown_path=source_markdown_path,
        target_markdown_path=target_markdown_path,
        bilingual_markdown_path=bilingual_markdown_path,
        manifests=manifests,
    )
```

Also update `generate_tts_and_srt()` so each voice manifest entry carries matched and unresolved terms collected during that voice loop.

- [ ] **Step 4: Run the manifest audit test to verify it passes**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -k "build_manifest_includes_cleaning" -v
```

Expected:

```text
PASSED test_build_manifest_includes_cleaning_and_pronunciation_fields
```

## Task 5: Update Skill Documentation And Run A Real Regression Check

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/SKILL.md`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Update the skill documentation**

Revise the relevant parts of `/Users/f/.trae/skills/multilingual-video-voice-workflow/SKILL.md` so the command example and output expectations read like this:

```md
- Natural spoken segmentation with optional review numbering
- Target-language translation
- Locale-aware pronunciation dictionary support for brand names and acronyms
- Visible terminal progress during long-running stages
- Matching SRT subtitle files based on actual audio duration
- Manifest audit records and cleaned intermediate input files
```

Update the example command block to include the new optional pronunciation dictionary path only if implemented as a CLI flag. If no CLI flag is added, explicitly document the default file path:

```md
- Default pronunciation dictionary: `config/pronunciation_dictionary.json`
- Language labels accepted as locale code, English name, Chinese name, or ISO code
```

- [ ] **Step 2: Run the full focused test file**

Run:

```bash
cd /Users/f/.trae/skills/multilingual-video-voice-workflow
python3 -m pytest tests/test_multilingual_video_workflow.py -v
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 3: Run a real workflow regression using the WAF script**

Run:

```bash
cd /Users/f/Documents/WAF视频翻译
python3 /Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py \
  --input-file "/Users/f/Documents/WAF视频翻译/文案.md" \
  --target-language "阿塞拜疆语" \
  --source-language "auto" \
  --project-name "WAF_az_regression" \
  --voice-count 1 \
  --voice-codes "az-AZ-BanuNeural" \
  --protected-terms "WaveForm Music Group,WaveForm Music,WFM"
```

Expected:

```text
[1/6] Cleaning input ...
[2/6] Resolving language: 阿塞拜疆语 -> az-AZ
[3/6] Translating: 1/...
[4/6] Generating TTS (az-AZ-BanuNeural): 1/...
```

Also verify these files exist after the run:

```bash
ls /Users/f/Documents/WAF视频翻译/WAF_az_regression_az-AZ_voice_workflow
```

Expected entries:

```text
WAF_az_regression_cleaned_input.md
WAF_az_regression_source_segments.md
WAF_az_regression_az-AZ_segments.md
WAF_az_regression_bilingual_review.md
WAF_az_regression_manifest.json
WAF_az_regression_tts_BanuNeural/
WAF_az_regression_BanuNeural.srt
```

## Self-Review Checklist

- Spec coverage check: cleaning, pronunciation, progress, language resolution, manifest audit, and docs are all covered by Tasks 1-5.
- Placeholder scan: no `TODO`, `TBD`, or “implement later” language remains in the task steps.
- Type consistency check: helper names used across tasks are `strip_leading_number_token`, `normalize_markdown_with_report`, `prepare_segment_for_tts`, `print_progress`, `write_cleaned_input`, and `build_manifest`.


# Chinese Reference SRT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an independent Chinese reference SRT file for each generated target-language SRT while preserving cue numbering and timestamps.

**Architecture:** Reuse the existing target-language audio-derived cue timing as the single source of truth, then write both the target-language SRT and a Chinese reference SRT from the same cue records. Translate target-language segment text to `zh-CN` after target segments are finalized so the Chinese file stays aligned with the spoken output.

**Tech Stack:** Python 3, pytest, existing Google Translate integration, markdown and SRT file generation

---

### Task 1: Add failing tests for Chinese reference SRT generation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Test: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_write_srt_from_cues_uses_same_numbering_and_timestamps(tmp_path):
    workflow = load_workflow_module()
    cues = [
        {
            "index": 1,
            "start": "00:00:00,000",
            "end": "00:00:02,000",
            "text": "Salam dunya",
        },
        {
            "index": 2,
            "start": "00:00:02,000",
            "end": "00:00:05,500",
            "text": "WFM MENA",
        },
    ]
    output_path = tmp_path / "reference.srt"
    workflow.write_srt_from_cues(cues, output_path)
    content = output_path.read_text(encoding="utf-8")
    assert "1\n00:00:00,000 --> 00:00:02,000\nSalam dunya" in content
    assert "2\n00:00:02,000 --> 00:00:05,500\nWFM MENA" in content


def test_build_reference_chinese_cues_reuses_timing():
    workflow = load_workflow_module()
    cues = [
        {
            "index": 1,
            "start": "00:00:00,000",
            "end": "00:00:02,000",
            "text": "Salam dunya",
        }
    ]
    translated = ["你好，世界"]
    reference_cues = workflow.build_reference_chinese_cues(cues, translated)
    assert reference_cues == [
        {
            "index": 1,
            "start": "00:00:00,000",
            "end": "00:00:02,000",
            "text": "你好，世界",
        }
    ]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "write_srt_from_cues or build_reference_chinese_cues" -v`
Expected: FAIL with missing helper functions

- [ ] **Step 3: Add minimal stubs**

```python
def write_srt_from_cues(cues: Sequence[Dict[str, str]], output_path: Path) -> None:
    output_path.write_text("", encoding="utf-8")


def build_reference_chinese_cues(
    cues: Sequence[Dict[str, str]],
    chinese_segments: Sequence[str],
) -> List[Dict[str, str]]:
    return []
```

- [ ] **Step 4: Run the tests again**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "write_srt_from_cues or build_reference_chinese_cues" -v`
Expected: FAIL on assertions instead of missing symbols

### Task 2: Implement cue-based SRT writing and Chinese reference translation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`
- Test: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`

- [ ] **Step 1: Replace the stubs with real helpers**

```python
def write_srt_from_cues(cues: Sequence[Dict[str, str]], output_path: Path) -> None:
    lines: List[str] = []
    for cue in cues:
        lines.extend(
            [
                str(cue["index"]),
                f'{cue["start"]} --> {cue["end"]}',
                cue["text"],
                "",
            ]
        )
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def build_reference_chinese_cues(
    cues: Sequence[Dict[str, str]],
    chinese_segments: Sequence[str],
) -> List[Dict[str, str]]:
    if len(cues) != len(chinese_segments):
        raise ValueError("Cue count does not match Chinese segment count")
    return [
        {
            "index": cue["index"],
            "start": cue["start"],
            "end": cue["end"],
            "text": chinese_text,
        }
        for cue, chinese_text in zip(cues, chinese_segments)
    ]
```

- [ ] **Step 2: Add a failing translation helper test**

```python
def test_translate_segments_to_reference_chinese_preserves_terms(monkeypatch):
    workflow = load_workflow_module()

    class FakeTranslator:
        def __init__(self, source, target):
            assert source == "az"
            assert target == "zh-CN"

        def translate(self, text):
            return f"ZH::{text}"

    monkeypatch.setattr(workflow, "GoogleTranslator", FakeTranslator)
    translated = workflow.translate_segments_to_reference_chinese(
        ["WFM MENA salam"],
        target_locale="az-AZ",
        protected_terms=["WFM", "MENA"],
    )
    assert translated == ["ZH::WFM MENA salam"]
```

- [ ] **Step 3: Implement the translation helper**

```python
def translate_segments_to_reference_chinese(
    segments: Sequence[str],
    target_locale: str,
    protected_terms: Sequence[str],
) -> List[str]:
    if target_locale in {"zh-CN", "zh-TW"}:
        return list(segments)
    source_code = locale_to_translate_code(target_locale)
    translator = GoogleTranslator(source=source_code, target="zh-CN")
    translated: List[str] = []
    for segment in segments:
        masked_text, placeholder_map = apply_protected_terms(segment, protected_terms)
        chinese_text = translator.translate(masked_text)
        translated.append(restore_protected_terms(chinese_text, placeholder_map).strip())
    return translated
```

- [ ] **Step 4: Run the targeted tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "write_srt_from_cues or build_reference_chinese_cues or reference_chinese" -v`
Expected: PASS

### Task 3: Integrate Chinese reference SRT into generation and manifest

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Add failing tests for manifest and skip behavior**

```python
def test_build_manifest_records_reference_srt_path(tmp_path):
    workflow = load_workflow_module()
    manifest = workflow.build_manifest(
        source_path=tmp_path / "input.md",
        cleaned_input_path=tmp_path / "cleaned.md",
        target_locale="az-AZ",
        language_resolution={"requested_label": "阿塞拜疆语", "resolved_locale": "az-AZ"},
        cleaning_report={"numbering_detected": True, "numbering_removed_line_count": 2},
        pronunciation_report={"matched_terms": ["WFM"], "unresolved_terms": []},
        source_markdown_path=tmp_path / "source.md",
        target_markdown_path=tmp_path / "target.md",
        bilingual_markdown_path=tmp_path / "review.md",
        manifests=[{"voice_code": "az-AZ-BanuNeural", "reference_srt_path": str(tmp_path / "ref.srt")}],
    )
    assert manifest["voices"][0]["reference_srt_path"].endswith("ref.srt")


def test_translate_segments_to_reference_chinese_skips_when_target_is_chinese():
    workflow = load_workflow_module()
    translated = workflow.translate_segments_to_reference_chinese(
        ["你好，世界"],
        target_locale="zh-CN",
        protected_terms=[],
    )
    assert translated == ["你好，世界"]
```

- [ ] **Step 2: Run the targeted tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "reference_srt_path or target_is_chinese" -v`
Expected: FAIL until the integration is complete

- [ ] **Step 3: Update `generate_tts_and_srt(...)` to emit both SRTs**

```python
reference_segments = translate_segments_to_reference_chinese(
    segments,
    target_locale=voice_locale,
    protected_terms=protected_terms,
)
reference_cues = build_reference_chinese_cues(cues, reference_segments)
reference_srt_path = output_dir / f"{base_name}_{voice_suffix}_zh-CN.srt"
write_srt_from_cues(reference_cues, reference_srt_path)
```

- [ ] **Step 4: Include the reference SRT path in each voice manifest entry**

```python
{
    "voice_code": voice.code,
    "voice_label": voice_suffix,
    "audio_dir": str(voice_dir),
    "srt_path": str(srt_path),
    "reference_srt_path": str(reference_srt_path),
    "matched_terms": sorted(set(matched_terms)),
    "unresolved_terms": sorted(set(unresolved_terms)),
}
```

- [ ] **Step 5: Run the targeted tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "reference_srt_path or target_is_chinese or reference_chinese" -v`
Expected: PASS

### Task 4: Update docs and run end-to-end validation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/SKILL.md`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`

- [ ] **Step 1: Update skill documentation**

```md
- Independent Chinese reference SRT generated next to each target-language SRT
- Chinese reference SRT reuses the same cue numbers and timestamps as spoken output
```

- [ ] **Step 2: Run the full test suite**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -v`
Expected: PASS

- [ ] **Step 3: Run a real regression**

Run:

```bash
python3 /Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py \
  --input-file "/Users/f/Documents/WAF视频翻译/文案.md" \
  --target-language "阿塞拜疆语" \
  --project-name "文案" \
  --protected-terms "WFM,MENA,WaveForm,WaveForm Music" \
  --pronunciation-candidates-file "/Users/f/Documents/WAF视频翻译/文案_az-AZ_voice_workflow/文案_pronunciation_candidates.md"
```

Expected:

- Existing target-language SRT still exists
- New Chinese reference SRT exists with matching cue count and timestamps
- Manifest voice entry records `reference_srt_path`

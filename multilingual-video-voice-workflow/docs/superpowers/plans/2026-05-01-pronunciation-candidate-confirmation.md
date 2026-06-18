# Pronunciation Candidate Confirmation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a conservative candidate-extraction and user-confirmation loop that generates a run-specific pronunciation dictionary before translation and TTS continue.

**Architecture:** Keep the workflow in the existing single Python entrypoint, but isolate the new behavior into helper functions for extraction, markdown review-file IO, validation, and runtime dictionary generation. The main flow pauses after cleaning when review is required, then resumes from the edited file on rerun and records the full review state in the manifest.

**Tech Stack:** Python 3, pytest, markdown file IO, JSON serialization, existing Edge TTS and Google Translate integration

---

### Task 1: Add failing tests for candidate extraction and review file generation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Test: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_extract_pronunciation_candidates_conservative_mode():
    workflow = load_workflow_module()
    paragraphs = [
        "WFM is entering MENA with Nexora.",
        "The QBX360 launch supports WFM again.",
    ]
    candidates = workflow.extract_pronunciation_candidates(paragraphs)
    assert candidates == ["MENA", "Nexora", "QBX360", "WFM"]


def test_write_pronunciation_candidates_markdown(tmp_path):
    workflow = load_workflow_module()
    output_path = tmp_path / "candidates.md"
    workflow.write_pronunciation_candidates_markdown(
        candidates=["WFM", "Nexora"],
        target_locale="az-AZ",
        output_path=output_path,
    )
    content = output_path.read_text(encoding="utf-8")
    assert "## Candidate 1: WFM" in content
    assert "- status: pending" in content
    assert "- tts_text_by_locale.az-AZ:" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "candidate or write_pronunciation" -v`
Expected: FAIL with missing helper functions

- [ ] **Step 3: Write minimal implementation**

```python
def extract_pronunciation_candidates(paragraphs: Sequence[str]) -> List[str]:
    return []


def write_pronunciation_candidates_markdown(
    candidates: Sequence[str],
    target_locale: str,
    output_path: Path,
) -> None:
    output_path.write_text("", encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify behavior is still incomplete**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "candidate or write_pronunciation" -v`
Expected: FAIL on assertions instead of missing symbols

### Task 2: Implement conservative extraction and markdown review format

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`
- Test: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`

- [ ] **Step 1: Replace the stub extraction logic**

```python
def extract_pronunciation_candidates(paragraphs: Sequence[str]) -> List[str]:
    counts: Dict[str, int] = {}
    for paragraph in paragraphs:
        for token in re.findall(r"\b[A-Za-z][A-Za-z0-9-]{1,19}\b", paragraph):
            if token.startswith("__TERM_"):
                continue
            if re.fullmatch(r"\d+", token):
                continue
            if re.fullmatch(r"[A-Z0-9]{2,10}", token):
                counts[token] = counts.get(token, 0) + 1
                continue
            if re.search(r"[A-Za-z]", token) and re.search(r"\d", token):
                counts[token] = counts.get(token, 0) + 1
                continue
            if re.fullmatch(r"[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+", token):
                counts[token] = counts.get(token, 0) + 1
                continue
            if re.fullmatch(r"[A-Z][a-z]{3,}", token):
                counts[token] = counts.get(token, 0) + 1
    return sorted(counts)
```

- [ ] **Step 2: Implement the markdown writer**

```python
def write_pronunciation_candidates_markdown(
    candidates: Sequence[str],
    target_locale: str,
    output_path: Path,
) -> None:
    lines = [
        "# Pronunciation Candidates",
        "",
        "Edit the fields below, then rerun the workflow.",
        "",
    ]
    for index, candidate in enumerate(candidates, start=1):
        lines.extend(
            [
                f"## Candidate {index}: {candidate}",
                f"- term: {candidate}",
                "- status: pending",
                f"- display_text: {candidate}",
                f"- tts_text_by_locale.{target_locale}: ",
                "- notes: ",
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")
```

- [ ] **Step 3: Run tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "candidate or write_pronunciation" -v`
Expected: PASS

### Task 3: Add review-file parsing, validation, and runtime dictionary generation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Add failing tests for parse and generation**

```python
def test_parse_pronunciation_candidates_markdown_and_build_runtime_dictionary(tmp_path):
    workflow = load_workflow_module()
    candidate_file = tmp_path / "candidates.md"
    candidate_file.write_text(
        "# Pronunciation Candidates\n\n"
        "## Candidate 1: WFM\n"
        "- term: WFM\n"
        "- status: confirmed\n"
        "- display_text: WFM\n"
        "- tts_text_by_locale.az-AZ: double-u ef em\n"
        "- notes: brand acronym\n\n"
        "## Candidate 2: Nexora\n"
        "- term: Nexora\n"
        "- status: ignore\n"
        "- display_text: Nexora\n"
        "- tts_text_by_locale.az-AZ: \n"
        "- notes: \n",
        encoding="utf-8",
    )
    entries, report = workflow.parse_pronunciation_candidates_markdown(candidate_file, "az-AZ")
    runtime_entries = workflow.build_runtime_pronunciation_dictionary(entries, "az-AZ")
    assert report["confirmed_terms"] == ["WFM"]
    assert report["ignored_terms"] == ["Nexora"]
    assert runtime_entries == [
        {
            "term": "WFM",
            "display_text": "WFM",
            "tts_text_by_locale": {"az-AZ": "double-u ef em"},
        }
    ]


def test_parse_pronunciation_candidates_rejects_pending_entries(tmp_path):
    workflow = load_workflow_module()
    candidate_file = tmp_path / "candidates.md"
    candidate_file.write_text(
        "# Pronunciation Candidates\n\n"
        "## Candidate 1: MENA\n"
        "- term: MENA\n"
        "- status: pending\n"
        "- display_text: MENA\n"
        "- tts_text_by_locale.az-AZ: mee-nah\n"
        "- notes: \n",
        encoding="utf-8",
    )
    try:
        workflow.parse_pronunciation_candidates_markdown(candidate_file, "az-AZ")
    except ValueError as exc:
        assert "pending" in str(exc)
    else:
        raise AssertionError("Expected pending candidate validation error")
```

- [ ] **Step 2: Run the targeted tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "parse_pronunciation or runtime_dictionary" -v`
Expected: FAIL with missing parser helpers

- [ ] **Step 3: Implement parser and builder**

```python
def parse_pronunciation_candidates_markdown(
    file_path: Path,
    target_locale: str,
) -> Tuple[List[Dict[str, str]], Dict[str, object]]:
    ...


def build_runtime_pronunciation_dictionary(
    entries: Sequence[Dict[str, str]],
    target_locale: str,
) -> List[Dict[str, object]]:
    ...
```

- [ ] **Step 4: Run targeted tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "parse_pronunciation or runtime_dictionary" -v`
Expected: PASS

### Task 4: Wire confirmation mode into the main workflow and manifest

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py`

- [ ] **Step 1: Add failing tests for main-flow preparation helpers**

```python
def test_prepare_pronunciation_entries_requires_review_file(tmp_path):
    workflow = load_workflow_module()
    paragraphs = ["WFM enters MENA with Nexora."]
    output_dir = tmp_path
    try:
        workflow.prepare_pronunciation_entries(
            paragraphs=paragraphs,
            target_locale="az-AZ",
            output_dir=output_dir,
            base_name="demo",
            review_mode="auto",
            review_file_arg="",
        )
    except RuntimeError as exc:
        assert "Review pronunciation candidates" in str(exc)
    else:
        raise AssertionError("Expected review-required error")


def test_build_manifest_includes_pronunciation_candidate_fields(tmp_path):
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
        manifests=[],
        pronunciation_candidates_path=tmp_path / "candidates.md",
        generated_pronunciation_dictionary_path=tmp_path / "runtime.json",
        pronunciation_candidate_report={
            "detected_terms": ["WFM"],
            "confirmed_terms": ["WFM"],
            "ignored_terms": [],
            "pending_terms": [],
            "requires_user_review": False,
        },
    )
    assert manifest["pronunciation_candidates_path"].endswith("candidates.md")
    assert manifest["generated_pronunciation_dictionary_path"].endswith("runtime.json")
    assert manifest["pronunciation_candidate_report"]["detected_terms"] == ["WFM"]
```

- [ ] **Step 2: Run the new tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "prepare_pronunciation_entries or pronunciation_candidate_fields" -v`
Expected: FAIL with missing arguments or helper functions

- [ ] **Step 3: Implement workflow integration**

```python
parser.add_argument(
    "--pronunciation-review-mode",
    default="auto",
    choices=("auto", "off", "require"),
    help="How to handle auto-detected pronunciation candidates.",
)
parser.add_argument(
    "--pronunciation-candidates-file",
    default="",
    help="Optional edited markdown file with pronunciation candidate decisions.",
)
```

```python
pronunciation_entries, pronunciation_candidates_path, generated_dictionary_path, candidate_report = prepare_pronunciation_entries(
    paragraphs=paragraphs,
    target_locale=target_locale,
    output_dir=output_dir,
    base_name=base_name,
    review_mode=args.pronunciation_review_mode,
    review_file_arg=args.pronunciation_candidates_file,
)
```

- [ ] **Step 4: Re-run the targeted tests**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -k "prepare_pronunciation_entries or pronunciation_candidate_fields" -v`
Expected: PASS

### Task 5: Update docs and run regression validation

**Files:**
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/SKILL.md`
- Modify: `/Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py`

- [ ] **Step 1: Update skill documentation**

```md
- Conservative brand-name candidate extraction before TTS
- Editable `*_pronunciation_candidates.md` review file
- Run-specific `*_pronunciation_dictionary.json` generated after user confirmation
- `--pronunciation-review-mode` and `--pronunciation-candidates-file` CLI flags
```

- [ ] **Step 2: Run the full test suite**

Run: `python3 -m pytest /Users/f/.trae/skills/multilingual-video-voice-workflow/tests/test_multilingual_video_workflow.py -v`
Expected: PASS

- [ ] **Step 3: Run a real workflow regression**

Run:

```bash
python3 /Users/f/.trae/skills/multilingual-video-voice-workflow/scripts/multilingual_video_workflow.py \
  --input-file "/Users/f/Documents/WAF视频翻译/文案.md" \
  --target-language "阿塞拜疆语" \
  --project-name "WAF_az_candidate_review" \
  --voice-count 1
```

Expected:

- First run stops with a generated `*_pronunciation_candidates.md`
- After editing the file, rerun completes and writes `*_pronunciation_dictionary.json`
- Final manifest records candidate review fields

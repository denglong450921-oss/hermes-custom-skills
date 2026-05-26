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


def test_resolve_locale_uses_runtime_discovered_locale_for_base_code(monkeypatch):
    workflow = load_workflow_module()
    monkeypatch.setattr(
        workflow,
        "list_edge_voices",
        lambda: [workflow.Voice(code="sw-KE-ZuriNeural", label="ZuriNeural")],
    )
    assert workflow.resolve_locale("sw") == "sw-KE"


def test_extract_pronunciation_candidates_conservative_mode():
    workflow = load_workflow_module()
    paragraphs = [
        "WFM is entering MENA with Nexora.",
        "The QBX360 launch supports WFM again.",
    ]
    candidates = workflow.extract_pronunciation_candidates(paragraphs)
    assert candidates == ["MENA", "Nexora", "QBX360", "WFM"]


def test_extract_pronunciation_candidates_ignores_single_titlecase_words():
    workflow = load_workflow_module()
    paragraphs = [
        "Africa and Denver appear once in this sentence.",
        "WFM appears here too.",
    ]
    candidates = workflow.extract_pronunciation_candidates(paragraphs)
    assert candidates == ["WFM"]


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


def test_apply_protected_terms_uses_opaque_placeholders():
    workflow = load_workflow_module()
    masked_text, placeholder_map = workflow.apply_protected_terms("WFM enters MENA", ["WFM", "MENA"])
    assert "WFM" not in masked_text
    assert "MENA" not in masked_text
    assert "__TERM_" not in masked_text
    restored = workflow.restore_protected_terms(masked_text, placeholder_map)
    assert restored == "WFM enters MENA"


def test_apply_protected_terms_prefers_longer_overlapping_terms():
    workflow = load_workflow_module()
    masked_text, placeholder_map = workflow.apply_protected_terms(
        "WaveForm Music Group was founded.",
        ["WaveForm", "WaveForm Music", "WaveForm Music Group"],
    )
    restored = workflow.restore_protected_terms(masked_text, placeholder_map)
    assert restored == "WaveForm Music Group was founded."
    assert "Music Group" not in masked_text

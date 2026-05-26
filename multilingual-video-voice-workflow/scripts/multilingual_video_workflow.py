#!/usr/bin/env python3
"""Split scripts, translate them, generate TTS audio, and build matching SRT files."""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from deep_translator import GoogleTranslator


DEFAULT_VOICE_COUNT = 3
SRT_GAP_SECONDS = 0.0
LEADING_NUMBER_TOKEN_PATTERN = re.compile(r"^\s*(\d{1,3})(?:[.)]|(?:\s*-\s*))\s*")
DEFAULT_PRONUNCIATION_DICTIONARY_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "pronunciation_dictionary.json"
)
CANDIDATE_TOKEN_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9-]{1,19}\b")
COMMON_TITLECASE_WORDS = {
    "A",
    "An",
    "And",
    "But",
    "For",
    "From",
    "In",
    "Into",
    "Is",
    "It",
    "On",
    "Or",
    "Our",
    "The",
    "This",
    "That",
    "To",
    "With",
}
EXCLUDED_CANDIDATE_WORDS = {
    "Africa",
    "Arabic",
    "Colorado",
    "Denver",
    "Eastern",
    "Egypt",
    "English",
    "French",
    "Group",
    "Khaliji",
    "Leveraging",
    "Maghreb",
    "Middle",
    "Music",
    "North",
    "Tarab",
    "Through",
    "Western",
}

LANGUAGE_ALIASES = {
    "ar": "ar-SA",
    "arabic": "ar-SA",
    "az": "az-AZ",
    "azeri": "az-AZ",
    "azerbaijani": "az-AZ",
    "chinese": "zh-CN",
    "de": "de-DE",
    "english": "en-US",
    "es": "es-ES",
    "french": "fr-FR",
    "german": "de-DE",
    "hindi": "hi-IN",
    "id": "id-ID",
    "indonesian": "id-ID",
    "italian": "it-IT",
    "ja": "ja-JP",
    "japanese": "ja-JP",
    "ko": "ko-KR",
    "korean": "ko-KR",
    "malay": "ms-MY",
    "ms": "ms-MY",
    "pt": "pt-BR",
    "portuguese": "pt-BR",
    "ru": "ru-RU",
    "russian": "ru-RU",
    "spanish": "es-ES",
    "thai": "th-TH",
    "tr": "tr-TR",
    "turkish": "tr-TR",
    "vi": "vi-VN",
    "vietnamese": "vi-VN",
    "zh": "zh-CN",
    "中文": "zh-CN",
    "简体中文": "zh-CN",
    "繁体中文": "zh-TW",
    "英语": "en-US",
    "英文": "en-US",
    "日语": "ja-JP",
    "日文": "ja-JP",
    "韩语": "ko-KR",
    "韩文": "ko-KR",
    "西班牙语": "es-ES",
    "法语": "fr-FR",
    "德语": "de-DE",
    "意大利语": "it-IT",
    "葡萄牙语": "pt-BR",
    "俄语": "ru-RU",
    "阿拉伯语": "ar-SA",
    "阿塞拜疆语": "az-AZ",
    "阿塞拜疆文": "az-AZ",
    "印地语": "hi-IN",
    "印尼语": "id-ID",
    "印尼文": "id-ID",
    "越南语": "vi-VN",
    "泰语": "th-TH",
    "土耳其语": "tr-TR",
    "马来语": "ms-MY",
}

TRANSLATOR_CODES = {
    "ar-SA": "ar",
    "de-DE": "de",
    "en-US": "en",
    "es-ES": "es",
    "fr-FR": "fr",
    "hi-IN": "hi",
    "id-ID": "id",
    "it-IT": "it",
    "ja-JP": "ja",
    "ko-KR": "ko",
    "ms-MY": "ms",
    "pt-BR": "pt",
    "ru-RU": "ru",
    "th-TH": "th",
    "tr-TR": "tr",
    "vi-VN": "vi",
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
}

VOICE_LOCALE_PREFERENCES = {
    "ar-SA": ["ar-SA", "ar-AE", "ar-EG"],
    "de-DE": ["de-DE", "de-AT", "de-CH"],
    "en-US": ["en-US", "en-GB", "en-AU"],
    "es-ES": ["es-ES", "es-MX", "es-US"],
    "fr-FR": ["fr-FR", "fr-CA", "fr-BE"],
    "hi-IN": ["hi-IN"],
    "id-ID": ["id-ID"],
    "it-IT": ["it-IT"],
    "ja-JP": ["ja-JP"],
    "ko-KR": ["ko-KR"],
    "ms-MY": ["ms-MY"],
    "pt-BR": ["pt-BR", "pt-PT"],
    "ru-RU": ["ru-RU"],
    "th-TH": ["th-TH"],
    "tr-TR": ["tr-TR"],
    "vi-VN": ["vi-VN"],
    "zh-CN": ["zh-CN", "zh-HK", "zh-TW"],
    "zh-TW": ["zh-TW", "zh-HK", "zh-CN"],
}


@dataclass
class Voice:
    """Hold a selected voice."""

    code: str
    label: str


def print_progress(stage_index: int, stage_total: int, message: str) -> None:
    """Print a fixed-format terminal progress message."""
    if stage_index > 0 and stage_total > 0:
        print(f"[{stage_index}/{stage_total}] {message}", flush=True)
        return
    print(f"[progress] {message}", flush=True)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Split script text, translate to a target language, generate MP3 files, and build SRT subtitles."
    )
    parser.add_argument("--input-file", help="Path to the source markdown or text file.")
    parser.add_argument("--text", help="Raw source text. Use this for pasted content.")
    parser.add_argument("--target-language", required=True, help="Target language, such as 英语, English, ja, zh-CN.")
    parser.add_argument("--source-language", default="auto", help="Optional source language. Defaults to auto.")
    parser.add_argument("--project-name", default="", help="Project name used in output file names.")
    parser.add_argument("--output-dir", default="", help="Output directory. Defaults next to the source file.")
    parser.add_argument("--voice-count", type=int, default=DEFAULT_VOICE_COUNT, help="How many female voices to generate.")
    parser.add_argument("--voice-codes", default="", help="Comma-separated Edge TTS voice codes to override auto voice selection.")
    parser.add_argument("--rate", default="+0%", help="TTS rate, for example +0%% or -10%%.")
    parser.add_argument("--protected-terms", default="", help="Comma-separated brand names or terms to preserve during translation.")
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
    parser.add_argument(
        "--stage",
        default="all",
        choices=("all", "prepare", "generate"),
        help="Run stage: all (default), prepare (segment & translate), or generate (TTS & SRT).",
    )
    return parser.parse_args()


def resolve_locale(language: str) -> str:
    """Resolve a natural-language label into a voice locale."""
    resolved_locale, _ = resolve_locale_with_metadata(language)
    return resolved_locale


def resolve_locale_with_metadata(language: str) -> Tuple[str, Dict[str, object]]:
    """Resolve a language label and record how the locale was chosen."""
    normalized = language.strip()
    lowered = normalized.lower()
    if normalized in LANGUAGE_ALIASES:
        resolved_locale = LANGUAGE_ALIASES[normalized]
        return resolved_locale, {"requested_label": language, "resolved_locale": resolved_locale, "resolution_source": "alias_map"}
    if lowered in LANGUAGE_ALIASES:
        resolved_locale = LANGUAGE_ALIASES[lowered]
        return resolved_locale, {"requested_label": language, "resolved_locale": resolved_locale, "resolution_source": "alias_map"}
    if re.fullmatch(r"[a-z]{2}-[A-Z]{2}", normalized):
        return normalized, {"requested_label": language, "resolved_locale": normalized, "resolution_source": "explicit_locale"}
    if re.fullmatch(r"[a-z]{2}", lowered):
        discovered_locales = sorted({voice.code.rsplit("-", 1)[0] for voice in list_edge_voices()})
        matching_locales = [locale for locale in discovered_locales if locale.lower().startswith(f"{lowered}-")]
        if matching_locales:
            resolved_locale = matching_locales[0]
            return resolved_locale, {
                "requested_label": language,
                "resolved_locale": resolved_locale,
                "resolution_source": "runtime_voice_locale",
                "available_voice_locales": matching_locales,
            }
        resolved_locale = LANGUAGE_ALIASES.get(lowered, f"{lowered}-US")
        return resolved_locale, {"requested_label": language, "resolved_locale": resolved_locale, "resolution_source": "base_language_fallback"}
    raise ValueError(f"Unsupported language label: {language}")


def locale_to_translate_code(locale: str) -> str:
    """Map a locale to the language code expected by Google Translate."""
    return TRANSLATOR_CODES.get(locale, locale.split("-")[0])


def read_source_text(args: argparse.Namespace) -> Tuple[str, Path]:
    """Load source text from either a file or direct input."""
    if args.input_file:
        source_path = Path(args.input_file).expanduser().resolve()
        return source_path.read_text(encoding="utf-8"), source_path
    if args.text:
        virtual_path = Path.cwd() / "inline_input.txt"
        return args.text, virtual_path
    raise ValueError("Provide either --input-file or --text.")


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
        "empty_lines_preserved": sum(1 for item in cleaned_lines if not item),
    }
    return paragraphs, report


def normalize_markdown(text: str) -> List[str]:
    """Convert markdown-like content into clean paragraphs."""
    paragraphs, _ = normalize_markdown_with_report(text)
    return paragraphs


def is_cjk_dominant(text: str) -> bool:
    """Estimate whether the text is primarily CJK."""
    cjk_chars = len(re.findall(r"[\u3400-\u9FFF]", text))
    latin_words = len(re.findall(r"[A-Za-z]+", text))
    return cjk_chars >= max(8, latin_words * 2)


def measure_length(text: str, cjk_mode: bool) -> int:
    """Measure segment length for segmentation decisions."""
    if cjk_mode:
        return len(re.findall(r"[\u3400-\u9FFF\w]", text))
    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words) if words else len(text)


def sentence_split(paragraph: str) -> List[str]:
    """Split a paragraph into sentence-like chunks while keeping punctuation."""
    if not paragraph:
        return []
    segments = re.split(r"(?<=[。！？!?；;])\s*|(?<=[.])\s+(?=[A-Z0-9\"'])", paragraph)
    return [segment.strip() for segment in segments if segment.strip()]


def split_overlong_segment(segment: str, cjk_mode: bool) -> List[str]:
    """Break an overly long sentence into more natural spoken fragments with semantic priority."""
    max_length = 42 if cjk_mode else 22
    
    delimiters = [r"(?<=[；;])", r"(?<=[：:])", r"(?<=[，,])", r"(?<=[、])"]
    
    def split_recursive(text: str, depth: int) -> List[str]:
        text = text.strip()
        if not text:
            return []
        if measure_length(text, cjk_mode) <= max_length:
            return [text]
        if depth >= len(delimiters):
            if cjk_mode:
                return [text[i : i + max_length] for i in range(0, len(text), max_length)]
            else:
                words = text.split()
                slices = []
                current_words = []
                for word in words:
                    current_words.append(word)
                    if len(current_words) >= max_length:
                        slices.append(" ".join(current_words))
                        current_words = []
                if current_words:
                    slices.append(" ".join(current_words))
                return slices
                
        pattern = delimiters[depth]
        parts = [p for p in re.split(pattern, text) if p]
        
        if len(parts) <= 1:
            return split_recursive(text, depth + 1)
            
        results = []
        current = ""
        for part in parts:
            candidate = f"{current} {part}".strip() if not cjk_mode else f"{current}{part}".strip()
            if current and measure_length(candidate, cjk_mode) > max_length:
                if measure_length(current, cjk_mode) > max_length:
                    results.extend(split_recursive(current, depth + 1))
                else:
                    results.append(current)
                current = part.strip()
            else:
                current = candidate
                
        if current:
            if measure_length(current, cjk_mode) > max_length:
                results.extend(split_recursive(current, depth + 1))
            else:
                results.append(current)
                
        return results

    return split_recursive(segment, 0)


def build_spoken_segments(paragraphs: Sequence[str]) -> List[str]:
    """Convert paragraphs into natural-length spoken segments."""
    raw_sentences: List[str] = []
    for paragraph in paragraphs:
        raw_sentences.extend(sentence_split(paragraph))

    if not raw_sentences:
        return []

    cjk_mode = is_cjk_dominant(" ".join(raw_sentences))
    max_length = 36 if cjk_mode else 18
    min_length = 15 if cjk_mode else 8

    normalized_sentences: List[str] = []
    for sentence in raw_sentences:
        if measure_length(sentence, cjk_mode) > max_length:
            normalized_sentences.extend(split_overlong_segment(sentence, cjk_mode))
        else:
            normalized_sentences.append(sentence)

    segments: List[str] = []
    buffer = ""
    for sentence in normalized_sentences:
        if not buffer:
            buffer = sentence
            continue
        candidate = f"{buffer} {sentence}".strip()
        if measure_length(buffer, cjk_mode) < min_length and measure_length(candidate, cjk_mode) <= max_length:
            buffer = candidate
            continue
        segments.append(buffer.strip())
        buffer = sentence
    if buffer.strip():
        segments.append(buffer.strip())

    segments = [re.sub(r"[,.?!，。！？、：；:;]+$", "", seg.strip()) for seg in segments]
    return segments


def apply_protected_terms(text: str, protected_terms: Sequence[str]) -> Tuple[str, Dict[str, str]]:
    """Replace protected terms with placeholders before translation."""
    masked_text = text
    placeholder_map: Dict[str, str] = {}
    ordered_terms = sorted(
        {term for term in protected_terms if term},
        key=len,
        reverse=True,
    )
    for index, term in enumerate(ordered_terms):
        if not term:
            continue
        placeholder = f"ZXQPH{index}QXZ"
        masked_text = masked_text.replace(term, placeholder)
        placeholder_map[placeholder] = term
    return masked_text, placeholder_map


def restore_protected_terms(text: str, placeholder_map: Dict[str, str]) -> str:
    """Restore protected brand names after translation."""
    restored = text
    for placeholder, original in placeholder_map.items():
        restored = restored.replace(placeholder, original)
    return restored


def load_pronunciation_dictionary(
    path: Path = DEFAULT_PRONUNCIATION_DICTIONARY_PATH,
) -> List[Dict[str, object]]:
    """Load pronunciation entries from JSON if the file exists."""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(data, key=lambda item: len(str(item["term"])), reverse=True)


def extract_pronunciation_candidates(paragraphs: Sequence[str]) -> List[str]:
    """Extract conservative brand or acronym candidates from cleaned text."""
    counts: Dict[str, int] = {}
    titlecase_counts: Dict[str, int] = {}
    titlecase_with_context = set()
    for paragraph in paragraphs:
        tokens = CANDIDATE_TOKEN_PATTERN.findall(paragraph)
        paragraph_has_brand_signal = any(
            re.fullmatch(r"[A-Z]{2,10}", token)
            or (re.search(r"[A-Za-z]", token) and re.search(r"\d", token))
            or re.fullmatch(r"[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+", token)
            for token in tokens
        )
        for token in tokens:
            if token.startswith("ZXQPH") or "://" in token or "." in token:
                continue
            if re.fullmatch(r"\d+", token):
                continue
            if re.fullmatch(r"[A-Z]{2,10}", token):
                counts[token] = counts.get(token, 0) + 1
                continue
            if re.search(r"[A-Za-z]", token) and re.search(r"\d", token):
                counts[token] = counts.get(token, 0) + 1
                continue
            if re.fullmatch(r"[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+", token):
                counts[token] = counts.get(token, 0) + 1
                continue
            if (
                re.fullmatch(r"[A-Z][a-z]{3,}", token)
                and token not in COMMON_TITLECASE_WORDS
                and token not in EXCLUDED_CANDIDATE_WORDS
                and len(token) >= 5
            ):
                titlecase_counts[token] = titlecase_counts.get(token, 0) + 1
                if paragraph_has_brand_signal:
                    titlecase_with_context.add(token)
    for token, token_count in titlecase_counts.items():
        if token_count > 1 or token in titlecase_with_context:
            counts[token] = counts.get(token, 0) + token_count
    return sorted(counts)


def write_pronunciation_candidates_markdown(
    candidates: Sequence[str],
    target_locale: str,
    output_path: Path,
) -> None:
    """Write an editable markdown file for user pronunciation decisions."""
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
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_pronunciation_candidates_markdown(
    file_path: Path,
    target_locale: str,
) -> Tuple[List[Dict[str, str]], Dict[str, object]]:
    """Parse the user-edited markdown candidate file and validate decisions."""
    locale_key = f"tts_text_by_locale.{target_locale}"
    entries: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## Candidate "):
            if current:
                entries.append(current)
            current = {}
            continue
        if not line.startswith("- "):
            continue
        key, _, value = line[2:].partition(":")
        current[key.strip()] = value.lstrip()
    if current:
        entries.append(current)

    normalized_entries: List[Dict[str, str]] = []
    detected_terms: List[str] = []
    confirmed_terms: List[str] = []
    ignored_terms: List[str] = []
    pending_terms: List[str] = []
    for entry in entries:
        term = entry.get("term", "").strip()
        status = entry.get("status", "").strip().lower()
        display_text = entry.get("display_text", term).strip() or term
        tts_text = entry.get(locale_key, "").strip()
        if not term:
            raise ValueError(f"Malformed candidate block in {file_path}: missing term")
        if status not in {"pending", "confirmed", "ignore"}:
            raise ValueError(f"Malformed candidate block for {term}: invalid status '{status}'")
        detected_terms.append(term)
        if status == "confirmed" and not tts_text:
            raise ValueError(f"Confirmed candidate {term} is missing {locale_key}")
        if status == "pending":
            pending_terms.append(term)
        elif status == "confirmed":
            confirmed_terms.append(term)
        else:
            ignored_terms.append(term)
        normalized_entries.append(
            {
                "term": term,
                "status": status,
                "display_text": display_text,
                locale_key: tts_text,
                "notes": entry.get("notes", "").strip(),
            }
        )

    if pending_terms:
        raise ValueError(f"Pronunciation candidate review still has pending entries: {', '.join(pending_terms)}")

    report = {
        "detected_terms": detected_terms,
        "confirmed_terms": confirmed_terms,
        "ignored_terms": ignored_terms,
        "pending_terms": pending_terms,
        "requires_user_review": False,
    }
    return normalized_entries, report


def build_runtime_pronunciation_dictionary(
    entries: Sequence[Dict[str, str]],
    target_locale: str,
) -> List[Dict[str, object]]:
    """Convert confirmed markdown entries into runtime pronunciation dictionary JSON."""
    locale_key = f"tts_text_by_locale.{target_locale}"
    runtime_entries: List[Dict[str, object]] = []
    for entry in entries:
        if entry.get("status") != "confirmed":
            continue
        runtime_entries.append(
            {
                "term": entry["term"],
                "display_text": entry.get("display_text", entry["term"]),
                "tts_text_by_locale": {target_locale: entry[locale_key]},
            }
        )
    return runtime_entries


def prepare_pronunciation_entries(
    paragraphs: Sequence[str],
    target_locale: str,
    output_dir: Path,
    base_name: str,
    review_mode: str,
    review_file_arg: str,
) -> Tuple[List[Dict[str, object]], Path, Path, Dict[str, object]]:
    """Prepare runtime pronunciation entries, requiring user review when needed."""
    default_entries = load_pronunciation_dictionary()
    candidates = extract_pronunciation_candidates(paragraphs)
    candidates_path = (
        Path(review_file_arg).expanduser().resolve()
        if review_file_arg.strip()
        else output_dir / f"{base_name}_pronunciation_candidates.md"
    )
    generated_dictionary_path = output_dir / f"{base_name}_pronunciation_dictionary.json"

    requires_review = review_mode == "require" or (review_mode == "auto" and bool(candidates))
    candidate_report: Dict[str, object] = {
        "detected_terms": candidates,
        "confirmed_terms": [],
        "ignored_terms": [],
        "pending_terms": candidates if requires_review else [],
        "requires_user_review": requires_review,
    }

    if review_mode == "off":
        if generated_dictionary_path.exists():
            generated_dictionary_path.unlink()
        return default_entries, candidates_path, generated_dictionary_path, candidate_report

    if not candidates:
        if generated_dictionary_path.exists():
            generated_dictionary_path.unlink()
        candidate_report["requires_user_review"] = False
        candidate_report["pending_terms"] = []
        return default_entries, candidates_path, generated_dictionary_path, candidate_report

    if not candidates_path.exists():
        write_pronunciation_candidates_markdown(candidates, target_locale, candidates_path)
        raise RuntimeError(f"Review pronunciation candidates in {candidates_path} and rerun the workflow.")

    parsed_entries, parsed_report = parse_pronunciation_candidates_markdown(candidates_path, target_locale)
    runtime_entries = build_runtime_pronunciation_dictionary(parsed_entries, target_locale)
    candidate_report = parsed_report
    generated_dictionary_path.write_text(
        json.dumps(runtime_entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return default_entries + runtime_entries, candidates_path, generated_dictionary_path, candidate_report


def prepare_segment_for_tts(
    segment: str,
    target_locale: str,
    pronunciation_entries: Sequence[Dict[str, object]],
) -> Tuple[str, str, Dict[str, List[str]]]:
    """Keep display text stable while applying TTS-only pronunciation overrides."""
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


def translate_segments(
    segments: Sequence[str],
    source_language: str,
    target_locale: str,
    protected_terms: Sequence[str],
) -> List[str]:
    """Translate each segment unless the target language matches the source."""
    target_code = locale_to_translate_code(target_locale)
    source_code = "auto" if source_language == "auto" else locale_to_translate_code(resolve_locale(source_language))
    if source_code != "auto" and source_code == target_code:
        return list(segments)

    translator = GoogleTranslator(source=source_code, target=target_code)
    translated: List[str] = []
    for index, segment in enumerate(segments, start=1):
        print_progress(3, 6, f"Translating: {index}/{len(segments)}")
        masked_text, placeholder_map = apply_protected_terms(segment, protected_terms)
        translated_text = translator.translate(masked_text)
        restored = restore_protected_terms(translated_text, placeholder_map).strip()
        restored = re.sub(r"[,.?!，。！？、：；:;]+$", "", restored)
        translated.append(restored)
    return translated


def translate_segments_to_reference_chinese(
    segments: Sequence[str],
    target_locale: str,
    protected_terms: Sequence[str],
) -> List[str]:
    """Translate finalized target-language segments into Chinese reference text."""
    if target_locale in {"zh-CN", "zh-TW"}:
        return list(segments)

    source_code = locale_to_translate_code(target_locale)
    translator = GoogleTranslator(source=source_code, target="zh-CN")
    translated: List[str] = []
    for segment in segments:
        masked_text, placeholder_map = apply_protected_terms(segment, protected_terms)
        translated_text = translator.translate(masked_text)
        translated.append(restore_protected_terms(translated_text, placeholder_map).strip())
    return translated


def run_checked(command: Sequence[str]) -> None:
    """Run a subprocess and raise a readable error if it fails."""
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{completed.stderr.strip()}")


def list_edge_voices() -> List[Voice]:
    """Query Edge TTS voice metadata and return female voice candidates."""
    completed = subprocess.run(
        ["edge-tts", "--list-voices"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Unable to list Edge voices: {completed.stderr.strip()}")

    voices: List[Voice] = []
    for line in completed.stdout.splitlines():
        if not line or line.startswith("Name") or line.startswith("-"):
            continue
        columns = re.split(r"\s{2,}", line.strip(), maxsplit=3)
        if len(columns) >= 2 and columns[1] == "Female":
            voices.append(Voice(code=columns[0], label=columns[0].split("-")[-1]))
    return voices


def select_voices(target_locale: str, voice_count: int, explicit_voice_codes: str) -> List[Voice]:
    """Select female voices that best match the target language."""
    if explicit_voice_codes.strip():
        return [Voice(code=item.strip(), label=item.strip().split("-")[-1]) for item in explicit_voice_codes.split(",") if item.strip()]

    available = list_edge_voices()
    preferred_prefixes = VOICE_LOCALE_PREFERENCES.get(target_locale, [target_locale])
    selected: List[Voice] = []

    def add_matching(prefixes: Sequence[str]) -> None:
        for prefix in prefixes:
            for voice in available:
                if voice in selected:
                    continue
                if voice.code.startswith(prefix):
                    selected.append(voice)
                if len(selected) >= voice_count:
                    return

    add_matching(preferred_prefixes)
    if len(selected) < voice_count:
        base_language = target_locale.split("-")[0]
        add_matching([f"{base_language}-"])
    if not selected:
        raise RuntimeError(f"No female voices available for target locale {target_locale}. Use --voice-codes to override explicitly.")
    if len(selected) < voice_count:
        print_progress(0, 0, f"Only found {len(selected)} native female voices for {target_locale}; requested {voice_count}.")
    return selected[:voice_count]


def make_safe_keyword(text: str, index: int) -> str:
    """Build a readable file-name keyword from the segment text."""
    compact = re.sub(r"[^\w\u3400-\u9FFF]+", "_", text, flags=re.UNICODE).strip("_")
    compact = re.sub(r"_+", "_", compact)
    if not compact:
        return f"segment_{index:02d}"
    return compact[:28]


def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    whole_seconds = int(seconds)
    milliseconds = int(round((seconds - whole_seconds) * 1000))
    if milliseconds == 1000:
        whole_seconds += 1
        milliseconds = 0
    hours = whole_seconds // 3600
    minutes = (whole_seconds % 3600) // 60
    secs = whole_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def get_audio_duration(file_path: Path) -> float:
    """Read audio duration with ffprobe."""
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Unable to read audio duration: {completed.stderr.strip()}")
    return float(completed.stdout.strip())


def write_numbered_markdown(title: str, segments: Sequence[str], output_path: Path) -> None:
    """Write numbered segments into a markdown file."""
    lines = [f"# {title}", ""]
    for index, segment in enumerate(segments, start=1):
        lines.append(f"{index}. {segment}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bilingual_markdown(source_segments: Sequence[str], target_segments: Sequence[str], output_path: Path) -> None:
    """Write side-by-side review markdown."""
    lines = ["# Bilingual Review", "", "| No. | Source | Target |", "| --- | --- | --- |"]
    for index, (source_text, target_text) in enumerate(zip(source_segments, target_segments), start=1):
        source_cell = source_text.replace("|", "\\|")
        target_cell = target_text.replace("|", "\\|")
        lines.append(f"| {index} | {source_cell} | {target_cell} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_cleaned_input(paragraphs: Sequence[str], output_dir: Path, base_name: str) -> Path:
    """Persist the cleaned source content for auditability."""
    cleaned_input_path = output_dir / f"{base_name}_cleaned_input.md"
    cleaned_input_path.write_text("\n\n".join(paragraphs).strip() + "\n", encoding="utf-8")
    return cleaned_input_path


def write_srt_from_cues(cues: Sequence[Dict[str, str]], output_path: Path) -> None:
    """Write an SRT file from normalized cue dictionaries."""
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
    """Reuse existing cue timing with Chinese text for editor reference."""
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
    manifests: Sequence[Dict[str, object]],
    pronunciation_candidates_path: Path = None,
    generated_pronunciation_dictionary_path: Path = None,
    pronunciation_candidate_report: Dict[str, object] = None,
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
        "pronunciation_candidates_path": str(pronunciation_candidates_path) if pronunciation_candidates_path else "",
        "generated_pronunciation_dictionary_path": str(generated_pronunciation_dictionary_path)
        if generated_pronunciation_dictionary_path
        else "",
        "pronunciation_candidate_report": pronunciation_candidate_report or {},
        "voices": list(manifests),
    }


def generate_tts_and_srt(
    segments: Sequence[str],
    voices: Sequence[Voice],
    output_dir: Path,
    base_name: str,
    rate: str,
    pronunciation_entries: Sequence[Dict[str, object]] = (),
    protected_terms: Sequence[str] = (),
) -> List[Dict[str, str]]:
    """Generate MP3 files and one cumulative SRT per voice."""
    manifests: List[Dict[str, str]] = []
    for voice in voices:
        voice_suffix = voice.code.split("-")[-1]
        voice_locale = "-".join(voice.code.split("-")[:2])
        voice_dir = output_dir / f"{base_name}_tts_{voice_suffix}"
        voice_dir.mkdir(parents=True, exist_ok=True)

        current_time = 0.0
        matched_terms: List[str] = []
        unresolved_terms: List[str] = []
        cues: List[Dict[str, str]] = []
        for index, text in enumerate(segments, start=1):
            print_progress(4, 6, f"Generating TTS ({voice.code}): {index}/{len(segments)}")
            display_text, tts_text, report = prepare_segment_for_tts(
                segment=text,
                target_locale=voice_locale,
                pronunciation_entries=pronunciation_entries,
            )
            matched_terms.extend(report["matched_terms"])
            unresolved_terms.extend(report["unresolved_terms"])
            keyword = make_safe_keyword(display_text, index)
            mp3_path = voice_dir / f"{index:02d}_{keyword}.mp3"
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
            start_time = format_srt_time(current_time)
            end_time = format_srt_time(current_time + duration)
            cues.append(
                {
                    "index": index,
                    "start": start_time,
                    "end": end_time,
                    "text": display_text,
                }
            )
            current_time += duration + SRT_GAP_SECONDS

        srt_path = output_dir / f"{base_name}_{voice_suffix}.srt"
        write_srt_from_cues(cues, srt_path)
        reference_srt_path = output_dir / f"{base_name}_{voice_suffix}_zh-CN.srt"
        if voice_locale in {"zh-CN", "zh-TW"}:
            reference_srt_path_str = ""
        else:
            chinese_segments = translate_segments_to_reference_chinese(
                segments,
                target_locale=voice_locale,
                protected_terms=protected_terms,
            )
            reference_cues = build_reference_chinese_cues(cues, chinese_segments)
            write_srt_from_cues(reference_cues, reference_srt_path)
            reference_srt_path_str = str(reference_srt_path)
        manifests.append(
            {
                "voice_code": voice.code,
                "voice_label": voice_suffix,
                "audio_dir": str(voice_dir),
                "srt_path": str(srt_path),
                "reference_srt_path": reference_srt_path_str,
                "matched_terms": sorted(set(matched_terms)),
                "unresolved_terms": sorted(set(unresolved_terms)),
            }
        )
    return manifests


def ensure_dependencies() -> None:
    """Verify external binaries required by the workflow."""
    missing = []
    for binary in ("edge-tts", "ffprobe"):
        if subprocess.run(["which", binary], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).returncode != 0:
            missing.append(binary)
    if missing:
        raise RuntimeError(f"Missing required binaries: {', '.join(missing)}")


def build_output_directory(args: argparse.Namespace, source_path: Path, target_locale: str) -> Tuple[Path, str]:
    """Resolve the output directory and stable file prefix."""
    project_name = args.project_name.strip() or source_path.stem
    base_name = re.sub(r"[^\w\u3400-\u9FFF-]+", "_", project_name, flags=re.UNICODE).strip("_") or "voice_project"
    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        output_dir = source_path.parent / f"{base_name}_{target_locale}_voice_workflow"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir, base_name


def load_bilingual_review(path: Path) -> Tuple[List[str], List[str]]:
    """Load source and target segments from an edited bilingual review markdown file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    source_segments = []
    target_segments = []
    for line in lines:
        if line.strip().startswith("|") and not line.strip().startswith("| No.") and not line.strip().startswith("| ---"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                source_segments.append(parts[2].replace("\\|", "|").strip())
                target_segments.append(parts[3].replace("\\|", "|").strip())
    return source_segments, target_segments


def main() -> int:
    """Run the full multilingual video voice workflow."""
    args = parse_args()
    ensure_dependencies()

    source_text, source_path = read_source_text(args)
    target_locale, language_resolution = resolve_locale_with_metadata(args.target_language)
    output_dir, base_name = build_output_directory(args, source_path, target_locale)
    protected_terms = [item.strip() for item in args.protected_terms.split(",") if item.strip()]
    language_resolution["translator_code"] = locale_to_translate_code(target_locale)

    source_markdown_path = output_dir / f"{base_name}_source_segments.md"
    target_markdown_path = output_dir / f"{base_name}_{target_locale}_segments.md"
    bilingual_markdown_path = output_dir / f"{base_name}_bilingual_review.md"
    manifest_path = output_dir / f"{base_name}_manifest.json"

    if args.stage in ("all", "prepare"):
        print_progress(1, 6, f"Cleaning input: {source_path}")
        print_progress(2, 6, f"Resolving language: {args.target_language} -> {target_locale}")

        paragraphs, cleaning_report = normalize_markdown_with_report(source_text)
        source_segments = build_spoken_segments(paragraphs)
        if not source_segments:
            raise RuntimeError("No usable content found after cleaning the source text.")
        pronunciation_entries, pronunciation_candidates_path, generated_dictionary_path, pronunciation_candidate_report = prepare_pronunciation_entries(
            paragraphs=paragraphs,
            target_locale=target_locale,
            output_dir=output_dir,
            base_name=base_name,
            review_mode=args.pronunciation_review_mode,
            review_file_arg=args.pronunciation_candidates_file,
        )

        target_segments = translate_segments(source_segments, args.source_language, target_locale, protected_terms)
        cleaned_input_path = write_cleaned_input(paragraphs, output_dir, base_name)

        print_progress(5, 6, "Writing review files")
        write_numbered_markdown("Source Segments", source_segments, source_markdown_path)
        write_numbered_markdown(f"Target Segments ({target_locale})", target_segments, target_markdown_path)
        write_bilingual_markdown(source_segments, target_segments, bilingual_markdown_path)
        
        if args.stage == "prepare":
            print_progress(6, 6, "Preparation complete. Review files written.")
            return 0

    if args.stage == "generate":
        if not bilingual_markdown_path.exists():
            raise FileNotFoundError(f"Review file not found: {bilingual_markdown_path}. Run --stage prepare first.")
        print_progress(1, 6, f"Loading reviewed segments from {bilingual_markdown_path.name}")
        source_segments, target_segments = load_bilingual_review(bilingual_markdown_path)
        
        # dummy reports since we skipped the prepare stage
        cleaning_report = {"numbering_detected": False, "numbering_removed_line_count": 0, "empty_lines_preserved": 0}
        paragraphs = source_segments
        cleaned_input_path = output_dir / f"{base_name}_cleaned_input.md"
        
        pronunciation_entries, pronunciation_candidates_path, generated_dictionary_path, pronunciation_candidate_report = prepare_pronunciation_entries(
            paragraphs=paragraphs,
            target_locale=target_locale,
            output_dir=output_dir,
            base_name=base_name,
            review_mode="off",
            review_file_arg=args.pronunciation_candidates_file,
        )

    voices = select_voices(target_locale, max(1, args.voice_count), args.voice_codes)
    manifests = generate_tts_and_srt(
        target_segments,
        voices,
        output_dir,
        base_name,
        args.rate,
        pronunciation_entries=pronunciation_entries,
        protected_terms=protected_terms,
    )

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
        pronunciation_candidates_path=pronunciation_candidates_path,
        generated_pronunciation_dictionary_path=generated_dictionary_path,
        pronunciation_candidate_report=pronunciation_candidate_report,
    )
    print_progress(6, 6, "Writing manifest")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

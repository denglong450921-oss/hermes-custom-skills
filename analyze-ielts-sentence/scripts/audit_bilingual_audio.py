#!/usr/bin/env python3
"""Audit IELTS HTML for complete bilingual, highlight, and Edge TTS coverage."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlparse


UI_ONLY_TAGS = {"title", "script", "style"}


class LessonParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict[str, object]] = []
        self.units: list[dict[str, object]] = []
        self.unpaired_english: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        inside_unit = any(frame["is_unit"] for frame in self.stack)
        frame: dict[str, object] = {
            "tag": tag,
            "is_unit": "english-unit" in classes,
            "lang": attributes.get("lang"),
            "line": self.getpos()[0],
        }
        self.stack.append(frame)
        if frame["is_unit"]:
            unit = {
                "line": frame["line"],
                "english": False,
                "english_parts": [],
                "chinese": False,
                "mark": False,
                "note": False,
                "play": False,
                "audio": False,
                "audio_transcript": attributes.get("data-audio-transcript") or "",
                "play_count": 0,
                "audio_sources": [],
                "button_transcripts": [],
            }
            frame["unit"] = unit
            self.units.append(unit)
        unit = self._active_unit()
        if unit:
            if attributes.get("lang") == "en":
                unit["english"] = True
            if attributes.get("lang") == "zh-CN":
                unit["chinese"] = True
            if tag == "mark":
                unit["mark"] = True
            if "highlight-note" in classes or "highlight-notes" in classes:
                unit["note"] = True
            if "tts-play" in classes:
                unit["play"] = True
                source = attributes.get("data-audio-src") or ""
                unit["audio"] = bool(source)
                unit["play_count"] = int(unit["play_count"]) + 1
                cast_sources = unit["audio_sources"]
                if isinstance(cast_sources, list):
                    cast_sources.append(source)
                cast_transcripts = unit["button_transcripts"]
                if isinstance(cast_transcripts, list):
                    cast_transcripts.append(
                        attributes.get("data-audio-transcript") or ""
                    )
        elif attributes.get("lang") == "en" and not inside_unit and tag not in UI_ONLY_TAGS:
            self.unpaired_english.append((self.getpos()[0], f"<{tag} lang=\"en\">"))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        unit = self._active_unit()
        if not unit:
            return
        if any(frame.get("lang") == "en" for frame in self.stack):
            parts = unit.get("english_parts")
            if isinstance(parts, list):
                parts.append(data)

    def _active_unit(self) -> dict[str, object] | None:
        for frame in reversed(self.stack):
            unit = frame.get("unit")
            if isinstance(unit, dict):
                return unit
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    lesson = LessonParser()
    lesson.feed(args.html.read_text(encoding="utf-8"))

    failures: list[str] = []
    if not lesson.units:
        failures.append("No .english-unit containers found.")
    required = ("english", "chinese", "mark", "note", "play", "audio")
    used_audio_sources: dict[str, int] = {}
    for unit in lesson.units:
        missing = [field for field in required if not unit[field]]
        if missing:
            failures.append(f"Line {unit['line']}: english-unit missing {', '.join(missing)}")
        line = int(unit["line"])
        visible_english = normalize_text(" ".join(unit["english_parts"]))
        declared_transcript = normalize_text(str(unit["audio_transcript"]))
        if not declared_transcript:
            failures.append(f"Line {line}: missing data-audio-transcript on .english-unit")
        elif visible_english != declared_transcript:
            failures.append(
                f"Line {line}: visible English does not exactly match "
                "data-audio-transcript"
            )
        if len(re.findall(r"[.!?](?:\s|$)", declared_transcript)) > 1:
            failures.append(
                f"Line {line}: one MP3 may not contain multiple English sentences"
            )
        if int(unit["play_count"]) != 1:
            failures.append(
                f"Line {line}: expected exactly one .tts-play control, "
                f"found {unit['play_count']}"
            )
        sources = [str(value) for value in unit["audio_sources"] if value]
        if len(sources) == 1:
            source = sources[0]
            used_audio_sources.setdefault(source, line)
            if used_audio_sources[source] != line:
                failures.append(
                    f"Line {line}: data-audio-src is reused from line "
                    f"{used_audio_sources[source]}: {source}"
                )
            validate_audio_source(args.html, line, source, failures)
        button_transcripts = [
            normalize_text(str(value)) for value in unit["button_transcripts"]
        ]
        if len(button_transcripts) == 1 and button_transcripts[0] != declared_transcript:
            failures.append(
                f"Line {line}: play-button transcript does not match unit transcript"
            )
    for line, element in lesson.unpaired_english:
        failures.append(f"Line {line}: learner-facing English outside .english-unit: {element}")

    text = args.html.read_text(encoding="utf-8")
    for speed in ("0.6", "0.7", "0.8", "0.9"):
        if f'data-speed="{speed}"' not in text:
            failures.append(f"Missing required speed control: {speed}x")
    if "playbackRate" not in text or "aria-pressed" not in text:
        failures.append("Playback-rate or aria-pressed state logic is missing.")

    if failures:
        print("Bilingual/audio audit failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(f"Bilingual/audio audit passed: {len(lesson.units)} English units checked.")


def normalize_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+([,.;:!?])", r"\1", value)


def validate_audio_source(
    html_path: Path,
    line: int,
    source: str,
    failures: list[str],
) -> None:
    parsed = urlparse(source)
    if parsed.scheme or source.startswith(("/", "//")):
        failures.append(f"Line {line}: audio source must be a local relative path: {source}")
        return
    if Path(parsed.path).suffix.lower() != ".mp3":
        failures.append(f"Line {line}: audio source must end in .mp3: {source}")
        return
    audio_path = (html_path.parent / parsed.path).resolve()
    if not audio_path.exists():
        failures.append(f"Line {line}: referenced MP3 does not exist: {source}")
    elif audio_path.stat().st_size == 0:
        failures.append(f"Line {line}: referenced MP3 is empty: {source}")


if __name__ == "__main__":
    main()

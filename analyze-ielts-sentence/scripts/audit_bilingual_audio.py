#!/usr/bin/env python3
"""Audit IELTS HTML for complete bilingual, highlight, and Edge TTS coverage."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path


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
                "chinese": False,
                "mark": False,
                "note": False,
                "play": False,
                "audio": False,
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
                unit["audio"] = bool(attributes.get("data-audio-src"))
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
    for unit in lesson.units:
        missing = [field for field in required if not unit[field]]
        if missing:
            failures.append(f"Line {unit['line']}: english-unit missing {', '.join(missing)}")
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


if __name__ == "__main__":
    main()

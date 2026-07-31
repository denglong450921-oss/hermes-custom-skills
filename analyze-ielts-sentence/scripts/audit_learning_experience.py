#!/usr/bin/env python3
"""Audit an IELTS learning-studio HTML page for the skill's core UX contract."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path


class StudioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.classes: list[set[str]] = []
        self.ids: set[str] = set()
        self.data_stages: set[str] = set()
        self.memory_strategies: list[str] = []
        self.question_dimensions: list[str] = []
        self.response_formats: set[str] = set()
        self.confidence_controls = 0
        self.hidden_results = False
        self.progressive_reveals = 0
        self.reveal_controls = 0
        self.keyword_labs = 0
        self.keyword_cards = 0
        self.difficulty_ladders = 0
        self.difficulty_levels: set[str] = set()
        self.has_reduced_motion = False
        self.has_live_region = False
        self.has_main = False
        self.has_nav = False
        self.scripts: list[str] = []
        self._in_script = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        classes = set((attrs.get("class") or "").split())
        self.classes.append(classes)
        if attrs.get("id"):
            self.ids.add(attrs["id"] or "")
        if attrs.get("data-stage"):
            self.data_stages.add(attrs["data-stage"] or "")
        if "memory-game" in classes:
            self.memory_strategies.append(attrs.get("data-memory-strategy") or "")
        if "progressive-reveal" in classes:
            self.progressive_reveals += 1
        if "keyword-lab" in classes:
            self.keyword_labs += 1
        if "keyword-card" in classes:
            self.keyword_cards += 1
        if "difficulty-ladder" in classes:
            self.difficulty_ladders += 1
        if attrs.get("data-difficulty"):
            self.difficulty_levels.add(attrs["data-difficulty"] or "")
        if "data-reveal-next" in attrs:
            self.reveal_controls += 1
        if "summative-question" in classes:
            if attrs.get("data-dimension"):
                self.question_dimensions.append(attrs["data-dimension"] or "")
            if attrs.get("data-response-format"):
                self.response_formats.add(attrs["data-response-format"] or "")
        if "data-confidence" in attrs:
            self.confidence_controls += 1
        if attrs.get("id") == "results" and "hidden" in attrs:
            self.hidden_results = True
        if attrs.get("aria-live"):
            self.has_live_region = True
        if tag == "main":
            self.has_main = True
        if tag == "nav":
            self.has_nav = True
        if tag == "script":
            self._in_script = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_script = False

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self.scripts.append(data)
        if "prefers-reduced-motion" in data:
            self.has_reduced_motion = True


def audit(path: Path) -> list[str]:
    parser = StudioParser()
    parser.feed(path.read_text(encoding="utf-8"))
    failures: list[str] = []

    required_stages = {"notice", "build", "recall", "transfer", "review"}
    if not required_stages.issubset(parser.data_stages):
        failures.append("missing one or more stages: notice, build, recall, transfer, review")
    if not parser.has_main or not parser.has_nav:
        failures.append("missing semantic main or nav landmark")
    if len(parser.memory_strategies) < 2:
        failures.append("fewer than two .memory-game sections")
    if parser.progressive_reveals < 1 or parser.reveal_controls < 1:
        failures.append("missing .progressive-reveal container or data-reveal-next control")
    if parser.keyword_labs < 1:
        failures.append("missing .keyword-lab section")
    if not 4 <= parser.keyword_cards <= 6:
        failures.append(
            f"expected 4–6 .keyword-card units, found {parser.keyword_cards}"
        )
    if parser.difficulty_ladders < 1:
        failures.append("missing .difficulty-ladder section")
    required_difficulties = {
        "easy-notice",
        "easy-use",
        "moderate-transfer",
    }
    if not required_difficulties.issubset(parser.difficulty_levels):
        failures.append(
            "difficulty ladder must include easy-notice, easy-use, and "
            "moderate-transfer"
        )
    if any("hard" in level.lower() for level in parser.difficulty_levels):
        failures.append("unrequested hard difficulty tier detected")
    if any(not strategy.strip() for strategy in parser.memory_strategies):
        failures.append("every memory game needs data-memory-strategy")
    if len(parser.question_dimensions) != 8:
        failures.append(f"expected 8 summative questions, found {len(parser.question_dimensions)}")
    expected_dimensions = {"meaning", "structure", "vocabulary", "transfer"}
    counts = {name: parser.question_dimensions.count(name) for name in expected_dimensions}
    if any(counts[name] != 2 for name in expected_dimensions):
        failures.append(f"dimension distribution must be 2 each; found {counts}")
    if len(parser.response_formats) < 3:
        failures.append("summative assessment uses fewer than three response formats")
    if parser.confidence_controls < 8:
        failures.append("each summative item needs a confidence control")
    if not parser.hidden_results:
        failures.append("#results must be hidden before submission")
    if not parser.has_reduced_motion:
        failures.append("missing prefers-reduced-motion support")
    if not parser.has_live_region:
        failures.append("missing aria-live status region")

    script = "\n".join(parser.scripts)
    for token, message in (
        ("retry-wrong", "missing retry-wrong behavior"),
        ("10 分钟", "missing 10-minute review"),
        ("1 天", "missing 1-day review"),
        ("3 天", "missing 3-day review"),
        ("confidentWrong", "missing confident-wrong calibration"),
    ):
        if token not in script and token not in path.read_text(encoding="utf-8"):
            failures.append(message)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    failures = audit(args.html)
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: learning-experience contract satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

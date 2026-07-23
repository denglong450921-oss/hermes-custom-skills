#!/usr/bin/env python3
"""Validate a generated course's 30/70 plan, review chain, and HTML shell."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_course_data(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8").strip()
    prefix = "window.COURSE_DATA = "
    if not raw.startswith(prefix) or not raw.endswith(";"):
        fail(f"{path} is not a supported course-data.js file")
    return json.loads(raw[len(prefix) : -1])


def validate_time_plan(day_number: int, day: dict[str, object]) -> None:
    plan = day.get("timePlan")
    if not isinstance(plan, list) or len(plan) != 6:
        fail(f"day {day_number} must contain six timePlan blocks")

    seen_ids: set[str] = set()
    totals = {"learning": 0, "testing": 0}
    for block in plan:
        if not isinstance(block, dict):
            fail(f"day {day_number} contains a non-object time block")
        block_id = block.get("id")
        mode = block.get("mode")
        percent = block.get("percent")
        if not isinstance(block_id, str) or block_id in seen_ids:
            fail(f"day {day_number} has a missing or duplicate block id")
        if mode not in totals:
            fail(f"day {day_number} block {block_id} has invalid mode {mode!r}")
        if not isinstance(percent, int) or percent <= 0:
            fail(f"day {day_number} block {block_id} has invalid percent")
        seen_ids.add(block_id)
        totals[mode] += percent

    if totals != {"learning": 30, "testing": 70}:
        fail(f"day {day_number} has time balance {totals}, expected 30/70")

    review_source = day.get("reviewSourceDay")
    expected_source: object = "prerequisites" if day_number == 1 else day_number - 1
    if review_source != expected_source:
        fail(
            f"day {day_number} reviews {review_source!r}; "
            f"expected {expected_source!r}"
        )


def validate_html_shell(course_root: Path, day_count: int) -> None:
    expected = [course_root / "index.html"] + [
        course_root / f"day{day:02}.html" for day in range(1, day_count + 1)
    ]
    for path in expected:
        if not path.is_file():
            fail(f"missing HTML page: {path}")
        text = path.read_text(encoding="utf-8")
        for marker in (
            '<meta charset="utf-8">',
            "assets/styles.css",
            "assets/course-data.js",
            "assets/app.js",
        ):
            if marker not in text:
                fail(f"{path.name} is missing {marker}")

    styles = (course_root / "assets" / "styles.css").read_text(encoding="utf-8")
    for token in ("--sun", "--coral", "--sky", "--grape", "--mint"):
        if token not in styles:
            fail(f"styles.css is missing vibrant palette token {token}")
    for marker in (
        "prefers-reduced-motion",
        ".mission-card",
        ".ratio-meter",
        ".motion-on",
    ):
        if marker not in styles:
            fail(f"styles.css is missing visual-system marker {marker}")

    app = (course_root / "assets" / "app.js").read_text(encoding="utf-8")
    for marker in (
        "localStorage",
        "motion-toggle",
        "progress-fill",
        "data-complete-block",
        "aria-live",
    ):
        if marker not in app:
            fail(f"app.js is missing interaction marker {marker}")

    for path in course_root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".html", ".css", ".js"}:
            if re.search(r"https?://", path.read_text(encoding="utf-8")):
                fail(f"external URL found in offline asset: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a child course's daily balance and HTML shell."
    )
    parser.add_argument("course_root", type=Path)
    args = parser.parse_args()
    course_root = args.course_root.expanduser().resolve()
    data_path = course_root / "assets" / "course-data.js"
    if not data_path.is_file():
        fail(f"missing course data: {data_path}")

    course = load_course_data(data_path)
    days = course.get("days")
    if not isinstance(days, list) or not days:
        fail("course has no daily records")
    split = course.get("timeSplit")
    if split != {"learning": 30, "testing": 70}:
        fail(f"course timeSplit is {split!r}, expected 30/70")

    for number, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            fail(f"day {number} is not an object")
        validate_time_plan(number, day)
    validate_html_shell(course_root, len(days))
    print(
        "PASS: "
        f"{len(days)} days, exact 30/70 balance, complete previous-day review chain, "
        "cartoon interaction shell, and offline assets"
    )


if __name__ == "__main__":
    main()

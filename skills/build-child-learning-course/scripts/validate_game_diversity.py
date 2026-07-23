#!/usr/bin/env python3
"""Validate the game library and a generated course's coherent game spine."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ENTRY_RE = re.compile(
    r"^## (G\d{2}) · ([^\n]+)\n(?P<body>.*?)(?=^## G\d{2} · |\Z)",
    re.MULTILINE | re.DOTALL,
)
REQUIRED_FIELDS = (
    "玩法家族",
    "核心动作",
    "记忆机制",
    "适用学科",
    "独立证据",
    "实现规则",
    "避免",
)


def parse_args() -> argparse.Namespace:
    skill_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Validate learning-game diversity and course rotation."
    )
    parser.add_argument(
        "--skill-root", type=Path, default=skill_root, help="Skill folder"
    )
    parser.add_argument(
        "--course-data",
        type=Path,
        help="Optional generated assets/course-data.js to validate",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse_library(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    games: dict[str, dict[str, str]] = {}
    for match in ENTRY_RE.finditer(text):
        game_id, title, body = match.group(1), match.group(2).strip(), match.group("body")
        if game_id in games:
            fail(f"duplicate game id {game_id}")
        fields: dict[str, str] = {}
        for field in REQUIRED_FIELDS:
            field_match = re.search(rf"^- \*\*{re.escape(field)}\*\*：(.+)$", body, re.MULTILINE)
            if not field_match:
                fail(f"{game_id} is missing field {field}")
            fields[field] = field_match.group(1).strip()
        games[game_id] = {"title": title, **fields}

    if len(games) <= 10:
        fail(f"game library has {len(games)} types; more than 10 are required")
    if len({game["玩法家族"] for game in games.values()}) < 8:
        fail("game library needs at least 8 distinct cognitive families")
    if sum("产出证据" in game["独立证据"] for game in games.values()) < 6:
        fail("game library needs at least 6 production-evidence games")
    for subject in ("英语", "数学", "语文"):
        coverage = sum(subject in game["适用学科"] for game in games.values())
        if coverage < 10:
            fail(f"{subject} is covered by only {coverage} game types")
    return games


def load_course_data(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8").strip()
    prefix = "window.COURSE_DATA = "
    if not raw.startswith(prefix) or not raw.endswith(";"):
        fail(f"{path} is not a supported course-data.js file")
    return json.loads(raw[len(prefix) : -1])


def validate_course(course: dict[str, object], library: dict[str, dict[str, str]]) -> None:
    days = course.get("days")
    if not isinstance(days, list) or not days:
        fail("course has no daily records")

    core_games = course.get("coreGames")
    if not isinstance(core_games, list) or not all(
        isinstance(game_id, str) for game_id in core_games
    ):
        fail("course must define a coreGames list")
    if len(set(core_games)) != len(core_games):
        fail("coreGames contains duplicate ids")
    if any(game_id not in library for game_id in core_games):
        fail("coreGames contains an unknown game id")
    if len(days) >= 10 and not 4 <= len(core_games) <= 6:
        fail(
            f"long course selects {len(core_games)} core games; "
            "four to six are required"
        )

    used: list[str] = []
    families: set[str] = set()
    evidence_types: set[str] = set()
    stages: dict[str, set[str]] = {game_id: set() for game_id in core_games}
    allowed_stages = {"onboarding", "consolidation", "transfer"}
    for index, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            fail(f"day {index} is not an object")
        games = day.get("games")
        if not isinstance(games, list) or not 1 <= len(games) <= 2:
            fail(f"day {index} must contain one or two games")
        day_ids: list[str] = []
        for game in games:
            if not isinstance(game, dict) or not isinstance(game.get("id"), str):
                fail(f"day {index} has an invalid game record")
            game_id = game["id"]
            if game_id not in library:
                fail(f"day {index} uses unknown game id {game_id}")
            if game_id not in core_games:
                fail(f"day {index} uses {game_id}, which is not a selected core game")
            if game_id in day_ids:
                fail(f"day {index} repeats game id {game_id}")
            stage = game.get("stage")
            if stage not in allowed_stages:
                fail(f"day {index} game {game_id} has invalid stage {stage!r}")
            day_ids.append(game_id)
            used.append(game_id)
            stages[game_id].add(stage)
            families.add(library[game_id]["玩法家族"])
            evidence = library[game_id]["独立证据"]
            if "识别" in evidence:
                evidence_types.add("recognition")
            if "产出" in evidence:
                evidence_types.add("production")

    if set(used) != set(core_games):
        missing = sorted(set(core_games) - set(used))
        fail(f"selected core games never used: {', '.join(missing)}")
    if len(days) >= 10:
        for game_id in core_games:
            count = used.count(game_id)
            if count < 3:
                fail(f"core game {game_id} appears only {count} times; three required")
            missing_stages = allowed_stages - stages[game_id]
            if missing_stages:
                fail(
                    f"core game {game_id} is missing stages: "
                    f"{', '.join(sorted(missing_stages))}"
                )
    if len(days) >= 5 and evidence_types != {"recognition", "production"}:
        fail("course must include both recognition and production evidence")

    print(
        "PASS: "
        f"{len(days)} days, {len(core_games)} coherent core games, "
        f"{len(used)} testing slots, {len(families)} families, "
        f"evidence={','.join(sorted(evidence_types))}"
    )


def main() -> None:
    args = parse_args()
    library_path = args.skill_root.resolve() / "references" / "game-patterns.md"
    if not library_path.is_file():
        fail(f"missing game library: {library_path}")
    library = parse_library(library_path)
    print(f"PASS: game library contains {len(library)} validated types")
    if args.course_data:
        validate_course(load_course_data(args.course_data.resolve()), library)


if __name__ == "__main__":
    main()

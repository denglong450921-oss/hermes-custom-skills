#!/usr/bin/env python3
"""Validate Harness exam cases and run artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_CASE_FILES = ["meta.yaml", "task.md", "rubric.md", "env.yaml"]
REQUIRED_REPORTS = [
    "reports/latest.md",
    "reports/latest-stats.yaml",
    "reports/score-history.yaml",
    "reports/batch-insights.md",
]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def parse_score(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip("'\"")
    return data


def validate_cases(root: Path) -> list[dict]:
    problems = []
    cases_dir = root / "cases"
    if not cases_dir.exists():
        return [{"path": "cases", "problem": "missing cases directory"}]
    case_dirs = [p for p in sorted(cases_dir.iterdir()) if p.is_dir()]
    if not case_dirs:
        return [{"path": "cases", "problem": "no exam case directories found"}]
    for case in case_dirs:
        for name in REQUIRED_CASE_FILES:
            if not (case / name).exists():
                problems.append({"path": str((case / name).relative_to(root)), "problem": "missing required case file"})
        task = read(case / "task.md") if (case / "task.md").exists() else ""
        rubric = read(case / "rubric.md") if (case / "rubric.md").exists() else ""
        if "Examinee Visible Prompt" not in task:
            problems.append({"path": str((case / "task.md").relative_to(root)), "problem": "task should mark the examinee-visible prompt"})
        if "Hard Pass" not in rubric:
            problems.append({"path": str((case / "rubric.md").relative_to(root)), "problem": "rubric should define hard pass criteria"})
        if "Evidence" not in rubric:
            problems.append({"path": str((case / "rubric.md").relative_to(root)), "problem": "rubric should define evidence requirements"})
    return problems


def validate_runs(root: Path) -> list[dict]:
    problems = []
    runs_dir = root / "runs"
    if not runs_dir.exists():
        return [{"path": "runs", "problem": "missing runs directory"}]
    run_dirs = [p for p in runs_dir.rglob("run-*") if p.is_dir()]
    if not run_dirs:
        return [{"path": "runs", "problem": "no run-* directories found"}]
    for run in sorted(run_dirs):
        rel = run.relative_to(root)
        for name in ["transcript.for-judge.txt", "score.yaml", "review.md"]:
            if not (run / name).exists():
                problems.append({"path": str(rel / name), "problem": "missing required run artifact"})
        score_path = run / "score.yaml"
        if score_path.exists():
            score = parse_score(read(score_path))
            for key in ["result", "compliance", "execution_quality", "overall", "summary"]:
                if key not in score:
                    problems.append({"path": str(score_path.relative_to(root)), "problem": f"score.yaml missing {key}"})
            if score.get("result") not in {"pass", "fail"}:
                problems.append({"path": str(score_path.relative_to(root)), "problem": "result should be pass or fail"})
        review_path = run / "review.md"
        if review_path.exists():
            review = read(review_path)
            if "evidence" not in review.lower():
                problems.append({"path": str(review_path.relative_to(root)), "problem": "review should include evidence"})
            for marker in ["[workflow]", "[eval]", "[capability]"]:
                if marker not in review:
                    problems.append({"path": str(review_path.relative_to(root)), "problem": f"review missing {marker} improvement category"})
    return problems


def validate_reports(root: Path) -> list[dict]:
    problems = []
    for rel in REQUIRED_REPORTS:
        if not (root / rel).exists():
            problems.append({"path": rel, "problem": "missing batch report"})
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Harness eval workspace root")
    parser.add_argument("--allow-missing-reports", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    problems = []
    problems.extend(validate_cases(root))
    problems.extend(validate_runs(root))
    if not args.allow_missing_reports:
        problems.extend(validate_reports(root))
    result = {"root": str(root), "passed": not problems, "problems": problems}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())


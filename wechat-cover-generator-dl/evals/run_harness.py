#!/usr/bin/env python3
"""Run the bundled cover generator against realistic eval cases."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
GRADER = SKILL_DIR / "evals" / "grader.py"
RUNNER = SKILL_DIR / "scripts" / "run_pipeline.py"
TRACES_DIR = SKILL_DIR / "evals" / "traces"


def load_evals() -> dict:
    return json.loads(EVALS_FILE.read_text(encoding="utf-8"))


def run_pipeline(case: dict, case_dir: Path) -> tuple[Path, subprocess.CompletedProcess[str]]:
    output = case_dir / "cover.png"
    report = case_dir / "report.json"
    cmd = [
        sys.executable,
        str(RUNNER),
        "--style",
        case.get("style", "auto"),
        "--output",
        str(output),
        "--report",
        str(report),
    ]
    if case.get("input_markdown"):
        md_path = case_dir / "article.md"
        md_path.write_text(case["input_markdown"], encoding="utf-8")
        cmd.extend(["--input", str(md_path)])
    elif case.get("topic"):
        cmd.extend(["--topic", case["topic"]])
    if case.get("title"):
        cmd.extend(["--title", case["title"]])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return report, result


def run_grader(report: Path, checks: list[str]) -> tuple[dict, subprocess.CompletedProcess[str]]:
    check_payload = [{"text": check, "check": check} for check in checks]
    result = subprocess.run(
        [sys.executable, str(GRADER), str(report), json.dumps(check_payload)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        parsed = {
            "grader_output": {
                "passed": False,
                "evidence": result.stdout or result.stderr,
            }
        }
    return parsed, result


def build_trace(case: dict, report: Path, pipeline_result: subprocess.CompletedProcess[str], grade: dict) -> dict:
    passed = sum(1 for result in grade.values() if result.get("passed"))
    total = len(grade)
    return {
        "case_id": case["id"],
        "task": case["task"],
        "pipeline_exit_code": pipeline_result.returncode,
        "report_path": str(report),
        "stdout_tail": pipeline_result.stdout[-1200:],
        "stderr_tail": pipeline_result.stderr[-1200:],
        "grade": {
            "success": pipeline_result.returncode == 0 and passed == total,
            "passed": passed,
            "total": total,
            "failures": [name for name, result in grade.items() if not result.get("passed")],
            "details": grade,
        },
    }


def print_report(trace: dict) -> None:
    grade = trace["grade"]
    status = "PASS" if grade["success"] else "FAIL"
    print(f"{trace['case_id']}: {status} ({grade['passed']}/{grade['total']}) - {trace['task']}")
    if grade["failures"]:
        print(f"  failures: {', '.join(grade['failures'])}")


def main() -> int:
    evals_data = load_evals()
    cases = evals_data["evals"]
    TRACES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Harness: {evals_data['skill_name']}")
    print(f"Cases: {len(cases)}")
    print("-" * 60)

    traces = []
    with tempfile.TemporaryDirectory(prefix="wechat-cover-evals-") as tmp:
        tmp_dir = Path(tmp)
        for case in cases:
            case_dir = tmp_dir / case["id"]
            case_dir.mkdir()
            report, pipeline_result = run_pipeline(case, case_dir)
            grade, _grader_result = run_grader(report, case["checks"])
            trace = build_trace(case, report, pipeline_result, grade)
            trace_path = TRACES_DIR / f"{case['id']}.json"
            trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
            traces.append(trace)
            print_report(trace)

    success = all(trace["grade"]["success"] for trace in traces)
    print("-" * 60)
    print("Overall: " + ("PASS" if success else "FAIL"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())

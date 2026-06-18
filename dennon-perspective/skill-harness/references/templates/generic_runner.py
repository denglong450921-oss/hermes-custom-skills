#!/usr/bin/env python3
"""Harness runner for non-HTML skills: task -> output -> trace -> grade."""

import json, sys, subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
GRADER = SKILL_DIR / "evals" / "grader.py"


def load_evals():
    with open(EVALS_FILE) as f:
        return json.load(f)


def run_grader(output_path, checks):
    checks_json = json.dumps(checks)
    result = subprocess.run(
        ["python3", str(GRADER), output_path, checks_json],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"error": result.stdout, "stderr": result.stderr}


def build_trace(case, output_path, grade_results):
    passed = sum(1 for r in grade_results.values() if r.get("passed"))
    total = len(grade_results)
    failures = [k for k, v in grade_results.items() if not v.get("passed")]
    return {
        "case_id": case["id"],
        "task": case.get("prompt", case.get("task", "")),
        "environment": {
            "files_available": list(case.get("files", [])),
            "tools_available": case.get("environment", {}).get("tools_available", []),
        },
        "tools_used": case.get("grader", {}).get("must_use", []),
        "answer": "Output saved to " + output_path,
        "grade": {
            "success": passed == total,
            "passed": passed,
            "total": total,
            "failures": failures,
            "details": grade_results,
        },
    }


def print_report(trace):
    g = trace["grade"]
    status = "PASS" if g["success"] else "FAIL"
    sep = "=" * 45
    print(f"\n{sep}")
    print(f"  Case:   {trace['case_id']}  [{status}]")
    print(f"  Task:   {trace['task'][:60]}...")
    print(f"  Result: {g['passed']}/{g['total']} passed")
    if g["failures"]:
        print(f"  Fail:   {', '.join(g['failures'])}")
    else:
        print(f"  All passed")
    print(f"{sep}")


def main():
    evals_data = load_evals()
    cases = evals_data["evals"]
    print(f"Harness: {evals_data['skill_name']}")
    print(f"Cases: {len(cases)}")
    print("-" * 50)

    check_map = {
        "script_ran_successfully": {"text": "Script ran", "check": "script_ran_successfully"},
        "manifest_created": {"text": "Manifest", "check": "manifest_created"},
        "file_generated": {"text": "Output file", "check": "file_generated"},
        "output_directory_listed": {"text": "Output dir", "check": "output_directory_listed"},
        "reports_failure_honestly": {"text": "Honest reporting", "check": "reports_failure_honestly"},
        "no_defensive_disclaimers": {"text": "No disclaimers", "check": "no_defensive_disclaimers"},
        "no_false_success": {"text": "No false success", "check": "no_false_success"},
    }

    for case in cases:
        print(f"\nRunning {case['id']}...")
        grader = case.get("grader", {})
        checks = []
        for tool in grader.get("must_use", []):
            if tool in check_map:
                checks.append(check_map[tool])
        if len(sys.argv) > 1:
            output_path = sys.argv[1]
            grade_results = run_grader(output_path, checks)
            trace = build_trace(case, output_path, grade_results)
            print_report(trace)
        else:
            print(f"  Need output path: python3 run_harness.py <output-file>")
            print(f"  Checks: {[c['check'] for c in checks]}")


if __name__ == "__main__":
    main()

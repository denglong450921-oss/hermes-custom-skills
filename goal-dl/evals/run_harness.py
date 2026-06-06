#!/usr/bin/env python3
"""Harness runner for goal-dl: test prompts -> grade 7-principle adherence."""

import json, sys, os, subprocess
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
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"error": result.stdout, "stderr": result.stderr}

def build_trace(case, output_path, grade_results):
    passed = sum(1 for r in grade_results.values() if r.get("passed"))
    total = len(grade_results)
    failures = [k for k, v in grade_results.items() if not v.get("passed")]

    trace = {
        "case_id": case["id"],
        "task": case["task"],
        "environment": {
            "tools_available": case["environment"].get("tools_available", []),
            "guidelines": case["environment"].get("guidelines", [])
        },
        "tools_used": case.get("tools", []),
        "answer": f"Output saved to {output_path}",
        "grade": {
            "success": passed == total,
            "passed": passed,
            "total": total,
            "failures": failures,
            "details": grade_results
        }
    }
    return trace

def print_report(trace):
    g = trace["grade"]
    status = "PASS" if g["success"] else "FAIL"
    print(f"""
=== Harness Report: {trace['case_id']} [{status}] ===
  Task: {trace['task'][:80]}...
  Principles checked: {', '.join(trace['tools_used'])}
  Results: {g['passed']}/{g['total']} assertions passed
  {('Failures: ' + ', '.join(g['failures']) if g['failures'] else 'All passed')}
{'=' * 50}""")

def main():
    evals_data = load_evals()
    cases = evals_data["evals"]

    print(f"Harness: {evals_data['skill_name']} (v{evals_data.get('harness_version','?')})")
    print(f"Cases: {len(cases)}")
    print("-" * 50)

    check_map = {
        "exit_criteria": {"text": "Exit criteria", "check": "exit_criteria"},
        "give_direction": {"text": "Give direction", "check": "give_direction"},
        "measurable_progress": {"text": "Measurable progress", "check": "measurable_progress"},
        "real_environment": {"text": "Real environment", "check": "real_environment"},
        "not_visual_only": {"text": "Not visual only", "check": "not_visual_only"},
        "track_progress": {"text": "Track progress", "check": "track_progress"},
        "cleanup": {"text": "Cleanup", "check": "cleanup"},
    }

    for case in cases:
        print(f"\n> Running {case['id']}...")

        checks = []
        for tool in case["grader"]["must_use"]:
            if tool in check_map:
                checks.append(check_map[tool])

        if len(sys.argv) > 1:
            output_path = sys.argv[1]
            grade_results = run_grader(output_path, checks)
            trace = build_trace(case, output_path, grade_results)
            print_report(trace)
        else:
            print(f"  Usage: python3 run_harness.py <output_file>")
            print(f"  Checks needed: {[c['check'] for c in checks]}")
            print(f"  Task summary: {case['task'][:80]}...")

if __name__ == "__main__":
    main()

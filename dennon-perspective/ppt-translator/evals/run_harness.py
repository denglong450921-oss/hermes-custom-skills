#!/usr/bin/env python3
"""Harness runner for ppt-translator skill: task -> output -> trace -> grade."""

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

    # Extract tools_used from grader.must_use
    grader = case.get("grader", {})
    tools_used = grader.get("must_use", [])

    # Extract environment files info
    env = case.get("environment", {})
    file_list = list(env.get("files", {}).keys()) if isinstance(env.get("files"), dict) else list(env.get("files", []))

    return {
        "case_id": case["id"],
        "task": case.get("prompt", case.get("task", "")),
        "environment": {
            "files_available": file_list,
            "tools_available": env.get("tools_available", []),
        },
        "tools_used": tools_used,
        "tools_arguments": {},
        "answer": f"Output saved to {output_path}",
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

    # Check map: maps check names from evals.json must_use to grader checks
    check_map = {
        "script_completed": {"text": "Script completed", "check": "script_completed"},
        "output_file_reported": {"text": "Output file", "check": "output_file_reported"},
        "progress_logs_visible": {"text": "Progress logs", "check": "progress_logs_visible"},
        "source_not_overwritten": {"text": "Source preserved", "check": "source_not_overwritten"},
        "protected_terms_preserved": {"text": "Protected terms", "check": "protected_terms_preserved"},
        "language_normalization_works": {"text": "Lang code", "check": "language_normalization_works"},
        "cache_loaded": {"text": "Cache loaded", "check": "cache_loaded"},
        "reports_failure_honestly": {"text": "Honest report", "check": "reports_failure_honestly"},
        "no_defensive_disclaimers": {"text": "No disclaimers", "check": "no_defensive_disclaimers"},
        "no_false_success": {"text": "No false success", "check": "no_false_success"},
        "rtl_layout_applied": {"text": "RTL layout", "check": "rtl_layout_applied"},
    }

    for case in cases:
        print(f"\n--- Running {case['id']} ---")
        grader = case.get("grader", {})
        checks = []
        for tool in grader.get("must_use", []):
            if tool in check_map:
                checks.append(check_map[tool])
            else:
                print(f"  Warning: unknown check '{tool}' in case {case['id']}")

        if len(sys.argv) > 1:
            output_path = sys.argv[1]
            grade_results = run_grader(output_path, checks)
            trace = build_trace(case, output_path, grade_results)
            print_report(trace)

            # Print trace as JSON
            print("\nTrace:")
            print(json.dumps(trace, indent=2, ensure_ascii=False))
        else:
            print(f"  Need output path: python3 run_harness.py <terminal-output-file>")
            print(f"  Checks: {[c['check'] for c in checks]}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Harness runner: task → produce HTML → trace → grade. Follows Agent Harness format."""

import json, sys, os, subprocess, re, textwrap
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
GRADER = SKILL_DIR / "evals" / "grader.py"
CSS_FILE = SKILL_DIR / "references" / "output.css"

def load_evals():
    with open(EVALS_FILE) as f:
        return json.load(f)

def run_grader(html_path, checks):
    """Run grader.py and return parsed results."""
    checks_json = json.dumps(checks)
    result = subprocess.run(
        ["python3", str(GRADER), html_path, checks_json],
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"error": result.stdout, "stderr": result.stderr}

def build_trace(case, html_path, grade_results):
    """Build trace record following article format."""
    passed = sum(1 for r in grade_results.values() if r.get("passed"))
    total = len(grade_results)
    failures = [k for k, v in grade_results.items() if not v.get("passed")]

    trace = {
        "case_id": case["id"],
        "task": case["task"],
        "environment": {
            "files_available": list(case["environment"]["files"].keys()),
            "tools_available": case["environment"]["tools_available"]
        },
        "tools_used": [t for t in case["tools"]],
        "tools_arguments": {
            "container": {"max_width": "800px", "margin": "auto"},
            "table": {"has_thead": True},
            "callout": {"border_left": "4px accent"},
            "steps": {"data_step_attr": True}
        },
        "answer": f"HTML output saved to {html_path}",
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
    """Print formatted report."""
    g = trace["grade"]
    status = "✅ PASS" if g["success"] else "❌ FAIL"
    print(f"""
╔══ Harness Report: {trace['case_id']} {status} ══╗
  Task: {trace['task'][:60]}...
  Tools: {', '.join(trace['tools_used'])}
  Results: {g['passed']}/{g['total']} assertions passed
  {'Failures: ' + ', '.join(g['failures']) if g['failures'] else 'All passed'}
╚{'═' * 45}╝""")

def main():
    evals_data = load_evals()
    cases = evals_data["evals"]

    print(f"Harness: {evals_data['skill_name']} (v{evals_data.get('harness_version','?')})")
    print(f"Cases: {len(cases)}")
    print("─" * 50)

    for case in cases:
        print(f"\n▶ Running {case['id']}...")

        # Build grader checks from must_use
        check_map = {
            "container": {"text": f"Uses .container", "check": "has_class_container"},
            "table": {"text": f"Has <table> with <thead>", "check": "has_table"},
            "callout": {"text": f"Has .callout", "check": "has_callout"},
            "steps": {"text": f"Has .steps", "check": "has_steps"},
            "details": {"text": f"Has details/summary", "check": "has_details"},
            "highlight": {"text": f"Has .highlight", "check": "has_highlight"},
            "tag": {"text": f"Has .tag", "check": "has_tag"},
            "meta": {"text": f"Has .meta", "check": "has_meta"},
            "insight": {"text": f"Has .insight", "check": "has_insight"},
        }

        checks = []
        for tool in case["grader"]["must_use"]:
            if tool in check_map:
                checks.append(check_map[tool])

        # If no HTML specified, print checks for manual review
        if len(sys.argv) > 1:
            html_path = sys.argv[1]
            grade_results = run_grader(html_path, checks)
            trace = build_trace(case, html_path, grade_results)
            print_report(trace)
        else:
            print(f"  Need HTML path: python3 run_harness.py ~/Desktop/my-output.html")
            print(f"  Checks needed: {[c['check'] for c in checks]}")

if __name__ == "__main__":
    main()

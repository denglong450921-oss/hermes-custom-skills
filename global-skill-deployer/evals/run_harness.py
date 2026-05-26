#!/usr/bin/env python3
"""Harness runner for global-skill-deployer: task → produce output → trace → grade."""

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
        "task": case.get("prompt", case.get("task", "")),
        "environment": {
            "files_available": list(case.get("files", [])),
            "tools_available": ["install_global_skill.py", "manage_global_skills.py"]
        },
        "tools_used": case.get("grader", {}).get("must_use", []),
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
    status = "✅ PASS" if g["success"] else "❌ FAIL"
    print(f"""
╔══ Harness: {trace['case_id']} {status} ══╗
  Task: {trace['task'][:60]}...
  Results: {g['passed']}/{g['total']} passed
  {'Failures: ' + ', '.join(g['failures']) if g['failures'] else 'All passed'}
╚{'═' * 45}╝""")

def main():
    evals_data = load_evals()
    cases = evals_data["evals"]
    
    print(f"Harness: {evals_data['skill_name']}")
    print(f"Cases: {len(cases)}")
    print("─" * 50)
    
    for case in cases:
        print(f"\n▶ Running {case['id']}...")
        
        # Build checks from grader definitions
        check_map = {
            "global_source_exists": {"text": "Global source exists", "check": "global_source_exists"},
            "symlinks_created": {"text": "Symlinks created", "check": "symlinks_created"},
            "cli_wrapper_created": {"text": "CLI wrapper created", "check": "cli_wrapper_created"},
            "inventory_reports_generated": {"text": "Inventory reports", "check": "inventory_reports_generated"},
            "backup_on_conflict": {"text": "Backup on conflict", "check": "backup_on_conflict"},
            "custom_only": {"text": "Custom-only mode", "check": "custom_only"},
            "needs_attention": {"text": "Needs attention", "check": "needs_attention"},
            "manifest_created": {"text": "Manifest created", "check": "manifest_created"},
            "refresh_baseline": {"text": "Baseline refreshed", "check": "refresh_baseline"},
            "verify_results": {"text": "Verification results", "check": "verify_results"},
            "skip_cli_wrapper": {"text": "Skip wrapper", "check": "skip_cli_wrapper"},
        }
        
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

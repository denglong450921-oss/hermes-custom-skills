#!/usr/bin/env python3
"""Check a skill for standard harness compliance. Reports missing/partial/present.

Usage:
    python3 scripts/check_harness.py ~/.hermes/skills/<target-skill>
    python3 scripts/check_harness.py ~/.hermes/skills/<target-skill> --json   # machine-readable

Exit codes:
    0 — full compliance (green)
    1 — partial compliance (yellow)
    2 — no harness (red)
"""

import json, sys, os, re
from pathlib import Path

# Standard harness checklist
HARNESS_CHECKS = [
    {
        "id": "evals_dir",
        "label": "evals/ directory",
        "check_type": "dir",
        "path": "evals",
        "required": True,
    },
    {
        "id": "evals_json",
        "label": "evals/evals.json (valid JSON with skill_name + ≥3 cases)",
        "check_type": "evals_json",
        "path": "evals/evals.json",
        "required": True,
    },
    {
        "id": "grader_py",
        "label": "evals/grader.py (has check function)",
        "check_type": "file_with_fn",
        "path": "evals/grader.py",
        "fn_name": "check_output",
        "alt_fn": "check_html",
        "required": True,
    },
    {
        "id": "run_harness_py",
        "label": "evals/run_harness.py (has main function)",
        "check_type": "file_with_fn",
        "path": "evals/run_harness.py",
        "fn_name": "main",
        "required": True,
    },
    {
        "id": "harness_section",
        "label": "SKILL.md has ## Harness (Self-Eval) section",
        "check_type": "harness_section",
        "path": "SKILL.md",
        "required": True,
    },
    {
        "id": "eval_must_use",
        "label": "Each eval case has grader.must_use",
        "check_type": "eval_must_use",
        "path": "evals/evals.json",
        "required": True,
    },
    {
        "id": "feedback_dir",
        "label": "feedback/ directory (evolution engine)",
        "check_type": "dir",
        "path": "feedback",
        "required": False,
    },
    {
        "id": "feedback_distill",
        "label": "feedback/distill.py",
        "check_type": "file",
        "path": "feedback/distill.py",
        "required": False,
    },
    {
        "id": "feedback_ftpr",
        "label": "feedback/ftpr.py",
        "check_type": "file",
        "path": "feedback/ftpr.py",
        "required": False,
    },
    {
        "id": "honesty_section",
        "label": "SKILL.md has Honesty & Truthfulness section",
        "check_type": "section",
        "path": "SKILL.md",
        "section_pattern": "防止模型说谎|Honesty.*Truthfulness",
        "required": False,
    },
]

def check_skill(skill_path, checks=None):
    """Run all checks against a skill directory. Returns list of check results."""
    skill = Path(skill_path).expanduser()
    
    if checks is None:
        checks = HARNESS_CHECKS
    
    results = []
    for check_def in checks:
        check_type = check_def["check_type"]
        check_path = skill / check_def["path"]
        
        result = {
            "id": check_def["id"],
            "label": check_def["label"],
            "required": check_def.get("required", True),
            "passed": False,
            "detail": "",
        }
        
        if check_type == "dir":
            result["passed"] = check_path.is_dir()
            result["detail"] = "Found" if result["passed"] else "Missing"
            
        elif check_type == "file":
            result["passed"] = check_path.is_file()
            result["detail"] = "Present" if result["passed"] else "Missing"
            
        elif check_type == "file_with_fn":
            result["passed"] = _check_file_has_function(check_path, check_def.get("fn_name"), check_def.get("alt_fn"))
            result["detail"] = "Found" if result["passed"] else f"Missing or no `{check_def.get('fn_name')}()`"
            
        elif check_type == "evals_json":
            result["passed"], result["detail"] = _check_evals_json(check_path)
            
        elif check_type == "harness_section":
            result["passed"], result["detail"] = _check_section(
                check_path, r"## Harness"
            )
            
        elif check_type == "section":
            result["passed"], result["detail"] = _check_section(
                check_path, check_def["section_pattern"]
            )
            
        elif check_type == "eval_must_use":
            result["passed"], result["detail"] = _check_eval_must_use(check_path)
        
        results.append(result)
    
    return results


def _check_file_has_function(filepath, fn_name, alt_fn=None):
    """Check that a Python file exists and contains a function definition."""
    if not filepath.is_file():
        return False
    content = filepath.read_text(encoding="utf-8", errors="replace")
    # Check for def fn_name(...)
    pattern = rf"^\s*def\s+{re.escape(fn_name)}\s*\("
    if re.search(pattern, content, re.MULTILINE):
        return True
    # Check alternative name
    if alt_fn:
        alt_pattern = rf"^\s*def\s+{re.escape(alt_fn)}\s*\("
        return bool(re.search(alt_pattern, content, re.MULTILINE))
    return False


def _check_evals_json(filepath):
    """Validate evals.json has skill_name, harness_version, and ≥3 evals with grader."""
    if not filepath.is_file():
        return False, "File missing"
    
    try:
        data = json.loads(filepath.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return False, "Invalid JSON"
    
    if "skill_name" not in data:
        return False, "Missing skill_name"
    
    evals = data.get("evals", [])
    if len(evals) < 3:
        return False, f"Only {len(evals)} cases (need ≥3)"
    
    # Check each case has required fields
    issues = []
    for i, case in enumerate(evals):
        if "id" not in case:
            issues.append(f"case[{i}] missing 'id'")
        task = case.get("task") or case.get("prompt")
        if not task:
            issues.append(f"case[{i}] missing task/prompt")
        if "grader" not in case:
            issues.append(f"case[{i}] missing grader")
        elif "must_use" not in case["grader"]:
            issues.append(f"case[{i}].grader missing must_use")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, f"{len(evals)} valid cases"


def _check_section(filepath, pattern):
    """Check SKILL.md contains a section matching pattern."""
    if not filepath.is_file():
        return False, "File missing"
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if re.search(pattern, content):
        return True, "Present"
    return False, "Missing"


def _check_eval_must_use(filepath):
    """Check that each eval case in evals.json has grader.must_use."""
    if not filepath.is_file():
        return False, "File missing"
    
    try:
        data = json.loads(filepath.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return False, "Invalid JSON"
    
    evals = data.get("evals", [])
    if not evals:
        return False, "No eval cases"
    
    missing = []
    for i, case in enumerate(evals):
        grader = case.get("grader", {})
        must_use = grader.get("must_use", [])
        if not must_use:
            missing.append(f"case[{i}] (id={case.get('id','?')})")
    
    if missing:
        return False, f"Missing must_use: {', '.join(missing)}"
    
    return True, f"All {len(evals)} cases have must_use"


def format_report(results, skill_name, machine=False):
    """Format check results as human-readable or JSON."""
    if machine:
        report = {
            "skill": skill_name,
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"] and r["required"]),
            "optional_failed": sum(1 for r in results if not r["passed"] and not r["required"]),
            "checks": results,
        }
        
        # Determine overall status
        required_failures = sum(1 for r in results if not r["passed"] and r["required"])
        if required_failures == 0:
            report["status"] = "full"
            report["exit_code"] = 0
        elif required_failures <= 2:
            report["status"] = "partial"
            report["exit_code"] = 1
        else:
            report["status"] = "none"
            report["exit_code"] = 2
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    # Human-readable
    lines = [
        f"╔══ Harness Check: {skill_name} ══╗",
    ]
    
    required_pass = 0
    required_total = 0
    for r in results:
        if r["required"]:
            required_total += 1
            if r["passed"]:
                required_pass += 1
        
        icon = "✅" if r["passed"] else ("⚠️" if not r["required"] else "❌")
        req = "[REQUIRED]" if r["required"] else "[OPTIONAL]"
        lines.append(f"  {icon} {req} {r['label']}")
        lines.append(f"     {r['detail']}")
    
    lines.append("")
    
    # Summary
    if required_pass == required_total:
        status = "✅ FULL COMPLIANCE — all required checks pass"
        exit_code = 0
    elif required_pass >= required_total - 2:
        status = "⚠️  PARTIAL COMPLIANCE — minor items missing"
        exit_code = 1
    else:
        status = "❌ NO HARNESS — major items missing"
        exit_code = 2
    
    lines.append(f"  Status: {status}")
    lines.append(f"  Required: {required_pass}/{required_total} passed")
    
    optional_pass = sum(1 for r in results if r["passed"] and not r["required"])
    optional_total = sum(1 for r in results if not r["required"])
    if optional_total > 0:
        lines.append(f"  Optional: {optional_pass}/{optional_total} passed")
    
    return "\n".join(lines), exit_code


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check a skill for standard harness compliance"
    )
    parser.add_argument("skill_path", help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    parser.add_argument("--strict", action="store_true", help="Fail on optional missing items too")
    
    args = parser.parse_args()
    
    skill_path = Path(args.skill_path).expanduser()
    if not skill_path.is_dir():
        print(f"❌ Not a directory: {skill_path}", file=sys.stderr)
        sys.exit(2)
    
    skill_name = skill_path.name
    
    results = check_skill(skill_path)
    
    if args.json:
        print(format_report(results, skill_name, machine=True))
        # Exit code is embedded in JSON
        report = json.loads(format_report(results, skill_name, machine=True))
        sys.exit(report["exit_code"])
    else:
        text, exit_code = format_report(results, skill_name)
        print(text)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()

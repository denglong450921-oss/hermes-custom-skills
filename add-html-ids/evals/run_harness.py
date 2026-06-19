#!/usr/bin/env python3
"""
add-html-ids harness runner — runs the ID scripts on test inputs, grades output.
Usage: python3 run_harness.py
"""
import json
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVALS_FILE = os.path.join(SKILL_DIR, "evals", "evals.json")
_SCRIPTS = os.path.join(SKILL_DIR, "scripts")
_GRADER = os.path.join(SKILL_DIR, "evals", "grader.py")


check_map = {
    "id_count_increased": {"text": "IDs added", "check": "id_count_increased", "min": 1},
    "new_ids_have_prefix": {"text": "New IDs prefixed", "check": "new_ids_have_prefix", "prefix": ""},
    "no_duplicate_ids": {"text": "No duplicate IDs", "check": "no_duplicate_ids"},
    "existing_ids_preserved": {"text": "Existing IDs preserved", "check": "existing_ids_preserved", "must_have": []},
    "id_only_delta": {"text": "Only id attributes changed", "check": "id_only_delta", "input_path": ""},
    "react_components_skipped": {"text": "React components skipped", "check": "react_components_skipped"},
    "no_str_markers_leaked": {"text": "No STR markers leaked", "check": "no_str_markers_leaked"},
    "script_style_uncorrupted": {"text": "Script/style uncorrupted", "check": "script_style_uncorrupted"},
    "apostrophe_preserved": {"text": "Apostrophe preserved", "check": "apostrophe_preserved", "must_have": ["world's"]},
    "original_text_preserved": {"text": "Original text preserved", "check": "original_text_preserved", "must_have": []},
}

# Per-case overrides for check parameters
case_overrides = {
    "case_001": {
        "id_count_increased": {"min": 8},
        "original_text_preserved": {"must_have": ["Welcome", "Click me", "Test Page", "site-header"]},
    },
    "case_002": {
        "existing_ids_preserved": {"must_have": ["case002_h1", "heroCopy", "scrollSection", "case002_div"]},
    },
    "case_003": {
        "id_count_increased": {"min": 3},
    },
    "case_004": {
        "id_count_increased": {"min": 14},
        "existing_ids_preserved": {"must_have": ["navRoot", "hero-title", "ctaPrimary", "footerAnchor"]},
        "original_text_preserved": {"must_have": [
            "#navRoot { position: sticky; top: 0; }",
            "#hero-title { color: #112233; }",
            "#ctaPrimary.is-active { transform: translateY(-1px); }",
            "href=\"#hero-title\"",
            "document.getElementById('ctaPrimary')",
            "document.querySelector('#navRoot')"
        ]},
    },
}


def run_case(case, output_dir):
    """Run the script for this case, return path to output file."""
    os.makedirs(output_dir, exist_ok=True)

    name = case["name"]
    prompt = case.get("prompt", "")
    files = case.get("files", [])
    grader_spec = case.get("grader", {})

    # Determine script and prefix based on case name
    script = os.path.join(_SCRIPTS, "add_html_ids.py")
    prefix = "case001_"
    ext = "html"

    if "tsx" in name.lower() or "002" in name:
        script = os.path.join(_SCRIPTS, "add_tsx_ids.py")
        prefix = "case002_"
        ext = "tsx"
    elif "script" in name.lower() or "003" in name:
        script = os.path.join(_SCRIPTS, "add_html_ids.py")
        prefix = "case003_"
        ext = "html"
    elif "004" in name or "case_004" in case.get("id", ""):
        script = os.path.join(_SCRIPTS, "add_html_ids.py")
        prefix = "case004_"
        ext = "html"

    input_file = files[0] if files else None
    if input_file and not os.path.isabs(input_file):
        input_file = os.path.join(SKILL_DIR, input_file)
    output_file = os.path.join(output_dir, f"output.{ext}")

    if not input_file or not os.path.exists(input_file):
        print(f"  SKIP: input file not found: {input_file}")
        return None

    # Copy input to output location first, then run script on output
    import shutil
    shutil.copy(input_file, output_file)

    # Run the script with --prefix override
    cmd = ["python3", script, output_file, "--prefix", prefix]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL_DIR)
    print(f"  script output: {result.stdout.strip()}")

    # Build checks
    checks = []
    overrides = case_overrides.get(case.get("id", ""), {})
    for gc in grader_spec.get("must_use", []):
        check_def = dict(check_map.get(gc, {"text": gc, "check": gc}))
        if not check_def.get("prefix"):
            check_def["prefix"] = prefix
        if "input_path" in check_def:
            check_def["input_path"] = input_file
        if check_def.get("check") in ("new_ids_have_prefix", "existing_ids_preserved", "react_components_skipped"):
            check_def["input_path"] = input_file
        # Apply per-case overrides
        if gc in overrides:
            check_def.update(overrides[gc])
        checks.append(check_def)

    # Grade
    if checks and os.path.exists(output_file):
        checks_json = json.dumps(checks)
        gr = subprocess.run(
            ["python3", _GRADER, output_file, checks_json],
            capture_output=True, text=True, cwd=SKILL_DIR
        )
        try:
            grade_results = json.loads(gr.stdout)
        except json.JSONDecodeError:
            grade_results = [{"text": "grade_error", "passed": False, "evidence": gr.stderr or gr.stdout}]
    else:
        grade_results = [{"text": "no_checks", "passed": False, "evidence": "No checks defined"}]

    passed_count = sum(1 for g in grade_results if g.get("passed"))
    total = len(grade_results)

    return {
        "output_file": output_file,
        "grade": {
            "passed": passed_count,
            "total": total,
            "success": passed_count == total if total > 0 else False,
            "details": grade_results
        }
    }


def main():
    with open(EVALS_FILE) as f:
        data = json.load(f)

    evals_list = data.get("evals", [])
    print(f"Running {len(evals_list)} eval cases...\n")

    all_passed = True
    for case in evals_list:
        cid = case.get("id", "?")
        name = case.get("name", cid)
        print(f"=== {cid} : {name} ===")

        output_dir = os.path.join(SKILL_DIR, "evals", name, "output")
        result = run_case(case, output_dir)

        if result:
            g = result["grade"]
            status = "PASS" if g["success"] else "FAIL"
            print(f"  Grade: {g['passed']}/{g['total']} {status}")
            for d in g.get("details", []):
                marker = "+" if d.get("passed") else "-"
                print(f"    {marker} {d.get('text')}: {d.get('evidence')}")
            if not g["success"]:
                all_passed = False
        else:
            print("  SKIPPED (no input)")
        print()

    if all_passed:
        print("ALL EVALS PASSED")
        return 0
    else:
        print("SOME EVALS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

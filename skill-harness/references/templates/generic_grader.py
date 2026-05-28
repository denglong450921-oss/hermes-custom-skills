#!/usr/bin/env python3
"""Grader for non-HTML skills. Customize checks for your skill's domain."""

import re, sys, json, os

def check_output(filepath, checks):
    if not os.path.exists(filepath):
        return {c.get("text", c["check"]): {"passed": False, "evidence": "File not found"} for c in checks}
    with open(filepath) as f:
        content = f.read()
    results = {}
    for check in checks:
        cid = check.get("text", check["check"])
        evidence = ""
        passed = False
        if check["check"] == "script_ran_successfully":
            passed = "error" not in content.lower()[:300]
            evidence = "No fatal error detected" if passed else "Script error found"
        elif check["check"] == "manifest_created":
            passed = "manifest" in content.lower()
            evidence = "Manifest referenced" if passed else "Missing manifest reference"
        elif check["check"] == "file_generated":
            passed = bool(re.search(r"\.(json|jsonl|csv|txt|html|md|mp3|srt)", content.lower()))
            evidence = "Output file referenced" if passed else "No output file reference"
        elif check["check"] == "output_directory_listed":
            passed = "output" in content.lower() or chr(30446) in content
            evidence = "Output directory mentioned" if passed else "Missing output directory"
        elif check["check"] == "reports_failure_honestly":
            passed = "error" in content.lower() or "failed" in content.lower()
            evidence = "Failure reported" if passed else "No failure detail"
        elif check["check"] == "no_defensive_disclaimers":
            defensive = ["this might not be correct", "i cannot guarantee", "i could be wrong"]
            passed = not any(d in content.lower() for d in defensive)
            evidence = "Clean" if passed else "Defensive language detected"
        elif check["check"] == "no_false_success":
            has_error = re.search(r"(FAIL|ERROR|Traceback)", content, re.I)
            claims_ok = re.search(r"(all passed|successfully)", content, re.I)
            passed = not (has_error and claims_ok)
            evidence = "Consistent" if passed else "Claims success but errors present"
        else:
            evidence = "Unknown check: " + check["check"]
        results[cid] = {"passed": passed, "evidence": evidence}
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [
        {"text": "Script ran", "check": "script_ran_successfully"},
        {"text": "Output file", "check": "file_generated"},
    ]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

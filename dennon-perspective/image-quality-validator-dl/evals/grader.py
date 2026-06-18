#!/usr/bin/env python3
"""Grader for image-quality-validator-dl. Checks JSON output from validate_image.py."""

import re, sys, json, os

def check_output(filepath, checks):
    if not os.path.exists(filepath):
        return {c.get("text", c["check"]): {"passed": False, "evidence": "File not found"} for c in checks}
    with open(filepath) as f:
        content = f.read()
    results = {}
    data = None
    if content.strip().startswith("{"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            pass
    for check in checks:
        cid = check.get("text", check["check"])
        passed = False
        evidence = ""
        if check["check"] == "script_exit_ok":
            passed = "Traceback" not in content and "Error" not in content[:300]
            evidence = "No script errors" if passed else "Script error detected"
        elif check["check"] == "output_is_json":
            passed = content.strip().startswith("{")
            evidence = "Valid JSON" if passed else "Not valid JSON"
        elif check["check"] == "has_status":
            if data:
                passed = data.get("status") in ("pass", "fail")
                evidence = f"status: {data.get('status')}" if passed else "Missing/invalid status"
            else:
                passed = '"status"' in content
                evidence = "status field found" if passed else "Missing status"
        elif check["check"] == "has_relevance_score":
            if data:
                r = data.get("relevance")
                passed = isinstance(r, (int, float)) and 0 <= r <= 1
                evidence = f"relevance: {r}" if passed else f"Invalid relevance: {r}"
            else:
                passed = '"relevance"' in content
                evidence = "relevance found" if passed else "Missing relevance"
        elif check["check"] == "has_clarity_score":
            if data:
                c = data.get("clarity")
                passed = isinstance(c, (int, float)) and 0 <= c <= 1
                evidence = f"clarity: {c}" if passed else f"Invalid clarity: {c}"
            else:
                passed = '"clarity"' in content
                evidence = "clarity found" if passed else "Missing clarity"
        elif check["check"] == "has_resolution":
            if data:
                rp = data.get("resolution_px")
                passed = isinstance(rp, (list, tuple)) and len(rp) == 2
                evidence = f"resolution_px: {rp}" if passed else "Missing/invalid resolution"
            else:
                passed = '"resolution_px"' in content
                evidence = "resolution_px found" if passed else "Missing resolution"
        elif check["check"] == "has_crop_check":
            if data:
                passed = "crop_check" in data
                evidence = "crop_check present" if passed else "Missing crop_check"
            else:
                passed = '"crop_check"' in content
                evidence = "crop_check found" if passed else "Missing"
        else:
            evidence = f"Unknown check: {check['check']}"
        results[cid] = {"passed": passed, "evidence": evidence}
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [{"text": "Script ran", "check": "script_exit_ok"}, {"text": "JSON output", "check": "output_is_json"}]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

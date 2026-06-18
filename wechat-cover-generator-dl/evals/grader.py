#!/usr/bin/env python3
"""Grader for wechat-cover-generator-dl. Checks orchestration output report."""

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
        if check["check"] == "pipeline_complete":
            passed = "cover_image_url" in content or "validation" in content or "final.png" in content
            evidence = "Pipeline completion signals found" if passed else "Missing pipeline signals"
        elif check["check"] == "cover_generated":
            if data:
                passed = bool(data.get("cover_image_url"))
                evidence = f"cover: {data.get('cover_image_url')[:60]}..." if passed else "Missing cover_image_url"
            else:
                passed = ".png" in content.lower() or "cover" in content.lower()
                evidence = "PNG/cover reference found" if passed else "No cover reference"
        elif check["check"] == "title_created":
            passed = "title" in content.lower() or ".md" in content
            evidence = "Title/MD reference found" if passed else "No title reference"
        elif check["check"] == "image_fetched":
            passed = "image" in content.lower() or "unsplash" in content.lower()
            evidence = "Image source referenced" if passed else "No image reference"
        elif check["check"] == "image_validated":
            passed = "validation" in content.lower() or "valid" in content.lower()
            evidence = "Validation referenced" if passed else "No validation reference"
        elif check["check"] == "honest_reporting":
            passed = "pass" in content.lower() or "fail" in content.lower() or "fallback" in content.lower()
            evidence = "Status reported" if passed else "No status found"
        else:
            evidence = f"Unknown check: {check['check']}"
        results[cid] = {"passed": passed, "evidence": evidence}
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [{"text": "Pipeline", "check": "pipeline_complete"}]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

#!/usr/bin/env python3
"""Grader for open-source-image-fetch-dl. Checks JSON output from fetch_image.py."""

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
            passed = "Traceback" not in content and "Error" not in content[:200]
            evidence = "No script errors" if passed else "Script error detected"
        elif check["check"] == "output_is_json":
            passed = content.strip().startswith("{")
            evidence = "Valid JSON" if passed else "Not valid JSON"
        elif check["check"] == "has_image_url":
            if data:
                passed = bool(data.get("image_url"))
                evidence = f"image_url: {data.get('image_url','')[:60]}..." if passed else "Missing image_url"
            else:
                passed = "image_url" in content
                evidence = "image_url found" if passed else "Missing image_url"
        elif check["check"] == "has_author":
            if data:
                passed = bool(data.get("author"))
                evidence = f"author: {data.get('author')}" if passed else "Missing author"
            else:
                passed = "author" in content
                evidence = "author found" if passed else "Missing author"
        elif check["check"] == "has_license":
            if data:
                passed = bool(data.get("license"))
                evidence = f"license: {data.get('license')[:50]}..." if passed else "Missing license"
            else:
                passed = "license" in content
                evidence = "license found" if passed else "Missing license"
        elif check["check"] == "has_width_ge_1200":
            if data:
                w = data.get("width", 0)
                passed = w >= 1200
                evidence = f"width={w}" if passed else f"width={w} < 1200"
            else:
                m = re.search(r'"width":\s*(\d+)', content)
                w = int(m.group(1)) if m else 0
                passed = w >= 1200
                evidence = f"width={w}" if passed else f"width={w} < 1200"
        elif check["check"] == "has_width_ge_1800":
            if data:
                w = data.get("width", 0)
                passed = w >= 1800
                evidence = f"width={w}" if passed else f"width={w} < 1800"
            else:
                m = re.search(r'"width":\s*(\d+)', content)
                w = int(m.group(1)) if m else 0
                passed = w >= 1800
                evidence = f"width={w}" if passed else f"width={w} < 1800"
        elif check["check"] == "has_relevance_score":
            if data:
                passed = isinstance(data.get("relevance_score"), (int, float))
                evidence = f"relevance_score: {data.get('relevance_score')}" if passed else "Missing relevance_score"
            else:
                passed = "relevance_score" in content
                evidence = "relevance_score found" if passed else "Missing"
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

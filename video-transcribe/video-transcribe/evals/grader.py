#!/usr/bin/env python3
"""Grader for video-transcribe: checks transcribed output for format, keywords, duration."""

import re, sys, json, os

def check_output(filepath, checks):
    if not os.path.exists(filepath):
        return {c.get("text", c["check"]): {"passed": False, "evidence": "Output file not found"} for c in checks}
    with open(filepath) as f:
        content = f.read()
    results = {}
    for check in checks:
        cid = check.get("text", check["check"])
        evidence = ""
        passed = False

        if check["check"] == "has_timestamp_format":
            # Lines should match [Xs -> Ys] text
            matches = re.findall(r'\[\d+\.?\d*s\s*->\s*\d+\.?\d*s\]', content)
            passed = len(matches) >= 2
            evidence = f"Found {len(matches)} timestamped segments"

        elif check["check"] == "has_chinese_keywords":
            expected = ["家长", "运动", "骨头"]
            found = [w for w in expected if w in content]
            passed = len(found) >= 2
            evidence = f"Keywords found: {found}" if found else "No Chinese keywords found"

        elif check["check"] == "has_english_words":
            expected = ["hello", "exercise", "transcription", "everyone", "taller"]
            found = [w for w in expected if w.lower() in content.lower()]
            passed = len(found) >= 2
            evidence = f"Keywords found: {found}" if found else "No English keywords found"

        elif check["check"] == "covers_duration":
            timestamps = re.findall(r'\[(\d+\.?\d*)s\s*->\s*\d+\.?\d*s\]', content)
            if timestamps:
                max_start = max(float(t) for t in timestamps)
                passed = max_start >= 50.0
                evidence = f"Last segment starts at {max_start}s"
            else:
                evidence = "No timestamps to check duration"

        elif check["check"] == "language_detected_en":
            passed = "language: en" in content.lower() or "p=1.00" in content
            evidence = "English language marker found" if passed else "No English language marker"
            # Also check first few words sound English
            has_english = bool(re.search(r'[Hh]ello|[Hh]ow|[Tt]oday|[Tt]his is', content))
            if has_english and not passed:
                evidence = "English text detected but no language marker"
                passed = True

        elif check["check"] == "language_detected_zh":
            passed = "language: zh" in content.lower() or "p=1.00" in content
            evidence = "Chinese language marker found" if passed else "No Chinese language marker"
            has_chinese = bool(re.search(r'[\u4e00-\u9fff]', content))
            if has_chinese and not passed:
                evidence = "Chinese text detected but no language marker"
                passed = True

        elif check["check"] == "no_crash":
            crash_patterns = ["Traceback", "Error:", "No module", "FileNotFoundError"]
            passed = not any(p in content for p in crash_patterns)
            evidence = "No crash detected" if passed else "Crash pattern found"

        elif check["check"] == "handles_missing_file":
            passed = "not found" in content.lower() or "no such" in content.lower() or "error" in content.lower()
            evidence = "Graceful error" if passed else "No error handling detected"

        else:
            evidence = f"Unknown check: {check['check']}"

        results[cid] = {"passed": passed, "evidence": evidence}
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [
        {"text": "Timestamp format", "check": "has_timestamp_format"},
        {"text": "No crash", "check": "no_crash"},
    ]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

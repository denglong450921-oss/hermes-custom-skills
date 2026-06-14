#!/usr/bin/env python3
"""Grader for wechat_article_cover_image_gen harness.

Checks that gen_cover.py produces a valid 900x383 PNG with the
expected text coverage and no errors.
"""

from __future__ import annotations

import json
import os
import re
import sys


def check_output(output_path: str, checks_json: str) -> list[dict]:
    """Evaluate assertion checks against the output.

    ``output_path`` points to grader-output.txt (stdout + stderr + metadata
    from the run).  ``checks_json`` is the JSON ``must_use`` array.

    Returns a dict matching the harness grading contract:
      {"text": ..., "passed": bool, "evidence": str}
    """
    with open(output_path, encoding="utf-8") as f:
        content = f.read()

    checks = json.loads(checks_json)
    results = []

    for check in checks:
        check_name = check["check"] if isinstance(check, dict) else check
        result = _run_check(check_name, content)
        results.append(result)

    return results


def _run_check(check_name: str, content: str) -> dict:
    """Dispatch a single check by name."""
    dispatch = {
        "script_exits_ok": _check_exit_ok,
        "output_file_exists": _check_file_exists,
        "valid_png": _check_valid_png,
        "correct_dimensions": _check_dimensions,
        "title_coverage_90plus": _check_title_coverage,
    }
    fn = dispatch.get(check_name)
    if fn is None:
        return {"text": check_name, "passed": False, "evidence": f"Unknown check: {check_name}"}
    return fn(content)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_exit_ok(content: str) -> dict:
    passed = "ERROR" not in content and "Traceback" not in content
    evidence = "No error/traceback in output" if passed else "Error or traceback detected"
    return {"text": "Script exits OK", "passed": passed, "evidence": evidence}


def _check_file_exists(content: str) -> dict:
    # Look for "Cover generated: /path/to/file.png"
    m = re.search(r"Cover generated:\s+(\S+)", content)
    if not m:
        return {"text": "Output file exists", "passed": False, "evidence": "No output path in stdout"}
    path = m.group(1)
    exists = os.path.isfile(path)
    return {"text": "Output file exists", "passed": exists, "evidence": f"Output path: {path}, exists={exists}"}


def _check_valid_png(content: str) -> dict:
    """Verify the output PNG is a valid image using Pillow."""
    m = re.search(r"Cover generated:\s+(\S+)", content)
    if not m:
        return {"text": "Valid PNG", "passed": False, "evidence": "No output path found"}
    path = m.group(1)
    if not os.path.isfile(path):
        return {"text": "Valid PNG", "passed": False, "evidence": f"File not found: {path}"}
    try:
        from PIL import Image
        img = Image.open(path)
        img.verify()  # checks file integrity
        # Re-open after verify (verify closes the file)
        img = Image.open(path)
        return {"text": "Valid PNG", "passed": True, "evidence": f"Valid {img.mode} image, {img.size}"}
    except Exception as e:
        return {"text": "Valid PNG", "passed": False, "evidence": f"Invalid PNG: {e}"}


def _check_dimensions(content: str) -> dict:
    m = re.search(r"Cover generated:\s+(\S+)", content)
    if not m:
        return {"text": "Correct dimensions", "passed": False, "evidence": "No output path"}
    path = m.group(1)
    try:
        from PIL import Image
        img = Image.open(path)
        w, h = img.size
        passed = (w, h) == (900, 383)
        return {"text": "Correct dimensions", "passed": passed, "evidence": f"Image size: {w}x{h}"}
    except Exception as e:
        return {"text": "Correct dimensions", "passed": False, "evidence": f"Failed to open: {e}"}


def _check_title_coverage(content: str) -> dict:
    """Check the script's self-reported title coverage is >= 90%."""
    m = re.search(r"Title width coverage:\s+(\d+)%", content)
    if m:
        pct = int(m.group(1))
        passed = pct >= 90
        return {"text": "Title coverage >= 90%", "passed": passed, "evidence": f"Title width coverage: {pct}%"}
    return {"text": "Title coverage >= 90%", "passed": False, "evidence": "No coverage info in output"}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: grader.py <output-file> '<checks-json>'", file=sys.stderr)
        sys.exit(1)
    results = check_output(sys.argv[1], sys.argv[2])
    print(json.dumps(results, indent=2, ensure_ascii=False))

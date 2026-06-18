#!/usr/bin/env python3
"""Harness runner for wechat_article_cover_image_gen.

Runs each eval case from evals.json through gen_cover.py, captures the
output, passes it to grader.py, and prints results.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


EVALS_FILE = os.path.join(os.path.dirname(__file__), "evals.json")
SKILL_DIR = os.path.dirname(os.path.dirname(__file__))
SCRIPT = os.path.join(SKILL_DIR, "scripts", "gen_cover.py")


def main() -> int:
    with open(EVALS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    evals = data.get("evals", [])
    if not evals:
        print("ERROR: No eval cases found in evals.json", file=sys.stderr)
        return 1

    all_passed = True
    total_checks = 0
    passed_checks = 0

    for case in evals:
        case_id = case["id"]
        args = case.get("args", {})
        grader_checks = case.get("graber", case.get("grader", {})).get("must_use", [])
        print(f"\n{'='*60}")
        print(f"Case: {case_id}")
        print(f"Task: {case['task'][:80]}...")
        print(f"{'='*60}")

        # Create temp output
        tmp_output = os.path.join(tempfile.mkdtemp(), f"{case_id}.png")

        # Build command
        cmd = [sys.executable, SCRIPT, "--output", tmp_output]
        if args.get("title"):
            cmd += ["--title", args["title"]]
        if args.get("subtitle"):
            cmd += ["--subtitle", args["subtitle"]]
        if args.get("tagline"):
            cmd += ["--tagline", args["tagline"]]
        if args.get("label"):
            cmd += ["--label", args["label"]]

        # Run
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
        except subprocess.TimeoutExpired:
            print("  TIMEOUT (>60s)")
            all_passed = False
            continue

        # Collect output
        out_path = os.path.join(tempfile.mkdtemp(), "grader-output.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"EXIT_CODE: {result.returncode}\n")
            f.write(f"STDOUT:\n{result.stdout}\n")
            if result.stderr:
                f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"OUTPUT_PATH: {tmp_output}\n")

        print(result.stdout)
        if result.stderr:
            print(f"  STDERR: {result.stderr[:200]}")

        # Grade
        if grader_checks:
            grader_py = os.path.join(os.path.dirname(__file__), "grader.py")
            checks_json = json.dumps([{"check": c} for c in grader_checks], ensure_ascii=False)
            try:
                grade_result = subprocess.run(
                    [sys.executable, grader_py, out_path, checks_json],
                    capture_output=True, text=True, timeout=30,
                )
                grades = json.loads(grade_result.stdout)
            except Exception as e:
                print(f"  GRADER ERROR: {e}")
                grades = []

            case_pass = True
            for g in grades:
                total_checks += 1
                status = "PASS" if g["passed"] else "FAIL"
                if g["passed"]:
                    passed_checks += 1
                else:
                    case_pass = False
                print(f"  [{status}] {g['text']:30s}  {g['evidence']}")

            if not case_pass:
                all_passed = False
        else:
            print("  (no grader checks configured)")

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {passed_checks}/{total_checks} checks passed")
    if all_passed:
        print("Result: ALL PASSED")
        return 0
    else:
        print("Result: SOME FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

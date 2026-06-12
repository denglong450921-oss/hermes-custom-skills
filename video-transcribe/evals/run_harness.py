#!/usr/bin/env python3
"""Harness runner for video-transcribe: run transcribe → grade output → trace."""

import json, sys, subprocess, os, shutil, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
GRADER = SKILL_DIR / "evals" / "grader.py"
TRANSCRIBE_SCRIPT = SKILL_DIR / "scripts" / "transcribe.py"


def load_evals():
    with open(EVALS_FILE) as f:
        return json.load(f)


def run_grader(output_path, checks):
    checks_json = json.dumps(checks)
    result = subprocess.run(
        ["python3", str(GRADER), output_path, checks_json],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"error": result.stdout, "stderr": result.stderr}


def run_transcribe(video_path, extra_args=None):
    """Run transcribe.py and capture output."""
    cmd = ["python3", str(TRANSCRIBE_SCRIPT), str(video_path)]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout, result.stderr, result.returncode


def build_trace(case, output_text, grade_results, stderr="", exit_code=0):
    passed = sum(1 for r in grade_results.values() if r.get("passed"))
    total = len(grade_results)
    failures = [k for k, v in grade_results.items() if not v.get("passed")]
    return {
        "case_id": case["id"],
        "task": case.get("task", ""),
        "environment": {
            "files_available": list(case.get("files", [])),
            "tools_available": case.get("environment", {}).get("tools_available", []),
        },
        "tools_used": case.get("grader", {}).get("must_use", []),
        "exit_code": exit_code,
        "answer": output_text[:300] + "..." if len(output_text) > 300 else output_text,
        "grade": {
            "success": passed == total,
            "passed": passed,
            "total": total,
            "failures": failures,
            "details": grade_results,
        },
    }


def print_report(trace):
    g = trace["grade"]
    status = "PASS" if g["success"] else "FAIL"
    sep = "=" * 50
    print(f"\n{sep}")
    print(f"  Case:   {trace['case_id']}")
    print(f"  Status: [{status}] {g['passed']}/{g['total']} passed")
    print(f"  Exit:   {trace['exit_code']}")
    print(f"  Task:   {trace['task'][:80]}")
    if g["failures"]:
        print(f"  Failures:")
        for fname in g["failures"]:
            detail = g["details"].get(fname, {})
            print(f"    ✗ {fname}: {detail.get('evidence', '')}")
    else:
        for k, v in g["details"].items():
            s = "✓" if v.get("passed") else "✗"
            print(f"    {s} {k}: {v.get('evidence', '')}")
    print(f"{sep}")


def main():
    evals_data = load_evals()
    cases = evals_data["evals"]
    print(f"video-transcribe Harness")
    print(f"Cases: {len(cases)}")
    print("=" * 50)

    check_map = {
        "has_timestamp_format": {"text": "Timestamp format", "check": "has_timestamp_format"},
        "has_chinese_keywords": {"text": "Chinese keywords", "check": "has_chinese_keywords"},
        "has_english_words": {"text": "English keywords", "check": "has_english_words"},
        "covers_duration": {"text": "Duration coverage", "check": "covers_duration"},
        "language_detected_en": {"text": "English language", "check": "language_detected_en"},
        "language_detected_zh": {"text": "Chinese language", "check": "language_detected_zh"},
        "no_crash": {"text": "No crash", "check": "no_crash"},
        "handles_missing_file": {"text": "Missing file", "check": "handles_missing_file"},
    }

    all_passed = True

    for case in cases:
        print(f"\n--- Running {case['id']} ---")

        grader = case.get("grader", {})
        checks = []
        for tool in grader.get("must_use", []):
            if tool in check_map:
                checks.append(check_map[tool])

        # Extract video path from task description or use files
        task = case.get("task", "")
        file_ref = case.get("environment", {}).get("files", {}).get("input", "")

        if file_ref:
            # Resolve path relative to SKILL_DIR
            video_path = SKILL_DIR / file_ref
        else:
            video_path = ""

        # Determine extra args from task hints
        extra_args = []
        if "--model" in task:
            m = __import__('re').search(r'--model\s+(\S+)', task)
            if m:
                extra_args.extend(["--model", m.group(1)])
        if "--language" in task:
            m = __import__('re').search(r'--language\s+(\S+)', task)
            if m:
                extra_args.extend(["--language", m.group(1)])
        if "zh" in task.lower() or "中文" in task or "chinese" in task.lower():
            if not any(a == "--language" for a in extra_args):
                pass  # Let auto-detect handle it

        # Run transcription
        if video_path and os.path.exists(str(video_path)):
            stdout, stderr, exit_code = run_transcribe(str(video_path), extra_args)
        else:
            # Test handling of missing file
            stdout, stderr, exit_code = run_transcribe("/tmp/nonexistent_video_xyz.mp4")

        # Save output to temp and grade
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, prefix=f"harness_{case['id']}_") as tmp:
            tmp.write(stdout)
            tmp_path = tmp.name

        grade_results = run_grader(tmp_path, checks)
        trace = build_trace(case, stdout, grade_results, stderr, exit_code)
        print_report(trace)
        os.unlink(tmp_path)

        if not trace["grade"]["success"]:
            all_passed = False

    print(f"\n{'=' * 50}")
    print(f"Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

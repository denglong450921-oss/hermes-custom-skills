#!/usr/bin/env python3
"""Grade wechat-article-cover-image-gen harness outputs."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ModuleNotFoundError:
    bundled_python = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    )
    if bundled_python.exists() and Path(sys.executable).resolve() != bundled_python.resolve():
        os.execv(str(bundled_python), [str(bundled_python), __file__, *sys.argv[1:]])
    pip = shutil.which("pip3") or "python3 -m pip"
    raise SystemExit(
        "ERROR: Pillow is required to grade PNG covers. "
        f"Install it with `{pip} install pillow`, or run this inside the Codex bundled Python runtime."
    )


EXPECTED_SIZE = (900, 383)


def _extract_path(content: str, key: str, pattern: str) -> Path | None:
    match = re.search(pattern, content)
    if match:
        return Path(match.group(1))
    match = re.search(rf"{key}:\s+(\S+)", content)
    return Path(match.group(1)) if match else None


def _load_context(output_path: str) -> dict:
    content = Path(output_path).read_text(encoding="utf-8")
    png = _extract_path(content, "OUTPUT_PATH", r"Cover generated:\s+(\S+)")
    report_path = _extract_path(content, "REPORT_PATH", r"Report:\s+(\S+)")
    report = {}
    if report_path and report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    return {"content": content, "png": png, "report_path": report_path, "report": report}


def check_output(output_path: str, checks_json: str) -> list[dict]:
    ctx = _load_context(output_path)
    checks = json.loads(checks_json)
    results = []
    for check in checks:
        check_name = check["check"] if isinstance(check, dict) else check
        results.append(_run_check(check_name, ctx))
    return results


def _run_check(check_name: str, ctx: dict) -> dict:
    dispatch = {
        "script_exits_ok": _check_exit_ok,
        "output_file_exists": _check_file_exists,
        "valid_png": _check_valid_png,
        "correct_dimensions": _check_dimensions,
        "title_coverage_in_range": _check_title_coverage,
        "high_render_scale": _check_render_scale,
        "text_sharpness_ok": _check_text_sharpness,
        "png_output_format": _check_png_format,
    }
    fn = dispatch.get(check_name)
    if fn is None:
        return {"text": check_name, "passed": False, "evidence": f"Unknown check: {check_name}"}
    return fn(ctx)


def _check_exit_ok(ctx: dict) -> dict:
    content = ctx["content"]
    exit_match = re.search(r"EXIT_CODE:\s+(\d+)", content)
    exit_code = int(exit_match.group(1)) if exit_match else 0
    passed = exit_code == 0 and "ERROR" not in content and "Traceback" not in content
    evidence = f"exit_code={exit_code}"
    return {"text": "Script exits OK", "passed": passed, "evidence": evidence}


def _check_file_exists(ctx: dict) -> dict:
    path = ctx["png"]
    passed = bool(path and path.is_file())
    return {"text": "Output file exists", "passed": passed, "evidence": f"path={path}, exists={passed}"}


def _check_valid_png(ctx: dict) -> dict:
    path = ctx["png"]
    if not path or not path.is_file():
        return {"text": "Valid PNG", "passed": False, "evidence": f"File not found: {path}"}
    try:
        with Image.open(path) as img:
            fmt = img.format
            mode = img.mode
            size = img.size
            img.verify()
        return {"text": "Valid PNG", "passed": fmt == "PNG", "evidence": f"format={fmt}, mode={mode}, size={size}"}
    except Exception as exc:
        return {"text": "Valid PNG", "passed": False, "evidence": f"invalid image: {exc}"}


def _check_dimensions(ctx: dict) -> dict:
    path = ctx["png"]
    try:
        with Image.open(path) as img:
            size = img.size
    except Exception as exc:
        return {"text": "Correct dimensions", "passed": False, "evidence": str(exc)}
    report_size = tuple(ctx["report"].get("canvas", []))
    passed = size == EXPECTED_SIZE and report_size == EXPECTED_SIZE
    return {"text": "Correct dimensions", "passed": passed, "evidence": f"image={size}, report={report_size}"}


def _check_title_coverage(ctx: dict) -> dict:
    pct = ctx["report"].get("title_coverage_pct")
    if pct is None:
        match = re.search(r"Title width coverage:\s+(\d+)%", ctx["content"])
        pct = int(match.group(1)) if match else None
    passed = isinstance(pct, int) and 32 <= pct <= 92
    return {"text": "Title coverage in range", "passed": passed, "evidence": f"title_coverage_pct={pct}"}


def _check_render_scale(ctx: dict) -> dict:
    scale = ctx["report"].get("render_scale")
    passed = isinstance(scale, int) and scale >= 3
    return {"text": "High render scale", "passed": passed, "evidence": f"render_scale={scale}"}


def _check_text_sharpness(ctx: dict) -> dict:
    score = ctx["report"].get("text_sharpness_score")
    passed = isinstance(score, (int, float)) and score >= 7.0
    return {"text": "Text sharpness OK", "passed": passed, "evidence": f"text_sharpness_score={score}"}


def _check_png_format(ctx: dict) -> dict:
    report_format = ctx["report"].get("format")
    path = ctx["png"]
    suffix = path.suffix.lower() if path else ""
    passed = report_format == "PNG" and suffix == ".png"
    return {"text": "PNG output format", "passed": passed, "evidence": f"report_format={report_format}, suffix={suffix}"}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: grader.py <output-file> '<checks-json>'", file=sys.stderr)
        sys.exit(1)
    results = check_output(sys.argv[1], sys.argv[2])
    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(0 if all(item["passed"] for item in results) else 1)

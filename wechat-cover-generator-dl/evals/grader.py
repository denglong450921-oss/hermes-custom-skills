#!/usr/bin/env python3
"""Grade wechat-cover-generator-dl JSON reports and generated PNGs."""

from __future__ import annotations

import json
import os
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
        "ERROR: Pillow is required to inspect PNG covers. "
        f"Install it with `{pip} install pillow`, or run this with a Python runtime that includes Pillow."
    )


EXPECTED_SIZE = (900, 383)


def _load_report(filepath: str) -> tuple[dict | None, str | None]:
    path = Path(filepath)
    if not path.exists():
        return None, f"Report not found: {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"Report is not valid JSON: {exc}"


def _cover_path(data: dict) -> Path | None:
    raw = data.get("cover_image_path") or data.get("cover_image_url")
    if not raw:
        return None
    return Path(raw)


def _image_size(path: Path | None) -> tuple[int, int] | None:
    if path is None or not path.exists():
        return None
    with Image.open(path) as img:
        return img.size


def check_output(filepath: str, checks: list[dict]) -> dict:
    data, error = _load_report(filepath)
    if error:
        return {
            c.get("text", c["check"]): {"passed": False, "evidence": error}
            for c in checks
        }

    assert data is not None
    cover = _cover_path(data)
    title_md = Path(data["title_md_path"]) if data.get("title_md_path") else None
    results = {}

    for check in checks:
        name = check.get("text", check["check"])
        kind = check["check"]
        passed = False
        evidence = ""

        if kind == "pipeline_complete":
            required = ["status", "cover_image_url", "title_md_path", "validation", "dimensions"]
            missing = [field for field in required if field not in data]
            passed = not missing
            evidence = "Required report fields present" if passed else f"Missing fields: {missing}"
        elif kind == "cover_generated":
            passed = bool(cover and cover.exists())
            evidence = str(cover) if passed else f"Missing cover file: {cover}"
        elif kind == "correct_dimensions":
            size = _image_size(cover)
            passed = size == EXPECTED_SIZE and data.get("dimensions") == list(EXPECTED_SIZE)
            evidence = f"PNG size={size}, report dimensions={data.get('dimensions')}"
        elif kind == "title_created":
            if title_md and title_md.exists():
                first_line = title_md.read_text(encoding="utf-8").splitlines()[0].strip()
                passed = first_line.startswith("# ") and len(first_line) > 2
                evidence = first_line
            else:
                evidence = f"Missing title metadata file: {title_md}"
        elif kind == "report_validation_pass":
            passed = data.get("validation") == "pass" and data.get("status") == "passed"
            evidence = f"status={data.get('status')} validation={data.get('validation')}"
        elif kind == "image_source_reported":
            passed = bool(data.get("image_source"))
            evidence = str(data.get("image_source"))
        elif kind == "has_attempt_count":
            attempts = data.get("image_validation_attempts")
            passed = isinstance(attempts, int) and attempts >= 1
            evidence = f"attempts={attempts}"
        elif kind == "honest_reporting":
            blockers = data.get("validation_details", {}).get("blockers", [])
            if data.get("status") == "failed":
                passed = bool(blockers)
                evidence = f"failed with blockers={blockers}"
            else:
                passed = data.get("validation") == "pass" and blockers == []
                evidence = f"passed with blockers={blockers}"
        else:
            evidence = f"Unknown check: {kind}"

        results[name] = {"passed": passed, "evidence": evidence}

    return results


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: grader.py <report-json> [checks_json]", file=sys.stderr)
        return 2
    checks = (
        json.loads(sys.argv[2])
        if len(sys.argv) > 2
        else [{"text": "Pipeline", "check": "pipeline_complete"}]
    )
    results = check_output(sys.argv[1], checks)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(item["passed"] for item in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

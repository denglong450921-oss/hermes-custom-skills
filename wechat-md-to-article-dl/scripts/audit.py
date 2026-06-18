#!/usr/bin/env python3
"""Audit WeChat article HTML against the five-dimensional quality gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from quality import audit_html
from official_verify import verify_article_structure


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit WeChat article HTML.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--threshold", type=int, default=90)
    parser.add_argument(
        "--official-check",
        action="store_true",
        help="Explicitly transmit HTML to WeChat's official structure verifier.",
    )
    parser.add_argument("--official-timeout", type=float, default=15.0)
    args = parser.parse_args()
    if not args.input.is_file():
        print(json.dumps({"status": "error", "message": "Input HTML not found."}))
        return 2
    result = audit_html(
        args.input.read_text(encoding="utf-8"),
        threshold=args.threshold,
    )
    if args.official_check and result["status"] == "passed":
        result["official_validation"] = verify_article_structure(
            args.input.read_text(encoding="utf-8"),
            timeout=args.official_timeout,
        )
        if result["official_validation"]["status"] != "passed":
            result["status"] = "blocked"
    else:
        result["official_validation"] = {
            "status": "skipped",
            "is_valid": None,
            "reason": (
                "local_audit_failed"
                if args.official_check
                else "not_requested"
            ),
            "violations": [],
            "violation_count": 0,
            "transport": None,
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

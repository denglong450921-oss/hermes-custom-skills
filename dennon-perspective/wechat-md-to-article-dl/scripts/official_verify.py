#!/usr/bin/env python3
"""Opt-in client for WeChat's official article structure verification API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = (
    "https://mp.weixin.qq.com/article-bin/verify_article_structure"
)


def normalize_violations(invalid_info: Any) -> list[dict[str, Any]]:
    """Convert rule-keyed API details into a stable list for callers."""
    if not isinstance(invalid_info, dict):
        return []
    violations = []
    for rule, raw_detail in invalid_info.items():
        detail = raw_detail if isinstance(raw_detail, dict) else {}
        normalized_items = []
        for item in detail.get("items") or []:
            if not isinstance(item, dict):
                continue
            normalized_items.append(
                {
                    "outer_html": str(item.get("outerHTML") or ""),
                }
            )
        violations.append(
            {
                "rule": str(rule),
                "message": str(detail.get("violateRules") or ""),
                "items": normalized_items,
            }
        )
    return violations


def verify_article_structure(
    content: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    timeout: float = 15.0,
) -> dict[str, Any]:
    """Transmit HTML to the official endpoint only when explicitly called."""
    request = Request(
        endpoint,
        data=json.dumps({"content": content}, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "md-to-wechat-article-dl/2",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as error:
        return {
            "status": "error",
            "is_valid": False,
            "endpoint": endpoint,
            "message": str(error),
            "invalid_info": {},
            "violations": [],
            "violation_count": 0,
            "transport": "json",
        }
    is_valid = bool(payload.get("isValid"))
    invalid_info = payload.get("inValidInfo") or {}
    violations = normalize_violations(invalid_info)
    return {
        "status": "passed" if is_valid else "blocked",
        "is_valid": is_valid,
        "endpoint": endpoint,
        "message": "",
        "invalid_info": invalid_info,
        "violations": violations,
        "violation_count": sum(
            max(1, len(violation["items"])) for violation in violations
        ),
        "transport": "json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send HTML to WeChat's official article structure verifier."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()
    if not args.input.is_file():
        print(json.dumps({"status": "error", "message": "Input HTML not found."}))
        return 2
    result = verify_article_structure(
        args.input.read_text(encoding="utf-8"),
        endpoint=args.endpoint,
        timeout=args.timeout,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

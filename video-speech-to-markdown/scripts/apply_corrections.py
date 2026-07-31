#!/usr/bin/env python3
"""Apply reviewed ASR corrections and rebuild the continuous transcript."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--corrections", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = args.markdown.read_text(encoding="utf-8")
    data = json.loads(args.corrections.read_text(encoding="utf-8"))
    corrections = data.get("corrections", data)
    if not isinstance(corrections, list):
        raise SystemExit("Corrections must be a list or {'corrections': [...]}.")
    if "## 带时间戳转写" not in source or "## 连续全文" not in source:
        raise SystemExit("Input Markdown lacks transcript sections.")
    before, rest = source.split("## 带时间戳转写", 1)
    segment_area, after_full = rest.split("## 连续全文", 1)
    if "## 转写质量报告" not in after_full:
        raise SystemExit("Input Markdown lacks quality report.")
    _, tail = after_full.split("## 转写质量报告", 1)
    log_rows = []
    for item in corrections:
        old = str(item["from"])
        new = str(item["to"])
        reason = str(item.get("reason", "结合上下文复核"))
        count = segment_area.count(old)
        if count == 0:
            raise SystemExit(f"Correction source text not found: {old}")
        segment_area = segment_area.replace(old, new)
        log_rows.append((old, new, reason, count))
    bodies = re.findall(
        r"### \[\d{2}:\d{2}:\d{2} → \d{2}:\d{2}:\d{2}\]\s*\n+(.+?)(?=\n+### |\Z)",
        segment_area, re.S
    )
    continuous = " ".join(x.strip() for x in bodies)
    log = [
        "## 校订记录", "",
        "| 原识别 | 校订后 | 依据 | 次数 |",
        "|---|---|---|---:|",
    ]
    for old, new, reason, count in log_rows:
        log.append(f"| {old} | {new} | {reason} | {count} |")
    result = (
        before + "## 带时间戳转写" + segment_area +
        "## 连续全文\n\n" + continuous + "\n\n" +
        "\n".join(log) + "\n\n## 转写质量报告" + tail
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Applied {len(log_rows)} reviewed corrections to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

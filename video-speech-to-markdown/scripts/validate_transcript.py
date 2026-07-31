#!/usr/bin/env python3
"""Validate structure, timeline, consistency, and quality of a transcript."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def seconds(value: str) -> int:
    h, m, s = map(int, value.split(":"))
    return h * 3600 + m * 60 + s


def normalized(value: str) -> str:
    return re.sub(r"\s+", "", value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat quality WARN as failure")
    args = parser.parse_args()
    path = args.markdown.expanduser().resolve()
    failures: list[str] = []
    warnings: list[str] = []
    if not path.is_file() or path.stat().st_size == 0:
        failures.append("Markdown file is missing or empty")
        text = ""
    else:
        text = path.read_text(encoding="utf-8")
    required = (
        "# 视频转写：", "## 文件信息", "## 处理计划", "## 带时间戳转写",
        "## 连续全文", "## 转写质量报告", "## 质量备注"
    )
    for heading in required:
        if heading not in text:
            failures.append(f"Missing required section: {heading}")
    for field in (
        "来源视频：", "视频时长：", "文件大小：", "识别语言：", "转写模型：",
        "处理模式：", "资源策略：", "分批数量：", "质量结论：", "已完成批次："
    ):
        if field not in text:
            failures.append(f"Missing metadata or quality field: {field}")
    forbidden = ("Traceback (most recent call last)", "TemporaryDirectory(", "/video-transcript-")
    if any(token in text for token in forbidden):
        failures.append("Transcript contains runtime error or temporary path leakage")

    segment_area = ""
    if "## 带时间戳转写" in text and "## 连续全文" in text:
        segment_area = text.split("## 带时间戳转写", 1)[1].split("## 连续全文", 1)[0]
    matches = re.findall(
        r"### \[(\d{2}:\d{2}:\d{2}) → (\d{2}:\d{2}:\d{2})\]\s*\n+(.+?)(?=\n+### |\Z)",
        segment_area, re.S
    )
    if not matches:
        failures.append("No timestamped transcript segments found")
    previous_start = -1
    previous_end = -1
    segment_texts = []
    for start_text, end_text, body in matches:
        start, end = seconds(start_text), seconds(end_text)
        body = body.strip()
        if start < previous_start:
            failures.append(f"Timestamp start is not monotonic at {start_text}")
        if end < start:
            failures.append(f"Timestamp ends before it starts at {start_text}")
        if start < previous_end - 2:
            warnings.append(f"Timestamp overlap exceeds 2 seconds near {start_text}")
        if not body:
            failures.append(f"Empty transcript segment at {start_text}")
        previous_start, previous_end = start, max(previous_end, end)
        segment_texts.append(body)
    for a, b in zip(segment_texts, segment_texts[1:]):
        if normalized(a) == normalized(b):
            warnings.append("Adjacent transcript segments are identical")

    full = ""
    if "## 连续全文" in text and "## 转写质量报告" in text:
        full_area = text.split("## 连续全文", 1)[1]
        if "## 校订记录" in full_area:
            full = full_area.split("## 校订记录", 1)[0].strip()
        else:
            full = full_area.split("## 转写质量报告", 1)[0].strip()
    if not full:
        failures.append("Continuous transcript is empty")
    elif segment_texts and normalized(full) != normalized(" ".join(segment_texts)):
        failures.append("Continuous transcript does not match timestamped segments")

    quality_match = re.search(r"质量结论：\*\*(PASS|WARN|FAIL)\*\*", text)
    quality = quality_match.group(1) if quality_match else ""
    if quality == "FAIL":
        failures.append("Embedded quality conclusion is FAIL")
    if quality == "WARN":
        warnings.append("Embedded quality conclusion is WARN")
    if args.strict and warnings:
        failures.extend(f"Strict quality check: {item}" for item in warnings)

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1
    if warnings:
        print("WARN")
        for item in warnings:
            print(f"- {item}")
        return 0
    print(f"PASS: structure and text quality satisfied ({len(matches)} segments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

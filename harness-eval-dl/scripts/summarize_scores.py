#!/usr/bin/env python3
"""Summarize score.yaml files into Harness eval reports."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_score(path: Path) -> dict:
    data = {"path": path}
    for line in read(path).splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip().strip("'\"")
        if key in {"compliance", "execution_quality", "overall"}:
            try:
                data[key] = float(value)
            except ValueError:
                data[key] = 0.0
        else:
            data[key] = value
    parts = path.parts
    if "runs" in parts:
        idx = parts.index("runs")
        rest = parts[idx + 1 :]
        if len(rest) >= 5:
            data["iteration"] = rest[0]
            data["case_id"] = rest[1]
            data["configuration"] = rest[2]
            data["run"] = rest[3]
    return data


def extract_improvements(review_path: Path) -> list[str]:
    if not review_path.exists():
        return []
    out = []
    for line in read(review_path).splitlines():
        if "[workflow]" in line or "[eval]" in line or "[capability]" in line:
            out.append(line.strip("- ").strip())
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--workflow-rev", default="unknown")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    scores = [parse_score(path) for path in sorted((root / "runs").rglob("score.yaml"))]
    grouped = defaultdict(list)
    improvements = []
    for score in scores:
        grouped[(score.get("case_id", "unknown"), score.get("configuration", "unknown"))].append(score)
        improvements.extend(extract_improvements(score["path"].with_name("review.md")))

    latest_lines = ["# Latest Harness Eval Summary", ""]
    stats_lines = [
        f"generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"workflow_rev: {args.workflow_rev}",
        "groups:",
    ]
    history_lines = ["records:"]
    for (case_id, config), rows in sorted(grouped.items()):
        pass_count = sum(1 for row in rows if row.get("result") == "pass")
        mean_overall = sum(float(row.get("overall", 0.0)) for row in rows) / len(rows)
        latest_lines.append(f"- `{case_id}` / `{config}`: {pass_count}/{len(rows)} pass, mean overall {mean_overall:.2f}")
        stats_lines.extend(
            [
                f"  - case_id: {case_id}",
                f"    configuration: {config}",
                f"    runs: {len(rows)}",
                f"    pass_rate: {pass_count / len(rows):.4f}",
                f"    mean_overall: {mean_overall:.4f}",
            ]
        )
        for row in rows:
            history_lines.extend(
                [
                    f"  - workflow_rev: {args.workflow_rev}",
                    f"    case_id: {case_id}",
                    f"    configuration: {config}",
                    f"    run: {row.get('run', 'unknown')}",
                    f"    result: {row.get('result', 'unknown')}",
                    f"    overall: {row.get('overall', 0)}",
                ]
            )

    counts = Counter()
    for item in improvements:
        if "[workflow]" in item:
            counts["workflow"] += 1
        elif "[eval]" in item:
            counts["eval"] += 1
        elif "[capability]" in item:
            counts["capability"] += 1

    insights = ["# Batch Insights", ""]
    insights.append(f"- Workflow improvements: {counts['workflow']}")
    insights.append(f"- Eval improvements: {counts['eval']}")
    insights.append(f"- Capability improvements: {counts['capability']}")
    if improvements:
        insights.append("")
        insights.append("## Evidence-backed Suggestions")
        insights.extend(f"- {item}" for item in improvements)

    (reports / "latest.md").write_text("\n".join(latest_lines) + "\n", encoding="utf-8")
    (reports / "latest-stats.yaml").write_text("\n".join(stats_lines) + "\n", encoding="utf-8")
    (reports / "score-history.yaml").write_text("\n".join(history_lines) + "\n", encoding="utf-8")
    (reports / "batch-insights.md").write_text("\n".join(insights) + "\n", encoding="utf-8")
    print(f"Summarized {len(scores)} score files into {reports}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

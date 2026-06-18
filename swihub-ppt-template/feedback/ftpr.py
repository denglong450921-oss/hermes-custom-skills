#!/usr/bin/env python3
"""First-Time Pass Rate (FTPR) calculator for skill harness.

Tracks the proportion of outputs that pass all assertions on the first try,
without needing any corrections or retries.

Usage:
    python3 scripts/ftpr.py <path-to-failures.jsonl> --total-runs 30

Output: JSON report with FTPR, trend if multiple time periods are available.
"""

import json, sys, os, argparse
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

def load_failures(path):
    """Load failures from JSONL file."""
    failures = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                failures.append(json.loads(line))
    return failures

def compute_ftpr(failures, total_runs):
    """Compute First-Time Pass Rate.
    
    FTPR = (runs with zero failures) / (total runs)
    
    If total_runs is not provided, uses distinct case_ids as proxy.
    """
    if total_runs == 0:
        return {"error": "total_runs must be > 0"}
    
    # Count distinct case_ids that had failures
    cases_with_failures = set()
    for f in failures:
        case_id = f.get("case_id")
        if case_id:
            cases_with_failures.add(case_id)
    
    # If no case_ids available, count each unique run identifier
    if not cases_with_failures:
        case_key = lambda f: (f.get("case_id", ""), f.get("timestamp", "")[:10])
        unique_runs = set(case_key(f) for f in failures)
        cases_with_failures = unique_runs
        total = max(total_runs, len(unique_runs))
    else:
        total = max(total_runs, len(cases_with_failures))
    
    passed_runs = total - len(cases_with_failures)
    ftpr = (passed_runs / total) * 100 if total > 0 else 0
    
    return {
        "ftpr_percent": round(ftpr, 1),
        "runs_passed": passed_runs,
        "runs_failed": len(cases_with_failures),
        "total_runs": total,
        "total_failures": len(failures),
        "failures_per_failed_run": round(
            len(failures) / len(cases_with_failures), 2
        ) if cases_with_failures else 0
    }

def compute_trend(failures, total_runs, window_days=7):
    """Compute FTPR trend over time windows."""
    if not failures:
        return []
    
    # Get date range
    timestamps = []
    for f in failures:
        ts = f.get("timestamp", "")
        if ts:
            try:
                timestamps.append(datetime.fromisoformat(ts))
            except (ValueError, TypeError):
                pass
    
    if not timestamps:
        return []
    
    earliest = min(timestamps).replace(hour=0, minute=0, second=0, microsecond=0)
    latest = max(timestamps).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create weekly windows
    trend = []
    current = earliest
    while current <= latest:
        window_end = current + timedelta(days=window_days)
        window_failures = [
            f for f in failures
            if current <= _parse_ts(f) < window_end
        ]
        if window_failures:
            # Estimate runs in this window proportionally
            window_runs = max(1, total_runs * (window_days / max(
                1, (latest - earliest).days + window_days
            )))
            ftpr_data = compute_ftpr(window_failures, round(window_runs))
            ftpr_data["window_start"] = current.isoformat()[:10]
            ftpr_data["window_end"] = window_end.isoformat()[:10]
            trend.append(ftpr_data)
        current = window_end
    
    return trend

def _parse_ts(failure):
    """Parse timestamp from failure entry."""
    ts = failure.get("timestamp", "")
    if ts:
        try:
            return datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            pass
    return datetime.min

def format_report(ftpr_data, trend):
    """Format FTPR report as text."""
    lines = [
        "📊 First-Time Pass Rate Report",
        "=" * 40,
        f"  FTPR:           {ftpr_data['ftpr_percent']}%",
        f"  Runs passed:    {ftpr_data['runs_passed']}",
        f"  Runs failed:    {ftpr_data['runs_failed']}",
        f"  Total runs:     {ftpr_data['total_runs']}",
        f"  Total failures: {ftpr_data['total_failures']}",
        f"  Failures/fail:  {ftpr_data['failures_per_failed_run']}",
        "",
    ]
    
    # Interpretation
    ftpr = ftpr_data['ftpr_percent']
    if ftpr < 50:
        lines.append("  🚨 CRITICAL: FTPR < 50% — Generator needs major improvement.")
        lines.append("     Run distillation immediately.")
    elif ftpr < 80:
        lines.append("  ⚠️  WARNING: FTPR 50-80% — Common failure patterns exist.")
        lines.append("     Distillation will help.")
    elif ftpr < 95:
        lines.append("  ✅ GOOD: FTPR 80-95% — Strong generator.")
        lines.append("     Distill for edge cases.")
    elif ftpr == 100:
        lines.append("  🤔 SUSPICIOUS: 100% — Harness may be too easy.")
        lines.append("     Consider adding harder assertions.")
    else:
        lines.append("  🎉 EXCELLENT: FTPR > 95% — Near-perfect.")
    
    # Trend
    if trend:
        lines.append("")
        lines.append("  Trend (weekly):")
        for t in trend:
            arrow = "↑" if t['ftpr_percent'] > 50 else "↓"
            lines.append(f"    {t['window_start']} → {t['window_end']}: "
                        f"{t['ftpr_percent']}% {arrow}")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="First-Time Pass Rate calculator for skill harness."
    )
    parser.add_argument("failures_path", help="Path to failures.jsonl")
    parser.add_argument("--total-runs", type=int, default=0,
                        help="Total number of generation runs (required for accuracy)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output path for JSON report")
    parser.add_argument("--trend", "-t", action="store_true",
                        help="Compute weekly trend")
    args = parser.parse_args()
    
    failures_path = Path(args.failures_path)
    if not failures_path.exists():
        print(f"❌ File not found: {failures_path}", file=sys.stderr)
        sys.exit(1)
    
    failures = load_failures(failures_path)
    
    if args.total_runs <= 0:
        print("⚠️  --total-runs not set. Using distinct case_ids as proxy "
              "(may be inaccurate).", file=sys.stderr)
        args.total_runs = max(len(set(f.get("case_id", "")
                                      for f in failures)), 1)
        if args.total_runs == 1 and not failures:
            args.total_runs = 0
    
    if args.total_runs == 0:
        print("No data to report.")
        sys.exit(0)
    
    ftpr_data = compute_ftpr(failures, args.total_runs)
    
    trend = []
    if args.trend:
        trend = compute_trend(failures, args.total_runs)
    
    report = format_report(ftpr_data, trend)
    print(report)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump({
                "ftpr": ftpr_data,
                "trend": trend
            }, f, indent=2, ensure_ascii=False)
        print(f"\n  📄 Report saved: {output_path}")


if __name__ == "__main__":
    main()

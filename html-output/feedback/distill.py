#!/usr/bin/env python3
"""Semi-automatic error distiller for skill harness feedback loop.

Reads failures.jsonl, clusters errors by assertion type and evidence pattern,
uses LLM to abstract each cluster into generalized prompt rules.

Usage:
    python3 scripts/distill.py <path-to-failures.jsonl> [--output <path>] [--min-cluster 3]

Output: JSON with clusters, each containing a generalized rule + severity + inject_to target.
"""

import json, sys, os, argparse
from collections import defaultdict
from datetime import datetime
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

def cluster_by_assertion(failures):
    """Cluster failures by assertion type."""
    clusters = defaultdict(list)
    for f in failures:
        key = f.get("assertion", "unknown")
        clusters[key].append(f)
    return dict(clusters)

def cluster_by_evidence(clusters):
    """Within each assertion cluster, sub-cluster by evidence pattern."""
    refined = {}
    for assertion, items in clusters.items():
        evidence_groups = defaultdict(list)
        for item in items:
            ev = item.get("evidence", "no evidence")
            evidence_groups[ev].append(item)
        
        # Merge small groups into "other"
        sorted_groups = sorted(evidence_groups.items(), key=lambda x: -len(x[1]))
        merged = {}
        other = []
        for evidence, group in sorted_groups:
            if len(group) >= 2 or len(sorted_groups) <= 3:
                merged[evidence] = group
            else:
                other.extend(group)
        if other:
            merged["other_variants"] = other
        
        refined[assertion] = merged
    
    return refined

def generate_rule_suggestion(assertion_type, evidence, count, severity="medium"):
    """Generate a generalized prompt rule from error pattern.
    
    Uses heuristic templates for known assertion types.
    For custom assertion types, outputs a generic template.
    """
    known_rules = {
        "has_class_container": (
            "ALL output must be wrapped in a top-level <div class=\"container\"> element. "
            "This is required for centering — without it content floats left on the page. "
            "Treat this as a structural requirement, not just a styling suggestion."
        ),
        "has_table": (
            "When presenting tabular data, ALWAYS use <table> with a <thead> section "
            "containing <th> headers. Tables without headers are not scannable. "
            "Example:\n<table>\n<thead><tr><th>Col1</th><th>Col2</th></tr></thead>\n"
            "<tbody>\n<tr><td>...</td><td>...</td></tr>\n</tbody>\n</table>"
        ),
        "has_callout": (
            "Key insights, core takeaways, and conclusions MUST NOT be buried in "
            "plain paragraph text. Use <div class=\"callout\"> to make important "
            "points visually distinct from body text with a blue left border box."
        ),
        "has_steps": (
            "Sequential processes MUST be rendered as <ol class=\"steps\"> with "
            "data-step attributes on each <li>. Do not use plain numbered lists "
            "for step-by-step instructions."
        ),
        "has_details": (
            "Use <details><summary>...</summary><div>...</div></details> for "
            "supplementary information that can be expanded on demand. This keeps "
            "the primary content clean and scannable."
        ),
        "has_meta": (
            "Every page should include a .meta line with author, date, and context. "
            "<p class=\"meta\"> provides subdued typography for this purpose."
        ),
        "has_insight": (
            "Punchline conclusions and one-sentence takeaways should use "
            "<p class=\"insight\"> to make them visually distinct. This helps "
            "readers immediately identify the key message."
        ),
        "has_highlight": (
            "Key metrics and statistics must be displayed in <div class=\"highlight\"> "
            "with <span class=\"num\"> for the number and <span class=\"label\"> "
            "for the label. This draws attention to important figures."
        ),
    }
    
    rule = known_rules.get(assertion_type)
    if rule:
        return rule
    
    # Generic template for unknown assertion types
    return (
        f"The output must satisfy the '{assertion_type}' check. "
        f"Evidence from failures: '{evidence}'. "
        f"Review the skill's specification and ensure compliance."
    )

def infer_inject_to(assertion_type):
    """Map assertion type back to the likely skill section needing the rule."""
    section_map = {
        "has_class_container": "layout-system",
        "has_table": "standard-components",
        "has_callout": "step-3",
        "has_steps": "step-3",
        "has_details": "standard-components",
        "has_highlight": "standard-components",
        "has_tag": "standard-components",
        "has_meta": "step-2",
        "has_insight": "step-3",
        "has_hr": "layout-system",
    }
    return section_map.get(assertion_type, "general-instructions")

def calculate_severity(count, total):
    """Calculate severity based on proportion of total failures."""
    ratio = count / total if total > 0 else 0
    if ratio >= 0.2:
        return "high"
    elif ratio >= 0.08:
        return "medium"
    else:
        return "low"

def distill(failures, min_cluster=3):
    """Main distillation pipeline."""
    if not failures:
        return {
            "distillation_run": datetime.now().isoformat()[:10],
            "total_failures": 0,
            "clusters": [],
            "note": "No failures to distill."
        }
    
    # Step 1: Cluster by assertion type
    assertion_clusters = cluster_by_assertion(failures)
    
    # Step 2: Sub-cluster by evidence pattern
    refined = cluster_by_evidence(assertion_clusters)
    
    # Step 3: Build cluster output with rules
    clusters = []
    total = len(failures)
    
    for assertion_type, evidence_groups in sorted(
        refined.items(), key=lambda x: -sum(len(g) for g in x[1].values())
    ):
        for evidence, group in evidence_groups.items():
            count = len(group)
            if count < min_cluster and evidence != "other_variants":
                continue  # skip small clusters unless other
            
            rule = generate_rule_suggestion(assertion_type, evidence, count)
            severity = calculate_severity(count, total)
            inject_to = infer_inject_to(assertion_type)
            
            clusters.append({
                "count": count,
                "pattern": evidence[:100],
                "rule": rule,
                "severity": severity,
                "inject_to": inject_to,
                "sample_failures": [
                    {
                        "case_id": f.get("case_id", "unknown"),
                        "evidence": f.get("evidence", "")
                    }
                    for f in group[:3]  # first 3 as examples
                ]
            })
    
    # Sort clusters by count descending
    clusters.sort(key=lambda c: -c["count"])
    
    return {
        "distillation_run": datetime.now().isoformat()[:10],
        "total_failures": total,
        "clusters": clusters
    }

def format_rules_markdown(result):
    """Format distilled rules as markdown for injection."""
    if not result["clusters"]:
        return "# Harness-Distilled Rules\n\nNo rules distilled from feedback log.\n"
    
    lines = [
        "# Hard Constraints (distilled from harness feedback)",
        "",
        f"Generated: {result['distillation_run']}",
        f"Based on: {result['total_failures']} failure records",
        "",
        "The following rules were automatically distilled from real failures "
        "caught by the harness. Inject them into the generator's instructions "
        "to prevent recurring errors.",
        "",
    ]
    
    for i, cluster in enumerate(result["clusters"], 1):
        lines.append(f"### {i}. {cluster['inject_to']}: {cluster['pattern'][:60]}")
        lines.append(f"*Severity: {cluster['severity']} | {cluster['count']} occurrences*")
        lines.append("")
        lines.append(cluster["rule"])
        lines.append("")
    
    lines.append("---")
    lines.append("*This file was auto-generated by distill.py. "
                  "Review rules before injecting into generator instructions.*")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Semi-automatic error distiller for harness feedback loop."
    )
    parser.add_argument("failures_path", help="Path to failures.jsonl")
    parser.add_argument("--output", "-o", default=None,
                        help="Output directory (default: next to failures.jsonl)")
    parser.add_argument("--min-cluster", type=int, default=3,
                        help="Minimum cluster size to include (default: 3)")
    args = parser.parse_args()
    
    failures_path = Path(args.failures_path)
    if not failures_path.exists():
        print(f"❌ File not found: {failures_path}", file=sys.stderr)
        sys.exit(1)
    
    failures = load_failures(failures_path)
    print(f"Loaded {len(failures)} failures from {failures_path}")
    
    if not failures:
        print("⚠️  No failures to distill.")
        sys.exit(0)
    
    result = distill(failures, min_cluster=args.min_cluster)
    
    output_dir = Path(args.output) if args.output else failures_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    json_path = output_dir / f"distillation_{result['distillation_run']}.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  📄 JSON: {json_path}")
    
    # Write markdown rules
    rules_md = format_rules_markdown(result)
    md_path = output_dir / "rules.md"
    with open(md_path, "w") as f:
        f.write(rules_md)
    print(f"  📄 Rules: {md_path}")
    
    # Print summary
    print(f"\n📊 Distillation Summary:")
    print(f"   Total failures:  {result['total_failures']}")
    print(f"   Clusters found:  {len(result['clusters'])}")
    for c in result["clusters"]:
        print(f"     [{c['severity']:>6}] ({c['count']:3}x) {c['pattern'][:60]}")
    
    if result["clusters"]:
        print(f"\n   ✅ Rules written to {md_path}")
        print(f"   Review before injecting into generator instructions.")


if __name__ == "__main__":
    main()

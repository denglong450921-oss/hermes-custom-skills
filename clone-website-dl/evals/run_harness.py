#!/usr/bin/env python3
"""
clone-website-dl Harness Runner — runs all evals against a generated output.

Reads evals/evals.json, maps each case's grader.must_use to grader.py checks,
and produces a trace with pass/fail results.

Usage:
  python3 evals/run_harness.py <output-file>
  python3 evals/run_harness.py <output-file> --case case_001
"""

import json
import os
import subprocess
import sys

EVALS_FILE = os.path.join(os.path.dirname(__file__), "evals.json")
GRADER = os.path.join(os.path.dirname(__file__), "grader.py")

check_map = {
    # Case 001: Spec template completeness
    "spec_has_all_sections":   {"text": "Spec has all required sections", "check": "spec_has_all_sections"},
    "spec_has_css_values":     {"text": "Spec references getComputedStyle + px values", "check": "spec_has_css_values"},
    "spec_has_states":         {"text": "Spec documents states & behaviors", "check": "spec_has_states"},
    "spec_has_assets":         {"text": "Spec references asset paths", "check": "spec_has_assets"},

    # Case 002: CSS extraction accuracy
    "has_get_computed_style":  {"text": "Uses getComputedStyle (no estimation)", "check": "has_get_computed_style"},
    "has_extraction_script":   {"text": "References extract-component-css.js", "check": "has_extraction_script"},
    "has_css_verification":    {"text": "References verify-css.js + discover-assets.js", "check": "has_css_verification"},

    # Case 003: Antipatterns + checkpoints
    "has_antipatterns_section": {"text": "Has Common Antipatterns section", "check": "has_antipatterns_section"},
    "has_checkpoint_count":    {"text": "Has >=4 🔴/🛑 checkpoints", "check": "has_checkpoint_count"},
    "has_fallback_table":      {"text": "Has Fallback Decision Table", "check": "has_fallback_table"},

    # Case 004: Firecrawl fallback
    "firecrawl_mentioned":     {"text": "Firecrawl referenced as fallback", "check": "firecrawl_mentioned"},
    "dual_mode_documented":    {"text": "Camofox + Firecrawl dual mode", "check": "dual_mode_documented"},

    # Case 005: Agent pipeline + component graph
    "agent_pipeline_documented": {"text": "Agent pipeline architecture", "check": "agent_pipeline_documented"},
    "component_graph_mentioned": {"text": "Post-clone component graph", "check": "component_graph_mentioned"},

    # Case 006: Per-page source-of-truth gate
    "page_source_truth_documented": {"text": "Canonical per-page SOURCE_OF_TRUTH.md documented", "check": "page_source_truth_documented"},
    "source_truth_gate_enforced": {"text": "Coding blocked until source-of-truth readiness gate passes", "check": "source_truth_gate_enforced"},

    # Case 007: Visual occupancy + booth fallback
    "asset_visibility_enforced": {"text": "Reachable source media must remain visibly rendered", "check": "asset_visibility_enforced"},
    "booth_fallback_documented": {"text": "Unavailable media receives documented booth fallback", "check": "booth_fallback_documented"},

    # Case 008: Measurable convergence harness
    "measurable_diff_harness_documented": {"text": "Deterministic capture, pixel diff, geometry diff, and repair loop documented", "check": "measurable_diff_harness_documented"},
    "acceptance_thresholds_enforced": {"text": "Objective acceptance thresholds gate 1:1 completion", "check": "acceptance_thresholds_enforced"},

    # Honesty checks
    "reports_failure_honestly": {"text": "Reports failures honestly", "check": "reports_failure_honestly"},
    "no_defensive_disclaimers": {"text": "No defensive disclaimers", "check": "no_defensive_disclaimers"},
    "no_false_success":         {"text": "No false success claims", "check": "no_false_success"},
}


def load_evals():
    with open(EVALS_FILE, 'r') as f:
        return json.load(f)


def run_case(output_path, case):
    """Run grader checks for a single eval case."""
    must_use = case.get("grader", {}).get("must_use", [])
    checks = [check_map[ck] for ck in must_use if ck in check_map]

    # Support grading against a different file (e.g., reference files)
    target_file = output_path
    grader_file = case.get("grader_file")
    if grader_file:
        # grader_file is relative to skill root (parent of evals/)
        skill_root = os.path.dirname(os.path.dirname(EVALS_FILE))
        abs_grader = os.path.join(skill_root, grader_file)
        if os.path.exists(abs_grader):
            target_file = abs_grader
        else:
            # Fallback: try relative to evals/
            abs_grader = os.path.join(os.path.dirname(EVALS_FILE), grader_file)
            if os.path.exists(abs_grader):
                target_file = abs_grader

    checks_json = json.dumps(checks)
    result = subprocess.run(
        ["python3", GRADER, target_file, checks_json],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": result.stderr or result.stdout,
            "exit_code": result.returncode
        }


def run_all(output_path, case_filter=None):
    """Run all eval cases against output_path."""
    data = load_evals()
    evals = data.get("evals", [])
    if case_filter:
        evals = [e for e in evals if e["id"] == case_filter]

    traces = []
    total_passed = 0
    total_checks = 0

    for case in evals:
        result = run_case(output_path, case)
        case_trace = {
            "case_id": case["id"],
            "case_name": case.get("name", case["id"]),
            "task": case["task"],
            "tools_used": case.get("tools", []),
            "grade": result
        }
        if result.get("success"):
            total_passed += 1
        if "results" in result:
            total_checks += len(result["results"])
        traces.append(case_trace)

    print(json.dumps({
        "skill": data.get("skill_name", "unknown"),
        "output_file": output_path,
        "cases_run": len(evals),
        "cases_passed": total_passed,
        "total_checks": total_checks,
        "traces": traces
    }, indent=2))

    return 0 if total_passed == len(evals) else 1


def main():
    """Entry point for check_harness.py compliance."""
    if len(sys.argv) < 2:
        print("Usage: python3 evals/run_harness.py <output-file> [--case <case_id>]")
        sys.exit(1)

    output_path = sys.argv[1]
    case_filter = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--case":
        case_filter = sys.argv[3]

    if not os.path.exists(output_path):
        print(f"Error: output file not found: {output_path}")
        sys.exit(1)

    sys.exit(run_all(output_path, case_filter))


if __name__ == "__main__":
    main()

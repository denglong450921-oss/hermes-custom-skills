#!/usr/bin/env python3
"""
clone-website-dl Harness Grader — domain-specific assertion checker.

Each check reads the output text (e.g., skill SKILL.md content, generated spec files)
and verifies it contains expected evidence for clone-website-dl workflow quality.

Usage:
  python3 evals/grader.py <output-file> '<checks-json>'
"""

import json
import re
import sys

def check_output(output_path, checks_json):
    """Run all checks in checks_json against the output file content."""
    with open(output_path, 'r') as f:
        content = f.read()

    checks = json.loads(checks_json)
    results = []
    all_passed = True

    for check in checks:
        check_name = check["check"]
        passed = False
        evidence = ""

        # ─── Case 001: Spec template completeness ───
        if check_name == "spec_has_all_sections":
            required_sections = [
                "Overview", "DOM Structure", "Computed Styles",
                "States & Behaviors", "Assets", "Text Content",
                "Implementation Notes", "Responsive Behavior"
            ]
            missing = [s for s in required_sections if s.lower() not in content.lower()]
            passed = len(missing) == 0
            evidence = f"All sections present" if passed else f"Missing: {', '.join(missing)}"

        elif check_name == "spec_has_css_values":
            # Must reference getComputedStyle or computed CSS values
            has_gcs = "getComputedStyle" in content or "computed" in content.lower()
            has_values = bool(re.search(r'\d+px', content))
            passed = has_gcs and has_values
            evidence = f"getComputedStyle: {has_gcs}, pixel values: {has_values}"

        elif check_name == "spec_has_states":
            has_states = "State" in content or "hover" in content.lower()
            passed = has_states
            evidence = "States section found" if has_states else "No state documentation"

        elif check_name == "spec_has_assets":
            has_assets = "public/" in content or "Asset" in content
            passed = has_assets
            evidence = "Asset references found" if has_assets else "No asset documentation"

        # ─── Case 002: CSS extraction accuracy ───
        elif check_name == "has_get_computed_style":
            passed = "getComputedStyle" in content
            evidence = "getComputedStyle found" if passed else "getComputedStyle NOT found"

        elif check_name == "has_extraction_script":
            passed = "extract-component-css.js" in content
            evidence = "extraction script referenced" if passed else "extraction script missing"

        elif check_name == "has_css_verification":
            has_verify = "verify-css.js" in content
            has_discover = "discover-assets.js" in content
            passed = has_verify and has_discover
            evidence = f"verify-css: {has_verify}, discover-assets: {has_discover}"

        # ─── Case 003: Antipatterns and checkpoints ───
        elif check_name == "has_antipatterns_section":
            passed = "Common Antipatterns" in content or "What NOT to Do" in content
            evidence = "Antipatterns section found" if passed else "No antipatterns section"

        elif check_name == "has_checkpoint_count":
            checkpoints = content.count("🔴 CHECKPOINT")
            stops = content.count("🛑 STOP")
            total = checkpoints + stops
            passed = total >= 4
            evidence = f"🔴: {checkpoints}, 🛑: {stops}, total: {total} (need >=4)"

        elif check_name == "has_fallback_table":
            passed = "Fallback Decision Table" in content or "references/fallback-table" in content
            evidence = "Fallback table found" if passed else "Fallback table missing"

        # ─── Case 004: Firecrawl fallback ───
        elif check_name == "firecrawl_mentioned":
            passed = "Firecrawl" in content
            evidence = "Firecrawl referenced" if passed else "Firecrawl NOT found"

        elif check_name == "dual_mode_documented":
            has_camofox = "Camofox" in content
            has_firecrawl = "Firecrawl" in content
            has_fallback = "fallback" in content.lower()
            passed = has_camofox and has_firecrawl and has_fallback
            evidence = f"Camofox: {has_camofox}, Firecrawl: {has_firecrawl}, fallback: {has_fallback}"

        # ─── Case 005: Agent pipeline + graph ───
        elif check_name == "agent_pipeline_documented":
            passed = "Agent Pipeline" in content or "Extraction Agent" in content
            evidence = "Agent pipeline found" if passed else "No agent pipeline"

        elif check_name == "component_graph_mentioned":
            passed = "component-graph" in content or "Component Relationship" in content or "component graph" in content.lower()
            evidence = "Component graph found" if passed else "No component graph"

        # ─── Case 006: Per-page source-of-truth gate ───
        elif check_name == "page_source_truth_documented":
            has_path = "docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md" in content
            has_template = "page-source-of-truth-template.md" in content
            has_unique = "unique authority" in content.lower() or "canonical" in content.lower()
            passed = has_path and has_template and has_unique
            evidence = f"path: {has_path}, template: {has_template}, canonical authority: {has_unique}"

        elif check_name == "source_truth_gate_enforced":
            has_gate = "source-of-truth gate" in content.lower()
            blocks_code = "Do not code yet" in content or "cannot start until" in content
            update_order = "update the source of truth first" in content.lower()
            passed = has_gate and blocks_code and update_order
            evidence = f"gate: {has_gate}, blocks coding: {blocks_code}, reconciliation order: {update_order}"

        # ─── Case 007: Visual occupancy + booth fallback ───
        elif check_name == "asset_visibility_enforced":
            has_visibility_rule = "reachable source media is rendered" in content.lower() or "asset is reachable, render it" in content.lower()
            names_hidden_css = "opacity: 0" in content and "display: none" in content
            audits_blank_space = "unexplained blank" in content.lower()
            passed = has_visibility_rule and names_hidden_css and audits_blank_space
            evidence = f"visibility rule: {has_visibility_rule}, hidden CSS named: {names_hidden_css}, blank-space audit: {audits_blank_space}"

        elif check_name == "booth_fallback_documented":
            has_booth = "booth fallback" in content.lower() or "booth layout" in content.lower()
            preserves_layout = "preserves the section's occupied area" in content.lower() or "preserving dimensions" in content.lower()
            records_substitution = "record the substitution" in content.lower() or "source of truth must name the booth fallback" in content.lower()
            passed = has_booth and preserves_layout and records_substitution
            evidence = f"booth fallback: {has_booth}, preserves layout: {preserves_layout}, recorded: {records_substitution}"

        # ─── Case 008: Measurable convergence harness ───
        elif check_name == "measurable_diff_harness_documented":
            has_capture = "capture-reference.mjs" in content
            has_visual_diff = "visual-diff.mjs" in content
            has_geometry = "compare-geometry.mjs" in content
            has_loop = "repair loop" in content.lower()
            passed = has_capture and has_visual_diff and has_geometry and has_loop
            evidence = f"capture: {has_capture}, visual diff: {has_visual_diff}, geometry: {has_geometry}, repair loop: {has_loop}"

        elif check_name == "acceptance_thresholds_enforced":
            has_static_threshold = "0.5%" in content
            has_text_threshold = "1.5%" in content
            has_geometry_threshold = "<=2px" in content
            has_completion_gate = "do not claim a 1:1 clone" in content.lower()
            passed = has_static_threshold and has_text_threshold and has_geometry_threshold and has_completion_gate
            evidence = f"static: {has_static_threshold}, text-heavy: {has_text_threshold}, geometry: {has_geometry_threshold}, completion gate: {has_completion_gate}"

        # ─── Honesty / truthfulness checks ───
        elif check_name == "reports_failure_honestly":
            has_errors = bool(re.search(r'(FAIL|ERROR|Traceback|Missing|incomplete)', content, re.I))
            has_honest = "fallback" in content.lower() or "recovery" in content.lower()
            passed = not has_errors or has_honest
            evidence = "Honest failure reporting" if passed else "Errors without recovery path"

        elif check_name == "no_defensive_disclaimers":
            defensive = [
                "but this might not be correct",
                "I cannot guarantee",
                "this may not be accurate",
                "but I could be wrong",
            ]
            found = [p for p in defensive if p.lower() in content.lower()]
            passed = len(found) == 0
            evidence = "No defensive disclaimers" if passed else f"Found: {found}"

        elif check_name == "no_false_success":
            has_errors = bool(re.search(r'(FAIL|ERROR|Traceback|assert.*Failed)', content, re.I))
            says_passed = bool(re.search(r'(all passed|all tests passed|successfully complete)', content, re.I))
            passed = not (has_errors and says_passed)
            evidence = "No contradiction" if passed else "Claims success but errors exist"

        else:
            passed = False
            evidence = f"Unknown check: {check_name}"

        results.append({
            "check": check_name,
            "passed": passed,
            "evidence": evidence
        })
        if not passed:
            all_passed = False

    return {"success": all_passed, "results": results}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: grader.py <output-file> '<checks-json>'")
        sys.exit(1)

    output_path = sys.argv[1]
    checks_json = sys.argv[2]
    result = check_output(output_path, checks_json)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)

#!/usr/bin/env python3
"""
clone-website Harness Grader — domain-specific assertion checker.

Each check reads the output text (e.g., skill SKILL.md content, generated spec files)
and verifies it contains expected evidence for clone-website workflow quality.

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
            passed = "Fallback Decision Table" in content
            evidence = "Fallback table found" if passed else "Fallback table missing"

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

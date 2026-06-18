#!/usr/bin/env python3
"""Grader for wechat_article_css_dl — checks CSS violation detection + fix output."""

import re, sys, json, os

def check_output(filepath, checks):
    if not os.path.exists(filepath):
        return {c.get("text", c["check"]): {"passed": False, "evidence": "File not found"} for c in checks}
    with open(filepath) as f:
        content = f.read()
    results = {}
    for check in checks:
        cid = check.get("text", check["check"])
        evidence = ""
        passed = False
        cl = check["check"]

        if cl == "detects_style_block":
            passed = bool(re.search(r"style.*block|style.*tag|<style>", content, re.I))
            evidence = "style block detected" if passed else "No style block mention"

        elif cl == "detects_gradient":
            passed = bool(re.search(r"gradient|linear-gradient", content, re.I))
            evidence = "Gradient detected" if passed else "No gradient mention"

        elif cl == "detects_flex":
            passed = bool(re.search(r"flex|flexbox", content, re.I))
            evidence = "Flex detected" if passed else "No flex mention"

        elif cl == "detects_pseudo_element":
            passed = bool(re.search(r"::before|::after|pseudo.element", content, re.I))
            evidence = "Pseudo-element detected" if passed else "No pseudo-element mention"

        elif cl == "detects_css_variable":
            passed = bool(re.search(r"var\(--|CSS variable|--[\w-]+", content, re.I))
            evidence = "CSS variable detected" if passed else "No CSS variable mention"

        elif cl == "detects_box_shadow":
            passed = bool(re.search(r"box.shadow", content, re.I))
            evidence = "box-shadow detected" if passed else "No box-shadow mention"

        elif cl == "detects_media_query":
            passed = bool(re.search(r"@media|media query", content, re.I))
            evidence = "@media detected" if passed else "No @media mention"

        elif cl == "applies_fix":
            passed = bool(re.search(r"fix|applied|removed|replaced", content, re.I))
            evidence = "Fix applied" if passed else "No fix mention"

        elif cl == "generates_output_path":
            passed = bool(re.search(r"(output|save|write|path|\.html)", content, re.I))
            evidence = "Output path referenced" if passed else "No output path"

        elif cl == "fixes_gradient":
            passed = bool(re.search(r"(gradient|linear.gradient|replaced.*solid)", content, re.I))
            evidence = "Gradient fix referenced" if passed else "No gradient fix"

        elif cl == "removes_style_block":
            passed = bool(re.search(r"(style.*block|removed.*style)", content, re.I))
            evidence = "Style block removal referenced" if passed else "No style block removal"

        elif cl == "reports_clean":
            passed = bool(re.search(r"No WeChat CSS violations", content))
            evidence = "Clean report" if passed else "Violations still reported"

        else:
            evidence = "Unknown check: " + cl

        results[cid] = {"passed": passed, "evidence": evidence}
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [
        {"text": "Detects style block", "check": "detects_style_block"},
        {"text": "Detects gradient", "check": "detects_gradient"},
    ]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

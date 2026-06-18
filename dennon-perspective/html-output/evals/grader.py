#!/usr/bin/env python3
"""HTML-output skill grader. Checks generated HTML against assertions."""

import re, sys, json, os

def check_html(filepath, checks):
    """Run assertion checks on a generated HTML file."""
    if not os.path.exists(filepath):
        return {c: {"passed": False, "evidence": "File not found"} for c in checks}

    with open(filepath) as f:
        html = f.read()

    results = {}
    for check in checks:
        cid = check.get("text", check["check"])
        evidence = ""
        passed = False

        if check["check"] == "has_class_container":
            passed = 'class="container"' in html or "class='container'" in html or "class=container" in html
            evidence = "container class found" if passed else "missing .container"

        elif check["check"] == "has_table":
            passed = "<table" in html and "<thead" in html
            evidence = "<table> with <thead> found" if passed else "missing <table> or <thead>"

        elif check["check"] == "has_callout":
            passed = 'class="callout"' in html
            evidence = ".callout found" if passed else "missing .callout"

        elif check["check"] == "has_steps":
            passed = 'class="steps"' in html
            evidence = ".steps found" if passed else "missing .steps"

        elif check["check"] == "steps_have_data_step":
            steps = re.findall(r'<li[^>]*data-step=["\'](\d+)["\'][^>]*>', html)
            passed = len(steps) >= 2
            evidence = f"{len(steps)} steps with data-step" if passed else f"only {len(steps)} steps with data-step"

        elif check["check"] == "has_details":
            passed = "<details" in html and "<summary" in html
            evidence = "<details>/<summary> found" if passed else "missing accordion"

        elif check["check"] == "has_highlight":
            passed = 'class="highlight"' in html
            evidence = ".highlight found" if passed else "missing .highlight"

        elif check["check"] == "has_tag":
            passed = 'class="tag"' in html
            evidence = ".tag found" if passed else "missing .tag"

        elif check["check"] == "desktop_file_exists":
            desktop_pattern = r'/Users/f/Desktop/[^"\']+\.html'
            passed = bool(re.search(desktop_pattern, html)) or bool(re.search(desktop_pattern, str(sys.argv)))
            evidence = "Desktop path referenced" if passed else "no Desktop path found"

        elif check["check"] == "file_size":
            size = len(html)
            passed = 2000 <= size <= 100000
            evidence = f"{size} bytes" if not passed else f"{size} bytes (OK)"

        elif check["check"] == "has_meta":
            passed = 'class="meta"' in html
            evidence = ".meta found" if passed else "missing .meta"

        elif check["check"] == "has_insight":
            passed = 'class="insight"' in html
            evidence = ".insight found" if passed else "missing .insight"

        elif check["check"] == "has_hr":
            passed = "<hr" in html
            evidence = "<hr> found" if passed else "missing <hr>"

        elif check["check"] == "has_executive_summary":
            passed = 'class="executive-summary"' in html
            evidence = ".executive-summary found" if passed else "missing opening .executive-summary"

        elif check["check"] == "summary_before_detail":
            summary_at = html.find('class="executive-summary"')
            detail_candidates = [pos for pos in [
                html.find("<hr"),
                html.find("<table"),
                html.find('class="logic-map"'),
                html.find("<section", summary_at + 1),
            ] if pos >= 0]
            passed = summary_at >= 0 and (not detail_candidates or summary_at < min(detail_candidates))
            evidence = "opening summary precedes detail sections" if passed else "summary is missing or buried after details"

        elif check["check"] == "has_logic_visual":
            passed = 'class="logic-map"' in html
            evidence = ".logic-map found" if passed else "missing .logic-map"

        elif check["check"] == "has_closing_synthesis":
            passed = 'class="closing-synthesis"' in html
            evidence = ".closing-synthesis found" if passed else "missing .closing-synthesis"

        elif check["check"] == "has_key_highlight":
            patterns = ['class="highlight-list"', 'class="callout"', 'class="highlight"', "<table"]
            passed = any(pattern in html for pattern in patterns)
            evidence = "key-point visual anchor found" if passed else "missing highlighted key points"

        else:
            evidence = f"Unknown check: {check['check']}"

        results[cid] = {"passed": passed, "evidence": evidence}

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <html_file> [checks_json]")
        sys.exit(1)

    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [
        {"text": "Has container", "check": "has_class_container"},
        {"text": "Has table with thead", "check": "has_table"},
        {"text": "Has callout", "check": "has_callout"},
        {"text": "Has steps", "check": "has_steps"},
    ]

    results = check_html(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))

    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

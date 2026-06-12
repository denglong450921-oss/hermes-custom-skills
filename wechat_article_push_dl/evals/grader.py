#!/usr/bin/env python3
"""Grader for wechat_article_push_dl — checks command construction + error handling."""

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

        if cl == "builds_html_command":
            passed = bool(re.search(r"--html", content))
            evidence = "--html flag found" if passed else "Missing --html flag"

        elif cl == "builds_markdown_command":
            passed = bool(re.search(r"--markdown", content))
            evidence = "--markdown flag found" if passed else "Missing --markdown flag"

        elif cl == "includes_cover":
            passed = bool(re.search(r"--cover", content))
            evidence = "--cover flag found" if passed else "Missing --cover flag"

        elif cl == "includes_style":
            passed = bool(re.search(r"--style\s+(tech|academic_gray|festival|announcement)", content, re.I))
            evidence = "--style flag found" if passed else "Missing --style flag"

        elif cl == "includes_type_newspic":
            passed = bool(re.search(r"--type\s+newspic", content))
            evidence = "--type newspic found" if passed else "Missing --type newspic"

        elif cl == "includes_comment":
            passed = bool(re.search(r"--comment", content))
            evidence = "--comment flag found" if passed else "Missing --comment flag"

        elif cl == "includes_fans_only_comment":
            passed = bool(re.search(r"--fans-only-comment", content))
            evidence = "--fans-only-comment found" if passed else "Missing fans-only-comment"

        elif cl == "handles_missing_cover":
            passed = bool(re.search(r"(cover.*required|MISSING_COVER|--cover.*need|add.*--cover)", content, re.I))
            evidence = "Missing cover handled" if passed else "No cover error handling"

        elif cl == "handles_ip_whitelist":
            passed = bool(re.search(r"(40164|IP.*whitelist|whitelist.*IP)", content, re.I))
            evidence = "IP whitelist error handled" if passed else "No IP whitelist handling"

        elif cl == "handles_auth_error":
            passed = bool(re.search(r"(40001|40013|AppSecret|AppID)", content, re.I))
            evidence = "Auth error handled" if passed else "No auth error handling"

        elif cl == "verifies_preconditions":
            passed = bool(re.search(r"(precondition|check.*\.env|verify.*credential|check.*install)", content, re.I))
            evidence = "Precondition check present" if passed else "Missing precondition check"

        elif cl == "returns_media_id":
            passed = bool(re.search(r"(media_id|draft.*created|草稿箱)", content))
            evidence = "media_id reference found" if passed else "Missing media_id output"

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
        {"text": "HTML command", "check": "builds_html_command"},
        {"text": "Cover flag", "check": "includes_cover"},
    ]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

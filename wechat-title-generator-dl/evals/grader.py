#!/usr/bin/env python3
"""Grader for wechat-title-generator-dl. Checks Markdown title output."""

import re, sys, json, os

CLICKBAIT_PATTERNS = [
    "震惊", "惊呆", "99%", "再不", "晚了", "全网", "疯了",
    "沸腾", "出大事", "紧急", "马上删", "内部流出", "一定看",
    "转疯了", "都在传", "必看", "跪了", "吓尿", "哭晕",
    "所有人都不知道", "千万别", "赶紧",
]

BLOCKED_TITLE_PATTERNS = [
    "再不.*就", "99%.*的人", "不看.*后悔", "看.*哭", "震惊.*",
]

def check_output(filepath, checks):
    if not os.path.exists(filepath):
        return {c.get("text", c["check"]): {"passed": False, "evidence": "File not found"} for c in checks}
    with open(filepath) as f:
        content = f.read()
    results = {}
    for check in checks:
        cid = check.get("text", check["check"])
        passed = False
        evidence = ""
        if check["check"] == "has_markdown_title":
            m = re.search(r"^#\s+(.+)", content, re.M)
            passed = bool(m)
            evidence = f"Title: {m.group(1)[:50]}..." if m else "No # title found"
        elif check["check"] == "has_subtitle":
            passed = "## 副标题" in content
            evidence = "Subtitle section found" if passed else "Missing ## 副标题"
        elif check["check"] == "has_tags":
            passed = "## 标签" in content
            evidence = "Tags section found" if passed else "Missing ## 标签"
        elif check["check"] == "no_clickbait":
            found = [p for p in CLICKBAIT_PATTERNS if p in content]
            passed = len(found) == 0
            evidence = f"Clickbait found: {found}" if found else "No clickbait detected"
        elif check["check"] == "has_structure":
            has_title = bool(re.search(r"^#\s+", content, re.M))
            has_sub = "## 副标题" in content
            has_tags = "## 标签" in content
            has_original = "## 原标题" in content or "#" in content
            passed = has_title and has_sub and has_tags
            evidence = f"title={has_title}, subtitle={has_sub}, tags={has_tags}" if passed else f"Missing: title={has_title} sub={has_sub} tags={has_tags}"
        else:
            evidence = f"Unknown check: {check['check']}"
        results[cid] = {"passed": passed, "evidence": evidence}
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [{"text": "Has title", "check": "has_markdown_title"}]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

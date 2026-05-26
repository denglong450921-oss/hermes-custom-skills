#!/usr/bin/env python3
"""Grader for global-skill-deployer. Checks deployment outputs against assertions."""

import re, sys, json, os
from pathlib import Path

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
        
        if check["check"] == "global_source_exists":
            # Check output mentions the global registry path
            passed = "~/.agents/skills" in content or "/.agents/skills" in content
            evidence = "Global registry path found" if passed else "Missing global registry path"
        
        elif check["check"] == "symlinks_created":
            # Check output mentions symlink creation
            passed = "symlink" in content.lower() or "链接" in content
            evidence = "Symlink reference found" if passed else "No symlink creation mentioned"
        
        elif check["check"] == "cli_wrapper_created":
            # Check output mentions CLI wrapper
            passed = "wrapper" in content.lower() or "~/.local/bin" in content
            evidence = "Wrapper reference found" if passed else "No CLI wrapper mentioned"
        
        elif check["check"] == "inventory_reports_generated":
            # Check output mentions JSON and MD inventory reports
            passed = ".json" in content and (".md" in content or ".markdown" in content)
            evidence = "JSON + MD reports referenced" if passed else "Missing report file references"
        
        elif check["check"] == "backup_on_conflict":
            # Check output mentions backup creation on conflict
            passed = "backup" in content.lower() or "备份" in content
            evidence = "Backup mentioned" if passed else "No backup handling mentioned"
        
        elif check["check"] == "custom_only":
            # Check output mentions custom-only mode
            passed = "custom-only" in content.lower() or "custom only" in content.lower() or "自建" in content
            evidence = "Custom-only mode detected" if passed else "No custom-only filtering mentioned"
        
        elif check["check"] == "needs_attention":
            # Check output mentions needs_attention or issues
            passed = "needs_attention" in content.lower() or "needs attention" in content.lower() or "issue" in content.lower()
            evidence = "Health status reported" if passed else "No attention flags mentioned"
        
        elif check["check"] == "manifest_created":
            # Check output mentions manifest
            passed = "manifest" in content.lower() or "custom-skill-manifest" in content
            evidence = "Manifest reference found" if passed else "Missing manifest mention"
        
        elif check["check"] == "refresh_baseline":
            # Check output mentions baseline refresh
            passed = "baseline" in content.lower() or "official-skills" in content
            evidence = "Baseline refresh mentioned" if passed else "No baseline refresh mentioned"
        
        elif check["check"] == "verify_results":
            # Check output includes verification steps
            passed = "verify" in content.lower() or "验证" in content or "检查" in content
            evidence = "Verification mentioned" if passed else "No verification results found"
        
        elif check["check"] == "skip_cli_wrapper":
            # Check output mentions --skip-wrapper or no wrapper
            passed = "skip" in content.lower() or "wrapper" not in content.lower() or "no wrapper" in content.lower()
            evidence = "Wrapper handling correct" if passed else "Wrapper not handled as expected"
        
        else:
            evidence = f"Unknown check: {check['check']}"
        
        results[cid] = {"passed": passed, "evidence": evidence}
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [
        {"text": "Global source exists", "check": "global_source_exists"},
        {"text": "Symlinks created", "check": "symlinks_created"},
        {"text": "CLI wrapper created", "check": "cli_wrapper_created"},
        {"text": "Inventory reports", "check": "inventory_reports_generated"},
    ]
    
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

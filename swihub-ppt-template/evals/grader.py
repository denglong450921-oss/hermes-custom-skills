#!/usr/bin/env python3
"""Grader for swihub-ppt-template. Checks PPTX generation outputs."""

import re, sys, json, os, zipfile

def check_output(filepath, checks):
    if not os.path.exists(filepath):
        return {c.get("text", c["check"]): {"passed": False, "evidence": "File not found"} for c in checks}
    
    with open(filepath) as f:
        content = f.read()
    
    # Check if referenced PPTX actually exists
    ptx_paths = re.findall(r'(/[^\s"\']+\.pptx)', content)
    ptx_valid = 0
    for p in set(ptx_paths[:10]):
        if os.path.exists(p):
            try:
                with zipfile.ZipFile(p) as z:
                    if 'ppt/presentation.xml' in z.namelist():
                        ptx_valid += 1
                    else:
                        ptx_valid -= 1
            except:
                pass
    
    results = {}
    for check in checks:
        cid = check.get("text", check["check"])
        evidence = ""
        passed = False
        
        if check["check"] == "script_ran_successfully":
            has_fatal = bool(re.search(r'(Traceback|FAIL|\\bError\\b|Failed)', content[:500]))
            has_output = bool(re.search(r'\.pptx', content))
            passed = not has_fatal and has_output
            evidence = "Script completed with output" if passed else "Error or missing output"
        
        elif check["check"] == "file_generated":
            passed = bool(re.search(r'\.pptx', content))
            evidence = "PPTX output referenced" if passed else "No .pptx output file"
        
        elif check["check"] == "valid_pptx":
            passed = ptx_valid > 0
            evidence = f"{ptx_valid} valid PPTX found" if passed else "No valid PPTX detected"
        
        elif check["check"] == "reports_failure_honestly":
            passed = "error" in content.lower()[:300] or "failed" in content.lower()[:300]
            evidence = "Failure detail present" if passed else "No failure introspection"
        
        elif check["check"] == "no_defensive_disclaimers":
            defensive = ["this might not work", "i cannot guarantee", "i could be wrong"]
            passed = not any(d in content.lower() for d in defensive)
            evidence = "Clean" if passed else "Defensive language detected"
        
        elif check["check"] == "no_false_success":
            has_fatal = bool(re.search(r'(Traceback|FAIL|\\bError\\b|Failed|corrupt|CORRUPT)', content[:500]))
            claims_ok = bool(re.search(r"(generated|completed|saved|success)", content, re.I))
            passed = not (has_fatal and claims_ok)
            evidence = "Consistent" if passed else "Claims success but fatal errors present"
        
        elif check["check"] == "gold_accent_used":
            passed = "#D4AF37" in content or "gold" in content.lower()
            evidence = "Gold accent pattern referenced" if passed else "Missing gold accent reference"
        
        elif check["check"] == "card_pattern":
            passed = "card" in content.lower() and ("gold" in content.lower() or "left" in content.lower())
            evidence = "Card + accent pattern found" if passed else "Missing card layout pattern"
        
        elif check["check"] == "slide_count":
            counts = re.findall(r'(\d+)\s*(?:slide|页|slides)', content, re.I)
            passed = any(int(c) >= 3 for c in counts) if counts else False
            evidence = f"Slides: {counts}" if counts else "No slide count found"
        
        else:
            evidence = "Unknown check: " + check["check"]
        
        results[cid] = {"passed": passed, "evidence": evidence}
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grader.py <output-file> [checks_json]")
        sys.exit(1)
    filepath = sys.argv[1]
    checks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [
        {"text": "Script ran", "check": "script_ran_successfully"},
        {"text": "PPTX output", "check": "file_generated"},
    ]
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

#!/usr/bin/env python3
"""Grader for multilingual-video-voice-workflow. Checks voice package outputs."""

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
        
        if check["check"] == "script_ran_successfully":
            passed = "error" not in content.lower()[:500] or "completed" in content.lower()
            evidence = "No fatal error detected" if passed else "Script error found"
        
        elif check["check"] == "manifest_created":
            passed = "manifest" in content.lower()
            evidence = "Manifest referenced" if passed else "Missing manifest reference"
        
        elif check["check"] == "mp3_files_generated":
            passed = "mp3" in content.lower() and ("tts" in content.lower() or "voice" in content.lower())
            evidence = "MP3 + voice references found" if passed else "Missing MP3 references"
        
        elif check["check"] == "srt_files_generated":
            passed = "srt" in content.lower()
            evidence = "SRT files referenced" if passed else "Missing SRT references"
        
        elif check["check"] == "bilingual_review_created":
            passed = "bilingual" in content.lower() or "review" in content.lower()
            evidence = "Bilingual review found" if passed else "Missing bilingual review"
        
        elif check["check"] == "pronunciation_protected":
            passed = re.search(r'protected|preserv|保留|不变|keep|protect', content, re.I) is not None
            evidence = "Protected terms handling mentioned" if passed else "No protection mention"
        
        elif check["check"] == "cleaned_input_created":
            passed = "cleaned" in content.lower() or "cleaned_input" in content.lower()
            evidence = "Cleaned input file mentioned" if passed else "Missing cleaned input"
        
        elif check["check"] == "two_stage_workflow":
            passed = "stage 1" in content.lower() or "stage 2" in content.lower() or "prepare" in content.lower()
            evidence = "Two-stage workflow referenced" if passed else "Missing stage separation"
        
        elif check["check"] == "output_directory_listed":
            passed = "output" in content.lower() or "目录" in content
            evidence = "Output directory mentioned" if passed else "Missing output directory"
        
        elif check["check"] == "three_voices":
            passed = content.lower().count("voice") >= 2 or "3" in content
            evidence = "Multiple voices mentioned" if passed else "Missing voice count"
        
        elif check["check"] == "chinese_reference_srt":
            passed = "zh-cn" in content.lower() or "chinese reference" in content.lower() or "中文参考" in content
            evidence = "Chinese reference SRT mentioned" if passed else "Missing CN reference SRT"
        
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
        {"text": "Script ran", "check": "script_ran_successfully"},
        {"text": "Manifest", "check": "manifest_created"},
        {"text": "MP3 files", "check": "mp3_files_generated"},
        {"text": "SRT files", "check": "srt_files_generated"},
    ]
    
    results = check_output(filepath, checks)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    all_pass = all(r["passed"] for r in results.values())
    sys.exit(0 if all_pass else 1)

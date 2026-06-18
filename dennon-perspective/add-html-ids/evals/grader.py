#!/usr/bin/env python3
"""
add-html-ids harness grader — verifies script output against assertions.
Usage: python3 grader.py <output_file> '<checks_json>'
Checks are specific to the IDs-only nature of the skill.
"""
import json
import re
import os
import sys


def check_output(output_path: str, checks_json: str):
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = json.loads(checks_json)
    results = []

    for check in checks:
        check_name = check.get("check", "unknown")
        passed = False
        evidence = ""

        # --- IDs added (count increased) ---
        if check_name == "id_count_increased":
            min_expected = check.get("min", 1)
            ids = re.findall(r'id="([^"]*)"', content)
            ids += re.findall(r"id='([^']*)'", content)
            passed = len(ids) >= min_expected
            evidence = f"{len(ids)} IDs found (need >= {min_expected})" if passed else f"Only {len(ids)} IDs (need >= {min_expected})"

        # --- All IDs follow prefix convention ---
        elif check_name == "all_ids_have_prefix":
            prefix = check.get("prefix", "")
            ids = re.findall(r'id="([^"]*)"', content)
            ids += re.findall(r"id='([^']*)'", content)
            nonconforming = [i for i in ids if not i.startswith(prefix)]
            passed = len(nonconforming) == 0
            evidence = f"All {len(ids)} IDs start with '{prefix}'" if passed else f"{len(nonconforming)} non-conforming: {nonconforming[:5]}"

        # --- No duplicate IDs ---
        elif check_name == "no_duplicate_ids":
            ids = re.findall(r'id="([^"]*)"', content)
            ids += re.findall(r"id='([^']*)'", content)
            dupes = [i for i in sorted(set(ids)) if ids.count(i) > 1]
            passed = len(dupes) == 0
            evidence = f"No duplicates among {len(ids)} IDs" if passed else f"Duplicates: {dupes}"

        # --- Convention-following IDs preserved ---
        elif check_name == "convention_ids_preserved":
            must_have = check.get("must_have", [])
            ids = re.findall(r'id="([^"]*)"', content)
            ids += re.findall(r"id='([^']*)'", content)
            missing = [m for m in must_have if m not in ids]
            passed = len(missing) == 0
            evidence = f"All {len(must_have)} preserved" if passed else f"Missing: {missing}"

        # --- Non-conforming IDs replaced ---
        elif check_name == "nonconforming_ids_replaced":
            must_not_have = check.get("must_not_have", [])
            ids = re.findall(r'id="([^"]*)"', content)
            ids += re.findall(r"id='([^']*)'", content)
            still_there = [n for n in must_not_have if n in ids]
            passed = len(still_there) == 0
            evidence = f"All non-conforming IDs removed" if passed else f"Still present: {still_there}"

        # --- React components skipped (no uppercase-tag IDs added) ---
        elif check_name == "react_components_skipped":
            uppercase_ids = re.findall(r'id="([A-Z][^"]*)"', content)
            uppercase_ids += re.findall(r"id='([A-Z][^']*)'", content)
            passed = len(uppercase_ids) == 0
            evidence = "No uppercase-prefixed IDs (React components skipped)" if passed else f"Found: {uppercase_ids}"

        # --- No masking markers leaked ---
        elif check_name == "no_str_markers_leaked":
            has_markers = '\x00STR\x00' in content
            passed = not has_markers
            evidence = "No STR markers found" if passed else "STR markers leaked into output"

        # --- Script/style content uncorrupted ---
        elif check_name == "script_style_uncorrupted":
            script_zones = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
            style_zones = re.findall(r'<style>(.*?)</style>', content, re.DOTALL)
            corrupted = []
            for zone in script_zones + style_zones:
                if '\x00STR\x00' in zone:
                    corrupted.append("STR marker in script/style")
                if zone.count('{') != zone.count('}'):
                    corrupted.append("Unbalanced braces in script")
            passed = len(corrupted) == 0
            evidence = "Script/style content intact" if passed else f"Corruption: {corrupted}"

        # --- Apostrophe in text content preserved ---
        elif check_name == "apostrophe_preserved":
            required = check.get("must_have", ["world's"])
            missing = [r for r in required if r not in content]
            passed = len(missing) == 0
            evidence = f"All required text preserved" if passed else f"Missing: {missing}"

        # --- Original text content preserved ---
        elif check_name == "original_text_preserved":
            required = check.get("must_have", [])
            missing = [r for r in required if r not in content]
            passed = len(missing) == 0
            evidence = f"All {len(required)} text snips present" if passed else f"Missing: {missing}"

        else:
            evidence = f"Unknown check: {check_name}"

        results.append({
            "text": check_name,
            "passed": passed,
            "evidence": evidence
        })

    return json.dumps(results, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 grader.py <output_file> '<checks_json>'")
        sys.exit(1)
    print(check_output(sys.argv[1], sys.argv[2]))

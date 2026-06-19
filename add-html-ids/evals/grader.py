#!/usr/bin/env python3
"""
add-html-ids harness grader — verifies script output against assertions.
Usage: python3 grader.py <output_file> '<checks_json>'
Checks are specific to the IDs-only nature of the skill.
"""
import json
import re
import sys
from collections import Counter


ID_ATTR_RE = re.compile(r'\sid\s*=\s*(["\'])([^"\']*)\1')


def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_ids(text: str):
    return [m.group(2) for m in ID_ATTR_RE.finditer(text)]


def strip_id_attrs(text: str) -> str:
    return ID_ATTR_RE.sub('', text)


def uppercase_component_id_tags(text: str):
    return re.findall(r'<([A-Z][A-Za-z0-9_.]*)(?=[\s/>])[^>]*\sid\s*=', text)


def first_diff_index(left: str, right: str) -> int:
    for i, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return i
    if len(left) != len(right):
        return min(len(left), len(right))
    return -1


def check_output(output_path: str, checks_json: str):
    content = read_text(output_path)

    checks = json.loads(checks_json)
    results = []

    for check in checks:
        check_name = check.get("check", "unknown")
        passed = False
        evidence = ""

        # --- IDs added (count increased) ---
        if check_name == "id_count_increased":
            min_expected = check.get("min", 1)
            ids = extract_ids(content)
            passed = len(ids) >= min_expected
            evidence = f"{len(ids)} IDs found (need >= {min_expected})" if passed else f"Only {len(ids)} IDs (need >= {min_expected})"

        # --- New IDs follow prefix convention ---
        elif check_name == "new_ids_have_prefix":
            prefix = check.get("prefix", "")
            input_ids = set(check.get("preexisting_ids", []))
            input_path = check.get("input_path")
            if input_path:
                input_ids.update(extract_ids(read_text(input_path)))
            ids = extract_ids(content)
            new_ids = [i for i in ids if i not in input_ids]
            bad = [i for i in new_ids if not i.startswith(prefix)]
            passed = len(bad) == 0
            evidence = f"All {len(new_ids)} new IDs start with '{prefix}'" if passed else f"{len(bad)} new IDs lack prefix: {bad[:5]}"

        # --- No duplicate IDs ---
        elif check_name == "no_duplicate_ids":
            ids = extract_ids(content)
            dupes = [i for i in sorted(set(ids)) if ids.count(i) > 1]
            passed = len(dupes) == 0
            evidence = f"No duplicates among {len(ids)} IDs" if passed else f"Duplicates: {dupes}"

        # --- Existing IDs preserved ---
        elif check_name == "existing_ids_preserved":
            must_have = check.get("must_have", [])
            input_path = check.get("input_path")
            if input_path and not must_have:
                must_have = extract_ids(read_text(input_path))
            ids = extract_ids(content)
            missing = [m for m in must_have if m not in ids]
            passed = len(missing) == 0
            evidence = f"All {len(must_have)} existing IDs preserved" if passed else f"Missing: {missing}"

        # --- IDs-only delta ---
        elif check_name == "id_only_delta":
            input_path = check.get("input_path")
            if not input_path:
                passed = False
                evidence = "Missing input_path for id-only comparison"
            else:
                before = strip_id_attrs(read_text(input_path))
                after = strip_id_attrs(content)
                passed = before == after
                if passed:
                    evidence = "Before/after match exactly after removing id attributes"
                else:
                    idx = first_diff_index(before, after)
                    evidence = f"Non-id change detected near offset {idx}"

        # --- React components skipped (no uppercase-tag IDs added) ---
        elif check_name == "react_components_skipped":
            before = Counter()
            input_path = check.get("input_path")
            if input_path:
                before = Counter(uppercase_component_id_tags(read_text(input_path)))
            after = Counter(uppercase_component_id_tags(content))
            added = list((after - before).elements())
            passed = len(added) == 0
            evidence = "No new IDs added to uppercase React components" if passed else f"New component IDs on: {added}"

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

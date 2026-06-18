#!/usr/bin/env python3
"""
Layout Diversity Checker for Dennon-style articles.

Scans a markdown file and checks the four hard constraints from Step 4:
  1. At least 5 different layout types used
  2. No more than 3 consecutive plain-text paragraphs
  3. Each chapter uses at least 1 layout type different from adjacent chapters
  4. (Advisory) Each layout element serves emphasis, not decoration

Usage:
    python3 scripts/layout-check.py path/to/article.md

Exit code: 0 if all checks pass, 1 if any fail.
"""

import sys
import re

# Layout types we track
LAYOUT_TYPES = {
    'table',          # | col | col |
    'blockquote',     # > text
    'bullet_list',    # - item
    'numbered_list',  # 1. item
    'h3',             # ### title
    'bold_anchor',    # **text** (inline, counted within paragraphs)
    'callout_card',   # :::type ... :::
    'code_block',     # ``` ... ```
    'ascii_tree',     # code block used as decision tree
    'colored_emphasis', # ==text== ^^text^^ !!text!!
    'short_paragraph',# 1-sentence standalone paragraph
    'contrast',       # side-by-side comparison (marked by table with contrast data)
}


def detect_layout_type(line: str, prev_line: str = '') -> set:
    """Return the set of layout types detected in a single line."""
    types = set()
    s = line.strip()

    if not s or s == '---':
        return types

    # Table row
    if s.startswith('|') and '|' in s[1:]:
        types.add('table')
        return types

    # Blockquote
    if s.startswith('> '):
        types.add('blockquote')
        return types

    # Bullet list
    if s.startswith('- ') or s.startswith('- ['):
        types.add('bullet_list')
        return types

    # Numbered list
    if re.match(r'^\d+\.\s', s):
        types.add('numbered_list')
        return types

    # h3 subheading
    if s.startswith('### '):
        types.add('h3')
        return types

    # Code block fence
    if s.startswith('```'):
        types.add('code_block')
        return types

    # Callout card
    if s.startswith(':::') and not s.startswith('``'):
        types.add('callout_card')
        return types

    # Colored emphasis markers
    if '==' in s or '^^' in s or '!!' in s:
        types.add('colored_emphasis')

    # Bold anchors (inline)
    if '**' in s:
        types.add('bold_anchor')

    # Short paragraph (standalone, <60 chars, not a heading)
    if (len(s) < 60 and not s.startswith('#') and not s.startswith('|')
            and not s.startswith('>') and not s.startswith('- ')
            and not re.match(r'^\d+\.\s', s) and not s.startswith('```')):
        types.add('short_paragraph')

    return types


def get_chapter_name(line: str) -> str:
    """Extract chapter name from an ## heading."""
    s = line.strip()
    if s.startswith('## '):
        return s[3:].strip()
    return ''


def check_file(filepath: str) -> bool:
    """Run all checks on the file. Return True if all pass."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # --- Parse structure ---
    chapters = []           # [(name, start_line_index)]
    line_layout = []        # layout types per line (sets)
    line_type = []          # 'text' or 'layout'

    current_chapter = '__intro__'
    chapters.append((current_chapter, 0))

    for i, line in enumerate(lines):
        cn = get_chapter_name(line)
        if cn:
            current_chapter = cn
            chapters.append((current_chapter, i))

        lt = detect_layout_type(line, lines[i-1] if i > 0 else '')
        line_layout.append(lt)

        s = line.strip()
        if not s or s == '---':
            line_type.append('blank')
        elif lt:
            line_type.append('layout')
        else:
            line_type.append('text')

    # --- Check 1: Global layout type count ---
    global_types = set()
    for lt in line_layout:
        global_types.update(lt)

    total_types = len(global_types)
    print(f'\n  [Check 1] Layout types used: {total_types}')
    for t in sorted(global_types):
        print(f'    + {t}')
    check1 = total_types >= 5
    print(f'    -> {"PASS" if check1 else "FAIL"} (need >=5)')

    # --- Check 2: Max consecutive text paragraphs ---
    max_consec = 0
    current_consec = 0
    for t in line_type:
        if t == 'text':
            current_consec += 1
            max_consec = max(max_consec, current_consec)
        elif t == 'layout':
            current_consec = 0
        # blank lines don't reset the counter (they separate paragraphs within same block)

    check2 = max_consec <= 3
    print(f'\n  [Check 2] Max consecutive text paragraphs: {max_consec}')
    print(f'    -> {"PASS" if check2 else "FAIL"} (must be <=3)')

    # --- Check 3: Adjacent chapter layout diversity ---
    # Build per-chapter layout types
    chapter_layouts = []
    for idx, (ch_name, ch_start) in enumerate(chapters):
        ch_end = chapters[idx + 1][1] if idx + 1 < len(chapters) else len(lines)
        ch_types = set()
        for i in range(ch_start, ch_end):
            ch_types.update(line_layout[i])
        chapter_layouts.append((ch_name, ch_types))

    failures_adjacent = []
    for i in range(len(chapter_layouts) - 1):
        name_a, types_a = chapter_layouts[i]
        name_b, types_b = chapter_layouts[i + 1]

        # Each chapter must have at least one layout type not in the adjacent one
        a_unique = types_a - types_b
        b_unique = types_b - types_a

        if not a_unique and not b_unique:
            failures_adjacent.append((name_a, name_b))

    check3 = len(failures_adjacent) == 0
    print(f'\n  [Check 3] Adjacent chapter diversity:')
    if failures_adjacent:
        for a, b in failures_adjacent:
            print(f'    FAIL: "{a}" and "{b}" have identical layout profiles')
    else:
        print(f'    PASS — all adjacent chapters differ in layout')
    print(f'    -> {"PASS" if check3 else "FAIL"}')

    # --- Summary ---
    all_pass = check1 and check2 and check3
    print(f'\n  {"=" * 40}')
    print(f'  OVERALL: {"ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED"}')
    print(f'  {"=" * 40}')

    return all_pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/layout-check.py <markdown-file>')
        sys.exit(1)
    success = check_file(sys.argv[1])
    sys.exit(0 if success else 1)

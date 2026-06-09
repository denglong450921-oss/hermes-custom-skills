#!/usr/bin/env python3
"""
Add meaningful HTML IDs to all JSX/TSX elements in a .tsx or .jsx file.
Usage: python3 add_tsx_ids.py <path/to/file.tsx> [--prefix custom_prefix]
"""
import os
import re
import argparse

SKIP_FROM_CONTEXT = {'div', 'span', 'form', 'label'}


def get_prefix(filepath):
    basename = os.path.basename(filepath)
    name, _ = os.path.splitext(basename)
    if name in ('index', 'page'):
        parent = os.path.basename(os.path.dirname(os.path.abspath(filepath)))
        name = parent
    prefix = re.sub(r'[^a-zA-Z0-9]', '_', name).lower()
    prefix = re.sub(r'_+', '_', prefix).strip('_')
    return prefix + '_'


def hint_from_attrs(attrs_str):
    pats = [
        (r'aria-label\s*=\s*["\']([^"\']+)["\']', False),
        (r'title\s*=\s*["\']([^"\']+)["\']', False),
        (r'alt\s*=\s*["\']([^"\']+)["\']', False),
        (r'name\s*=\s*["\']([^"\']+)["\']', False),
        (r'placeholder\s*=\s*["\']([^"\']+)["\']', False),
        (r'className\s*=\s*["\']([^"\']+)["\']', True),
    ]
    for pat, is_class in pats:
        m = re.search(pat, attrs_str)
        if m:
            val = m.group(1)
            if is_class:
                classes = val.split()
                # Filter out stop words and versioned/framework classes (e.g. "ecwid-v19-hero")
                skip_classes = {'container', 'wrapper', 'inner', 'content', 'flex', 'grid'}
                meaningful = [c for c in classes
                              if c not in skip_classes
                              and not re.search(r'[a-z]+-v\d+', c)]
                val = max(meaningful, key=len) if meaningful else None
                if not val:
                    continue
            clean = re.sub(r'[^a-zA-Z0-9_-]', '', val.replace(' ', '-'))
            if clean:
                return clean.lower().strip('-').replace('-', '_')
    return None


def has_attr(attrs_str, attr_name):
    return bool(re.search(r'(?<![a-zA-Z0-9_-])' + re.escape(attr_name) + r'\s*(?:=|(?:\s|/?>|$))', attrs_str))


# Pre-process: replace string contents with markers to simplify tag parsing
STRING_MARKER = '\x00STR\x00'


def mask_strings(text):
    """Replace string literal contents with markers, return (masked, [originals])"""
    parts = []
    originals = []
    i = 0
    while i < len(text):
        # Skip comments
        if text[i:i+2] == '//':
            end = text.find('\n', i)
            if end == -1: end = len(text)
            parts.append(text[i:end])
            i = end
            continue
        if text[i:i+2] == '/*':
            end = text.find('*/', i+2)
            if end == -1: end = len(text)
            parts.append(text[i:end+2])
            i = end + 2
            continue
        if text[i:i+3] == '{/*':
            end = text.find('*/}', i+3)
            if end == -1: end = len(text)
            parts.append(text[i:end+3])
            i = end + 3
            continue

        quote = None
        if text[i] in ('"', "'", '`'):
            quote = text[i]

        if quote:
            start = i
            i += 1
            s = ''
            while i < len(text):
                if text[i] == '\\' and i+1 < len(text):
                    s += text[i:i+2]
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    s += text[i]
                    i += 1
            originals.append(quote + s + quote)
            parts.append(f'{STRING_MARKER}{len(originals)-1}{STRING_MARKER}')
        else:
            parts.append(text[i])
            i += 1

    return ''.join(parts), originals


def unmask_strings(text, originals):
    for idx, orig in enumerate(originals):
        text = text.replace(f'{STRING_MARKER}{idx}{STRING_MARKER}', orig)
    return text


def find_jsx_tags(masked):
    """Find all JSX tag positions in masked content. Returns list of (start, end, tag_name, attrs_str, self_closing)."""
    tags = []
    i = 0
    while i < len(masked):
        if masked[i] != '<':
            i += 1
            continue

        # Skip TypeScript generics: if preceded by identifier/), it's a generic not JSX
        if i > 0 and re.search(r'[a-zA-Z0-9_)\]]', masked[i-1]):
            i += 1
            continue

        # Skip closing tags
        if i+1 < len(masked) and masked[i+1] == '/':
            i += 2
            continue

        # Skip fragments and comment-like
        if i+1 < len(masked) and masked[i+1] in ('>', '!', '?'):
            i += 2
            continue

        # Find tag name
        m = re.match(r'<([a-zA-Z_][a-zA-Z0-9_.]*)', masked[i:])
        if not m:
            i += 1
            continue

        tag_name = m.group(1)
        pos = i + m.end()
        start = i

        # Parse attributes until > or />
        depth = 0
        self_closing = False
        end_pos = -1

        while pos < len(masked):
            c = masked[pos]
            if c == '>':
                end_pos = pos + 1
                break
            elif c == '/' and pos+1 < len(masked) and masked[pos+1] == '>':
                self_closing = True
                end_pos = pos + 2
                break
            elif c == '{':
                # Skip balanced braces
                stack = 1
                pos += 1
                while pos < len(masked) and stack > 0:
                    if masked[pos] == '{': stack += 1
                    elif masked[pos] == '}': stack -= 1
                    elif masked[pos] == STRING_MARKER[0]:
                        # Skip a marker
                        end_m = masked.find(STRING_MARKER, pos+1)
                        if end_m != -1:
                            pos = end_m + len(STRING_MARKER)
                            continue
                    pos += 1
            else:
                pos += 1

        if end_pos == -1:
            i += 1
            continue

        attrs_str = masked[start + len(tag_name) + 1: end_pos - (2 if self_closing else 1)]
        tags.append((start, end_pos, tag_name, attrs_str.strip(), self_closing))
        i = end_pos

    return tags


def process_tsx(content, prefix):
    masked, originals = mask_strings(content)
    tags = find_jsx_tags(masked)

    # Initialize seen_ids with existing convention-following IDs
    existing_ids = set()
    for m in re.finditer(r'id\s*=\s*["\']([^"\']+)["\']', content):
        existing_ids.add(m.group(1))
    seen_ids = {id for id in existing_ids if id.startswith(prefix)}
    result = list(masked)

    # Forward pass: find elements needing IDs
    tag_info = []  # (start, tag_name, id_str)
    tags_fwd = sorted(tags, key=lambda t: t[0])

    for start, end, tag_name, attrs_str, self_closing in tags_fwd:
        if not tag_name or tag_name.startswith('_'):
            continue

        # Skip React components (capitalized) — they may not accept id prop
        if tag_name[0].isupper():
            continue

        # Already has convention-following id — preserve
        if has_attr(attrs_str, 'id'):
            # Check if existing id follows convention (id value is masked, but
            # we stripped non-conforming IDs in the pre-processing step, so any
            # remaining id= must be a convention-following one)
            continue

        # Generate id — flat naming (no parent context chain)
        # Unmask attrs_str for hint extraction (attribute values are masked)
        unmasked_attrs = unmask_strings(attrs_str, originals)
        hint = hint_from_attrs(unmasked_attrs)
        el_name = hint or tag_name
        if tag_name == 'a' and not hint:
            href_m = re.search(r'href\s*=\s*["\']([^"\']+)["\']', unmasked_attrs)
            if href_m:
                href = href_m.group(1)
                el_name = re.sub(r'[^a-zA-Z0-9_-]', '', href.split('/')[-1] or href.split('/')[-2] or 'link') or 'link'

        el_name = re.sub(r'[^a-z0-9_-]', '', el_name.lower()).strip('-_')
        if not el_name:
            el_name = tag_name.lower()

        id_str = f"{prefix}{el_name}"
        id_str = re.sub(r'_+', '_', id_str).strip('_')

        if id_str in seen_ids:
            c = 2
            while f"{id_str}_{c}" in seen_ids:
                c += 1
            id_str = f"{id_str}_{c}"
        seen_ids.add(id_str)

        tag_info.append((start, tag_name, id_str))

    # Apply IDs in reverse
    for start, tag_name, id_str in reversed(tag_info):
        insert_pos = start + len(tag_name) + 1
        result.insert(insert_pos, f' id="{id_str}"')

    output = ''.join(result)
    output = unmask_strings(output, originals)
    return output


def main():
    parser = argparse.ArgumentParser(description='Add JSX IDs to .tsx/.jsx files')
    parser.add_argument('filepath', help='Path to .tsx or .jsx file')
    parser.add_argument('--prefix', help='Custom prefix (overrides filename detection)')
    args = parser.parse_args()

    prefix = args.prefix if args.prefix else get_prefix(args.filepath)

    with open(args.filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pre-process: strip non-conforming existing id attributes
    # (id values that don't start with the prefix)
    _nonconf_pat = re.compile(
        r'\s+id\s*=\s*(["\'])(?!' + re.escape(prefix) + r')[^"\']+\1'
    )
    content = _nonconf_pat.sub('', content)

    result = process_tsx(content, prefix)

    with open(args.filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    count_before = content.count(' id="') + content.count(" id='")
    count_after = result.count(' id="') + result.count(" id='")
    added = count_after - count_before
    print(f"Done. Prefix: '{prefix}', Total IDs: {count_after} ({added} added)")


if __name__ == '__main__':
    main()

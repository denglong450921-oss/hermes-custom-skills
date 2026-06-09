#!/usr/bin/env python3
"""
Add meaningful HTML IDs to all elements in an HTML file.
Usage: python3 add_html_ids.py <path/to/file.html> [--prefix custom_prefix]

Uses flat naming: {prefix}_{hint} — no parent-context chains.
"""
import os
import re
import argparse

STR = '\x00STR\x00'


def get_prefix(filepath):
    basename = os.path.basename(filepath)
    name, _ = os.path.splitext(basename)
    if name == 'index':
        parent = os.path.basename(os.path.dirname(os.path.abspath(filepath)))
        name = parent
    prefix = re.sub(r'[^a-zA-Z0-9]', '_', name).lower()
    prefix = re.sub(r'_+', '_', prefix).strip('_')
    return prefix + '_'


def mask_strings(text):
    parts = []
    originals = []
    i = 0
    in_tag = False
    in_script = False
    in_style = False
    while i < len(text):
        if text[i:i+4] == '<!--':
            end = text.find('-->', i+4)
            if end == -1: end = len(text)
            parts.append(text[i:end+3])
            i = end + 3
            continue

        if text[i] == '<':
            # Inside script/style: only detect closing tags
            if in_script:
                if text[i:i+9] == '</script>':
                    in_script = False
                parts.append('<')
                i += 1
                continue
            if in_style:
                if text[i:i+8] == '</style>':
                    in_style = False
                parts.append('<')
                i += 1
                continue
            # Normal HTML context — entering a tag
            in_tag = True
            if text[i:i+8] == '<script>':
                in_script = True
            elif text[i:i+7] == '<style>':
                in_style = True
            parts.append('<')
            i += 1
            continue

        if text[i] == '>':
            in_tag = False
            parts.append('>')
            i += 1
            continue

        if text[i] in ('"', "'"):
            # Only mask quotes that are string delimiters:
            # inside HTML tags (attributes) or inside script/style
            if in_tag or in_script or in_style:
                q = text[i]
                i += 1
                s = ''
                while i < len(text):
                    if text[i] == '\\' and i+1 < len(text):
                        s += text[i:i+2]; i += 2
                    elif text[i] == q:
                        i += 1; break
                    else:
                        s += text[i]; i += 1
                originals.append(q + s + q)
                parts.append(f'{STR}{len(originals)-1}{STR}')
            else:
                # In text content — apostrophe, not a string delimiter
                parts.append(text[i])
                i += 1
            continue

        else:
            parts.append(text[i])
            i += 1
    return ''.join(parts), originals


def unmask(text, originals):
    for idx, orig in enumerate(originals):
        text = text.replace(f'{STR}{idx}{STR}', orig)
    return text


def hint_from_attrs(attrs_str):
    pats = [
        (r'aria-label\s*=\s*["\']([^"\']+)["\']', False),
        (r'title\s*=\s*["\']([^"\']+)["\']', False),
        (r'alt\s*=\s*["\']([^"\']+)["\']', False),
        (r'name\s*=\s*["\']([^"\']+)["\']', False),
        (r'placeholder\s*=\s*["\']([^"\']+)["\']', False),
        (r'class\s*=\s*["\']([^"\']+)["\']', True),
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


def has_attr(attrs_str, name):
    return bool(re.search(r'(?<![a-zA-Z0-9_-])' + re.escape(name) + r'\s*(?:=|(?:\s|/?>|$))', attrs_str))


def find_tags(masked):
    tags = []
    i = 0
    while i < len(masked):
        if masked[i] != '<':
            i += 1
            continue
        if i+1 >= len(masked):
            break
        c = masked[i+1]
        if c == '/':
            i += 2
            continue
        if c in ('!', '?'):
            end = masked.find('>', i)
            i = end + 1 if end != -1 else len(masked)
            continue
        m = re.match(r'<([a-zA-Z_][a-zA-Z0-9_.]*)', masked[i:])
        if not m:
            i += 1
            continue
        tag_name = m.group(1)
        pos = i + m.end()
        start = i
        self_closing = False
        end_pos = -1
        while pos < len(masked):
            cc = masked[pos]
            if cc == '>':
                end_pos = pos + 1
                break
            elif cc == '/' and pos+1 < len(masked) and masked[pos+1] == '>':
                self_closing = True
                end_pos = pos + 2
                break
            elif cc in ('"', "'"):
                q = cc
                pos += 1
                while pos < len(masked):
                    if masked[pos] == '\\' and pos+1 < len(masked):
                        pos += 2; continue
                    if masked[pos] == q:
                        break
                    pos += 1
            pos += 1
        if end_pos == -1:
            i += 1
            continue
        void_tags = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
        attrs_str = masked[start + len(tag_name) + 1: end_pos - (2 if self_closing else 1)].strip()
        tags.append((start, end_pos, tag_name, attrs_str, self_closing or tag_name in void_tags))
        i = end_pos
    return tags


def process_html(content, prefix):
    masked, originals = mask_strings(content)

    # Replace script/style/template BODY with spaces in a COPY of the masked content
    # for tag-finding, so JavaScript < operators inside <script> aren't mistaken for
    # HTML tags.  Positions stay aligned (spaces preserve length).
    masked_for_tags = list(masked)
    for tag in ('script', 'style', 'template'):
        search_from = 0
        while True:
            start_tag = masked.find(f'<{tag}', search_from)
            if start_tag == -1:
                break
            gt_pos = masked.find('>', start_tag)
            if gt_pos == -1:
                break
            end_tag = masked.find(f'</{tag}>', gt_pos + 1)
            if end_tag == -1:
                break
            # Replace body (between > and </tag>) with spaces of same length
            body_start = gt_pos + 1
            body_end = end_tag
            for j in range(body_start, body_end):
                masked_for_tags[j] = ' '
            search_from = end_tag + len(f'</{tag}>')
    masked_for_tags = ''.join(masked_for_tags)

    tags = find_tags(masked_for_tags)
    # Initialize seen_ids with existing convention-following IDs
    existing_ids = set()
    for m in re.finditer(r'id\s*=\s*["\']([^"\']+)["\']', content):
        existing_ids.add(m.group(1))
    seen_ids = {id for id in existing_ids if id.startswith(prefix)}
    result = list(masked)
    tags_fwd = sorted(tags, key=lambda t: t[0])
    to_insert = []  # (start, tag_name, id_str)
    for start, end, tag_name, attrs_str, self_closing in tags_fwd:
        if not tag_name or tag_name.startswith('_'):
            continue
        # Already has convention-following id — preserve
        if has_attr(attrs_str, 'id'):
            # Non-conforming IDs were stripped in pre-processing, so any
            # remaining id= must be convention-following
            continue
        # Unmask attrs_str for hint extraction (attribute values are masked)
        unmasked_attrs = unmask(attrs_str, originals)
        hint = hint_from_attrs(unmasked_attrs)
        el_name = hint or tag_name
        if tag_name == 'a' and not hint:
            hm = re.search(r'href\s*=\s*["\']([^"\']+)["\']', unmasked_attrs)
            if hm:
                href = hm.group(1)
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
        to_insert.append((start, tag_name, id_str))
    for start, tag_name, id_str in reversed(to_insert):
        result.insert(start + len(tag_name) + 1, f' id="{id_str}"')
    output = ''.join(result)
    output = unmask(output, originals)
    return output


def main():
    parser = argparse.ArgumentParser(description='Add HTML IDs to all elements')
    parser.add_argument('filepath', help='Path to HTML file')
    parser.add_argument('--prefix', help='Custom prefix')
    args = parser.parse_args()
    prefix = args.prefix if args.prefix else get_prefix(args.filepath)
    with open(args.filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Pre-process: strip non-conforming existing id attributes
    _nonconf_pat = re.compile(
        r'\s+id\s*=\s*(["\'])(?!' + re.escape(prefix) + r')[^"\']+\1'
    )
    content = _nonconf_pat.sub('', content)
    result = process_html(content, prefix)
    with open(args.filepath, 'w', encoding='utf-8') as f:
        f.write(result)
    count_before = content.count(' id="') + content.count(" id='")
    count_after = result.count(' id="') + result.count(" id='")
    print(f"Done. Prefix: '{prefix}', Total IDs: {count_after} ({count_after - count_before} added)")


if __name__ == '__main__':
    main()

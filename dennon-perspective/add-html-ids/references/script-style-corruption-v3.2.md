# Script/style corruption (v3.2 fix)

## The bug

The HTML script (`add_html_ids.py`) silently corrupted inline `<script>` and
`<style>` tag content. Two independent root causes:

### Root 1: Apostrophe in text content → mask_strings eats everything

An apostrophe like `world's` in HTML text content (outside any tag) was treated
by `mask_strings` as a `'` string delimiter. The function would "mask" from that
apostrophe until the next `'` — which could be thousands of characters later,
consuming `<script>` and `<style>` tags, large chunks of HTML, and more.

**Diagnosis**: The masked content was ~16KB vs ~33KB original — nearly half the
file was consumed by a single open quote. The `<script>` tag was completely
absent from the masked content, so tag-finding and exclusion logic failed.

**Fix**: `mask_strings` is now context-aware. State machine tracks:
- `in_tag` (between `<` and `>`) — mask quotes as string delimiters
- `in_script` (inside `<script>` body) — mask quotes as JS string delimiters
- `in_style` (inside `<style>` body) — mask quotes as CSS string delimiters
- None of the above (text content) — pass quotes through unchanged

The closing `</script>` and `</style>` tags are detected from within the
`in_script`/`in_style` states so the flags get cleared.

### Root 2: JavaScript `<` operators → find_tags inserts IDs into JS code

Inside `<script>` tags, JavaScript code has `<` operators like `i < total`,
`dx < 0`. The `find_tags` function treated these as HTML opening tags and
generated fake tag entries (e.g. `<total`, `<0`). The script then inserted
`id="present_total"` etc. at those positions inside the JavaScript code,
corrupting it.

**Diagnosis**: The final output had leaked STR markers inside JavaScript code
and unbalanced braces/parens. The `toggle` line went from
`d.classList.toggle('active', i === current);` to a corrupted string with
markers and inserted content.

**Fix**: Before calling `find_tags`, create a copy of the masked content where
the body of every `<script>`, `<style>`, and `<template>` tag is replaced with
same-length spaces. `find_tags` runs on this sanitized copy and never sees the
`<` operators inside script code. The original `result = list(masked)` is used
for ID insertion (keeping the real markers), so unmasking still works correctly.

## Detection

After running `add_html_ids.py`, verify:

```python
with open(file) as f:
    c = f.read()
# Check script/style integrity
for tag in ('script', 'style'):
    for m in re.finditer(rf'<{tag}>.*?</{tag}>', c, re.DOTALL):
        if '\x00STR\x00' in m.group(0):
            print(f'LEAK in {tag}!')
s = c.find('<script>')
e = c.find('</script>', s)
js = c[s+8:e]
print(f'Braces: {js.count("{")} vs {js.count("}")}')
print(f'Parens: {js.count("(")} vs {js.count(")")}')
```

## Prevention

Any change to `mask_strings` or `find_tags` must test with an HTML file that
has:
1. An apostrophe in text content (`it's`, `world's`, `don't`)
2. An inline `<script>` tag with `<` comparison operators
3. A `<style>` tag with CSS
3. Double-quoted, single-quoted, and backtick strings inside scripts
4. Template literals with `${...}` interpolation
 
The file `present.html` in the ecwid project has all four.

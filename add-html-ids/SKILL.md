---
name: add-html-ids
description: >
  Add meaningful, page-prefixed HTML IDs only to elements that lack IDs in HTML
  and TSX/JSX files.  Use whenever a user asks to "add IDs", "id every element",
  "add id name for every element of html/tsx", "fix missing ids", or when a
  project has HTML/React files without consistent element IDs and the user
  needs to reference elements precisely.  Also trigger when refactoring or
  extending HTML/CSS/JS/React and the lack of IDs makes targeted edits hard
  — the skill prevents the "how do I target that specific div?" problem
  before it starts.  SKIP when the user only wants to add one or two IDs
  manually — the script is for bulk/complete coverage.
---

# Add HTML / TSX IDs

## ⚠️ CRITICAL RULE: IDs ONLY — NEVER change anything else

This skill has ONE job: add `id` attributes to elements. Do NOT:

- **Change text content** — never translate, rephrase, fix spelling, or touch any text
- **Modify CSS** — never add/remove/change styles, classes, or layout
- **Fix formatting** — never adjust whitespace, indentation, line breaks, or code style
- **Add/remove elements** — never change the DOM structure
- **Fix accessibility** — never add aria-labels, alt text, or semantic elements
- **Convert syntax** — never change HTML to JSX or vice versa
- **Optimize** — never refactor, deduplicate, or "improve" the code in any way

The scripts are purpose-built to only insert `id="prefix_name"` into tags that
lack an `id` attribute. If a tag already has any `id`, preserve it byte-for-byte.
Existing IDs are live API surface for CSS, JS, anchors, tests, and analytics.
Never rename, normalize, replace, remove, or empty an existing `id`.

🛑 **STOP. If the user asks for anything beyond adding IDs** (translations, styling, formatting,
refactoring) — stop and handle it as a separate task outside this skill. Do NOT try to
"also fix that thing while I'm in there." This rule exists because multi-change runs
have caused script/style corruption, double IDs, and broken i18n in production files.

Add `{page_prefix}_{purpose}` IDs to every element that lacks an `id` in `.html`
or `.tsx`/`.jsx` files. The goal is that new targetable elements can be addressed
from CSS/JS/React without guessing, while existing page behavior remains untouched.

## When to use

- User says "add id name for every element of html" or "every element of tsx"
- User says "add ids" or "fix element ids" on a project with HTML or React files
- You're about to write CSS or JS that targets DOM elements and the HTML/JSX has no IDs or incomplete IDs
- A project uses generic HTML or JSX templates and you want to make it easier to maintain
- User says "the same applies to page.tsx" or "also works on .tsx files"

## File type detection

The skill auto-detects the file type from the extension:

| Extension | Script | Parsing approach | 
|-----------|--------|------------------|
| `.html` | `add_html_ids.py` | Regex-based (string masking preserves attribute case like `viewBox`, self-closing tags, and HTML entities) | 
| `.tsx`, `.jsx` | `add_tsx_ids.py` | Regex-based JSX parser with string masking (handles `className`, template literals, expression blocks, React components) |

## Workflow

### 1. Determine the page prefix

Derive the prefix from the filename, or accept the user's override:

| File | Prefix | Example IDs |
|------|--------|-------------|
| `index.html` in `support-site/` → `support_` | `support_header`, `support_hero_title` |
| `page.tsx` in `sell/` → `sell_` | `sell_section`, `sell_hero_h1` |
| `about.tsx` → `about_` | `about_section`, `about_team_img` |
| `checkout.tsx` → `checkout_` | `checkout_form`, `checkout_total` |

Rules:
- `index.html` / `page.tsx` → uses the **parent directory** name instead
- Other files use the filename stem (before extension)
- Strip non-alphanumeric chars, collapse underscores
- User can pass `--prefix custom_` to override

### 2. Run the bundled script

**For HTML:**
```bash
python3 /Users/f/.hermes/skills/add-html-ids/scripts/add_html_ids.py path/to/file.html
```

**For TSX/JSX:**
```bash
python3 /Users/f/.hermes/skills/add-html-ids/scripts/add_tsx_ids.py path/to/page.tsx
```

**With custom prefix (same for both):**
```bash
python3 .../add_tsx_ids.py path/to/file.tsx --prefix bkk_
```

🛑 **STOP — verify before proceeding.** After the script runs, immediately check for duplicate IDs and leaked STR markers:
```bash
python3 -c "import re,sys;c=open(sys.argv[1]).read();ids=re.findall(r'id=\"([^\"]*)\"',c);d=[i for i in sorted(set(ids)) if ids.count(i)>1];print(f'{len(d)} dupes' if d else 'No dupes');print('STR leaked' if '\x00STR\x00' in c else 'No leaks')" <file>
```
If dupes or leaks are found → don't continue. Re-run the script or patch manually.

### 3. Review the output

The script adds IDs to **every** element that doesn't already have one:

**HTML:** `<html>`, `<head>`, `<meta>`, `<title>`, `<link>`, `<script>`,
`<div>`, `<section>`, `<header>`, `<footer>`, `<main>`, `<nav>`, `<p>`,
`<h1>`-`<h6>`, `<a>`, `<img>`, `<button>`, `<input>`, `<form>`, `<label>`,
`<ul>`, `<ol>`, `<li>`, `<span>`, `<svg>`, `<path>`, `<circle>`, `<rect>`

**TSX:** Same lowercase HTML elements as HTML, JSX expression support, and
`className` attribute hints. Capitalized React component tags (`<Header />`,
`<Footer />`) are skipped unless they already had an `id`, because many
components do not accept an `id` prop.

### 4. Spot-check

- Check that React component elements (capitalized tags) did not receive new IDs
- Verify `className` was parsed correctly for naming hints
- Check nested JSX expressions (`{condition && <Tag/>}`) are covered
- Ensure no duplicate IDs (script uses counters but double-check)

🛑 **CHECKPOINT: Verify the IDs-Only rule.** Before delivering, confirm:
- No text was translated or rephrased
- No CSS styles or classes were changed
- No elements were added, removed, or restructured
- The file diff shows ONLY new `id="..."` insertions

Run `git diff` on the file and visually scan — every changed line should contain `id=`.
If any line was changed for any other reason, revert that specific change.
For a stricter check, the before/after content should match exactly after removing
all quoted `id` attributes from both versions.

## Naming conventions

IDs use **flat naming** — no parent context chain:

```
{prefix}_{element_hint}
```

Where `{element_hint}` comes from (in priority order):
1. Existing `className` / `class`, `aria-label`, `title`, `alt`, `name`, or `placeholder` attribute
2. `<a href>` → last path segment of the URL (cleaned)
3. The HTML/JSX tag name (e.g., `div`, `section`, `Header`)

All hyphens from class names are converted to underscores — final IDs use
only underscores and alphanumerics.  A class like `mobile-color-block-right`
produces `herosection_mobile_color_block_right`, never `herosession_mobile-color-block-right`.

If a sibling element would get the same ID, a numeric suffix is appended (`_2`, `_3`).

Do not rename IDs during this skill. If a user later wants semantic ID cleanup,
handle it as a separate refactor because changing existing IDs can break CSS,
JavaScript, anchors, tests, or analytics.

### Why flat naming?

Flat naming prevents absurdly long IDs caused by deep parent-context chains.
Previous context-based naming produced IDs like
`shop_site-footer_site-footer_social-links_twitter_svg_path` — long, brittle,
and hard to reference. Flat naming produces `shop_svg_path`, `shop_svg_path_2`,
etc.**, which are shorter and stable against DOM structure changes.

## Important: why TSX uses flat naming (gotchas)

The TSX script deliberately avoids parent-context chains because `.tsx` files
often define multiple React components in one file. A shared chain would cross
function boundaries and give you `home_strong_p_header_herosection` instead of
`home_header`.  The flat approach (`{prefix}_{hint}`) avoids this entirely.

Three TSX-specific gotchas the script handles automatically:

1. **TypeScript generics look like JSX** — `useRef<HTMLDivElement>(null)` uses `<`
   but it's not a tag.  The script checks the character before `<`: if it's a
   word character (`Ref`), it skips it.  If it's whitespace or `=`, it parses
   it as JSX.  This is already built in — you don't need to do anything.

2. **React components don't accept `id`** — `<Header id="home_header" />` would
   fail TypeScript if `Header` doesn't define an `id` prop.  The script skips
   any tag that starts with an uppercase letter (React component convention).
   Only lowercase HTML elements (div, section, img, input) get IDs.

3. **All existing IDs are preserved** — any existing `id=` value is kept exactly,
   even if it does not start with the page prefix (for example
   `id="mobileColorBlock"`). Only tags that lack an `id` receive a generated
   prefixed ID. This is required because existing IDs may be referenced by CSS,
   JavaScript, anchors, tests, or analytics.

## String masking pitfalls (critical for maintainers)

Both scripts mask string literal contents (class names, alt text, aria-labels)
with binary markers (`\x00STR\x00N\x00STR\x00`) before parsing tags. This keeps
the tag parser from being confused by `<` or `>` inside attribute values. But
it causes two subtle bugs that are easy to introduce:

1. **`hint_from_attrs` returns `None` on masked attrs_str** — because attribute
   values like `className="mobile-color-block-right"` are replaced with markers
   like `className=\x00STR\x0042\x00`. The regex `class\s*=\s*["\']...["\']`
   can't match `\x00` as a quote character. Always unmask the attrs_str before
   passing it to `hint_from_attrs`:
   ```python
   unmasked_attrs = unmask_strings(attrs_str, originals)
   hint = hint_from_attrs(unmasked_attrs)
   ```

2. **`id` value extraction fails on masked content** — same reason:
   `id="mobileColorBlock"` becomes `id=\x00STR\x0043\x00`. The regex
   `id\s*=\s*["\']([^"\']+)["\']` fails because the value is a marker, not a
   quoted string. Never try to read existing attribute values from masked
   content. Scan the original unmasked content to seed the full set of existing
   IDs, then use masked content only to detect whether a tag already has an
   `id` attribute.

3. **Position indices don't match masked vs. unmasked content** — markers are
   shorter than the original strings they replace, so a `start` index from
   `find_jsx_tags(masked)` does not correspond to the same position in the
   original content. Never use masked-content indices to modify unmasked content.
   Only operate on the `result = list(masked)` string, then unmask at the end.

4. **`seen_ids` must be seeded from all pre-existing IDs** — when re-running
   on an already-processed file, the `has_attr` check detects existing IDs
   correctly (via the marker) but the new-ID generator doesn't know their values.
   Initialize `seen_ids` from a regex scan of the original (unmasked) content:
   ```python
   for m in re.finditer(r'id\s*=\s*["\']([^"\']+)["\']', content):
       existing_ids.add(m.group(1))
   seen_ids = set(existing_ids)
   ```

## Changelog

- **v3.4 (2026-06-19)**: Preserve all existing IDs exactly. Scripts now only
  insert IDs into tags that lack an `id`; they never strip, replace, normalize,
  or rename existing IDs. Harness adds an `id_only_delta` check that compares
  before/after content after removing quoted `id` attributes, catching any
  non-ID text, style, layout, script, or structure changes.
- **v3.3 (2026-06-10)**: Hyphens in class names → underscores in IDs
  (`mobile-color-block-right` → `herosection_mobile_color_block_right`).
  Aligns with user's underscore-only ID convention.  Both the `hint_from_attrs`
  return path and the fallback `el_name` processing now convert `-` to `_`.
- **v3.2 (2026-06-10)**: Fixed catastrophic HTML `<script>`/`<style>` corruption.
  Two root bugs fixed in `mask_strings`: (1) Apostrophe in text content (`world's`)
  treated as string delimiter, consuming everything including `<script>` tag.
  Fix: context-aware masking — only mask quotes inside HTML tags (attributes),
  `<script>` body, and `<style>` body; text-content quotes pass through.
  (2) JavaScript `<` operators (`i < total`) mistaken for HTML tags inside
  `<script>` body, causing ID insertions that corrupt JS code.
  Fix: replace script/style/template body with same-length spaces in a copy
  of masked content used for tag-finding, so `find_tags` never sees these `<` characters.
- **v3.1 (2026-06-10)**: Fix pre-processing regex `\s*` → `\s+` to consume leading space before `id`, preventing double-space artifacts.  Filter out versioned/framework class names like `ecwid-v19-hero` from hint extraction.  Return `None` from `hint_from_attrs` when all classes filtered.
- **v3 (2026-06-10, historical)**: Earlier behavior replaced non-conforming
  existing IDs. This is superseded by v3.4 because existing IDs must be
  preserved to avoid breaking page behavior. `hint_from_attrs` now operates on
  UNMASKED attribute strings so class names, aria-labels, etc. are properly
  readable.
- **v2.1 (2026-06-09)**: HTML script also switched to flat naming — was still
  using context-based chains, producing IDs like `support_svg_path_path_path_path_a_a`
  for deeply nested elements.  Now both HTML and TSX scripts use `{prefix}_{hint}`
  flat naming.  Added `references/output-examples.md` with real before/after and
  a warning against context-based naming patterns.
- **v2 (2026-06-09)**: Swapped HTMLParser for regex (fixes `viewBox` lowercasing,
  `/>` expansion, entity decoding).  Added TSX script with `mask_strings` to
  handle string literals.  TSX uses flat naming to avoid cross-function
  context pollution.  TSX skips capitalized-component tags.

## Failure recovery table

If any issue below occurs, follow the recovery path. Don't guess — use the table.

| Trigger | First response | Fallback |
|---------|---------------|----------|
| Duplicate IDs found after run | Check whether the duplicate was pre-existing or generated. If generated, fix `seen_ids` seeding (pitfall #4). | If duplicate was pre-existing, report it and stop; do not rename it inside this skill |
| STR markers in output | String unmasking failed. Re-run script on the original file and inspect the failing tag/string boundary | Patch the script so markers are unmasked; do not remove or rewrite existing IDs as a workaround |
| Script corrupts `<script>` content | `<script>` body has unescaped `</script>` or CDATA. v3.2+ space-fill should handle normal cases | Manually wrap JS in `/*<![CDATA[*/ ... /*]]>*/` or use external .js file |
| React component gets an `id` | Component name is lowercase — script treated it as HTML. Rename component to uppercase (React convention) | Add `id` prop type to the component so TS accepts it |
| File with `src/app/page.tsx` nested 3+ deep | Prefix derivation uses immediate parent, may collide. Check other locale folders for duplicate prefixes | Pass `--prefix` override explicitly |
| `id=""` (empty) in source | Preserve it because it is an existing attribute. Report it as pre-existing bad markup if relevant | Ask for a separate cleanup/refactor before changing it |
| Node.js HTTP request in script content | `http://` or `https://` in `<script>` body triggers `<` matching in old parser. v3.2+ space-fill prevents this | If using pre-v3.2, upgrade the script

## Reference examples

See `references/output-examples.md` for real before/after outputs from all
script variants (HTML, TSX pages, TSX components, and the broken HTMLParser
approach to avoid).

## Verification

After running, verify. Use `grep -Eo` (works on both GNU/Linux and macOS
BSD grep) or Python for portable duplicate checks:

```bash
# Count IDs
grep -c 'id="' <file>

# Check for duplicates (portable: use grep -Eo, not GNU-only -oP)
grep -Eo 'id="[^"]*"' <file> | sort | uniq -d

# Check TSX (handles single quotes too)
grep -Eo "id='[^']*'" <file> | sort | uniq -d

# Python alternative (works everywhere, no grep flag differences)
python3 -c "
import re, sys
with open(sys.argv[1]) as f:
    content = f.read()
ids = re.findall(r'id=\"([^\"]*)\"', content)
ids += re.findall(r\"id='([^']*)'\", content)
dupes = [i for i in sorted(set(ids)) if ids.count(i) > 1]
if dupes:
    for d in dupes: print(f'DUPE: {d} (x{ids.count(d)})')
else:
    print(f'{len(ids)} IDs, 0 dupes')
" <file>
```

**macOS note**: `grep -oP` is GNU grep only — macOS BSD grep rejects it.
Use `grep -Eo` or the Python script instead.

## Harness (Self-Eval)

The harness validates that the scripts correctly add IDs without corrupting
content. 4 test cases cover the skill's core guarantees.

### Cases

| ID | Name | Principle Tested |
|----|------|-----------------|
| `case_001` | basic-html-no-existing-ids | ID count, new-ID prefix convention, no dupes, id-only delta |
| `case_002` | tsx-mixed-ids | Existing IDs preserved, missing lowercase JSX IDs added, React skipped |
| `case_003` | html-with-script-style | No STR markers leaked, script/style uncorrupted, apostrophe safe, id-only delta |
| `case_004` | html-preserve-existing-id-hooks | Existing CSS/anchor/JS ID hooks preserved, missing IDs added, id-only delta |

### Checks

| Check | What it detects |
|-------|----------------|
| `id_count_increased` | Output has more IDs than input (IDs actually added) |
| `new_ids_have_prefix` | Generated IDs start with the expected `{prefix}_`; pre-existing IDs may use any value |
| `no_duplicate_ids` | Zero duplicate id values in the output |
| `existing_ids_preserved` | Existing IDs remain unchanged, whether or not they match the prefix |
| `id_only_delta` | Before/after content matches exactly after removing quoted `id` attributes |
| `react_components_skipped` | No new `id` attributes are added to uppercase React component tags |
| `no_str_markers_leaked` | Output contains zero `\x00STR\x00` binary markers |
| `script_style_uncorrupted` | Script/style tag bodies have balanced braces, no markers |
| `apostrophe_preserved` | Text apostrophes (`world's`) survive masking |
| `original_text_preserved` | Key text content still present in output |

### Run

```bash
# Full harness (runs scripts on test inputs, grades output)
python3 evals/run_harness.py

# Grade a specific output file
python3 evals/grader.py <output_file> '<checks_json>'
```

### Honesty & Truthfulness

Report results exactly as they are:
- Test failed → state "failed" with the actual evidence
- Skipped verification → say "not verified", don't imply it passed
- No defensive disclaimers on correct results ("but this might not be correct")
- No false success — if output shows failure, don't claim "all passed"

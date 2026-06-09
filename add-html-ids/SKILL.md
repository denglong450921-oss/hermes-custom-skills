---
name: add-html-ids
description: >
  Add meaningful, page-prefixed HTML IDs to every element in HTML and
  TSX/JSX files.  Use whenever a user asks to "add IDs", "id every element",
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

The scripts are purpose-built to only insert `id="prefix_name"` into tags that lack one.
If a file already has IDs, the script replaces non-conforming IDs with correct ones
— that is the ONLY change allowed.

**If the user asks for anything beyond adding IDs** (translations, styling, formatting,
refactoring) — stop and handle it as a separate task outside this skill.

Add `{page_prefix}_{purpose}` IDs to every element in `.html` or `.tsx`/`.jsx` files.
The goal is that any element — `<div>`, `<Header />`, `<path>`, `<meta>`, etc. — can
be uniquely addressed from CSS/JS/React without guessing.

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

### 3. Review the output

The script adds IDs to **every** element that doesn't already have one:

**HTML:** `<html>`, `<head>`, `<meta>`, `<title>`, `<link>`, `<script>`,
`<div>`, `<section>`, `<header>`, `<footer>`, `<main>`, `<nav>`, `<p>`,
`<h1>`-`<h6>`, `<a>`, `<img>`, `<button>`, `<input>`, `<form>`, `<label>`,
`<ul>`, `<ol>`, `<li>`, `<span>`, `<svg>`, `<path>`, `<circle>`, `<rect>`

**TSX:** Same as HTML plus React component tags (`<Header />`, `<Footer />`),
JSX expression support, `className` attribute used as hint.

### 4. Spot-check

- Check that React component elements (capitalized tags) got IDs
- Verify `className` was parsed correctly for naming hints
- Check nested JSX expressions (`{condition && <Tag/>}`) are covered
- Ensure no duplicate IDs (script uses counters but double-check)

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

**After running the script, rename key structural IDs by hand** to follow the
user's preferred convention `{prefix}_{context}_{purpose}` with shorter,
more semantic names.  The auto-generated IDs provide a complete baseline —
every element has one — but important wrappers, sections, and interactive
elements should get short semantic names with context traces.

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

3. **Non-conforming existing IDs are REPLACED** — any existing `id=` value
   that doesn't start with the page prefix (e.g. `id="mobileColorBlock"` instead
   of `herosection_mobileColorBlock`) is stripped before processing, then a
   proper prefixed ID is generated.  IDs that already follow the convention
   (`id="herosection_h1"`) are preserved unchanged.  This means running the
   script on a file that already has some IDs is safe — it'll upgrade the
   stragglers without touching the good ones.

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
   quoted string. Never try to read existing attribute values from the masked
   content. Either:
   - **Pre-process** the original (unmasked) content to strip non-conforming IDs
     (v3 approach — robust, simple, recommended).
   - **Post-process** the final unmasked output with a regex to remove non-conforming
     IDs (v3.1+ could use this if pre-processing causes issues).

3. **Position indices don't match masked vs. unmasked content** — markers are
   shorter than the original strings they replace, so a `start` index from
   `find_jsx_tags(masked)` does not correspond to the same position in the
   original content. Never use masked-content indices to modify unmasked content.
   Only operate on the `result = list(masked)` string, then unmask at the end.

4. **`seen_ids` must be seeded from pre-existing convention IDs** — when
   re-running on an already-processed file, the `has_attr` check detects
   convention-following IDs correctly (via the marker) but the new-ID generator
   doesn't know about them. Initialize `seen_ids` from a regex scan of the
   original (unmasked) content:
   ```python
   for m in re.finditer(r'id\s*=\s*["\']([^"\']+)["\']', content):
       existing_ids.add(m.group(1))
   seen_ids = {id for id in existing_ids if id.startswith(prefix)}
   ```

## Changelog

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
- **v3 (2026-06-10)**: Non-conforming existing IDs are now REPLACED (previously they were silently skipped), so every element gets a convention-following ID even if it already had a custom one.  `hint_from_attrs` now operates on UNMASKED attribute strings so class names, aria-labels, etc. are properly readable.  `seen_ids` initialized from existing convention-following IDs so re-running on an already-processed file doesn't create duplicates.
- **v2.1 (2026-06-09)**: HTML script also switched to flat naming — was still
  using context-based chains, producing IDs like `support_svg_path_path_path_path_a_a`
  for deeply nested elements.  Now both HTML and TSX scripts use `{prefix}_{hint}`
  flat naming.  Added `references/output-examples.md` with real before/after and
  a warning against context-based naming patterns.
- **v2 (2026-06-09)**: Swapped HTMLParser for regex (fixes `viewBox` lowercasing,
  `/>` expansion, entity decoding).  Added TSX script with `mask_strings` to
  handle string literals.  TSX uses flat naming to avoid cross-function
  context pollution.  TSX skips capitalized-component tags.

## Current known edges

- **Always-visible UI inside responsive containers**: If the file being ID'ed
  is part of a responsive layout, check that elements you plan to target from
  CSS/JS aren't placed inside a container that gets `display: none` at certain
  breakpoints (e.g., `.site-header__desktop-actions` hides at ≤899px).  If a
  button or control needs to work at all screen sizes (like a language
  switcher), it must live OUTSIDE any responsive-hiding container.  This is a
  CSS architecture issue, not a script bug, but it commonly surfaces when
  developers rely on the new IDs to write targeting CSS/JS.
- **TSX expression blocks** (`{variable}`): The JSX parser skips balanced `{}` blocks
  that don't contain JSX tags. Review the output if the file has complex nested ternaries.
- **SVG `<path>` / `<circle>`**: Both scripts handle these. For complex SVGs with
  `<defs>`, `<use>`, or `<clipPath>`, add IDs manually.
- **Existing IDs that follow the convention are preserved** — non-conforming
  IDs (`id="myCustomId"`) are stripped and replaced with proper prefixed IDs.
- **Fragment `<>...</>`**: Skipped intentionally (can't have attributes).
- **Pre-existing duplicate IDs**: The v3+ pre-processing step strips any `id=`
  whose value doesn't start with the prefix, so many pre-existing dupes (e.g.
  copy-pasted SVGs in FAQ cards that all had the same `id="svg_icon"`) get
  cleaned up automatically — each instance gets a unique suffix (`_2`, `_3`).
  BUT: if the pre-existing dupes already follow the convention (e.g. two
  elements both have `id="header_div"`), neither is stripped and the dupes
  persist. After running, always verify with the duplicate check below and
  manually patch any surviving dupes.
- **HTML `<script>` / `<style>` content (v3.2+ SAFE)**: The HTML script now
  contextually masks quotes — only quotes inside HTML tags, `<script>` body,
  and `<style>` body are treated as string delimiters. Apostrophes in text
  content (`world's`) pass through safely. The tag-finding step replaces
  script/style/template body with same-length spaces to prevent JavaScript `<`
  operators (`i < total`) from being mistaken for HTML tags. Review only if
  the file uses non-standard script embedding (e.g. CDATA sections, XMP tags).
- **`.tsx` with custom Babel transforms**: Review edge cases if the project uses
  unusual JSX pragmas or custom element types.

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
    ids = re.findall(r'id=\"([^\"]*)\"', f.read())
    ids += re.findall(r\"id='([^']*)'\", f.read())
dupes = [i for i in sorted(set(ids)) if ids.count(i) > 1]
if dupes:
    for d in dupes: print(f'DUPE: {d} (x{ids.count(d)})')
else:
    print(f'{len(ids)} IDs, 0 dupes')
" <file>
```

**macOS note**: `grep -oP` is GNU grep only — macOS BSD grep rejects it.
Use `grep -Eo` or the Python script instead.

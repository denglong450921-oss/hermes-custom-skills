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
  before it starts.  When the user says "don't change original IDs" or
  "preserve existing IDs", use --preserve-existing mode which adds IDs
  only to elements lacking one and never renames anything.
  SKIP when the user only wants to add one or two IDs manually — the script
  is for bulk/complete coverage.
  v4.0+: Map-aware — TSX script detects .map() loops and generates
  dynamic template-literal IDs (id={`prefix_name__${key}`}) ensuring every
  runtime instance gets a unique ID.
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
- **Hardcode display text** — if the task requires NEW text (new element, new label,
  new section heading), always use the project's existing i18n system (`t("key.name")`),
  never write bare English strings. This prevents creating untranslated content that
  breaks in other locales and will get flagged by users who check translations.
- **i18n text with line breaks** — when translation values contain `\n` for structured
  content (bullet lists, address blocks), add `white-space: pre-line` to the element's
  CSS so the line breaks render correctly. Without this, `\n` appears as literal text.

The scripts are purpose-built to insert `id="prefix_name"` into tags that lack one.
The main HTML script (`add_html_ids.py`) has two modes:

- **Default mode** — replaces non-conforming existing IDs (e.g. `id="mobileCarousel"` →
  `id="herosection_mobile_carousel"`). Use for fresh files with no CSS/JS references.
- **`--preserve-existing` mode** — never touches any existing `id=`. Only adds IDs to
  elements that have none. Use when inline `<style>` blocks or JS reference the current
  IDs. Activate with: `python3 .../add_html_ids.py file.html --preserve-existing`

  For convenience, `add_ids_preserve_existing.py` is a companion script that always
  runs in preserve-existing mode (same behavior as the flag). Use whichever is more
  convenient.

Choose preserve-existing mode whenever the file has existing CSS selectors, JS
`getElementById` calls, or the user says "don't change the original IDs." The trade-off
is that non-prefixed original IDs (like `mediaCenterPageContent`) stay as-is — CSS
compatibility is preserved at the cost of naming consistency.

🛑 **STOP. If the user asks for anything beyond adding IDs** (translations, styling, formatting,
refactoring) — stop and handle it as a separate task outside this skill. Do NOT try to
"also fix that thing while I'm in there." This rule exists because multi-change runs
have caused script/style corruption, double IDs, and broken i18n in production files.

Add `{page_prefix}_{purpose}` IDs to every element in `.html` or `.tsx`/`.jsx` files.
The goal is that any element — `<div>`, `<Header />`, `<path>`, `<meta>`, etc. — can
be uniquely addressed from CSS/JS/React without guessing.

## When to use

- User says "add id name for every element of html" or "every element of tsx"
- User says "add ids" or "fix element ids" on a project with HTML or React files
- You're about to write CSS or JS that targets DOM elements and the HTML/JSX has no IDs or incomplete IDs
- A project uses generic HTML or JSX templates and you want to make it easier to maintain
- User says "the same applies to page.tsx" or "also works on .tsx files"
- User says "do not change original IDs", "preserve existing IDs", or "existing styles reference these IDs" → use the preserve-existing script in step 2 instead of the bundled script

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

**For HTML (default — replaces non-conforming existing IDs):**
```bash
python3 /Users/f/.hermes/skills/add-html-ids/scripts/add_html_ids.py path/to/file.html
```

**For HTML (preserve all existing IDs — use when inline CSS/JS reference current IDs):**
```bash
python3 /Users/f/.hermes/skills/add-html-ids/scripts/add_html_ids.py path/to/file.html --preserve-existing
```
Or use the convenience companion:
```bash
python3 /Users/f/.hermes/skills/add-html-ids/scripts/add_ids_preserve_existing.py path/to/file.html
```
This script never changes an existing `id=`: it only adds IDs to elements that lack one.
Use this when the user says "do not change original IDs" or when inline `<style>` blocks
reference the current IDs. Also use it when you cannot audit all CSS/JS references after
the script runs. The trade-off is that non-prefixed original IDs (like `mediaCenterPageContent`)
stay as-is—CSS compatibility is preserved at the cost of naming consistency.

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

**TSX:** Same as HTML plus React component tags (`<Header />`, `<Footer />`),
JSX expression support, `className` attribute used as hint.

### 4. Spot-check

- Check that React component elements (capitalized tags) got IDs
- Verify `className` was parsed correctly for naming hints
- Check nested JSX expressions (`{condition && <Tag/>}`) are covered
- Ensure no duplicate IDs (script uses counters but double-check)
- **If the file contains `.map()` loops**, check that the script generated dynamic
  template-literal IDs (`id={`prefix_name__${key}`}`) instead of static duplicates
- **Dynamic IDs CANNOT be targeted by `getElementById()`** — the runtime suffix is
  interpolated and unknown at design time. Use CSS attribute selectors instead:
  `document.querySelector('[id^="prefix_name__"]')` (starts-with match) or
  `` document.querySelector(`[id="prefix_name__${knownValue}"]) `` (exact match
  with known key value). For CSS, use `[id^="prefix_name__"]` or `[id="prefix_name__someValue"]`.
  See the failure recovery table for remediation steps.
- **After running on React components, verify TypeScript succeeds** — if a component has `id: string` in its props interface and callers don't pass `id`, the TS build will fail. See the "TSX-specific: TypeScript interface `id` prop" section below for the fix.

🛑 **CHECKPOINT: Verify the IDs-Only rule.** Before delivering, confirm:
- No text was translated or rephrased
- No CSS styles or classes were changed
- No elements were added, removed, or restructured
- The file diff shows ONLY `id="..."` insertions and old-ID replacements

**Automated check (preferred) — proves zero non-ID changes:**
```bash
cd <project-root> && git diff <file> | grep -v 'id=' | grep '^[+-]' | head -20
```
If this returns any output, those lines changed something other than `id=` — investigate and revert.

**Fallback:** Run `git diff <file>` and visually scan — every changed line should contain `id=`.
If any line was changed for any other reason, revert that specific change.

A common user concern is "don't break the CSS." The automated check above is the definitive answer: if the command returns nothing, zero style/class/text/structure changes were made.

🛑 **CHECKPOINT: Check for broken JS references.** The script replaces non-conforming
IDs (like `id="mobileCarousel"` → `id="herosection_mobile_and_tablet_in_device_carousel"`).
Any JavaScript that references the old ID via `getElementById`, `querySelector`, or CSS
`#old-id` selectors will silently break. After running, search the project for references
to any ID that was renamed:

```bash
# For each replaced ID, search project for references
grep -rn '"mobileCarousel"' src/  # old ID → update to new ID
```

🛑 **CHECKPOINT: Inline `<style>` blocks — same risk, different fix.** The script
renames IDs inside `<style>` blocks the same way it does in `<div>` tags. If inline
CSS in the same file references `#oldId` and the element's ID gets renamed, every
CSS rule using that selector goes dead. Unlike external JS/CSS files where you grep
and update references, the quickest fix for **heavily-referenced inline IDs** is to
revert the single element's ID back to its original value (preserves CSS) rather
than updating 30+ selectors in the `<style>` block:

```bash
# 1. Restore the file from git
git checkout <file>
# 2. Re-run the script
python3 .../add_html_ids.py <file>
# 3. Revert just the critical element's ID back to the original
#    (use patch to change id="new_prefix_name" → id="oldName")
```

**Better: prevent the problem.** Before running the bundled script, check if the
file has inline `<style>` blocks with ID selectors that match element IDs. If it
does, use the preserve-existing script instead — it never renames existing IDs:

```bash
python3 .../add_ids_preserve_existing.py <file>
```

This keeps all 200+ new IDs from the script while fixing the single ID that
inline CSS depends on. Only do this for IDs that are referenced in 3+ CSS rules
in inline `<style>` blocks — for single references, update the CSS selector instead.
See `references/inline-css-collision.md` for the full diagnostic and recovery workflow.

🛑 **CHECKPOINT: Dynamic IDs need different JS targeting.** If the script generated
dynamic template-literal IDs (`.map()` loops), those IDs CANNOT be looked up with
`getElementById()` because the runtime suffix is interpolated. Use CSS attribute selectors:

```js
// ❌ WON'T WORK — dynamic suffix unknown at design time
document.getElementById('footer_h4__${column.titleKey}')

// ✅ WORKS — attribute selector starts-with
document.querySelector('[id^="footer_h4__"]')

// ✅ WORKS — attribute selector exact match with known key value
document.querySelector(`[id="footer_h4__${knownKey}"]`)
```

For CSS, use `[id^="prefix_name__"]` to style all instances, or `[id="prefix_name__someValue"]`
for a specific one.

🛑 **CHECKPOINT: TypeScript build must pass.** The script adds `id` attributes to JSX
elements inside React components. If a component's TypeScript interface already declares
`id: string` as a required prop but its callers don't pass `id`, the TypeScript build
will fail after the script runs. Run `npx next build` or `npx tsc --noEmit` to verify.

> **Post‑ID‑sync**: if the renamed IDs are referenced by JavaScript (`getElementById`, CSS `#id` selectors),
> those references also need updating. See `references/js-reference-sync.md` for the audit workflow.

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

### Map-awareness (v4.0)

When a tag appears inside a `.map()` callback (e.g. `{items.map((item, i) => <div>...</div>)}`),
a static `id="prefix_name"` would be duplicated for every iteration at runtime.

The TSX script detects `.map()` callbacks and generates **dynamic template-literal IDs**
instead:

```tsx
{items.map((item) => <div id={`prefix_name__${item.key}`}>...</div>)}
```

How it works:

1. **Detect map regions** — finds `.map()` callbacks, extracts the iteration variable, and
   determines the callback body boundaries (handles parenthesized `=> ( ... )`, block
   `=> { ... }`, and direct `=> <Tag/>` forms).
2. **Find the nearest `key` expression** — scans the tag and its parent elements for
   `key={...}` within the same map body. Uses this expression as the dynamic suffix.
3. **Generate dynamic ID** — `id={`prefix_hint__${keyExpr}`}` guarantees runtime uniqueness.
4. **Replace existing static IDs** — any existing `id="..."` inside a map region is
   automatically removed and replaced with the dynamic form.

**Nested maps**: The script picks the innermost containing map context, so inner
`.map()` loops correctly use their own iteration variable and key expression.

**Fallback**: If no `key={...}` expression is found, the iteration variable name is
used as the suffix (`id={`prefix_name__${var}`}`).

### Selective editing inside map loops

Elements inside `.map()` loops use the same template for every iteration. If you need
to modify (delete, replace) content in ONLY ONE specific instance, you CANNOT simply
remove the expression from the template — that would affect ALL instances.

**Pattern: conditional rendering with `key` check**

Use the `key` expression value (or equivalent data field) as a conditional guard:

```tsx
// Delete content from only the "Ecwid" h4, keep other column titles
<h4 id={`footer_h4__${column.titleKey}`}>
  {column.titleKey !== "footer.column.ecwid" ? t(column.titleKey) : null}
</h4>

// Replace content in only the "Sell Everywhere" link, keep others
<a id={`footer_a__${link.labelKey}`} ...>
  {link.labelKey !== "footer.link.sellEverywhere" ? t(link.labelKey) : replacementText}
</a>
```

This works because each instance has a unique `key`/ID at runtime. The check is done
against the raw data field (not the translated value) to avoid false matches.

**When to use this pattern:**
- User says "delete the content of just this one ID" and the element is inside `.map()`
- User says "replace only this specific link/heading, keep others"
- User gives you a runtime ID like `footer_h4__footer.column.ecwid` and expects only
  that one instance to change

**Pitfall**: The conditional adds complexity to the template. If 3+ instances need
different treatment, consider extracting the data into separate components instead.

### TSX-specific gotchas

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
   **Exception:** The HTML script supports `--preserve-existing` which skips
   this replacement step entirely. Use this flag when inline CSS/JS reference
   the current IDs and you want zero renames.

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

5. **`result` list: removals before insertions** — When replacing existing IDs
   (e.g. inside `.map()` regions), both a removal (zero out the old `id="..."`)
   and an insertion (add new `id={`...`}`) happen near the same position.
   Processing both in one reverse-order loop causes the removal to eat the newly
   inserted text if at the same position. Always process ALL removals first (in
   reverse order), then ALL insertions (in reverse order):
   ```python
   for action in reversed(tag_info):
       if action[0] == 'remove': result[rs:re_pos] = [''] * (re_pos - rs)
   for action in reversed(tag_info):
       if action[0] == 'insert': result.insert(pos, text)
   ```

6. **TypeScript generic regex broken on Python 3.12+** — The generic-skip check
   in `find_jsx_tags` uses a regex to detect characters that precede a `<` opening
   a type parameter. The original regex `r'[a-zA-Z0-9_)\\\\]]'` has an extraneous
   trailing `]` after the escaped `\\]`. On CPython 3.9 (macOS system Python)
   this compiled to a working (though oversized) class; on 3.12+ (Anaconda) it
   silently compiles to a class that matches **nothing**, causing every `<` to be
   treated as a JSX tag opening. This corrupts TypeScript generics:
   `Record<string, string>` → `Record<string id="xxx", string>`.

   **Fix**: the character class must be `[a-zA-Z0-9_)\\]` — `]` is included as a
   literal character, not the first in the class so it must appear before the
   closing `]`:
   ```python
   re.search(r'[a-zA-Z0-9_)\\]', masked[i-1])
   ```

   **Diagnostic**: if `re.compile(r'[a-zA-Z0-9_)\\\\]]').search('d')` returns None,
   the regex is broken. A working version returns a Match object.

## Changelog

- **v4.1.0 (2026-06-27)**: Added `--preserve-existing` / `-p` flag to `add_html_ids.py` that skips the non-conforming-ID replacement step and only adds IDs to elements without one. Created `add_ids_preserve_existing.py` as a convenience wrapper (same behavior). Created `references/inline-css-collision.md` with concrete diagnostic and recovery workflow. Updated the critical-rule section, workflow, TSX gotchas, frontmatter description, and inline-CSS checkpoint to recommend preserve-existing mode when CSS/JS references exist. Added trigger condition "do not change original IDs".
- **v4.0.3 (2026-06-27)**: Added "Inline `<style>` blocks" checkpoint after the JS references checkpoint with recovery workflow (git checkout → re-run → revert single element ID). Added corresponding "Inline CSS breaks" row to the failure recovery table. Added "Patch `replace_all` substring collisions" pitfall to the failure recovery table.
- **v4.0.1 (2026-06-11)**: Fixed TypeScript generic-skip regex. Created `references/scroll-spy-sidebar.md`, `references/regex-patterns.md`. Added duplicate-component-instance pitfall to failure recovery table. Cleaned up duplicate recovery rows.
- **v4.0 (2026-06-11)**: Map-aware TSX script. Detects `.map()` callbacks and generates dynamic template-literal IDs. Added selective editing inside map loops section, checkpoint about dynamic IDs not working with `getElementById()`, and failure recovery entries for map-loop editing.

- v3.4 (2026-06-10)
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

## Failure recovery table

If any issue below occurs, follow the recovery path. Don't guess — use the table.

| Trigger | First response | Fallback |
|---------|---------------|----------|
| Duplicate IDs found after run | Script counters should prevent this. Check `seen_ids` seeding (pitfall #4). Re-create `seen_ids` from existing IDs | Manually rename duplicates with unique suffixes |
| **Duplicate IDs from `.map()`** — same ID appears for every map iteration at runtime | v4.0+ auto-detects `.map()` and generates dynamic template-literal IDs. First check that the file actually uses `.map()` — if it does, re-run the script (it will convert static IDs to `id={`prefix_name__${key}`}`) | Manually convert to template literals: `id={`prefix_name__${item.key}`}` or add a unique `key` prop for the script to use |
| **User wants to modify ONE specific map instance** — "delete content of just this one ID" but the ID is inside `.map()` | The element is a shared template — deleting the content expression deletes ALL instances. Use the Selective editing pattern: add a conditional check on the `key` expression | If 3+ instances need different treatment, extract into separate components instead |
| **JS/DOM breaks with dynamic IDs** — `getElementById("prefix_name")` returns null because the ID is now a template literal (`id={`prefix_name__${key}`}`) | Dynamic IDs can't be targeted by `getElementById()` since the runtime suffix is unknown. Use CSS attribute selectors instead: `document.querySelector('[id^="prefix_name__"]')` (starts-with) or `` document.querySelector(`[id="prefix_name__${value}"]`) `` with the known key value | For CSS, use `[id^="prefix_name__"]` to match all dynamic instances, or `[id="prefix_name__someValue"]` for a specific one |
| STR markers in output | Pre-processing regex failed to strip old IDs. Re-run script on original file | Post-processing regex on final output: `content = re.sub(r'\s+id\s*=\s*(["\x27])(?!herosection_)[^"\x27]+\1', '', content)` |
| **Duplicate IDs from reused component instances** — the same component (`<StickyPromo />`) is rendered 4 times on a page, each with a static `id="stickypromo_img"`. At runtime, 4 elements share one ID | The script can't fix this — it only sees the component definition once. The `id` must be made dynamic by including a differentiating prop: `id={`stickypromo_img__${id}`}` where `id` is the component's section prop | If the component has no unique prop, add one, or use CSS `nth-child` selectors instead of IDs to target instances |
| Script corrupts `<script>` content | `<script>` body has unescaped `</script>` or CDATA. v3.2+ space-fill should handle normal cases | Manually wrap JS in `/*<![CDATA[*/ ... /*]]>*/` or use external .js file |
| React component gets an `id` | Component name is lowercase — script treated it as HTML. Rename component to uppercase (React convention) | Add `id` prop type to the component so TS accepts it |
| **JS/DOM breaks** — `getElementById("oldName")` returns null | Script renamed the old non-conforming ID to a prefixed version (e.g. `mobileCarousel` → `herosection_mobile_and_tablet_in_device_carousel`). Any `document.getElementById("oldName")` or CSS `#oldName` selector now silently breaks | Search the project for the old ID string — `grep -rn '"oldName"' src/` — and update all references to the new prefixed ID. Check both `.ts`/`.tsx` files for `getElementById` AND `.css` files for `#old-name` selectors |
| **Inline CSS breaks** — page layout collapses after script run | The script renamed an element ID that is referenced by inline `<style>` blocks in the same file (e.g. `mediaCenterPageContent` → `media_center_mediacenterpagecontent`). CSS selectors like `#mediaCenterPageContent .something` all go dead. **Quickest fix:** `git checkout` the file, re-run with `add_ids_preserve_existing.py` instead, which never renames existing IDs. See `references/inline-css-collision.md` for the full diagnostic. | If the bundled script already ran: revert the single element ID via patch (see "Inline `<style>` blocks" checkpoint). For future runs, use the preserve-existing script. |
| **Patch `replace_all` corrupts similar selectors** — converting `body #mediaCenterPageContent .sectionLink` with `replace_all=true` also corrupts `.sectionRow`, `.sectionColumnContent`, `.sectionImage` because the tool's fuzzy matching treats `.section` as a common prefix across unrelated rules | Never use `replace_all=true` on a string that shares a common prefix with other distinct selectors. Always supply enough context for a unique match, or patch each selector individually with a unique snippet (e.g. include the opening `{` or a unique property). | If corruption already happened: `git checkout` the file and redo all ID-renamed CSS selectors one at a time with unique context |
| **TS generic corrupted** — `id="supportsection_string"` injected inside `Record<string, string>` | The generic-skip regex failed to match. Re-run with v4.0.1+ which has the fixed regex. Verify: `python3 -c "import re; print(bool(re.search(r'[a-zA-Z0-9_)\\]', 'd')))"` → must print True | Restore from backup, fix regex, re-run |
| **Element deletion breaks mobile layout** — old offsets persist | Check that no surrounding elements relied on the deleted container for layout or spacing | Adjust margins/padding on adjacent siblings |
| File with `src/app/page.tsx` nested 3+ deep | Prefix derivation uses immediate parent, may collide. Check other locale folders for duplicate prefixes | Pass `--prefix` override explicitly |
| **TypeScript generic corrupted** — Record<string id=xxx> in output after script run | Generic-skip regex broken on Python 3.12+. Diagnostic: compile the regex in find_jsx_tags and test on 'd' — if it returns None, fix to the corrected form | Restore from backup, fix regex, re-run |
| Node.js HTTP request in script content | `http://` or `https://` in `<script>` body triggers `<` matching in old parser. v3.2+ space-fill prevents this | If using pre-v3.2, upgrade the script |
| **Container-relative layout** — animation elements (`color-block-*`, `devices-unit`) use `vw` positioning and break when page is constrained to `max-width: 1440px` | Static positions (`left: 57vw`): change to `%` (`left: 57%`). JS-set CSS variables (`--b1-w`): use `calc(var(--b1-w) * 1440px / 100vw)` in CSS | See `references/container-relative-vw.md` for full technique with examples and edge cases |

## TSX-specific: TypeScript interface `id` prop

The TSX script (`add_tsx_ids.py`) does NOT modify TypeScript interface definitions —
it only inserts `id="xxx"` into JSX tag attributes. However, if a component already
has an `id` field in its Props interface (added by a previous run or by hand), the
script preserves it.

**Problem scenario**: A component has `id: string` in its Props interface but none of
its callers pass an `id` prop. After running the script, the component still compiles
(because the script only adds `id` to the JSX element, not to the interface). But if
someone later makes `id` required (`id: string` instead of `id?: string`), all callers
break. This is NOT a script bug — it's an interface design issue.

**Fix if this happens**:
1. Determine if the component internally uses `id` as a data key (`logos[id]`, `data[id]`)
2. If yes → `id` must stay required; update all callers to pass a unique string
3. If no → change `id: string` to `id?: string` in the interface; callers work as-is


## Reference examples

See `references/output-examples.md` for real before/after outputs from all
script variants (HTML, TSX pages, TSX components, and the broken HTMLParser
approach to avoid).

## Verification

After running, verify. Use the automated checks below — they are more reliable than visual scanning.

**No-CSS-integrity check (proves zero non-ID changes):**
```bash
cd <project-root> && git diff <file> | grep -v 'id=' | grep '^[+-]'
```
If this returns nothing, zero style/class/text/structure changes were made. If it returns lines, those are changes outside `id=` — investigate.

**Duplicate IDs:** Use `grep -Eo` (works on both macOS BSD grep and GNU grep) or Python:

```bash
# Count IDs (static + dynamic)
grep -c 'id="' <file>
grep -c 'id={`' <file>  # dynamic map IDs

# Check for duplicates (portable: use grep -Eo, not GNU-only -oP)
grep -Eo 'id="[^"]*"' <file> | sort | uniq -d

# Check TSX (handles single quotes too)
grep -Eo "id='[^']*'" <file> | sort | uniq -d

# Python alternative (works everywhere, no grep flag differences)
python3 -c "
import re, sys
with open(sys.argv[1]) as f:
    c = f.read()
    ids = re.findall(r'id=\"([^\"]*)\"', c)
    ids += re.findall(r\"id='([^']*)'\", c)
    dyn = re.findall(r'id=\{\`([^\`]*)\`\}', c)
dupes = [i for i in sorted(set(ids)) if ids.count(i) > 1]
if dupes:
    for d in dupes: print(f'DUPE: {d} (x{ids.count(d)})')
else:
    print(f'{len(ids)} static IDs, {len(dyn)} dynamic, 0 dupes')
" <file>
```

**macOS note**: `grep -oP` is GNU grep only — macOS BSD grep rejects it.
Use `grep -Eo` or the Python script instead.

## Container-relative vw conversion

When a page is constrained to `max-width: 1440px` but animation elements use `vw`-based positioning (color blocks, device mockups), those elements extend beyond the container and get clipped. Fix by converting `vw` to container-relative values:

### Static positions (CSS-only):

```css
/* BEFORE — clips on wide screens */
left: 57vw;
width: 34vw;
right: -2.8vw;

/* AFTER — proportional to 1440px container */
left: 57%;
width: 34%;
right: -2.8%;
```

`%` is relative to the containing block width. At 1440px, `57% = 821px` (same as `57vw` on a 1440px viewport). On wider viewports, the value stays proportional to the container, not the viewport.

### JS-set CSS variables (animation lerp values):

```css
/* JS sets --b1-w to "42vw" via lerp. CSS uses: */
width: var(--b1-w, 42vw);

/* Fix — convert vw to container-proportional px: */
width: calc(var(--b1-w, 42vw) * 1440px / 100vw);
```

The `calc` cancels the vw units: `42vw * 1440px / 100vw = 42/100 * 1440px = 604.8px`.
Works for any variable JS sets with `vw` suffix (`--b1-x`, `--b2-w`, `--devices-x`, etc.).

### Transform translateX with vw:

```css
/* BEFORE */
transform: translate3d(var(--b1-x, -1vw), var(--b1-y, -26vh), 0);

/* AFTER */
transform: translate3d(calc(var(--b1-x, -1vw) * 1440px / 100vw), var(--b1-y, -26vh), 0);
```

### Vertical (vh) values — leave as-is:

`vh` values control scroll-driven vertical positioning and are NOT affected by horizontal max-width. Only convert horizontal (`vw`, `left`, `right`, `width`) properties.

See `references/container-relative-vw.md` for full examples and edge cases.

## Script maintainer references

- `references/css-integrity-check.md` — Programmatic "no non-ID changes" verification step for user-facing delivery.
- `references/inline-css-collision.md` — Concrete scenario (mediaCenterPageContent) with pre-flight check, diagnostic, and recovery workflow.
- `references/regex-patterns.md` — Key regex patterns and Python-version portability pitfalls (TypeScript generic skip on 3.12+).
- `references/scroll-spy-sidebar.md` — IntersectionObserver-based sidebar active-section tracking with smooth-scroll anchor clicks (privacy page pattern).
- `references/ts-generic-skip-bug.md` — Detailed reproduction and fix for the TypeScript generic regex bug.
- `references/output-examples.md` — Before/after outputs from both HTML and TSX scripts.
- `references/container-relative-vw.md` — Converting vw-based animation positions to container-relative %.
- `references/js-reference-sync.md` — Workflow for updating JS getElementById / CSS #id references after ID rename.
- `references/expand-collapse-card.md` — Reusable expand/collapse card detail pattern with max-height animation and inner text fade-in. Designed for "Read more" toggles on card grids.
- `references/script-style-corruption-v3.2.md` — Root cause and fix for `<script>`/`<style>` body corruption.

## Harness (Self-Eval)

The harness validates that the scripts correctly add IDs without corrupting
content. 3 test cases cover the skill's core guarantees.

### Cases

| ID | Name | Principle Tested |
|----|------|-----------------|
| `case_001` | basic-html-no-existing-ids | ID count, prefix convention, no dupes, text preserved |
| `case_002` | tsx-mixed-ids | Convention IDs preserved, non-conforming replaced, React skipped |
| `case_003` | html-with-script-style | No STR markers leaked, script/style uncorrupted, apostrophe safe |

### Checks

| Check | What it detects |
|-------|----------------|
| `id_count_increased` | Output has more IDs than input (IDs actually added) |
| `all_ids_have_prefix` | Every id value starts with the expected `{prefix}_` |
| `no_duplicate_ids` | Zero duplicate id values in the output |
| `convention_ids_preserved` | Existing convention-following IDs remain unchanged |
| `nonconforming_ids_replaced` | Old non-conforming IDs (camelCase, generic) are gone |
| `react_components_skipped` | No uppercase-prefixed IDs (React components get no id) |
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

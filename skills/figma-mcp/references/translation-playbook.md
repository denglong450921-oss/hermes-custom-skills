# Multi-Language Translation Playbook (validated on AMR pages)

## ⛔ IRON RULE 6 — TRANSLATE ONLY (user-mandated, highest priority)

**Do NOT record original text-box sizes, do NOT adjust font sizes, letter
spacing, or dimensions. Just translate.** Every auto-fit / font-size /
spacing adjustment the agent makes is rework for the user ("越调越难看，我需要
返工的地方越多"). This supersedes IRON RULE 4 (Auto-Fit) and the overflow
steps below: they apply ONLY when the user explicitly asks for them.

- No pre-translation bounds recording (`dump-source-bounds.js`), no
  `text-fit.py` / `apply-auto-fit.js`, no font-size reduction to fit.
- FONT_FIX (font swap so the target script renders, e.g. Arial Unicode MS) and
  passthrough preservation (numbers/INR/codes keep source font) are still part
  of "translating" — they are NOT sizing adjustments.
- If translated text overflows its box: **stop and ask the user** how to
  proceed. Never shrink fonts or tweak spacing on your own.

## ⛔ IRON RULE — TEXT NODES ONLY

**Images are never translated. Never.** Only Figma TEXT nodes get their
`characters` changed. This applies to:

- RECTANGLE / IMAGE / VECTOR / FRAME nodes — never `set_text`, never "translate"
  embedded raster text, never treat a screenshot region as translatable copy.
- Screenshot exports are for VERIFICATION ONLY (layout/overflow/ink check),
  never a source of translatable strings and never a target of edits.
- `scan_text_nodes` returns only TEXT nodes; the translate scripts additionally
  verify live node types and abort/skip if anything non-TEXT sneaks in.
- Text baked into images (screenshots of posters, "ChatGPT Image" fills, QR
  codes, fund cards) stays as-is — if the design needs that text translated,
  the source design must replace the image, not the translation step.

If a frame contains a mix of TEXT nodes and images, translate exactly the text
nodes and leave every image node untouched. Report images as "left as-is".

Field-tested workflow for cloning a Figma frame and translating it into 10+
languages (Russian, Kazakh, Uzbek, Kyrgyz, Tajik, Azerbaijani, Turkmen,
Spanish, Arabic, Armenian) using the local figma-mcp-go bridge. 170+ text
nodes translated, verified byte-exact, layout preserved.

## The One-Line Version

```
node scan-frame.js 851:7          # 1. dump source text
# 2. translate the JSON (your LLM / translator)
node translate-frame.js 851:7 translations.json      # clone-per-language
node translate-inplace.js 897:8317 translations.json # existing frame, no clone
```

`translate-frame.js` clones the frame once per language, renames each clone
`<frame>-<语言>`, sets every text node, and verifies byte-exact. Layout is
untouched by design (clone copies geometry; only `characters` change).
`translate-inplace.js` does the same for a frame that ALREADY exists (the
user selected a language clone holding placeholder/English text) — scan, set,
verify, optional screenshot, all on ONE bridge connection.

## Speed Rules (learned the hard way)

- **Never run a translation tool-by-tool with the mcp-client.js CLI.** Every
  CLI invocation spawns a fresh bridge + plugin reconnect (~1-2 s). One
  `translate-inplace.js` / `translate-frame.js` run replaces 15+ manual calls.
- **The CLI no longer truncates** — it prints full output (cap with
  `CLI_CAP=2000` if bounded output is needed). Resolve the target with
  `get_selection` directly instead of re-calling to "see more".
- **Verify byte-exactness with one `get_nodes_info` call**, not per-node
  re-scans. The scripts already do this.
- **Do NOT reach for OCR.** Tesseract on this Mac lacks `fra` data; Swift/Vision
  compile takes minutes. The fast check is ink density on the exported PNG:
  `python3 scripts/ink-check.py <shot.png>` — a rendered text region shows
  ~10%+ ink; blank/missing font shows ~3%. White text on dark cards needs
  `--white-text`.
- **`get_screenshot` takes `nodeIds` (array), not `nodeId`.** The wrong param
  silently exports the current selection — the giveaway is a screenshot whose
  size doesn't match the node. Export at scale 1 per node for ink checks, and
  the frame at scale 1 for the full layout.
- **In-place translations (existing clone frames)**: keep the `translations`
  JSON index aligned to the frame's own `scan-frame.js` order. Leftover text
  from another language (e.g. a Portuguese string inside an English frame) is
  still index-aligned — translate it too, don't skip it.
- **French / Canadian French needs no FONT_FIX** — Tai Heritage Pro and Times
  New Roman both carry é è à ç ô. One ink check is enough; no glyph zooming.

## 1. Get the Source Text

```bash
node scan-frame.js 851:7
# {"nodeId":"851:7","count":17,"textNodes":[{"id":"851:12","characters":"338 Euston Road, London","fontSize":30,"fontFamily":"Inter"},...]}
```

The output order (index 0..N-1) is the order `set_text` expects in the
translations JSON. **Order is matched by index, never by node ID** — cloned
text nodes get fresh IDs.

## 2. Build the Translations JSON

```json
{
  "languages": [ {"code":"ru","name":"俄语"}, {"code":"es","name":"西班牙语"} ],
  "translations": {
    "ru": ["text0", "text1", "..."],
    "es": ["text0", "text1", "..."]
  }
}
```

Rules learned the hard way:

- **Preserve `\n` line breaks exactly.** Use real newlines in the JSON
  strings, not the literal two-character `\\n`.
- **Keep brands/numbers/addresses verbatim**: `AMR`, `TikTok Shop`,
  `TCNAMR.COM`, `AMR@TCNAMR.COM`, `338 EUSTON ROAD, LONDON NW1 3BT, GB`,
  USD/GBP amounts, dates, percentages.
- **Translate full meaning, never shorten to fit.** Fix overflow later.
- **Continent/country lists** (Asia/Europe/Americas/Middle East) translate
  the region name and each country; keep the leading space of continuation
  lines (`" Thailand\n Singapore\n Malaysia"` → translated lines keep the
  leading space).
- **Cyrillic scripts**: Kazakh/Kyrgyz/Tajik use Cyrillic; Uzbek/Azerbaijani/
  Turkmen use Latin; Arabic is RTL (Figma handles bidi automatically);
  Armenian uses the Armenian alphabet.

## 3. Run the Translation

```bash
node translate-frame.js 851:7 translations.json
```

- Clones are placed in a grid **below** the source (cols default 5,
  `GRID_COLS=3` to change). Positions never overlap the source.
- Each clone is renamed `<source>-<语言名>` (e.g. `1.修改-俄语`).
- After the run it re-scans every clone and reports
  `exact=N/N` — the byte-exact verification.

## 4. Font Coverage — the #1 Silent Failure

`set_text` writes characters fine, but **rendering depends on the node's font
having the target script's glyphs**. The scan will show the correct text while
the screenshot shows blank space. Verified font coverage in Figma Desktop:

| Font | Cyrillic | Arabic | Armenian |
|---|---|---|---|
| Times New Roman | ✅ | ✅ | ❌ blank |
| Inter / Noto Sans / Arial / Arimo | ✅ | ❌ | ❌ blank |
| Noto Sans/Serif Armenian, Sylfaen, .SF Armenian | – | – | ❌ not loadable |
| **Arial Unicode MS** | ✅ | ✅ | ✅ (no Bold weight) |

**Armenian fix** (and any script the source font lacks):

```bash
FONT_FIX="hy:Arial Unicode MS" node translate-frame.js 851:7 translations.json
```

`translate-frame.js` then creates `Body/FF-ArialUnicodeMS-<size>` styles and
applies them to every text node of the Armenian clone automatically.

**Always verify non-Latin translations by screenshot, never by scan alone.**
Quick ink check (Python/PIL): a text region that renders shows ~10%+ dark
pixels; a blank-font region shows ~3% (only Latin runs like "AMR").

**Pitfall — `fontSize: "mixed"`:** some nodes (e.g. a "$5 ~ $6" stat with
per-character formatting) report `fontSize: "mixed"` instead of a number.
`translate-frame.js` now falls back to size 32 for these during FONT_FIX, so
the font gets applied instead of silently skipping the node. Check the
`FONT_FIX ... applied to N/M` line — if N < M, re-run the fix for the missed
nodes manually.

## 5. Overflow Handling

Translated text is often 15-30% longer (Russian, Spanish, Kazakh). If a fixed
container clips:

1. `get_nodes_info(nodeIds)` and compare `bounds.height` before/after.
2. Create a smaller text style: `create_text_style(name, fontFamily,
   fontSize=0.8x, fontStyle)` then `apply_style_to_node(nodeId, styleId)`.
3. Rule of thumb: headings ~0.8x, table column headers ~0.7x for Romance
   languages; Arabic rarely needs reduction (compact script).

## 6. Mixed-Format Warning

Nodes whose scan shows `fontName: "mixed"` or `fills: "mixed"` carry
per-character formatting (colored/bold substrings). `set_text` wipes it.
List these node IDs in the report so the user can restore the formatting in
Figma after translation.

## Numeric / Table-Cell Passthrough (IRON RULE 2)

Numbers and codes in tables are NEVER touched — not their text, not their font.
Level codes (Q1–S3), INR amounts, percentages (5%-2%-1%), digits, "/", and any
node whose text is pure numbers/punctuation: pass through byte-identical AND
keep the source font.

- **Why**: table alignment depends on the source font's metrics (e.g. Poppins
  SemiBold vs Arial Unicode MS have very different widths). Changing the font on
  numeric cells breaks column alignment even though the digits are unchanged.
- **In the translations JSON**: mark these nodes passthrough (same string as
  source). `translate-frame.js` then never `set_text`s them.
- **FONT_FIX must NOT cover passthrough nodes**: the FONT_FIX loop in
  `translate-frame.js` applies the fallback font to EVERY text node in the
  clone. For table-heavy frames, do a follow-up restore pass instead:
  1. `node scripts/restore-fonts.js` — restores source family/size/style/lineHeight
     on every node whose text equals the source (passthrough). Config: edit the
     PAIRS list (source frame, clone id) at the top of the script.
  2. `node scripts/restore-letter-spacing.js` — second pass when the source has
     letterSpacing (e.g. Poppins cells at 10%). Uses styles extracted from a
     full `get_selection` dump (get_node does NOT return letterSpacing);
     regenerate `/tmp/source_styles_full.json` from the cached selection log if
     the target frame changes.
- **Verify**: re-read a clone and confirm passthrough nodes carry the source
  font (`styles.fontFamily` = Poppins/Calistoga/…) and translated nodes carry
  the FONT_FIX font.

## Box Geometry Drift (IRON RULE 3)

`set_text` re-fits auto-width text boxes: the box width shrinks to the new
text's width and the position re-anchors (e.g. `Specialist` w=159 x=2325 became
`ತಜ್ಞ` w=40 x=2266 after translation). In tables this breaks column alignment
even though every text node's *content* is correct.

- **Fix**: after translating a table-heavy frame, restore the SOURCE box
  geometry (x, y, width, height) on every TRANSLATED node:
  `node scripts/restore-bounds.js` — walks each clone, compares each translated
  node's bounds against the source frame's, and runs `resize_nodes` +
  `move_nodes` per drifted node. Passthrough nodes are never touched (their
  boxes were never re-fit). Edit the PAIRS list at the top for new runs.
- **Trap**: `scan_text_nodes` does NOT return bounds — get them from
  `get_nodes_info` (DFS walk, map id → bounds) on both source and clone.
  Bounds are frame-local on both sides, so they are directly comparable.
- **Text vs box**: restoring the box makes alignment exact, but Indic glyphs
  are wider than Latin — a translated cell can overflow its restored box.
  Check with `PIL.ImageFont.getlength` (Arial Unicode MS) per line against the
  box width; overflow in a CENTER-aligned cell usually stays within the column
  and is visually fine, but if it collides with a neighbour, reduce the font
  size on that node only (proportionally).
- **Verify**: re-read the clone group and compare every text node's bounds to
  the source group's (all four dims within 1px).

## Newline-Aligned Table Cells: Split First (IRON RULE 5)

Some source tables align rows with a SINGLE multi-line text node per column
(lines separated by `\n`, one line per row). Translating such a node always
breaks row alignment — translated lines are longer/shorter, wrap, or shift.
Never translate these as multi-line nodes. SPLIT them into one TEXT node per
line BEFORE translating:

1. Identify alignment-critical multi-line cells (line count × lineHeight ≈ box
   height; lines pair with rows of adjacent columns).
2. Record each line's position: `y = cell.y + k*lineHeight` — this reproduces
   the source's own line layout exactly.
3. `restore-split-cells.js` creates one node per line (centered in the cell
   via measured width, `x = cell.x + (cell.w - w)/2`), then deletes the
   multi-line node ONLY if every line was created.
4. Source fonts for the source, TARGET_FONT + per-line width fit for clones.

Script: `restore-split-cells.js <frameId> <targets.json> [port]` (targets.json
= array of source node ids). It re-creates source cells as per-line nodes from
the saved scan/styles/bounds JSONs (idempotent: skips targets still present)
and splits the same cells in every clone (env `PAIRS`). Also: `dedupe-source.js`
(position-based dedupe), `verify-split.js` (per-line layout check).

**Bridge gotchas learned the hard way:**
- `scan_text_nodes` returns NO bounds — read `get_nodes_info` for geometry.
- `create_text` parentId must be the node ID string; a node OBJECT serializes
  to `[object Object]` → "Parent node not found" (silent failure).
- Spawned `python3` may resolve to conda's python, which crashes on startup
  when spawned by node (plugin env issue) — set `PY_BIN=/usr/bin/python3`
  (PIL is available there).
- Arial Unicode MS ships Regular ONLY — `Bold`/`SemiBold`/`mixed` fail to load.
- **Row pairing must be by CONTENT, never by sorted order.** Some tables are
  bottom-up (headers at the BOTTOM, rows ascending upward — e.g. GM at the
  smallest y, Specialist at the largest). Sorting old nodes by y and pairing
  them with rows in amount order REVERSES the pairs. Parse the number from
  each line's text ("12 members"→12, "3,000 members"→3000 — strip commas!)
  and place it at its row by the ground-truth mapping. Same for sub-captions:
  pair each sub to its member by adjacency (sub.y = member.y - subOffset).
- When in doubt about create_text's coordinate space, create ONE probe node at
  a known position and read it back — the delta is the space offset.

Row-alignment toolkit (all in scripts/):
- `restore-split-cells.js <frameId> <targets.json>` — recreate source cells as
  per-line nodes from saved JSONs + split clones (delete only if all created).
- `fix-pair-rows.js` — position pairs at correct rows (needs clean rowY).
- `fix-source-cleanup.js` — remove polluted duplicates, re-read clean rowY from
  the reference column (e.g. INR cells with x < 1700), rebuild source + clones.
- `fix-clone-pairs.js` — rebuild clone pairs by CONTENT (number parse + sub
  adjacency), immune to row-order confusion.

## Auto-Fit: Keep the Box, Shrink the Font (IRON RULE 4)

Translated text is usually wider than the source (Indic scripts ~1.5-2x for the
same meaning). To keep the page layout intact — no deformation, no overflow, no
unwanted wrapping — record the original box BEFORE translation, then shrink the
font size so the translated text fits its own box.

Recommended per-frame pipeline:
1. `node scripts/dump-source-bounds.js <frameId> <bounds.json>` — record every
   text box (x,y,w,h) BEFORE anything is translated.
2. `scan-frame.js` → build `translations.json` (passthrough = numbers/codes).
3. `translate-frame.js` (clone + set_text + FONT_FIX).
4. `node scripts/restore-bounds.js` — restore source geometry on translated
   nodes (auto-width boxes re-fit on set_text).
5. `python3 scripts/text-fit.py <translations.json> <scan.json> <styles.json>
   <bounds.json> <fit-sizes.json>` — estimate rendered width/height with PIL
   (Arial Unicode MS metrics) per node; where the text would exceed the box,
   binary-search the largest font size that fits. Output: {lang: {idx: size}}.
6. `node scripts/apply-auto-fit.js <fit-sizes.json>` — apply the smaller sizes
   via text styles (created per size; lineHeight from source is preserved so
   rows stay aligned). Run once per source frame with the right fit file.
7. Verify: re-read a clone; assert fitted nodes carry the new size, boxes match
   source bounds, text is byte-exact.

Fit rules encoded in text-fit.py:
- **Single-line source cells** (text that rendered on one line, e.g. table
  headers, position titles): must NOT wrap — shrink until width fits.
- **Nodes that already wrap in the source** (paragraphs, long headings):
  wrapping is normal; only total height constrains (wrapped lines × lineHeight
  ≤ box height).
- Only shrink, never enlarge; FIT_MARGIN=0.96 guards metric drift between PIL
  and Figma; MIN_SIZE=8 floor.

Trap: **Arial Unicode MS ships Regular only** — text styles requesting
Bold/SemiBold/mixed fail with "could not be loaded". apply-auto-fit.js forces
fontStyle Regular when the target font is Arial Unicode MS (FONT_FIX in
translate-frame.js does the same).

## Restarting the Bridge
The bridge allows exactly ONE plugin connection. If a stale server holds the
port, kill it (`pkill -f figma-mcp-go` or `kill <pid>`); the Figma plugin
auto-reconnects within ~2s once the new server listens. All scripts wait for
the plugin automatically (`waitForPlugin: true`).

## Getting the Bridge Binary

The scripts resolve the binary from: explicit `binary` option → `vendor/` in
the skill dir → `~/.figma-mcp-go/figma-mcp-go`. To install:

```bash
# Option A: symlink the npm binary into the skill's vendor dir (macOS arm64):
npm pack @vkhanhqui/figma-mcp-go
tar xzf figma-mcp-go-*.tgz
ln -sf "$PWD/package/bin/darwin-arm64/figma-mcp-go" \
  ~/.hermes/skills/figma-mcp/vendor/figma-mcp-go

# Option B: run the server yourself and let the scripts connect to it:
npx -y @vkhanhqui/figma-mcp-go@latest

# Option C (any platform): copy your platform binary to
# ~/.figma-mcp-go/figma-mcp-go — the client finds it automatically.
```

`vendor/` is gitignored; the repo documents the install instead of shipping a
23 MB platform-specific binary.

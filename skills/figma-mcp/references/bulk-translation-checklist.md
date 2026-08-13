# Bulk Translation — Production Checklist

Patterns discovered during a large Russian (Cyrillic) translation run across ~200+ text nodes in a multi-frame Figma document. Applicable to any non-Latin-script batch translation.

## Pre-flight

- [ ] **Complete mandatory user review** — Per SKILL.md rule, list all nodes with full text, fontSize, and fontFamily to the user. Get `confirm` before proceeding. Do NOT skip this step.
- [ ] **Identify already-translated nodes** — Scan current text content. Nodes already in the target language should be flagged as skipped in the presentation. Do not re-translate them.
- [ ] **Scan font families** — `scan_text_nodes(frameId)`. Every node using Times New Roman, DIN Alternate, or other font without target-script glyphs will fail on `set_text`.
- [ ] **Create fallback styles** — One per unique font size × weight combo. Use Inter (Latin + Cyrillic) or Noto Sans (broad script coverage). Name pattern: `Body/AMR-Desc-RU-<size>` or `Heading/AMR-RU-<size>`.
- [ ] **Reuse existing styles** — Check `get_styles()` first. If a style with matching font/size/weight exists from an earlier batch, reuse its `styleId`. Do NOT create duplicates (clutters the Figma styles panel).

## During translation

- [ ] **Apply style BEFORE set_text** — Otherwise `set_text` throws "unloaded font" error for non-Latin scripts, which can destabilise the MCP bridge (30-60s downtime).
- [ ] **Bulk style application** — Apply the same fallback style to ALL nodes sharing that font/size before translating any of them. Reduces round-trips.
- [ ] **Watch for Chinese character contamination** — When translating English→Russian via a multilingual LLM, CJK characters leak into Russian output. Scan visually before confirming completion. Overwrite with corrected `set_text` (idempotent).
- [ ] **Mark mixed-formatting nodes** — If `fontFamily` or `fills` show `"mixed"`, `set_text` will wipe per-character formatting (bold substrings, colored text). Note these for manual restoration in Figma after the batch.

## Fill-Color Loss After set_text (validated fix)

`set_text` flattens nodes whose scan shows `fills: "mixed"` (per-character
two-tone colors, e.g. gold `#FFD446` stats with red accents) to the node's
base fill — usually near-black `#101010`. Text is correct but the color pops
are gone.

**Detection:** compare `get_nodes_info(...).styles.fills` between source and
each clone, index by index. Only `"mixed"` source nodes mismatch.

**Fix:** `set_fills(nodeId, color, mode="replace")` restores a SOLID fill.
Choose the source's **text** color — NOT the dominant color of the region.
Sampling the median pixel color of a node's bounds is a trap when the text
sits on a colored card: the card (e.g. gold `#FFD446`) occupies far more
pixels than the text strokes and skews the median. The text on those cards
was `#FF0000` red. To get the true text color, sample only pixels that
differ strongly from the card color (e.g. `|pixel - card| > 150`), or check
sibling text nodes on the same card that were NOT mixed. One color only —
the two-tone per-character accents cannot be reproduced via the bridge; note
them for manual touch-up in Figma if the user wants the exact two-tone back.

**Prevention:** after translating, always diff fills source-vs-clone and
re-apply `set_fills` for every mismatched node — do not wait for the user to
spot it. Add this to the standard post-translation verification loop.

## Post-flight

- [ ] **Warn about mixed-format loss** — Tell the user which node IDs had mixed formatting and need manual fix (double-click → select substring → reapply fill).
- [ ] **Check overflow** — Russian text is 15-30% longer than English. If a node's container has fixed height, text may clip. Use `get_nodes_info` to compare bounds before/after, or create reduced-font-size styles as needed.
- [ ] **Verify style count** — Ensure no orphan styles were left from cancelled experiments. Clean up unused styles if the user cares about style panel hygiene.

## Font Coverage Pitfall (Armenian & other non-Latin scripts)

`set_text` writes characters fine, but **rendering depends on the node's font having
the target script's glyphs**. A node can hold correct Armenian/Cyrillic/Arabic text
and still render blank if the font lacks glyphs. Symptom: `scan_text_nodes` returns
the expected text, but the screenshot shows empty space (or only Latin runs).

Fonts verified in Figma Desktop (via this bridge, loadFontAsync):

| Font | Armenian | Notes |
|---|---|---|
| Times New Roman | ❌ blank | Figma build has no Armenian glyphs |
| Noto Sans (base) | ❌ blank | Latin/Cyrillic/Greek only |
| Arial | ❌ blank | no Armenian in Figma build |
| Arimo | ❌ blank | no Armenian |
| Noto Sans Armenian / Noto Serif Armenian | ❌ not loadable | "could not be loaded" via create_text_style |
| Sylfaen / .SF Armenian | ❌ not loadable | system fonts not synced to Figma |
| **Arial Unicode MS** | ✅ **works** | full Unicode coverage; **Regular only — no Bold style** |

**Armenian fix recipe:**
1. `create_text_style(name, fontFamily="Arial Unicode MS", fontSize=<orig size>, fontStyle="Regular")`
2. `apply_style_to_node(nodeId, styleId)` per text node
3. Verify with `get_screenshot` + pixel-ink check (text region dark-pixel % should jump from ~3% to ~10%+), not just `scan_text_nodes` — the scan reads `characters`, not rendered glyphs.

Trade-off: Arial Unicode MS has no Bold weight, so bold headings render as Regular.
A closer visual match would need a local font installed **and** synced into Figma
Desktop (Figma → Fonts), then loadFontAsync may pick it up on a fresh session.

**Golden rule:** after any non-Latin translation, verify by **screenshot + ink
analysis or eyeballing**, never by `scan_text_nodes` alone.

## Style naming convention (established in production)

```
Body/AMR-Desc-RU-<size>       — Inter Regular (default body text)
Body/AMR-Desc-RU-<size>-Bold  — Inter Bold (section headers, emphasis)
Heading/AMR-RU-<size>         — Inter Bold (page titles, section headings)
```

Reuse the same name across frames so future sessions can call `get_styles()` and pick them up without recreating.

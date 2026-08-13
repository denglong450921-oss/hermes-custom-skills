# Figma Text Translation Pipeline

Full 5-step workflow for translating Figma text frames to any language via MCP. Validated across 15+ pages in Spanish, Arabic, French, and Portuguese.

## Step 1: Find the Target Frame

```python
# Search by name
search_nodes(query="4xiban")  # or "M1spanish", "10French", etc.
# Returns: { count, nodes: [{ id, name, type, bounds }] }
```

Multiple pages with same template (e.g., 4xiban clones across languages) can be found by naming convention: `{page}_{language}`.

## Step 2: Scan All Text Nodes

```python
scan_text_nodes(nodeId="674:2")
# Returns: { count, textNodes: [{ id, characters, fontName, fontSize, ... }] }
```

**What to translate:**
- English text labels, descriptions, headings → translate
- Numbers (USDT amounts, percentages) → keep as-is
- Level labels (LV1, LV2) → keep as-is
- Special characters (+, %) → keep as-is

**What to watch:**
- `fontName: "mixed"` or `fontSize: "mixed"` → the node has per-character formatting (e.g., "5%" in red, rest in black). `set_text` will WIPE this. User must manually restore colors.
- `fills: "mixed"` → same issue with mixed text colors.

## Step 3: Translate

```python
set_text(nodeId="674:26", text="BONO DE PRIMER DEPÓSITO")
```

Use real newlines in multi-line text (don't escape `\n` — escaped produces literal backslash-n):

```python
# CORRECT:
set_text(nodeId, text="Line 1\nLine 2")

# WRONG (produces literal \n characters):
set_text(nodeId, text="Line 1\\nLine 2")
```

## Step 4: Check for Overflow

```python
get_nodes_info(nodeIds=["674:26", "674:27"])
# Check: bounds.height vs original height
# If height grew → text is wrapping → font too large
```

**Overflow signal:** A text node that was single-line (e.g., 103px at 40px font) now shows 206px — it wrapped to 2 lines. Need font reduction.

## Step 5: Adjust Font Size

Two-step process since `set_text` alone doesn't change font size:

```python
# 1. Create a text style with smaller font
create_text_style(
    name="Heading/Deposit-ES",
    fontFamily="Inknut Antiqua",
    fontSize=32,
    fontStyle="ExtraBold"
)

# 2. Apply it to the overflowing node
apply_style_to_node(
    nodeId="674:26",
    styleId="S:20e9e5731f6aa3986ea94b495ebe8b6c35ed079e,"
)
```

## Step 6: Screenshot & Verify

```python
save_screenshots(items=[{
    nodeId: "674:2",
    outputPath: "4xiban_es.png",
    scale: 2
}])
```

Output path must be within the working directory. Check `get_metadata` for allowed paths.

## Per-Language Font Size Ratios

Empirical ratios from this session (original → translated):

| Language | Heading | Description | Column Headers | Notes |
|----------|---------|-------------|----------------|-------|
| Spanish | 40→32 (0.80x) | 24→18 (0.75x) | 32→22 (0.69x) | "Bono por Invitación" wider than English |
| French | 40→34 (0.85x) | 35→26 (0.74x) | 32→22 (0.69x) | French tends to be ~1.3x longer |
| Portuguese | 40→34 (0.85x) | — | 32→22 (0.69x) | Similar to Spanish in length |
| Arabic | no change | no change | no change | Arabic script is compact — rarely needs reduction |

**Rule of thumb:** Start by checking the heading. If it wraps, reduce to ~0.8x. Column headers in table layouts almost always need reduction (0.7x) for Romance languages.

## Font Families Per Page Template

Pages in this project use specific fonts per template variant:

| Template | Heading Font | Body Font | Number Font |
|----------|-------------|-----------|-------------|
| 4xiban | Inknut Antiqua ExtraBold 40 | Inter SemiBold 24-32 | Inter SemiBold 28 |
| 5xiban | Holtwood One SC 60 | Inter SemiBold 23-32 | Inter SemiBold 28 |
| 6xiban | Inria Serif Bold 60 (LV) | Inter ExtraBold Italic 40 | Inter SemiBold Italic 25 |
| M1 variant | Inder Regular 50 | Inter SemiBold 35 | Inter SemiBold 28 |
| M2 variant | DIN Alternate Bold 80 | Inter SemiBold 23 | Iosevka Charon Bold 34 |
| M3 variant | Inter ExtraBold Italic 40 | Inter SemiBold Italic 25 | Inter ExtraBold Italic 26 |

When creating text styles for overflow fixes, match the font family exactly — `apply_style_to_node` will replace the font if mismatched.

## Mixed-Formatting Warning

`set_text` replaces the entire text content. If the original had per-character formatting:
- Numbers in different color than body text
- "5%" in red within a black paragraph
- Mixed font weights within one node

These are LOST after `set_text`. There is no MCP tool to set per-character formatting. **User must manually restore in Figma.** Always warn the user which nodes had `fontName:"mixed"` or `fills:"mixed"` after translation.

## Page Clone Pattern (Multi-Language Batch)

When a project has the same design cloned across pages/languages, work in this order:

1. **Translate the first language completely** — text + font adjustments + screenshot verification
2. **Copy text styles for remaining languages** — reuse style IDs via `apply_style_to_node` instead of creating new styles per language
3. **Batch translate remaining languages** — all `set_text` calls first, then check overflow, then apply pre-existing styles

**Style reuse example** (this session — 30 pages, 4 languages):

```
Style                    ID          Used for
Heading/Deposit-FR (34)  S:0052c807  M1 French, M1 Portuguese, M1 Spanish
Heading/Invite-FR (48)   S:bc5c217c  M2 French, M2 Portuguese, M2 Spanish, M2 Arabic
ColHeader/FR (22)        S:052bba4c  All M2 columns (FR, PT, ES, AR)
Body/Desc-M1 (26)        S:9d1f2040  All M1 descriptions (FR, PT, ES, AR)
```

This saves ~20 `create_text_style` calls per multi-language project.

## Multi-Language Audit

After translating all languages, run a comparative audit against English originals:

1. Scan text from English templates → compare to each translation
2. Flag: original typos that propagated ("eash", "CALCULATEDAS", "rewaro", "ofthe")
3. Flag: content shortened for container fit (user must approve)
4. Flag: mixed-format nodes where per-character coloring was lost

**Typo discovery pattern**: originals with typos → all translations inherit them. Fix typos at source first, then re-translate.

## Batch Export

Export all frames to a dedicated directory in batches of 10:

```python
save_screenshots(items=[
    {nodeId: "668:4", outputPath: "all_pngs/1_original.png", scale: 2},
    # ... up to 10 items per call
])
# File-already-exists → skip, move to next batch
```

**Frame naming convention**: `{nodeId}: {frameName}` — the MCP keeps the original frame name. Watch for naming typos (e.g., "M3Franch" instead of "M3French") when searching.

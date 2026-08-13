# Figma Translation Patterns

Language-specific font adjustments, style reuse, and multi-language frame conventions from production sessions.

## Known Font Adjustments by Language

| Language | Heading (40px) | Heading (50px Inder) | Heading (60px Holtwood) | Heading (80px DIN Alt) | Column Headers (32px) | Description (35px) | Desc Body (32px) | Disclaimer (28px) |
|---|---|---|---|---|---|---|---|---|
| Spanish (es) | 32px | 34px | 48px | 48px | 22px | 26px | 26px | 20px |
| French (fr) | 34px | 34px | 48px | 48px | 22px | 26px | 26px | — |
| Portuguese (pt) | 34px | 34px | 48px | 48px | 22px | 26px | — | — |
| Arabic (ar) | — | — | — | — | — | — | — | — |

Arabic is compact — typically no adjustments needed. RTL alignment must be done manually in Figma.

## Reusable Style IDs

These styles were created during multi-language translation sessions and can be reused across frames:

| Style ID | Name | Font | Size | LineH | Use Case |
|---|---|---|---|---|---|
| S:...2dbdb3, | Heading/Deposit-FR | Inknut Antiqua ExtraBold | 34px | — | Deposit page heading (FR, ES, PT) |
| S:...f1169, | Heading/Invite-FR | Holtwood One SC | 48px | — | Invitation page heading (FR, ES, PT) |
| S:...f8da2, | ColHeader/FR | Inter SemiBold | 22px | 24px | Table column headers (all langs) |
| S:...3016de, | Body/Desc-M1 | Inter SemiBold | 26px | — | M1 variant description (LS 10%) |
| S:...5ed17, | Tier/ES | Inter SemiBold | 20px | 28px | Tier values in table |

To find the full style IDs in a session: run `get_styles` and grep for the name.

## Multi-Language Frame Naming Convention

Typical file structure when one design is cloned for multiple languages:

```
Frame name      Template        Content
─────────────────────────────────────────
4xiban          4xiban clone    First deposit bonus + tier table
5xiban          5xiban clone    Invitation bonus + examples
6xiban          6xiban clone    Trading signals tier list
7abaric         4xiban clone    (Arabic variant)
8abaric         5xiban clone    (Arabic variant)
9abaric         6xiban clone    (Arabic variant)
10French        4xiban clone    (French variant)
11French        5xiban clone    (French variant)
12French        6xiban clone    (French variant)
13pt            4xiban clone    (Portuguese variant)
14pt            5xiban clone    (Portuguese variant)
15pt            6xiban clone    (Portuguese variant)
M1spanish       M1 variant      First deposit (Inder font, different copy)
M2spanish       M2 variant      Invitation bonus (DIN Alternate, condensed)
M3spanish       M3 variant      Trading signals (merged Extra label)
M1abaric        M1 variant      (Arabic)
M2abaric        M2 variant      (Arabic)
M3abaric        M3 variant      (Arabic)
M1French        M1 variant      (French)
M2French        M2 variant      (French)
M3Franch        M3 variant      (French — note typo in name)
M1pt            M1 variant      (Portuguese)
M2pt            M2 variant      (Portuguese)
M3pt            M3 variant      (Portuguese)
```

The M-series variants differ from the numbered series:
- **M1 variants**: Use Inder font at 50px for heading, different copy ("Enjoy a flat 5% bonus on your first deposit...")
- **M2 variants**: Use DIN Alternate at 80px for heading, Iosevka Charon for numbers, condensed layout
- **M3 variants**: Merged "Extra Signals: 5" into the same text node as trading signals, LV labels at 40px Inter ExtraBold instead of 60px Inria Serif

## Translation Workflow Checklist

1. `search_nodes query="framename"` → find target frame IDs
2. `scan_text_nodes nodeId="..."` → list all text nodes
3. Identify: numbers-only nodes (skip), LV labels (skip), English text (translate)
4. Note: `fontName:"mixed"` nodes — warn user about manual color fix
5. `set_text` for each translatable node (use real newlines, not `\n`)
6. `get_nodes_info` on translated nodes → check bounds.height
7. For overflow: reuse existing style or `create_text_style` → `apply_style_to_node`
8. `get_nodes_info` again → verify heights fit within parent containers
9. `save_screenshots` at scale:2 → visual confirmation
10. `terminal command="open ..."` → show user the result

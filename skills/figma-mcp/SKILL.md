---
name: figma-mcp
description: >-
  Connect Codex or ChatGPT to Figma, inspect node URLs, edit designs, translate
  text, manage styles and variables, and verify screenshots. Routes explicitly
  between the official Codex Figma plugin and an optional local figma-mcp-go
  bridge, including current-selection limitations, safe write workflows, text
  formatting preservation, and overflow checks. Use for Figma connection tests,
  node inspection, design-to-code context, scoped edits, exports, or translation.
---

# Figma MCP Operations

Use this skill as a router. First identify the Figma backend actually exposed in
the current session, then follow that backend's contract. A skill installation by
itself does not provide Figma access.

## 1. Detect the Backend

Inspect the available tools before claiming a connection.

| Backend | Runtime signal | Target model |
|---|---|---|
| Official Codex Figma plugin | Tools such as `mcp__codex_apps__figma_whoami`, `...get_design_context`, and `...use_figma` | URL/file-key based; do not assume access to the desktop selection |
| Local `figma-mcp-go` bridge | Tools such as `get_selection`, `scan_text_nodes`, `set_text`, and `get_nodes_info` | Selection-aware while its Figma editor plugin and local MCP server are running |
| No backend | No callable Figma tools | Skill installed, Figma not connected |

Never mix tool names or capabilities from the two backends. In particular, do
not promise `get_selection` when only the official Codex plugin is available.

Read [references/codex-backends.md](references/codex-backends.md) for the full
capability matrix, package audit, local bridge setup, and security boundaries.

For the exact signature of every local-bridge tool (73 tools: parameters,
required fields, descriptions), read
[references/tools-reference.md](references/tools-reference.md). A machine-readable
copy of the full `tools/list` output lives in
[references/tools-schema.json](references/tools-schema.json) — load it directly
when you need exact JSON Schemas for tool calls.

## 2. Report the Access State

Start connection and test responses with exactly one state:

- `Connected`: authentication works and a concrete Figma target is available.
- `Connected but no target selected`: authentication works, but no usable URL,
  file key, page, or node is in scope.
- `Not connected`: the session exposes no working Figma backend.

For the official Codex plugin, `whoami` is an authentication smoke test only. It
does not identify an open Figma file or the user's current desktop selection.
Do not print account details returned by the test unless the user asks for them.

Read [references/chatgpt-connection.md](references/chatgpt-connection.md) when
the user asks how to connect, asks for a test, or reports missing tools.

## 3. Resolve the Target

### Official Codex plugin

Prefer a Figma URL. Extract its file key and, when present, convert
`node-id=123-456` to node ID `123:456`.

- A `/design/` URL without `node-id` can be used to list top-level pages with
  `get_metadata`; node inspection still requires a concrete node ID.
- `/board/`, `/slides/`, and `/make/` have different tool support. Check the
  selected tool's schema instead of assuming design-file behavior.
- If the user says "selected node" but gives no node-specific URL, ask them to
  copy the link to that node from Figma. Never guess a node ID.
- For branch URLs, use the branch key where the official tool contract requires
  it.

### Local bridge

Use `get_selection` to resolve the live Figma editor selection. If it returns
zero or multiple nodes and the requested scope is singular, stop and ask the
user to select exactly one node. For very large selections, follow
[references/get_selection-truncation.md](references/get_selection-truncation.md).

**Tool family overview** (73 tools total — full signatures in
[references/tools-reference.md](references/tools-reference.md)):

| Family | Tools |
|---|---|
| Read & inspect | `get_selection`, `get_metadata`, `get_pages`, `get_document`, `get_node`, `get_nodes_info`, `get_design_context`, `get_viewport`, `get_fonts`, `get_annotations`, `get_reactions`, `search_nodes`, `scan_text_nodes`, `scan_nodes_by_types` |
| Screenshot & export | `get_screenshot`, `save_screenshots`, `export_frames_to_pdf`, `export_tokens` |
| Text | `set_text`, `find_replace_text`, `create_text` |
| Create | `create_frame`, `create_rectangle`, `create_ellipse`, `create_section`, `create_component`, `clone_node`, `import_image`, `add_page` |
| Style | `set_fills`, `set_strokes`, `set_effects`, `set_blend_mode`, `set_opacity`, `set_corner_radius`, `set_visible`, `set_constraints`, `set_auto_layout` |
| Layout & structure | `move_nodes`, `resize_nodes`, `rotate_nodes`, `reorder_nodes`, `group_nodes`, `ungroup_nodes`, `reparent_nodes`, `lock_nodes`, `unlock_nodes`, `rename_node`, `rename_page`, `navigate_to_page`, `delete_nodes`, `delete_page`, `detach_instance`, `swap_component`, `batch_rename_nodes` |
| Design system | `create_paint_style`, `create_text_style`, `create_effect_style`, `create_grid_style`, `update_paint_style`, `apply_style_to_node`, `delete_style`, `create_variable_collection`, `create_variable`, `add_variable_mode`, `delete_variable`, `set_variable_value`, `bind_variable_to_node` |
| Reactions | `set_reactions`, `remove_reactions` |

## 4. Read-Only Workflow

Use the smallest call that answers the question.

### Official Codex plugin

1. Run `whoami` only when authentication needs testing.
2. With a target URL, prefer `get_design_context` for structured inspection.
3. Use `get_metadata` for a lightweight page or hierarchy overview.
4. Use `get_screenshot` for visual verification when a node ID is available.
5. Report the file key, node IDs, and any unsupported file-type limitation.

### Local bridge

1. Run `get_metadata` to confirm file and page.
2. Run `get_selection` or `get_design_context(depth=1)` to resolve scope.
3. Use `scan_text_nodes` for translation or copy audits.
4. Use `get_node` or `get_nodes_info` for exact properties and bounds.

Do not use a write tool merely to test connectivity.

## 5. Write Workflow

Every edit follows: inspect, mutate, verify, report.

### Official Codex plugin

1. Load the official `figma-use` skill before every `use_figma` call.
2. Inspect the target and existing design system before creating or changing it.
3. Keep each call small. Use top-level `await`; return every mutated or created
   node ID; do not use `figma.closePlugin()` or rely on `console.log()` output.
4. For text, load every font used by the current styled ranges before assigning
   characters. Preserve mixed styles intentionally.
5. Verify structure and appearance with returned IDs, metadata, bounds, and a
   screenshot. If the tool errors, inspect the error before retrying.

### Local bridge

1. Re-read the exact node immediately before mutation.
2. Use the narrowest direct tool, such as `set_text` or `set_fills`.
3. Re-read changed nodes and compare bounds; export a screenshot when visual
   correctness matters.
4. Treat destructive or batch operations as high impact and make the node list
   explicit before calling them.

The bundled local bridge's `set_text` loads only one font and falls back to
Inter Regular for mixed-font nodes. Mixed-format text can fail or lose range
fidelity. Prefer the official `use_figma` text recipe when preservation matters;
otherwise disclose the caveat and verify the styled ranges after editing.

## 6. Translation and Overflow

**⛔ IRON RULE — TEXT NODES ONLY.** Images, rectangles, and vector nodes are
never translated. Only TEXT nodes get `set_text`. Screenshots are verification
only, never a translation source or edit target. The bundled scripts enforce
this: `scan_text_nodes` returns only text, and both translate scripts re-check
live node types before writing. Text baked into images stays as-is.

For text translation:

1. **Translate ONLY (user-mandated, highest priority).** Do NOT record box
   sizes, adjust font sizes, letter spacing, or dimensions — any auto-fit /
   font-size / spacing adjustment makes the design worse and causes rework.
2. Translate the full meaning. Do not shorten or omit content merely to fit.
3. Preserve deliberate line breaks with actual newline characters, not the
   literal two-character sequence `\\n`.
4. Apply the translation through the active backend.
5. Re-read the text and styled ranges, compare bounds, and inspect a screenshot.
6. If text overflows, **DO NOT auto-shrink fonts or adjust spacing — ask the
   user how to proceed first.**

**Automated path (recommended for multi-language batches).** The bundled
scripts drive the whole pipeline — no manual MCP calls needed:

```bash
# 1. dump all text of a frame (order = translation index)
node scripts/scan-frame.js 851:7

# 2. build translations.json (template: scripts/translations.template.json),
#    then clone + translate + verify in one shot:
node scripts/translate-frame.js 851:7 translations.json
#    env: FONT_FIX="hy:Arial Unicode MS" for scripts the source font lacks
#         (omit when the source font already has the target script — clones inherit it)
#    env: GRID_COLS=3  GRID_GAP=300  NAME_PREFIX=""
#    env: GRID_X0=... GRID_Y0=...  override the grid anchor to steer clones
#         clear of other frames stacked below the source (multi-frame translate)

# 2b. frame already exists (language clone with placeholder text)? No clone:
node scripts/translate-inplace.js 897:8317 translations.json
#    env: SHOT=1 to also export <frame>.png for an ink check

# 3. ad-hoc tool calls from any client / language (full output, no truncation):
node scripts/mcp-client.js 1994 get_selection
node scripts/mcp-client.js 1994 scan_text_nodes '{"nodeId":"851:7"}'

# 4. fast render verification instead of OCR (needs PIL):
python3 scripts/ink-check.py <exported.png> [--white-text] [--min 5]
```

Read [references/translation-playbook.md](references/translation-playbook.md)
for the full validated workflow: font coverage table (Arial Unicode MS is the
only verified Armenian-capable font), overflow ratios, mixed-format warning,
and bridge-restart rules.

For multi-language sizing, style reuse, and batch checks, read:

- [references/translation-workflow.md](references/translation-workflow.md)
- [references/translation-patterns.md](references/translation-patterns.md)
- [references/font-size-table.md](references/font-size-table.md)
- [references/bulk-translation-checklist.md](references/bulk-translation-checklist.md)
- [references/multi-language-batch.md](references/multi-language-batch.md)

## 7. Response Contract

After a successful read, report the backend, target URL/file key, inspected node
IDs, and concise findings. After a write, report changed node IDs, formatting or
layout caveats, and the verification performed.

When blocked, give the smallest concrete next action. For the official Codex
plugin, that is usually a node-specific Figma URL. For the local bridge, it is
usually opening the Figma development plugin, keeping it on loopback, starting
the MCP server, or selecting exactly one node.

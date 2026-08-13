# figma-mcp-go Tool Reference

Complete reference for the **73 MCP tools** exposed by the local `figma-mcp-go` bridge
(v0.1.3). This bridge reads and edits the node currently selected in the **Figma
Desktop editor** through a development plugin over a loopback WebSocket.

```
┌────────────┐  MCP stdio   ┌──────────────┐  ws://127.0.0.1:1994/ws  ┌──────────────┐
│ AI Agent   │ ───────────▶ │ figma-mcp-go │ ─────────────────────────▶ │ Figma plugin │
│ (Codex,    │ ◀─────────── │   (server)   │ ◀───────────────────────── │  (in editor) │
│  Hermes…)  │   JSON-RPC   └──────────────┘        JSON-RPC            └──────────────┘
└────────────┘
```

## Quick Start for Any Agent

1. **Prereqs**: Figma Desktop open with a file, the **Figma MCP Go** development
   plugin running (Plugins → Development → Figma MCP Go, port matching the
   server, e.g. 1994), and the MCP server registered in your client.
2. **Resolve scope first** (read-only):
   - `get_selection` — what is selected in the editor right now
   - `get_metadata` — current file + page name
   - `get_pages` / `get_document` — file structure
3. **Inspect before you write.** Use `get_node`, `get_nodes_info`, or
   `get_design_context(depth=1)` to see bounds, fills, fonts, and children.
4. **Write narrow, then verify.** Edit the smallest node, re-read it, and check
   bounds / screenshot if layout matters.
5. **Never mix with the official Codex Figma plugin** — the official plugin is
   URL/file-key based and does not see the desktop selection; this bridge is
   selection-based. Use one backend per session.

## Conventions

- Node IDs are colon format: `851:7` (from URL `node-id=851-7`).
- Colors: hex strings like `"#ff0000"` (CSS-style, may include alpha).
- Fonts: `fontFamily` + `fontStyle` (e.g. `"Inter"`, `"Bold"`).
- `nodeIds` params accept arrays: `["851:7", "851:8"]`.
- Most write tools accept `parentId` (default: current page or selection parent).

---


## Read & Inspect

### `get_annotations`

Get dev-mode annotations in the current document or scoped to a specific node. Returns annotation objects with label text, measurement type, and the ID of the annotated node. Omit nodeId to retrieve all annotations on the current page.

**Parameters:**
- `nodeId` (string, opt) — Optional — scope results to annotations on this node and its descendants, colon format e.g. '4029:12345'

### `get_design_context`

Get a depth-limited, token-efficient tree of the current selection or page. Use this instead of get_document when exploring large files. Supports detail levels (minimal/compact/full) and dedupe_components for pages heavy with repeated component instances.

**Parameters:**
- `dedupe_components` (boolean, opt) — When true, INSTANCE nodes are serialized compactly (mainComponentId + componentProperties + overrides array of differing text/nested content) and unique component definitions are collected once in a top-level componentDefs map. Highly token-efficient for screens with many repeated component instances.
- `depth` (number, opt) — How many levels deep to traverse (default 2)
- `detail` (string, opt) — Property verbosity: minimal (id/name/type/bounds only), compact (+fills/strokes/opacity), full (everything, default)

### `get_document`

Get the full node tree of the current page (not the whole file — only the active page). Returns all nodes recursively and can be very large. Prefer get_design_context for exploration or when token efficiency matters.

### `get_fonts`

List all fonts used in the current page, sorted by usage frequency. Useful for understanding typography without scanning all text nodes.

### `get_local_components`

Get all components defined in the current Figma file.

### `get_metadata`

Get metadata about the current Figma document: file name, pages, current page

### `get_node`

Get a single node by ID with full detail. Use get_nodes_info to fetch multiple nodes in one round-trip instead of calling this repeatedly. Node ID must be colon format e.g. '4029:12345', never hyphens.

**Required:** `nodeId`

**Parameters:**
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'

### `get_nodes_info`

Get full details for multiple nodes by ID in one round-trip. Prefer this over calling get_node repeatedly when you need several nodes.

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — List of node IDs in colon format e.g. ['4029:12345', '4029:67890']

### `get_pages`

List all pages in the document with their IDs and names. Lightweight alternative to get_document.

### `get_reactions`

Get the prototype reactions defined on a node. Returns an array of reaction objects — each has a trigger (e.g. ON_CLICK, ON_HOVER, AFTER_TIMEOUT) and an actions array (navigate to node, open URL, go back, etc.). Use set_reactions to add or replace reactions, remove_reactions to delete them.

**Required:** `nodeId`

**Parameters:**
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'

### `get_selection`

Get the nodes currently selected in Figma. Returns an empty array if nothing is selected. Use get_design_context or get_node to retrieve deeper detail about a specific node by ID.

### `get_styles`

Get all local styles in the document (paint, text, effect, and grid). Returns each style's ID, name, type, and properties. Use the style ID with apply_style_to_node or update_paint_style. For design tokens (variables), use get_variable_defs instead.

### `get_variable_defs`

Get all local variable definitions: collections, modes, and values. Variables are Figma's design token system.

### `get_viewport`

Get the current Figma viewport: scroll center, zoom level, and visible bounds.

### `scan_nodes_by_types`

Find all nodes of specific types in a subtree, regardless of name. Use search_nodes instead when you need to filter by name.

**Required:** `nodeId`, `types`

**Parameters:**
- `nodeId` (string, req) — Root node ID to scan from, colon format e.g. '4029:12345'
- `types` (array, req) — Node types to find e.g. ['FRAME', 'COMPONENT', 'INSTANCE']

### `scan_text_nodes`

Scan all TEXT nodes in a subtree and return their content. Shorthand for scan_nodes_by_types with ['TEXT'] — use when you only need text copy from a component or frame.

**Required:** `nodeId`

**Parameters:**
- `nodeId` (string, req) — Root node ID to scan from, colon format e.g. '4029:12345'

### `search_nodes`

Search for nodes by name substring and/or type within a subtree. Use this when you know (part of) the node name. Use scan_nodes_by_types when you want all nodes of a type regardless of name.

**Required:** `query`

**Parameters:**
- `limit` (number, opt) — Maximum results to return (default: 50)
- `nodeId` (string, opt) — Scope search to this subtree (default: current page), colon format e.g. '4029:12345'
- `query` (string, req) — Name substring to match (case-insensitive)
- `types` (array, opt) — Filter by Figma node type e.g. ['TEXT', 'FRAME', 'COMPONENT']

---

## Screenshot & Export

### `export_frames_to_pdf`

Export multiple frames as a single multi-page PDF file. Each frame becomes one page in order. Ideal for pitch decks, proposals, and slide exports.

**Required:** `nodeIds`, `outputPath`

**Parameters:**
- `nodeIds` (array, req) — Ordered list of frame node IDs to export as PDF pages, colon format e.g. '4029:12345'
- `outputPath` (string, req) — File path to write the PDF to, must end in .pdf (relative to working directory or absolute)

### `export_tokens`

Export all design tokens (variables and paint styles) as JSON or CSS custom properties. Ideal for bridging Figma variables into your codebase.

**Parameters:**
- `format` (string, opt) — Output format: json (default) or css

### `get_screenshot`

Export a screenshot of one or more nodes as base64-encoded image data (held in memory). Use save_screenshots instead when you want to write images directly to disk without base64 in the response.

**Parameters:**
- `format` (string, opt) — Export format: PNG (default), SVG, JPG, or PDF
- `nodeIds` (array, opt) — Optional node IDs to export, colon format. If empty, exports current selection.
- `scale` (number, opt) — Export scale for raster formats (default 2)

### `save_screenshots`

Export screenshots for multiple nodes and write them to the local filesystem. Returns file metadata (path, size, dimensions) — no base64 in the response. Use get_screenshot instead when you need the image data in memory.

**Required:** `items`

**Parameters:**
- `format` (string, opt) — Default export format: PNG (default), SVG, JPG, or PDF
- `items` (array, req) — List of {nodeId, outputPath, format?, scale?} objects
- `scale` (number, opt) — Default export scale for raster formats (default 2)

---

## Text Editing

### `create_text`

Create a new text node on the current page or inside a parent node. The font is loaded automatically before insertion. Returns the created node ID and bounds. Use set_text to update the content of an existing text node.

**Required:** `text`

**Parameters:**
- `fillColor` (string, opt) — Text color as hex e.g. #000000 (default black)
- `fontFamily` (string, opt) — Font family name e.g. 'Inter', 'Roboto', 'SF Pro Display' (default Inter). Must be a font installed in Figma.
- `fontSize` (number, opt) — Font size in pixels (default 14)
- `fontStyle` (string, opt) — Font style variant e.g. 'Regular', 'Bold', 'Italic', 'Medium', 'SemiBold' (default Regular). Must match an available style for the chosen fontFamily.
- `name` (string, opt) — Node name shown in the layers panel (defaults to the text content)
- `parentId` (string, opt) — Parent node ID in colon format. Defaults to current page.
- `text` (string, req) — Text content to display
- `x` (number, opt) — X position in pixels (default 0)
- `y` (number, opt) — Y position in pixels (default 0)

### `find_replace_text`

Find and replace text content across all TEXT nodes in a subtree. Searches the entire current page if no nodeId is given.

**Required:** `find`, `replace`

**Parameters:**
- `find` (string, req) — Text string (or regex pattern when useRegex=true) to search for
- `nodeId` (string, opt) — Root node ID to scope the search. Defaults to the entire current page.
- `regexFlags` (string, opt) — Regex flags e.g. 'gi' (default 'g'). Only used when useRegex=true.
- `replace` (string, req) — Replacement string (use empty string to delete matches)
- `useRegex` (boolean, opt) — Treat find as a regular expression (default false)

### `set_text`

Update the text content of an existing TEXT node.

**Required:** `nodeId`, `text`

**Parameters:**
- `nodeId` (string, req) — TEXT node ID in colon format e.g. '4029:12345'
- `text` (string, req) — New text content

---

## Create

### `add_page`

Add a new page to the Figma document.

**Parameters:**
- `index` (number, opt) — Position index to insert the page (0 = first). Defaults to last position.
- `name` (string, opt) — Name for the new page (default 'Page')

### `clone_node`

Clone an existing node, optionally repositioning it or placing it in a new parent.

**Required:** `nodeId`

**Parameters:**
- `nodeId` (string, req) — Source node ID in colon format e.g. '4029:12345'
- `parentId` (string, opt) — Parent node ID for the clone. Defaults to same parent as source.
- `x` (number, opt) — X position of the clone
- `y` (number, opt) — Y position of the clone

### `create_component`

Convert an existing FRAME node into a reusable COMPONENT. The frame is replaced in place by the new component.

**Required:** `nodeId`

**Parameters:**
- `name` (string, opt) — Optional name for the component. Defaults to the frame's current name.
- `nodeId` (string, req) — FRAME node ID to convert, in colon format e.g. '4029:12345'

### `create_ellipse`

Create a new ellipse (circle/oval) on the current page or inside a parent node.

**Parameters:**
- `fillColor` (string, opt) — Fill color as hex e.g. #3B82F6
- `height` (number, opt) — Height in pixels (default 100)
- `name` (string, opt) — Ellipse name
- `parentId` (string, opt) — Parent node ID in colon format. Defaults to current page.
- `width` (number, opt) — Width in pixels (default 100)
- `x` (number, opt) — X position (default 0)
- `y` (number, opt) — Y position (default 0)

### `create_frame`

Create a new frame on the current page or inside a parent node.

**Parameters:**
- `counterAxisAlignItems` (string, opt) — Cross-axis alignment: MIN, CENTER, MAX, or BASELINE
- `counterAxisSizingMode` (string, opt) — Cross-axis sizing: FIXED or AUTO (hug)
- `counterAxisSpacing` (number, opt) — Gap between wrapped rows/columns (only when layoutWrap is WRAP)
- `fillColor` (string, opt) — Fill color as hex e.g. #FFFFFF
- `height` (number, opt) — Height in pixels (default 100)
- `itemSpacing` (number, opt) — Auto-layout gap between children
- `layoutMode` (string, opt) — Auto-layout direction: HORIZONTAL, VERTICAL, or NONE
- `layoutWrap` (string, opt) — Wrap behaviour: NO_WRAP or WRAP
- `name` (string, opt) — Frame name
- `paddingBottom` (number, opt) — Auto-layout bottom padding
- `paddingLeft` (number, opt) — Auto-layout left padding
- `paddingRight` (number, opt) — Auto-layout right padding
- `paddingTop` (number, opt) — Auto-layout top padding
- `parentId` (string, opt) — Parent node ID in colon format. Defaults to current page.
- `primaryAxisAlignItems` (string, opt) — Main-axis alignment: MIN, CENTER, MAX, or SPACE_BETWEEN
- `primaryAxisSizingMode` (string, opt) — Main-axis sizing: FIXED or AUTO (hug)
- `width` (number, opt) — Width in pixels (default 100)
- `x` (number, opt) — X position (default 0)
- `y` (number, opt) — Y position (default 0)

### `create_rectangle`

Create a new rectangle on the current page or inside a parent node.

**Parameters:**
- `cornerRadius` (number, opt) — Corner radius in pixels
- `fillColor` (string, opt) — Fill color as hex e.g. #FF5733
- `height` (number, opt) — Height in pixels (default 100)
- `name` (string, opt) — Rectangle name
- `parentId` (string, opt) — Parent node ID in colon format. Defaults to current page.
- `width` (number, opt) — Width in pixels (default 100)
- `x` (number, opt) — X position (default 0)
- `y` (number, opt) — Y position (default 0)

### `create_section`

Create a Figma Section node on the current page. Sections are the modern way to organize frames and groups on a page.

**Parameters:**
- `height` (number, opt) — Height in pixels
- `name` (string, opt) — Section name (default 'Section')
- `width` (number, opt) — Width in pixels
- `x` (number, opt) — X position (default 0)
- `y` (number, opt) — Y position (default 0)

### `import_image`

Import a base64-encoded image into Figma as a rectangle with an image fill. Use get_screenshot to capture images or provide your own base64 PNG/JPG.

**Required:** `imageData`

**Parameters:**
- `height` (number, opt) — Height in pixels (default 200)
- `imageData` (string, req) — Base64-encoded image data (PNG or JPG)
- `name` (string, opt) — Node name
- `parentId` (string, opt) — Parent node ID in colon format. Defaults to current page.
- `scaleMode` (string, opt) — Image scale mode: FILL (default), FIT, CROP, or TILE
- `width` (number, opt) — Width in pixels (default 200)
- `x` (number, opt) — X position (default 0)
- `y` (number, opt) — Y position (default 0)

---

## Style & Fill & Effects

### `set_auto_layout`

Set or update auto-layout (flex) properties on an existing frame.

**Required:** `nodeId`

**Parameters:**
- `counterAxisAlignItems` (string, opt) — Cross-axis alignment: MIN, CENTER, MAX, or BASELINE
- `counterAxisSizingMode` (string, opt) — Cross-axis sizing: FIXED or AUTO (hug)
- `counterAxisSpacing` (number, opt) — Gap between wrapped rows/columns (only when layoutWrap is WRAP)
- `itemSpacing` (number, opt) — Gap between children
- `layoutMode` (string, opt) — Auto-layout direction: HORIZONTAL, VERTICAL, or NONE
- `layoutWrap` (string, opt) — Wrap behaviour: NO_WRAP or WRAP
- `nodeId` (string, req) — Frame node ID in colon format e.g. '4029:12345'
- `paddingBottom` (number, opt) — Bottom padding
- `paddingLeft` (number, opt) — Left padding
- `paddingRight` (number, opt) — Right padding
- `paddingTop` (number, opt) — Top padding
- `primaryAxisAlignItems` (string, opt) — Main-axis alignment: MIN, CENTER, MAX, or SPACE_BETWEEN
- `primaryAxisSizingMode` (string, opt) — Main-axis sizing: FIXED or AUTO (hug)

### `set_blend_mode`

Set the blend mode of one or more nodes (e.g. MULTIPLY, SCREEN, OVERLAY).

**Required:** `nodeIds`, `blendMode`

**Parameters:**
- `blendMode` (string, req) — Blend mode: NORMAL, MULTIPLY, SCREEN, OVERLAY, DARKEN, LIGHTEN, COLOR_DODGE, COLOR_BURN, HARD_LIGHT, SOFT_LIGHT, DIFFERENCE, EXCLUSION, HUE, SATURATION, COLOR, LUMINOSITY, PASS_THROUGH
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']

### `set_constraints`

Set layout constraints (pinning behaviour) on one or more nodes relative to their parent.

**Required:** `nodeIds`

**Parameters:**
- `horizontal` (string, opt) — Horizontal constraint: MIN (left), MAX (right), CENTER, STRETCH, or SCALE
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `vertical` (string, opt) — Vertical constraint: MIN (top), MAX (bottom), CENTER, STRETCH, or SCALE

### `set_corner_radius`

Set corner radius on one or more nodes. Provide a uniform cornerRadius or individual per-corner values.

**Required:** `nodeIds`

**Parameters:**
- `bottomLeftRadius` (number, opt) — Bottom-left corner radius
- `bottomRightRadius` (number, opt) — Bottom-right corner radius
- `cornerRadius` (number, opt) — Uniform corner radius applied to all corners
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `topLeftRadius` (number, opt) — Top-left corner radius
- `topRightRadius` (number, opt) — Top-right corner radius

### `set_effects`

Apply one or more effects (drop shadow, inner shadow, layer blur, background blur) directly to a node. Replaces all existing effects. Pass an empty array to clear all effects.

**Required:** `nodeId`, `effects`

**Parameters:**
- `effects` (array, req) — Array of effect objects. Each has: type (DROP_SHADOW | INNER_SHADOW | LAYER_BLUR | BACKGROUND_BLUR), radius, color (hex, shadows only), opacity (0–1, shadows only), offsetX, offsetY (shadows only), spread (shadows only), visible (default true)
- `nodeId` (string, req) — Target node ID in colon format e.g. 4029:12345

### `set_fills`

Set the fill color on a single node (takes one nodeId, not an array). Use mode='append' to stack a new fill on top of existing fills instead of replacing them.

**Required:** `nodeId`, `color`

**Parameters:**
- `color` (string, req) — Fill color as hex: #RRGGBB e.g. #FF5733 or #RRGGBBAA e.g. #FF573380 for 50% alpha
- `mode` (string, opt) — 'replace' (default) overwrites all existing fills; 'append' stacks this fill on top of existing ones
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'
- `opacity` (number, opt) — Fill opacity 0–1 (default 1). Combines multiplicatively with any alpha in the color hex.

### `set_opacity`

Set the opacity of one or more nodes (0 = fully transparent, 1 = fully opaque).

**Required:** `nodeIds`, `opacity`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `opacity` (number, req) — Opacity value between 0 and 1

### `set_strokes`

Set the stroke color and weight on a single node (takes one nodeId, not an array). Use mode='append' to stack a new stroke on top of existing strokes instead of replacing them.

**Required:** `nodeId`, `color`

**Parameters:**
- `color` (string, req) — Stroke color as hex e.g. #000000
- `mode` (string, opt) — 'replace' (default) overwrites all strokes; 'append' stacks on top of existing strokes
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'
- `strokeWeight` (number, opt) — Stroke weight in pixels (default 1)

### `set_visible`

Show or hide one or more nodes by setting their visibility.

**Required:** `nodeIds`, `visible`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `visible` (boolean, req) — true to show the node, false to hide it

---

## Layout & Structure

### `batch_rename_nodes`

Rename multiple nodes using find/replace, regex substitution, or prefix/suffix addition.

**Required:** `nodeIds`

**Parameters:**
- `find` (string, opt) — String (or regex pattern when useRegex=true) to search for in the node name
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `prefix` (string, opt) — String to prepend to the node name
- `regexFlags` (string, opt) — Regex flags e.g. 'gi' (default 'g'). Only used when useRegex=true.
- `replace` (string, opt) — Replacement string. Required when find is provided.
- `suffix` (string, opt) — String to append to the node name
- `useRegex` (boolean, opt) — Treat find as a regular expression (default false)

### `delete_nodes`

Delete one or more nodes. This cannot be undone via MCP — use with care.

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — Node IDs to delete in colon format e.g. ['4029:12345']

### `delete_page`

Delete a page from the Figma document. Cannot delete the only remaining page.

**Parameters:**
- `pageId` (string, opt) — Page node ID in colon format e.g. '0:2'
- `pageName` (string, opt) — Exact page name to delete (alternative to pageId)

### `detach_instance`

Detach one or more component instances, converting them to plain frames. The link to the main component is broken; all visual properties are preserved.

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — INSTANCE node IDs in colon format e.g. ['4029:12345']

### `group_nodes`

Group two or more nodes into a GROUP. All nodes must share the same parent.

**Required:** `nodeIds`

**Parameters:**
- `name` (string, opt) — Optional name for the new group
- `nodeIds` (array, req) — Node IDs to group (minimum 2), in colon format e.g. ['4029:12345', '4029:12346']

### `lock_nodes`

Lock one or more nodes to prevent accidental edits in Figma.

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']

### `move_nodes`

Move one or more nodes to an absolute canvas position. The same x/y is applied to every node independently (not a relative offset from current position).

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `x` (number, opt) — Target X position
- `y` (number, opt) — Target Y position

### `navigate_to_page`

Switch the active Figma page. Provide either pageId or pageName.

**Parameters:**
- `pageId` (string, opt) — Page node ID in colon format e.g. '0:1'
- `pageName` (string, opt) — Exact page name to navigate to

### `rename_node`

Rename a single node by ID. Returns the updated node with its new name. Use batch_rename_nodes to rename multiple nodes at once or to apply find/replace patterns across many nodes.

**Required:** `nodeId`, `name`

**Parameters:**
- `name` (string, req) — New name for the node. Figma supports slash-separated path notation e.g. 'Icons/Arrow/Left' to organise nodes in component panels.
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'

### `rename_page`

Rename an existing page in the Figma document.

**Required:** `newName`

**Parameters:**
- `newName` (string, req) — New name for the page
- `pageId` (string, opt) — Page node ID in colon format e.g. '0:2'
- `pageName` (string, opt) — Current page name to find (alternative to pageId)

### `reorder_nodes`

Change the z-order (layer stack position) of one or more nodes.

**Required:** `nodeIds`, `order`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `order` (string, req) — Order operation: bringToFront, sendToBack, bringForward, or sendBackward

### `reparent_nodes`

Move one or more nodes to a different parent frame, group, or section.

**Required:** `nodeIds`, `parentId`

**Parameters:**
- `nodeIds` (array, req) — Node IDs to move in colon format e.g. ['4029:12345']
- `parentId` (string, req) — Target parent node ID in colon format e.g. '4029:99'

### `resize_nodes`

Resize one or more nodes. The same width/height is applied to every node in the list independently. Provide width, height, or both.

**Required:** `nodeIds`

**Parameters:**
- `height` (number, opt) — New height in pixels
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `width` (number, opt) — New width in pixels

### `rotate_nodes`

Rotate one or more nodes to an absolute angle in degrees.

**Required:** `nodeIds`, `rotation`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']
- `rotation` (number, req) — Rotation angle in degrees (positive = counter-clockwise in Figma)

### `swap_component`

Swap the main component of an existing INSTANCE node, replacing it with a different component while keeping position and size.

**Required:** `nodeId`, `componentId`

**Parameters:**
- `componentId` (string, req) — Target COMPONENT node ID in colon format (from get_local_components)
- `nodeId` (string, req) — INSTANCE node ID in colon format e.g. 4029:12345

### `ungroup_nodes`

Ungroup one or more GROUP nodes, moving their children to the parent and removing the group.

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — GROUP node IDs in colon format e.g. ['4029:12345']

### `unlock_nodes`

Unlock one or more nodes, allowing them to be edited again.

**Required:** `nodeIds`

**Parameters:**
- `nodeIds` (array, req) — Node IDs in colon format e.g. ['4029:12345']

---

## Design System (Styles & Variables)

### `add_variable_mode`

Add a new mode to an existing variable collection (e.g. Light/Dark, Desktop/Mobile). IMPORTANT — Figma free plan only allows 1 mode per collection; calling this tool on a free-plan account will return the error 'Limited to 1 modes only'. If that error occurs, stop retrying and switch to the name-prefix workaround: keep the single default mode and create variables prefixed by mode, e.g. 'light/color-bg' and 'dark/color-bg' in the same collection. Tell the user that native multi-mode variables require a paid Figma plan (Professional or above).

**Required:** `collectionId`, `modeName`

**Parameters:**
- `collectionId` (string, req) — Variable collection ID
- `modeName` (string, req) — Name for the new mode

### `apply_style_to_node`

Apply an existing local style (paint, text, effect, or grid) to a node, linking the node to that style.

**Required:** `nodeId`, `styleId`

**Parameters:**
- `nodeId` (string, req) — Target node ID in colon format e.g. 4029:12345
- `styleId` (string, req) — Style ID to apply (from get_styles)
- `target` (string, opt) — For paint styles only — apply to 'fill' (default) or 'stroke'

### `bind_variable_to_node`

Bind a local variable to a node property so the property is driven by the variable's value. COLOR variables: use fillColor or strokeColor. BOOLEAN variables: use visible. FLOAT variables: use opacity, rotation, width, height, cornerRadius, topLeftRadius, topRightRadius, bottomLeftRadius, bottomRightRadius, strokeWeight, itemSpacing, paddingTop, paddingRight, paddingBottom, paddingLeft.

**Required:** `nodeId`, `variableId`, `field`

**Parameters:**
- `field` (string, req) — Property to bind: fillColor | strokeColor | visible | opacity | rotation | width | height | cornerRadius | topLeftRadius | topRightRadius | bottomLeftRadius | bottomRightRadius | strokeWeight | itemSpacing | paddingTop | paddingRight | paddingBottom | paddingLeft
- `nodeId` (string, req) — Target node ID in colon format e.g. 4029:12345
- `variableId` (string, req) — Variable ID to bind (from get_variable_defs)

### `create_effect_style`

Create a new local effect style (drop shadow, inner shadow, or blur).

**Required:** `name`

**Parameters:**
- `color` (string, opt) — Shadow color as hex e.g. #000000 (default #000000, shadows only)
- `description` (string, opt) — Optional style description
- `name` (string, req) — Style name e.g. 'Shadow/Card'
- `offsetX` (number, opt) — Shadow X offset in pixels (default 0, shadows only)
- `offsetY` (number, opt) — Shadow Y offset in pixels (default 4, shadows only)
- `opacity` (number, opt) — Shadow color opacity 0–1 (default 0.25, shadows only)
- `radius` (number, opt) — Blur radius in pixels (default 8 for shadows, 4 for blurs)
- `spread` (number, opt) — Shadow spread in pixels (default 0, shadows only)
- `type` (string, opt) — Effect type: DROP_SHADOW (default), INNER_SHADOW, LAYER_BLUR, or BACKGROUND_BLUR

### `create_grid_style`

Create a new local layout grid style.

**Required:** `name`

**Parameters:**
- `alignment` (string, opt) — Alignment: STRETCH (default), CENTER, MIN, or MAX (COLUMNS/ROWS only)
- `color` (string, opt) — Grid line color as hex e.g. #FF0000 (GRID only, default #FF0000)
- `count` (number, opt) — Number of columns or rows (COLUMNS/ROWS only, default 12)
- `description` (string, opt) — Optional style description
- `gutterSize` (number, opt) — Gutter size in pixels (COLUMNS/ROWS only, default 16)
- `name` (string, req) — Style name e.g. 'Grid/Desktop'
- `offset` (number, opt) — Margin/offset in pixels (COLUMNS/ROWS only, default 0)
- `opacity` (number, opt) — Grid line opacity 0–1 (GRID only, default 0.1)
- `pattern` (string, opt) — Grid pattern: GRID (default), COLUMNS, or ROWS
- `sectionSize` (number, opt) — Grid cell size in pixels (GRID only, default 8)

### `create_paint_style`

Create a new local paint style with a solid fill color.

**Required:** `name`, `color`

**Parameters:**
- `color` (string, req) — Fill color as hex e.g. #FF5733
- `description` (string, opt) — Optional style description
- `name` (string, req) — Style name e.g. 'Brand/Primary'

### `create_text_style`

Create a new local text style (typography preset). Returns the new style's ID. Apply it to nodes with apply_style_to_node. Use get_styles to list existing text styles.

**Required:** `name`

**Parameters:**
- `description` (string, opt) — Optional human-readable description shown in the Figma style panel
- `fontFamily` (string, opt) — Font family name e.g. 'Inter', 'Roboto' (default Inter). Must be installed in Figma.
- `fontSize` (number, opt) — Font size in pixels (default 16)
- `fontStyle` (string, opt) — Font style variant e.g. 'Regular', 'Bold', 'Medium', 'SemiBold' (default Regular)
- `letterSpacingUnit` (string, opt) — Letter spacing unit: PIXELS (default) or PERCENT
- `letterSpacingValue` (number, opt) — Letter spacing value (unit set by letterSpacingUnit)
- `lineHeightUnit` (string, opt) — Line height unit: PIXELS (default) or PERCENT
- `lineHeightValue` (number, opt) — Line height value (unit set by lineHeightUnit)
- `name` (string, req) — Style name — use slash notation to organise into groups e.g. 'Heading/H1', 'Body/Regular'
- `textDecoration` (string, opt) — Text decoration: NONE (default), UNDERLINE, or STRIKETHROUGH

### `create_variable`

Create a new variable (design token) inside an existing collection. Returns the new variable's ID. Use get_variable_defs to find collection IDs, set_variable_value to set values per mode, and bind_variable_to_node to apply the variable to a node property.

**Required:** `name`, `collectionId`, `type`

**Parameters:**
- `collectionId` (string, req) — ID of the variable collection to add this variable to (from get_variable_defs)
- `name` (string, req) — Variable name — use slash notation to group e.g. 'Color/Primary', 'Spacing/MD'
- `type` (string, req) — Variable type: COLOR (hex color), FLOAT (numeric dimension/spacing), STRING (text), or BOOLEAN (true/false toggle)
- `value` (string, opt) — Initial value for the first mode. COLOR: hex e.g. #FF5733. FLOAT: number e.g. 16. STRING: text. BOOLEAN: true or false.

### `create_variable_collection`

Create a new local variable collection with an optional initial mode name. NOTE — Figma free plan limits each collection to 1 mode. If you need Light/Dark (or any multi-mode) theming and the user is on the free plan, do NOT try to call add_variable_mode; instead use the name-prefix workaround: create all variables in a single collection and prefix each variable name with its mode, e.g. 'light/color-bg' and 'dark/color-bg'. Inform the user of this limitation.

**Required:** `name`

**Parameters:**
- `initialModeName` (string, opt) — Name for the initial mode (default 'Mode 1')
- `name` (string, req) — Collection name

### `delete_style`

Delete a style (paint, text, effect, or grid) by its ID.

**Required:** `styleId`

**Parameters:**
- `styleId` (string, req) — Style ID to delete

### `delete_variable`

Delete a single variable (provide variableId) or an entire collection and all its variables (provide collectionId). Provide exactly one of the two — not both.

**Parameters:**
- `collectionId` (string, opt) — Collection ID to delete (removes all variables in the collection)
- `variableId` (string, opt) — Variable ID to delete

### `set_variable_value`

Set a variable's value for a specific mode.

**Required:** `variableId`, `modeId`, `value`

**Parameters:**
- `modeId` (string, req) — Mode ID within the collection
- `value` (string, req) — Value to set. COLOR: hex e.g. #FF5733. FLOAT: number e.g. 16. STRING: text. BOOLEAN: true or false.
- `variableId` (string, req) — Variable ID

### `update_paint_style`

Update an existing paint style's name, color, or description. Only paint styles support in-place updates — to modify text, effect, or grid styles, use delete_style and recreate them.

**Required:** `styleId`

**Parameters:**
- `color` (string, opt) — New fill color as hex e.g. #FF5733
- `description` (string, opt) — New style description
- `name` (string, opt) — New style name
- `styleId` (string, req) — Paint style ID

---

## Reactions

### `remove_reactions`

Remove prototype reactions from a node. Omit indices to remove all reactions. Provide a zero-based indices array to remove specific reactions (use get_reactions first to see current indices).

**Required:** `nodeId`

**Parameters:**
- `indices` (array, opt) — Zero-based indices of reactions to remove. Omit or pass [] to remove all.
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'

### `set_reactions`

Set prototype reactions on a node. Use mode "replace" (default) to overwrite all reactions, or "append" to add to existing ones.  Supported triggers: ON_CLICK, ON_HOVER, ON_PRESS, ON_DRAG, AFTER_TIMEOUT, MOUSE_ENTER, MOUSE_LEAVE, MOUSE_UP, MOUSE_DOWN Supported action types: NODE (navigation), BACK, CLOSE, URL   NODE navigation values: NAVIGATE, OVERLAY, SCROLL_TO, SWAP, CHANGE_TO Transition types: DISSOLVE, SMART_ANIMATE, MOVE_IN, MOVE_OUT, PUSH, SLIDE_IN, SLIDE_OUT   DISSOLVE / SMART_ANIMATE: {"type":"DISSOLVE","duration":0.3,"easing":{"type":"EASE_OUT"}}   Directional (PUSH, MOVE_IN, MOVE_OUT, SLIDE_IN, SLIDE_OUT): also require "direction" (LEFT|RIGHT|TOP|BOTTOM) and "matchLayers" (bool):     {"type":"PUSH","direction":"LEFT","matchLayers":false,"duration":0.3,"easing":{"type":"EASE_OUT"}}  Each reaction has a "trigger" and an "actions" array (plural). Each action in the array is an Action object.  Example — on-click navigate with dissolve: {"nodeId":"1:2","reactions":[{"trigger":{"type":"ON_CLICK"},"actions":[{"type":"NODE","destinationId":"1:3","navigation":"NAVIGATE","transition":{"type":"DISSOLVE","duration":0.3,"easing":{"type":"EASE_OUT"}},"preserveScrollPosition":false}]}]}  Example — on-click navigate with push (directional transition): {"nodeId":"1:2","reactions":[{"trigger":{"type":"ON_CLICK"},"actions":[{"type":"NODE","destinationId":"1:3","navigation":"NAVIGATE","transition":{"type":"PUSH","direction":"LEFT","matchLayers":false,"duration":0.3,"easing":{"type":"EASE_OUT"}},"preserveScrollPosition":false}]}]}  Example — open URL on hover: {"nodeId":"1:2","reactions":[{"trigger":{"type":"ON_HOVER"},"actions":[{"type":"URL","url":"https://example.com"}]}]}  Example — auto-advance after 3 seconds: {"nodeId":"1:2","reactions":[{"trigger":{"type":"AFTER_TIMEOUT","timeout":3000},"actions":[{"type":"NODE","destinationId":"1:4","navigation":"NAVIGATE","transition":{"type":"DISSOLVE","duration":0.3,"easing":{"type":"EASE_OUT"}},"preserveScrollPosition":false}]}]}  Example — go back on click: {"nodeId":"1:2","reactions":[{"trigger":{"type":"ON_CLICK"},"actions":[{"type":"BACK"}]}]}

**Required:** `nodeId`, `reactions`

**Parameters:**
- `mode` (string, opt) — "replace" (default) overwrites all existing reactions; "append" adds to them
- `nodeId` (string, req) — Node ID in colon format e.g. '4029:12345'
- `reactions` (array, req) — Array of reaction objects. Each has a 'trigger' and an 'actions' array (plural) of Action objects.

---

## Safety & Limits

- **Read-only tools** (all `get_*`, `scan_*`, `search_*`): safe to call anytime.
- **Destructive tools** (`delete_nodes`, `delete_page`, `delete_style`,
  `delete_variable`, `ungroup_nodes`, `set_text` on mixed-font nodes): inspect
  first, state the node list before calling, and verify after.
- **`set_text` caveat**: the bridge loads only one font and falls back to Inter
  Regular for mixed-font nodes — mixed-format ranges can lose fidelity.
  Prefer the official Figma `use_figma` recipe when style preservation matters.
- **Free-plan limits**: Figma free accounts allow only 1 variable mode per
  collection (`add_variable_mode` returns "Limited to 1 modes only"). Use
  name-prefixed variables (`light/color-bg`, `dark/color-bg`) instead.
- **Security**: keep the plugin + server on loopback (127.0.0.1). The plugin
  has no auth layer and broad read/write access to the open document.
- **PDF/export paths** (`export_frames_to_pdf`) are written relative to the
  server process's working directory.

## When to Use the Official Codex Figma Plugin Instead

| Capability | Local bridge (this doc) | Official Codex plugin |
|---|---|---|
| Current editor selection | ✅ `get_selection` | ❌ (URL-based only) |
| Node from a URL/file key | ⚠️ only if file is open locally | ✅ |
| Full font-range text editing | ❌ single-font `set_text` | ✅ canonical recipe |
| Slides / FigJam / Make files | ❌ | ✅ |
| Auth model | None (loopback trust) | OAuth via Codex app |

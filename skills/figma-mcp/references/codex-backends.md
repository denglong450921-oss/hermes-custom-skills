# Codex Figma Backends

This reference separates the official Codex Figma plugin from the optional
`figma-mcp-go` local bridge. They are different integrations with different
target and security models.

## Package Audit

The common `figma-mcp` ZIP contains a skill (`SKILL.md` plus translation
references). It does not contain a Codex plugin manifest or an MCP server.

The common `mcp_figma_plugin` ZIP contains a Figma editor development plugin:

- `manifest.json`
- `dist/code.js`
- `dist/index.html`

It is not a Codex plugin because it has no `.codex-plugin/plugin.json`. Importing
it into Figma does not register tools in Codex by itself.

The audited build contained no embedded access token or obvious credential. Its
manifest allows all network domains because the WebSocket host is configurable,
and its bundled code connects to `ws://<host>:<port>/ws`, defaulting to
`127.0.0.1:1994`.

## Capability Matrix

| Task | Official Codex Figma plugin | Local `figma-mcp-go` bridge |
|---|---|---|
| Authentication test | `figma_whoami` | MCP server startup plus editor-plugin connection |
| File target | Figma URL or file key | File open in the Figma editor |
| Current selection | Not exposed as a legacy selection tool | `get_selection` |
| Structured read | `get_design_context`, `get_metadata` | `get_design_context`, `get_node`, `get_nodes_info` |
| Screenshot | `get_screenshot` or `node.screenshot()` in `use_figma` | `get_screenshot` or `save_screenshots` |
| Text scan | Design context or read-only `use_figma` | `scan_text_nodes` |
| General write | `use_figma` | Direct write tools such as `set_text`, `set_fills`, and layout tools |
| Design system | `search_design_system`, variables, styles, Code Connect | Style and variable RPC tools |
| New files and generated content | Dedicated official tools | Depends on local server tool set |

## Preferred Codex Route

Use the official Codex Figma plugin for normal Codex work. It carries
authentication through the installed app, provides node-targeted reads and
writes, and has dedicated skills for `use_figma`, design-to-code, components,
Slides, and FigJam.

Target rules:

1. Parse the file key from the Figma URL.
2. Parse `node-id=1-2` as node ID `1:2`.
3. Omit `nodeId` only when a tool explicitly supports file- or page-level reads.
4. Never pass an empty or guessed node ID.
5. Never claim that a desktop selection is available without a selection-aware
   tool in the current session.

For writes, load the official `figma-use` skill before each `use_figma` call and
follow its current API rules. The official skill is the source of truth for font
loading, page switching, return values, atomic errors, and incremental writes.

## Optional Local Selection Bridge

Use the local bridge only when the user specifically needs live desktop
selection access or legacy direct tools and accepts the local setup.

1. Extract the Figma editor plugin ZIP.
2. In Figma Desktop, import its `manifest.json` as a development plugin.
3. Start and register the matching `figma-mcp-go` MCP server in Codex.
4. Keep the editor plugin endpoint on loopback and use the same port as the MCP
   server. The default is `127.0.0.1:1994`; if another client already owns that
   port, choose an unused loopback port such as `1995` for both sides.
5. Restart or reconnect Codex so the local MCP tools appear in the session.
6. Run `get_metadata`, then `get_selection`, before any write.

Do not hard-code a token into the Figma plugin ZIP, its manifest, the skill, or a
repository. Configure any server-side credential through the local MCP process's
secret mechanism, outside chat.

## Local Bridge Security Boundary

The editor plugin forwards JSON requests from its WebSocket to Figma Plugin API
handlers. The audited build exposes broad read operations and powerful writes,
including text/style/layout changes, page operations, and deletion.

The WebSocket URL uses plaintext `ws://` and the editor plugin does not add its
own authentication layer. A remote or untrusted endpoint could read or mutate the
open document. Keep the endpoint on loopback, run only a trusted matching server,
and close the editor plugin when the local bridge is not in use.

The manifest's `allowedDomains: ["*"]` is broader than ideal. It exists to allow
a configurable server address, but it also increases the consequence of entering
an untrusted host. Do not silently install or run this plugin for a user.

## Text-Edit Difference

The local bridge's bundled `set_text` implementation loads `node.fontName` and
falls back to Inter Regular when `fontName` is mixed. It then assigns
`node.characters`. This is not sufficient to guarantee preservation of every
styled text range.

For mixed fonts or colors:

1. Inspect styled segments before editing.
2. Load every font used by those segments.
3. Define how styles map onto the replacement string.
4. Apply the edit.
5. Re-read styled segments and inspect a screenshot.

The official `use_figma` route is preferred for this because it can implement
the full canonical text-edit recipe explicitly.

## Verification Recipes

### Official plugin

1. `figma_whoami` succeeds.
2. `get_metadata(fileKey)` lists pages, or `get_design_context(fileKey, nodeId)`
   returns the expected node.
3. `get_screenshot(fileKey, nodeId)` visually matches the target.
4. For writes, `use_figma` returns all mutated IDs and a post-write read confirms
   content and bounds.

### Local bridge

1. The editor plugin UI shows `Connected` and the expected file/page.
2. `get_metadata` matches that file/page.
3. `get_selection` returns the selected node IDs.
4. After a write, `get_nodes_info` and a screenshot confirm the result.

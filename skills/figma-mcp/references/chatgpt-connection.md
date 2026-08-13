# ChatGPT and Codex Figma Connection

Use this reference when the user asks how to connect, asks for a test, or reports
that Figma tools are missing.

## Access States

| State | Meaning | Response pattern |
|---|---|---|
| `Connected` | A Figma backend is callable and a concrete target is in scope. | Perform the requested read or scoped write. |
| `Connected but no target selected` | Authentication works, but the backend has no usable file or node target. | Ask for a Figma URL; for node work, ask for a node-specific URL. |
| `Not connected` | No callable Figma backend is available. | Explain that the skill is installed but cannot access Figma yet. |

Do not report `Connected` merely because the skill folder exists, a ZIP is
present, or a token exists in a shell.

## Official App Setup

When the current chat has no official Figma tools, direct the user to the
product's Apps or Plugins area, find Figma if available, choose `Connect`, and
complete the authorization flow. Availability can depend on product, plan,
region, and workspace policy. Prefer current UI labels over brittle menu paths.

Do not ask the user to paste a Figma access token into chat. Do not print,
inspect, or store tokens. A supported app or custom MCP connection must carry
authentication through its own configuration or authorization flow.

Do not give Hermes configuration commands as the default Codex or ChatGPT
solution. Hermes is a separate local client.

## Official Codex Smoke Test

1. Call `mcp__codex_apps__figma_whoami` to validate authentication.
2. Treat success as `Connected but no target selected` until a file URL or file
   key is provided.
3. If a `/design/` URL has no node ID, call `get_metadata` without `nodeId` to
   list top-level pages.
4. For node reads, require `node-id` and prefer `get_design_context`; use
   `get_screenshot` when visual confirmation is useful.

The official Codex backend does not expose the legacy local bridge's
`get_selection` tool. A request such as "edit the selected node" therefore needs
the selected node's copied Figma URL. Never infer the current desktop selection.

## Local Bridge Smoke Test

Only use this path when local `figma-mcp-go` tools are actually visible in the
session:

1. `get_metadata` confirms the open file and current page.
2. `get_selection` confirms the live editor selection.
3. `get_design_context(depth=1)` is a compact fallback for a large selection.

If these tools are absent, importing the Figma editor plugin alone is not enough;
the local MCP server must also be running and registered with Codex.

## Failure Categories

Report the actual category instead of simulating a result:

- no Figma tools in the session
- expired or missing authorization
- inaccessible file
- missing file key or node ID
- unsupported Figma file type
- local editor plugin disconnected from the MCP server
- write tool unavailable or insufficient permission

## Useful Prompts

- `Use $figma-mcp to test my Codex Figma connection. Do not expose account details.`
- `Use $figma-mcp to inspect this node URL and summarize its text, layout, and styles: <URL>`
- `Use $figma-mcp to replace the text at this node URL with 古吉拉特语 and verify the result: <URL>`
- `Use $figma-mcp to translate this frame URL into Spanish, preserve mixed formatting, and check overflow: <URL>`

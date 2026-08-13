#!/usr/bin/env node
/**
 * dump-source-bounds.js — record every TEXT node's box geometry in a frame
 * BEFORE translation. Output feeds text-fit.py (auto-fit) and restore-bounds.js.
 *
 * Usage: node dump-source-bounds.js <frameId> <out.json> [port]
 *   node dump-source-bounds.js 921:7 /tmp/source_bounds_full.json
 */
const { connect } = require("./mcp-client.js");
const fs = require("fs");

(async () => {
  const frameId = process.argv[2];
  const outPath = process.argv[3];
  const port = Number(process.argv[4] || 1994);
  if (!frameId || !outPath) { console.error("usage: dump-source-bounds.js <frameId> <out.json> [port]"); process.exit(1); }

  const mcp = await connect({ port, waitForPlugin: true });
  const info = await mcp.callJson("get_nodes_info", { nodeIds: [frameId] });
  const root = (Array.isArray(info) ? info : [info])[0];
  const map = {};
  (function walk(n) {
    if (n.type === "TEXT" && n.bounds) map[n.id] = n.bounds;
    for (const c of n.children || []) walk(c);
  })(root);
  fs.writeFileSync(outPath, JSON.stringify(map, null, 1));
  console.log(`recorded ${Object.keys(map).length} text-node bounds for ${frameId} -> ${outPath}`);
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

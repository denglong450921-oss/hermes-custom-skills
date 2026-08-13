#!/usr/bin/env node
/**
 * scan-frame.js — dump every text node of a frame as JSON.
 * Output feeds translate-frame.js (the translations JSON template).
 *
 * Usage: node scan-frame.js <nodeId> [port]
 *   node scan-frame.js 851:7
 * Prints:
 *   {"nodeId":"851:7","count":17,"textNodes":[{"id":"851:12","characters":"...","fontSize":30,"fontFamily":"Inter"},...]}
 */
const { connect } = require("./mcp-client.js");

(async () => {
  const nodeId = process.argv[2];
  const port = Number(process.argv[3] || 1994);
  if (!nodeId) { console.error("usage: node scan-frame.js <nodeId> [port]"); process.exit(1); }

  const mcp = await connect({ port, waitForPlugin: true });
  const scan = await mcp.callJson("scan_text_nodes", { nodeId });
  const nodes = (scan && scan.textNodes) || [];
  const out = {
    nodeId,
    count: nodes.length,
    textNodes: nodes.map((n) => ({
      id: n.id,
      characters: n.characters,
      fontSize: n.fontSize,
      fontFamily: n.fontName && n.fontName.family,
    })),
  };
  console.log(JSON.stringify(out, null, 1));
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

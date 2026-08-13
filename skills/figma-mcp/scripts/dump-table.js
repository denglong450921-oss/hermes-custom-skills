#!/usr/bin/env node
/* Dump the FULL source table group 921:347 — all text nodes with content + position. */
const { connect } = require("./mcp-client.js");
(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const info = await mcp.callJson("get_nodes_info", { nodeIds: ["921:347"] });
  const root = (Array.isArray(info) ? info : [info])[0];
  const texts = [];
  (function walk(n) {
    if (n.type === "TEXT") texts.push(n);
    for (const c of n.children || []) walk(c);
  })(root);
  texts.sort((a, b) => a.bounds.y - b.bounds.y);
  console.log("total text nodes:", texts.length);
  for (const t of texts) {
    const c = t.characters.replace(/\n/g, "\\n");
    console.log(`${t.id} | y=${Math.round(t.bounds.y)} x=${Math.round(t.bounds.x)} w=${Math.round(t.bounds.width)} | ${c.slice(0, 44)}`);
  }
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

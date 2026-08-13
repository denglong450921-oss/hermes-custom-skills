#!/usr/bin/env node
/* Verify split result in one clone (923:9381 mr): table group should have
   exactly 14 per-line nodes (7 members + 7 sub-caption), no multi-line. */
const { connect } = require("./mcp-client.js");

(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const info = await mcp.callJson("get_nodes_info", { nodeIds: ["923:9274"] });
  const root = (Array.isArray(info) ? info : [info])[0];
  const texts = [];
  (function walk(n) {
    if (n.type === "TEXT") texts.push(n);
    for (const c of n.children || []) walk(c);
  })(root);
  console.log("group text nodes:", texts.length);
  const members = texts.filter((t) => /^\d/.test(t.characters.trim()) && !/INR/.test(t.characters)).sort((a, b) => a.bounds.y - b.bounds.y);
  const subs = texts.filter((t) => /\(/.test(t.characters)).sort((a, b) => a.bounds.y - b.bounds.y);
  console.log("--- members lines (text @y) ---");
  for (const m of members) console.log("  ", m.characters.trim(), "@", Math.round(m.bounds.y), "size", (m.styles && m.styles.fontSize));
  console.log("--- sub lines ---");
  for (const s of subs) console.log("  ", s.characters.trim().slice(0, 24), "@", Math.round(s.bounds.y), "size", (s.styles && s.styles.fontSize));
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

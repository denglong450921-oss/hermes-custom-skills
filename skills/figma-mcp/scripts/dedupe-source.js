#!/usr/bin/env node
/* Dedupe + verify the source table after restore-split ran twice.
   Source group 921:347 should have exactly 14 per-line nodes:
   7 at y = 2926 + k*104 (members), 7 at y = 2894 + k*104 (sub-caption). */
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
  const byKey = {};
  for (const t of texts) {
    const y = Math.round(t.bounds.y);
    const k = `${Math.round(t.bounds.x)}|${y}`;
    (byKey[k] = byKey[k] || []).push(t);
  }
  const dupes = [];
  for (const k of Object.keys(byKey)) if (byKey[k].length > 1) dupes.push(...byKey[k].slice(1));
  console.log("total TEXT in group:", texts.length);
  console.log("duplicates found:", dupes.length, dupes.map((d) => d.id).join(","));
  if (dupes.length) {
    await mcp.call("delete_nodes", { nodeIds: dupes.map((d) => d.id) });
    console.log("deleted", dupes.length, "duplicates");
  }
  // verify positions of remaining members/sub-caption lines
  const info2 = await mcp.callJson("get_nodes_info", { nodeIds: ["921:347"] });
  const root2 = (Array.isArray(info2) ? info2 : [info2])[0];
  const lines = [];
  (function walk(n) { if (n.type === "TEXT") lines.push(n); for (const c of n.children || []) walk(c); })(root2);
  const members = lines.filter((t) => /^\d/.test(t.characters.trim()) && t.characters.trim().length < 20).map((t) => `${t.characters.trim()}@${Math.round(t.bounds.y)}`).sort((a, b) => a.localeCompare(b));
  const subs = lines.filter((t) => /\(/.test(t.characters) && /A-level|A-/.test(t.characters)).map((t) => `${t.characters.trim().slice(0, 18)}@${Math.round(t.bounds.y)}`);
  console.log("--- members lines ---");
  for (const m of members) console.log("  ", m);
  console.log("--- sub lines ---");
  for (const s of subs) console.log("  ", s);
  console.log("total TEXT after dedupe:", lines.length);
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

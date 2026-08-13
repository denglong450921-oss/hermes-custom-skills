#!/usr/bin/env node
/* Final verification: kn clone 927:10369 vs source table 927:10332.
   Expect: multi-line members/subs nodes present with translated text,
   positions match the source, numbers in Poppins/Calistoga. */
const { connect } = require("./mcp-client.js");
(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  for (const gid of ["927:10332", "927:10369"]) {
    const r = await mcp.call("get_nodes_info", { nodeIds: [gid] });
    const root = JSON.parse(String(r))[0];
    const out = [];
    (function walk(n) { if (!n) return; if (n.type === "TEXT") out.push(n); for (const c of n.children || []) walk(c); })(root);
    console.log(`\n=== ${gid} — ${out.length} text nodes ===`);
    for (const n of out) {
      const b = n.bounds || {};
      const st = n.styles || {};
      const c = n.characters.replace(/\n/g, "\\n");
      console.log(`y=${String(b.y).padStart(5)} x=${String(Math.round(b.x)).padStart(5)} ${String(st.fontSize).padStart(5)} ${String(st.fontFamily || "").padStart(20)} ${c.slice(0, 42)}`);
    }
  }
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

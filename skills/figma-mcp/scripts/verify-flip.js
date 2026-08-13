#!/usr/bin/env node
/* Verify the flipped table: source (921:347) + MR clone group (923:9414).
   Expect: headers at top (~2222), rows descending: Specialist/12 members first,
   GM/3,000 last; subs BELOW members; all x within [2027, 2310]. */
const { connect } = require("./mcp-client.js");
(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  for (const gid of ["921:347", "923:9414"]) {
    const info = await mcp.callJson("get_nodes_info", { nodeIds: [gid] });
    const root = (Array.isArray(info) ? info : [info])[0];
    const g = root.id === gid ? root : (function find(n) { if (n.id === gid) return n; for (const c of n.children || []) { const r = find(c); if (r) return r; } return null; })(root);
    const nodes = [];
    (function walk(n) { if (n.type === "TEXT") nodes.push(n); for (const c of n.children || []) walk(c); })(g);
    nodes.sort((a, b) => a.bounds.y - b.bounds.y);
    console.log(`\n===== ${gid} (${nodes.length} nodes) =====`);
    for (const t of nodes) {
      const c = t.characters.replace(/\n/g, "\\n");
      const kind = /INR/.test(c) ? "SAL " : (/Team Size|Company Position|Monthly Salary|ತಂಡ|ಹುದ್ದೆ|ವೇತನ|Company|Team|Monthly/.test(c) ? "HDR " : (/^\d/.test(c.trim()) ? "MEM " : (/^\(/.test(c.trim()) ? "SUB " : "POS ")));
      console.log(` ${kind} y=${Math.round(t.bounds.y)} x=${Math.round(t.bounds.x)} w=${Math.round(t.bounds.width)} | ${c.slice(0, 40)}`);
    }
  }
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

#!/usr/bin/env node
/* Step 0: BACKUP (hard rule) + verify the new source table's scan order
   matches translations2.json indices before re-cloning. */
const { connect } = require("./mcp-client.js");
const fs = require("fs");

(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-");

  // 1) BACKUP: full tree of the source frame + the 6 frame-2 clone frames
  const targets = ["921:30", "923:9241", "923:9312", "923:9381", "923:9450", "923:9519", "923:9588"];
  const bak = {};
  for (const id of targets) {
    const r = await mcp.call("get_nodes_info", { nodeIds: [id] });
    bak[id] = r ? String(r) : null;
  }
  const bakPath = `/tmp/table-backup-${ts}.json`;
  fs.writeFileSync(bakPath, JSON.stringify(bak, null, 1));
  console.log("BACKUP written:", bakPath);

  // 2) verify scan order of the CURRENT source frame vs translations2.json indices
  const scan = await mcp.call("scan_text_nodes", { nodeId: "921:30" });
  const nodes = JSON.parse(String(scan)).textNodes || [];
  const t2 = JSON.parse(fs.readFileSync("/tmp/translations2.json", "utf-8"));
  const src2 = JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes;
  let match = 0, mismatch = 0;
  for (let i = 0; i < Math.min(nodes.length, src2.length); i++) {
    if (nodes[i].characters === src2[i].characters) match++;
    else { mismatch++; if (mismatch <= 3) console.log(`  scan[${i}] differs:\n    now: ${JSON.stringify(nodes[i].characters.slice(0, 40))}\n    old: ${JSON.stringify(src2[i].characters.slice(0, 40))}`); }
  }
  console.log(`SCAN compare vs scan2.json: ${nodes.length} nodes now / ${src2.length} old; ${match} identical, ${mismatch} differ`);
  console.log(`translations2.json langs: ${Object.keys(t2.translations).join(",")}; per-lang length: ${Object.values(t2.translations).map((a) => a.length).join("/")}`);
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

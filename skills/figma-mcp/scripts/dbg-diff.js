#!/usr/bin/env node
/* Full diff: current source frame scan vs scan2.json (old). */
const { connect } = require("./mcp-client.js");
const fs = require("fs");
(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const scan = JSON.parse(String(await mcp.call("scan_text_nodes", { nodeId: "921:30" })));
  const old = JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes;
  for (let i = 0; i < scan.textNodes.length; i++) {
    const a = scan.textNodes[i].characters.replace(/\n/g, "\\n");
    const b = old[i].characters.replace(/\n/g, "\\n");
    if (a !== b) console.log(`[${i}] NOW ${JSON.stringify(a.slice(0, 50))}  OLD ${JSON.stringify(b.slice(0, 50))}`);
  }
  console.log("--- total:", scan.textNodes.length);
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

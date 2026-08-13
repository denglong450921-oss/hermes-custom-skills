#!/usr/bin/env node
/* Show node 28 in the current source frame scan vs the old scan2.json. */
const { connect } = require("./mcp-client.js");
const fs = require("fs");
(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const scan = JSON.parse(String(await mcp.call("scan_text_nodes", { nodeId: "921:30" })));
  const old = JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes;
  for (const i of [28]) {
    console.log("NOW:", JSON.stringify(scan.textNodes[i] && scan.textNodes[i].characters));
    console.log("OLD:", JSON.stringify(old[i] && old[i].characters));
    console.log("NOW id:", scan.textNodes[i] && scan.textNodes[i].id, "| OLD id:", old[i] && old[i].id);
  }
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

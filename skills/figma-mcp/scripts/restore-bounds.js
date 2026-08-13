#!/usr/bin/env node
/**
 * restore-bounds.js — restore SOURCE box geometry (x,y,width,height) on every
 * TRANSLATED text node of every language clone.
 *
 * Root cause: set_text re-fit auto-width text boxes (width shrank to the new
 * text, position re-anchored), breaking table column alignment. Passthrough
 * (untranslated) nodes were never set_text'd, so their boxes already match.
 *
 * Usage: node restore-bounds.js
 */
const { connect } = require("./mcp-client.js");
const fs = require("fs");

const PAIRS = JSON.parse(process.env.PAIRS || JSON.stringify([
  // frame2 921:30 clones (rebuilt from the user's restored source table)
  ["921:30", "927:10369"], ["921:30", "927:10438"], ["921:30", "927:10507"],
  ["921:30", "927:10576"], ["921:30", "927:10645"], ["921:30", "927:10714"],
]));

const SCAN = {
  "921:7": JSON.parse(fs.readFileSync("/tmp/scan1.json", "utf-8")).textNodes,
  "921:30": JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes,
};
const TRANS = {
  "921:7": JSON.parse(fs.readFileSync("/tmp/translations1.json", "utf-8")),
  "921:30": JSON.parse(fs.readFileSync("/tmp/translations2.json", "utf-8")),
};

// translated index set per source frame (NOT passthrough)
function translatedIdx(frameId) {
  const scan = SCAN[frameId];
  const kn = TRANS[frameId].translations["kn"];
  const out = new Set();
  for (let i = 0; i < scan.length; i++) {
    if (kn[i] !== scan[i].characters) out.add(i);
  }
  return out;
}

// DFS collect bounds for TEXT nodes IN ORDER (index = scan order; the source
// frame's node ids changed after the user restored the table — index is stable)
function collect(node, arr) {
  if (node.type === "TEXT" && node.bounds) {
    arr.push(node.bounds);
  }
  for (const c of node.children || []) collect(c, arr);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });

  // source bounds per frame (arrays in DFS/scan order)
  const srcBounds = {};
  for (const frameId of ["921:7", "921:30"]) {
    const info = await mcp.callJson("get_nodes_info", { nodeIds: [frameId] });
    const root = (Array.isArray(info) ? info : [info])[0];
    const arr = [];
    collect(root, arr);
    srcBounds[frameId] = arr;
  }

  let totalMoved = 0, totalSkipped = 0, totalFail = 0;
  for (const [srcFrame, cloneId] of PAIRS) {
    const translated = translatedIdx(srcFrame);
    const srcNodes = SCAN[srcFrame];
    const scan = await mcp.callJson("scan_text_nodes", { nodeId: cloneId });
    const nodes = (scan && scan.textNodes) || [];

    // bounds come from get_nodes_info (scan_text_nodes does not return them)
    const info = await mcp.callJson("get_nodes_info", { nodeIds: [cloneId] });
    const cloneRoot = (Array.isArray(info) ? info : [info])[0];
    const cloneBounds = [];
    collect(cloneRoot, cloneBounds);

    let moved = 0, skipped = 0, fail = 0;
    for (let i = 0; i < nodes.length; i++) {
      if (!translated.has(i)) continue;
      const src = srcBounds[srcFrame][i];
      const cur = cloneBounds[i];
      if (!src || !cur) { fail++; continue; }
      const drift =
        Math.abs(src.x - cur.x) + Math.abs(src.y - cur.y) +
        Math.abs(src.width - cur.width) + Math.abs(src.height - cur.height);
      if (drift < 1) { skipped++; continue; }
      try {
        await mcp.call("resize_nodes", { nodeIds: [nodes[i].id], width: src.width, height: src.height });
        await mcp.call("move_nodes", { nodeIds: [nodes[i].id], x: src.x, y: src.y });
        moved++;
        await sleep(60);
      } catch (e) { fail++; }
    }
    totalMoved += moved; totalSkipped += skipped; totalFail += fail;
    console.log(`[${cloneId}] translated=${translated.size} moved=${moved} already-ok=${skipped} fail=${fail}`);
  }
  console.log(`\nDONE total moved=${totalMoved} already-ok=${totalSkipped} fail=${totalFail}`);
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

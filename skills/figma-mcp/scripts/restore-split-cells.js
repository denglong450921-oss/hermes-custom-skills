#!/usr/bin/env node
/**
 * restore-split-cells.js — restore the SOURCE table's newline-aligned cells as
 * PER-LINE text nodes (from the saved scan/styles/bounds JSONs — the original
 * multi-line nodes were lost), then split the same cells in every clone.
 *
 * Per line: single node, centered in the cell (x = cell.x + (cell.w - w)/2),
 * y = cell.y + k*lineHeight, font = source family/size (source) or TARGET_FONT
 * with per-line width fit (clones). Creates FIRST, deletes the multi-line node
 * ONLY if every line was created.
 *
 * Usage:
 *   node restore-split-cells.js <frameId> <targets.json> [port]
 *   node restore-split-cells.js 921:30 /tmp/split_targets.json 1994
 * env: TARGET_FONT (default Arial Unicode MS), PAIRS (clones, default all 12)
 */
const { connect } = require("./mcp-client.js");
const fs = require("fs");
const { execFileSync } = require("child_process");

const DEFAULT_PAIRS = [
  ["921:7", "922:8397"], ["921:7", "923:8541"], ["921:7", "923:8681"],
  ["921:7", "923:8821"], ["921:7", "923:8961"], ["921:7", "923:9101"],
  ["921:30", "923:9241"], ["921:30", "923:9312"], ["921:30", "923:9381"],
  ["921:30", "923:9450"], ["921:30", "923:9519"], ["921:30", "923:9588"],
];
const SCAN = {
  "921:7": JSON.parse(fs.readFileSync("/tmp/scan1.json", "utf-8")).textNodes,
  "921:30": JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes,
};
const STYLES = JSON.parse(fs.readFileSync("/tmp/source_styles_full.json", "utf-8"));
const BOUNDS = JSON.parse(fs.readFileSync("/tmp/source_bounds_all.json", "utf-8"));
const TRANS = {
  "921:7": JSON.parse(fs.readFileSync("/tmp/translations1.json", "utf-8")),
  "921:30": JSON.parse(fs.readFileSync("/tmp/translations2.json", "utf-8")),
};
const TARGET_FONT = process.env.TARGET_FONT || "Arial Unicode MS";
const LANGS = ["kn", "ml", "mr", "lus", "ta", "te"];
const PAIRS = JSON.parse(process.env.PAIRS || JSON.stringify(DEFAULT_PAIRS));
const LANG_OF_CLONE = {};
for (let i = 0; i < PAIRS.length; i++) LANG_OF_CLONE[PAIRS[i][1]] = LANGS[i % 6];
const normStyle = (s) => (s || "").replace("Semi Bold", "SemiBold").replace("Display SemiBold", "SemiBold");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const PY = `
import json, sys
from PIL import ImageFont
F = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
d = json.load(sys.stdin)
res = []
for i, t in enumerate(d["lines"]):
    f = ImageFont.truetype(F, int(round(d["sizes"][i])))
    w = f.getlength(t)
    fit = d["sizes"][i]
    if w > d["boxWs"][i]:
        fit = max(round((d["sizes"][i] * d["boxWs"][i] / w) * d["margin"] * 2) / 2, 8)
    res.append([round(w, 1), round(fit, 1)])
print(json.dumps(res))
`;
const PY_BIN = process.env.PY_BIN || "/usr/bin/python3"; // conda python crashes when spawned by node (plugin env issue)
function measure(lines, sizes, boxWs, margin) {
  let out;
  try {
    out = execFileSync(PY_BIN, ["-c", PY], { input: JSON.stringify({ lines, sizes, boxWs, margin }), encoding: "utf-8", maxBuffer: 1 << 22 });
  } catch (e) {
    console.error("PY FAIL FULL:", (e.stderr || e.message).slice(0, 1500));
    throw e;
  }
  return JSON.parse(out.trim());
}

(async () => {
  const frameId = process.argv[2];
  const targetsPath = process.argv[3];
  const port = Number(process.argv[4] || 1994);
  if (!frameId || !targetsPath) { console.error("usage: restore-split-cells.js <frameId> <targets.json> [port]"); process.exit(1); }
  const targets = JSON.parse(fs.readFileSync(targetsPath, "utf-8"));
  const mcp = await connect({ port, waitForPlugin: true });

  // known parent group per frame (from earlier tree inspection)
  const PARENT_OF = { "921:30": "921:347", "921:7": "921:7" };
  const srcScan = SCAN[frameId];
  const idxOf = {};
  for (let i = 0; i < srcScan.length; i++) idxOf[srcScan[i].id] = i;
  const styles = STYLES[frameId] || {};
  const bounds = BOUNDS[frameId] || {};
  const trans = TRANS[frameId].translations;

  // ---------- SOURCE: recreate per-line nodes from saved data (idempotent) ----------
  const sInfo = await mcp.callJson("get_nodes_info", { nodeIds: [frameId] });
  const sRoot = (Array.isArray(sInfo) ? sInfo : [sInfo])[0];
  const sIds = new Set();
  (function walk(n) { sIds.add(n.id); for (const c of n.children || []) walk(c); })(sRoot);
  for (const tid of targets) {
    if (sIds.has(tid)) { console.log(`[src] ${tid}: already present — skip restore`); continue; }
    const st = styles[tid] || {};
    const b = bounds[tid];
    const scanNode = srcScan[idxOf[tid]];
    if (!st || !b || !scanNode) { console.log(`SKIP ${tid}: missing saved data`); continue; }
    const lines = scanNode.characters.split("\n");
    const lh = (st.lineHeight && st.lineHeight.value) || Number(st.fontSize) * 1.2 || 30;
    const family = st.fontFamily || "Poppins";
    const size = Number(st.fontSize || 14);
    const style = normStyle(st.fontStyle || "Regular");
    const meas = measure(lines, lines.map(() => size), lines.map(() => b.width), 0.96);
    let created = 0;
    for (let k = 0; k < lines.length; k++) {
      const [w, fit] = meas[k];
      const x = b.x + (b.width - w) / 2;
      const y = b.y + k * lh;
      try {
        const r = await mcp.callJson("create_text", {
          parentId: PARENT_OF[frameId], x, y, text: lines[k].replace(/\s+$/, ""),
          fontFamily: family, fontSize: fit, fontStyle: style,
          name: lines[k].replace(/\s+$/, "").slice(0, 40),
        });
        if (r && (r.id || r.nodeId)) created++;
        else console.log(`   create no-id for ${tid} L${k}: ${JSON.stringify(r).slice(0, 100)}`);
      } catch (e) { console.log(`   create ERR ${tid} L${k}: ${e.message.slice(0, 100)}`); }
      await sleep(100);
    }
    // delete the (already gone or still present) multi-line node ONLY if all created
    if (created === lines.length) {
      try { await mcp.call("delete_nodes", { nodeIds: [tid] }); console.log(`[src] ${tid}: recreated as ${created} per-line nodes (original deleted if present)`); }
      catch (e) { console.log(`   delete ERR ${tid}: ${e.message.slice(0, 80)}`); }
    } else {
      console.log(`[src] ${tid}: created ${created}/${lines.length} — original NOT deleted`);
    }
  }

  // ---------- CLONES: split translated multi-line cells ----------
  for (const [sf, cloneId] of PAIRS) {
    if (sf !== frameId) continue;
    const lang = LANG_OF_CLONE[cloneId];
    const t = trans[lang];
    const scan = await mcp.callJson("scan_text_nodes", { nodeId: cloneId });
    const nodes = (scan && scan.textNodes) || [];
    // clone tree: find the parent group of each node
    const cInfo = await mcp.callJson("get_nodes_info", { nodeIds: [cloneId] });
    const cRoot = (Array.isArray(cInfo) ? cInfo : [cInfo])[0];
    const cParents = {};
    (function walk(n, p) { if (p) cParents[n.id] = p.id; for (const c of n.children || []) walk(c, n); })(cRoot);
    let perClone = 0;
    for (const tid of targets) {
      const idx = idxOf[tid];
      const cloneNode = nodes[idx];
      if (!cloneNode) continue;
      const st = styles[tid] || {};
      const b = bounds[tid];
      const lh = (st.lineHeight && st.lineHeight.value) || 30;
      const translatedText = (t && t[idx]) || cloneNode.characters;
      const lines = translatedText.split("\n");
      const meas = measure(lines, lines.map(() => Number(st.fontSize || 14)), lines.map(() => b.width), 0.96);
      let created = 0;
      for (let k = 0; k < lines.length; k++) {
        const [w, fit] = meas[k];
        const x = b.x + (b.width - w) / 2;
        const y = b.y + k * lh;
        try {
          const r = await mcp.callJson("create_text", {
            parentId: cParents[cloneNode.id] || cRoot.id,
            x, y, text: lines[k].replace(/\s+$/, ""),
            fontFamily: TARGET_FONT, fontSize: fit, fontStyle: "Regular",
            name: lines[k].replace(/\s+$/, "").slice(0, 40),
          });
          if (r && (r.id || r.nodeId)) created++;
          else console.log(`   [${cloneId}] create no-id ${tid} L${k}: ${JSON.stringify(r).slice(0, 100)}`);
        } catch (e) { console.log(`   [${cloneId}] create ERR ${tid} L${k}: ${e.message.slice(0, 100)}`); }
        await sleep(100);
      }
      if (created === lines.length) {
        try { await mcp.call("delete_nodes", { nodeIds: [cloneNode.id] }); perClone += created; }
        catch (e) { console.log(`   [${cloneId}] delete ERR ${cloneNode.id}: ${e.message.slice(0, 80)}`); }
      } else {
        console.log(`   [${cloneId}] ${tid}: created ${created}/${lines.length} — original NOT deleted`);
      }
    }
    console.log(`[${cloneId}] (${lang}) split ${perClone} per-line nodes`);
  }
  console.log("\nDONE");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

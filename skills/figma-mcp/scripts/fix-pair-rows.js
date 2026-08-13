#!/usr/bin/env node
/**
 * fix-pair-rows.js v2 — reposition the split per-line nodes (members + subs)
 * to their CORRECT rows. Ground truth (user):
 *   12 members↔Specialist, 25↔Supervisor, 100↔Manager, 300↔Deputy Director,
 *   600↔Director, 1,200↔Assistant GM, 3,000↔General Manager
 * Row y = the salary-amount cells' y (read at runtime, source group).
 * Column anchor = "Team Size Requirement" header center (read at runtime).
 * Sub line sits 32px above its members line. Creates first, deletes old only
 * if all created. Probe verified create_text coords == reported coords.
 * Usage: node fix-pair-rows.js [port]
 */
const { connect } = require("./mcp-client.js");
const { execFileSync } = require("child_process");

const DEFAULT_PAIRS = [
  ["921:7", "922:8397"], ["921:7", "923:8541"], ["921:7", "923:8681"],
  ["921:7", "923:8821"], ["921:7", "923:8961"], ["921:7", "923:9101"],
  ["921:30", "923:9241"], ["921:30", "923:9312"], ["921:30", "923:9381"],
  ["921:30", "923:9450"], ["921:30", "923:9519"], ["921:30", "923:9588"],
];
const PAIRS = JSON.parse(process.env.PAIRS || JSON.stringify(DEFAULT_PAIRS));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const AMOUNTS = ["10,000", "15,000", "30,000", "75,000", "200,000", "600,000", "1,600,000"];

const PY = `
import json, sys
from PIL import ImageFont
F = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
d = json.load(sys.stdin)
print(json.dumps([round(ImageFont.truetype(F, int(round(s))).getlength(t), 1) for t, s in zip(d["texts"], d["sizes"])]))
`;
function widths(texts, sizes) {
  return JSON.parse(execFileSync("/usr/bin/python3", ["-c", PY], { input: JSON.stringify({ texts, sizes }), encoding: "utf-8", maxBuffer: 1 << 22 }).trim());
}
function textNodes(root) {
  const out = [];
  (function walk(n) { if (n.type === "TEXT") out.push(n); for (const c of n.children || []) walk(c); })(root);
  return out;
}
// per-line nodes = name starts with digit or "(", and is NOT an INR amount
const isPerLine = (n) => (/^\d/.test(n.name || "") || /^\(/.test(n.name || "")) && !/INR/.test(n.name || "");

(async () => {
  const port = Number(process.argv[2] || 1994);
  const mcp = await connect({ port, waitForPlugin: true });

  const sInfo = await mcp.callJson("get_nodes_info", { nodeIds: ["921:347"] });
  const sRoot = (Array.isArray(sInfo) ? sInfo : [sInfo])[0];
  const sNodes = textNodes(sRoot);
  const rowY = {};
  for (const n of sNodes) {
    const m = (n.characters || "").match(/^([\d,]+) INR/);
    if (m && AMOUNTS.includes(m[1])) rowY[m[1]] = n.bounds.y;
  }
  const headerRef = sNodes.find((t) => /Team Size Requirement/.test(t.characters));
  const colX = headerRef ? headerRef.bounds.x + headerRef.bounds.width / 2 : 2190;
  console.log("rowY:", JSON.stringify(rowY), "colX:", colX);

  async function fixGroup(groupId, isSource) {
    const gInfo = await mcp.callJson("get_nodes_info", { nodeIds: [groupId] });
    const gRoot = (Array.isArray(gInfo) ? gInfo : [gInfo])[0];
    const g = gRoot.id === groupId ? gRoot : (function find(n) { if (n.id === groupId) return n; for (const c of n.children || []) { const r = find(c); if (r) return r; } return null; })(gRoot);
    const nodes = textNodes(g);
    const old = nodes.filter(isPerLine);
    const members = old.filter((t) => /^\d/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
    const subs = old.filter((t) => /^\(/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
    console.log(`[${groupId}] per-line: ${members.length} members + ${subs.length} subs (old total ${old.length})`);
    if (members.length !== 7 || subs.length !== 7) { console.log(`  unexpected counts — SKIP (no deletion)`); return; }
    const mws = widths(members.map((m) => m.characters), members.map(() => 32));
    const sws = widths(subs.map((s) => s.characters), subs.map(() => 24));
    const created = [];
    for (let k = 0; k < 7; k++) {
      const ry = rowY[AMOUNTS[k]];
      if (ry === undefined) { console.log(`  rowY missing for ${AMOUNTS[k]} — abort`); return; }
      for (const [t, isSub] of [[members[k], false], [subs[k], true]]) {
        const r = await mcp.callJson("create_text", {
          parentId: groupId,
          x: colX - (isSub ? sws[k] : mws[k]) / 2,
          y: (isSub ? ry - 32 : ry),
          text: t.characters.replace(/\s+$/, ""),
          fontFamily: isSource ? "Poppins" : "Arial Unicode MS",
          fontSize: isSub ? 24 : 32,
          fontStyle: isSource ? "SemiBold" : "Regular",
          name: t.characters.replace(/\s+$/, "").slice(0, 40),
        });
        if (r && (r.id || r.nodeId)) created.push(r.id || r.nodeId);
        else console.log(`  create no-id ${k}${isSub ? "s" : ""}: ${JSON.stringify(r).slice(0, 90)}`);
        await sleep(120);
      }
    }
    if (created.length === old.length) {
      await mcp.call("delete_nodes", { nodeIds: old.map((o) => o.id) });
      console.log(`[${groupId}] recreated ${created.length} at row positions, old deleted`);
    } else {
      console.log(`[${groupId}] created ${created.length}/${old.length} — old kept (no delete)`);
    }
  }

  await fixGroup("921:347", true);

  for (const [sf, cloneId] of PAIRS) {
    if (sf !== "921:30") continue;
    const cInfo = await mcp.callJson("get_nodes_info", { nodeIds: [cloneId] });
    const cRoot = (Array.isArray(cInfo) ? cInfo : [cInfo])[0];
    // table group = the GROUP that contains an INR text node
    let gid = null;
    (function walk(n, parentId) {
      if (gid) return;
      if (n.type === "GROUP" && parentId) {
        const hasInr = textNodes(n).some((t) => /INR/.test(t.characters || ""));
        if (hasInr) { gid = n.id; return; }
      }
      for (const c of n.children || []) walk(c, n.id);
    })(cRoot);
    if (!gid) { console.log(`[${cloneId}] table group not found — skip`); continue; }
    await fixGroup(gid, false);
  }
  console.log("\nDONE");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

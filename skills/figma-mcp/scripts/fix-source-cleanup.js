#!/usr/bin/env node
/**
 * fix-source-cleanup.js — clean up the v1 pollution in the source table group
 * and re-position per-line nodes (source + all frame2 clones) at the CORRECT
 * rows, using rowY re-read from the ORIGINAL INR cells (x < 1700, column 3).
 *
 * Pollution: v1 fix-pair-rows matched INR cells as "members", creating 7 extra
 * INR-text nodes at row positions (x > 1900) and leaving 28 per-line nodes.
 * Cleanup: delete per-line nodes + INR-text nodes with x > 1900, then recreate
 * exactly 7 members + 7 subs at the correct rows.
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
const isPerLine = (n) => (/^\d/.test(n.name || "") || /^\(/.test(n.name || "")) && !/INR/.test(n.name || "");

(async () => {
  const port = Number(process.argv[2] || 1994);
  const mcp = await connect({ port, waitForPlugin: true });

  // ---- 1. clean the SOURCE group ----
  const sInfo = await mcp.callJson("get_nodes_info", { nodeIds: ["921:347"] });
  const sRoot = (Array.isArray(sInfo) ? sInfo : [sInfo])[0];
  const sNodes = textNodes(sRoot);
  const perLine = sNodes.filter(isPerLine);
  const dupInr = sNodes.filter((n) => /INR/.test(n.name || "") && n.bounds.x > 1900);
  const toDelete = [...perLine, ...dupInr].map((n) => n.id);
  console.log(`[src] deleting ${perLine.length} per-line + ${dupInr.length} duplicate-INR = ${toDelete.length}`);
  if (toDelete.length) { await mcp.call("delete_nodes", { nodeIds: toDelete }); await sleep(500); }

  // ---- 2. re-read rowY from the ORIGINAL INR cells (x < 1700) ----
  const sInfo2 = await mcp.callJson("get_nodes_info", { nodeIds: ["921:347"] });
  const sRoot2 = (Array.isArray(sInfo2) ? sInfo2 : [sInfo2])[0];
  const sNodes2 = textNodes(sRoot2);
  const rowY = {};
  for (const n of sNodes2) {
    const m = (n.characters || "").match(/^([\d,]+) INR/);
    if (m && AMOUNTS.includes(m[1]) && n.bounds.x < 1700) rowY[m[1]] = n.bounds.y;
  }
  // fallback: known-correct values (verified in multiple dumps)
  const FALLBACK = { "10,000": 2880, "15,000": 2775, "30,000": 2670, "75,000": 2565, "200,000": 2460, "600,000": 2355, "1,600,000": 2250 };
  for (const a of AMOUNTS) if (rowY[a] === undefined) rowY[a] = FALLBACK[a];
  console.log("rowY (clean):", JSON.stringify(rowY));
  const headerRef = sNodes2.find((t) => /Team Size Requirement/.test(t.characters));
  const colX = headerRef ? headerRef.bounds.x + headerRef.bounds.width / 2 : 2190.93;
  console.log("colX:", colX);

  // ---- 3. recreate source per-line nodes at correct rows ----
  const members = ["12 members", "25 members", "100 members", "300 members", "600 members", "1,200 members", "3,000 members"];
  const subs = ["(A-level subordinates)", "(A-level subordinates)", "(including A, B, C grades)", "(including A, B, C grades)", "(including A, B, C grades)", "(including A, B, C grades)", "(including A, B, C grades)"];
  const mws = widths(members, members.map(() => 32));
  const sws = widths(subs, subs.map(() => 24));
  let srcCreated = 0;
  for (let k = 0; k < 7; k++) {
    const ry = rowY[AMOUNTS[k]];
    for (const [txt, isSub] of [[members[k], false], [subs[k], true]]) {
      const r = await mcp.callJson("create_text", {
        parentId: "921:347",
        x: colX - (isSub ? sws[k] : mws[k]) / 2, y: (isSub ? ry - 32 : ry),
        text: txt, fontFamily: "Poppins", fontSize: isSub ? 24 : 32, fontStyle: "SemiBold",
        name: txt,
      });
      if (r && (r.id || r.nodeId)) srcCreated++;
      await sleep(120);
    }
  }
  console.log(`[src] created ${srcCreated}/14 per-line nodes at correct rows`);

  // ---- 4. re-fix all frame2 clones (their previous fix used polluted rowY) ----
  for (const [sf, cloneId] of PAIRS) {
    if (sf !== "921:30") continue;
    const cInfo = await mcp.callJson("get_nodes_info", { nodeIds: [cloneId] });
    const cRoot = (Array.isArray(cInfo) ? cInfo : [cInfo])[0];
    let gid = null;
    (function walk(n) {
      if (gid) return;
      if (n.type === "GROUP") { const hasInr = textNodes(n).some((t) => /INR/.test(t.characters || "")); if (hasInr) { gid = n.id; return; } }
      for (const c of n.children || []) walk(c);
    })(cRoot);
    if (!gid) { console.log(`[${cloneId}] table group not found — skip`); continue; }
    const gInfo = await mcp.callJson("get_nodes_info", { nodeIds: [gid] });
    const gRoot = (Array.isArray(gInfo) ? gInfo : [gInfo])[0];
    const g = gRoot.id === gid ? gRoot : (function find(n) { if (n.id === gid) return n; for (const c of n.children || []) { const r = find(c); if (r) return r; } return null; })(gRoot);
    const nodes = textNodes(g);
    const old = nodes.filter(isPerLine);
    const mem = old.filter((t) => /^\d/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
    const sub = old.filter((t) => /^\(/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
    if (mem.length !== 7 || sub.length !== 7) { console.log(`[${cloneId}] unexpected per-line counts (${mem.length}+${sub.length}) — skip`); continue; }
    const mws2 = widths(mem.map((m) => m.characters), mem.map(() => 32));
    const sws2 = widths(sub.map((s) => s.characters), sub.map(() => 24));
    const created = [];
    for (let k = 0; k < 7; k++) {
      const ry = rowY[AMOUNTS[k]];
      for (const [t, isSub] of [[mem[k], false], [sub[k], true]]) {
        const r = await mcp.callJson("create_text", {
          parentId: gid, x: colX - (isSub ? sws2[k] : mws2[k]) / 2, y: (isSub ? ry - 32 : ry),
          text: t.characters.replace(/\s+$/, ""), fontFamily: "Arial Unicode MS",
          fontSize: isSub ? 24 : 32, fontStyle: "Regular", name: t.characters.replace(/\s+$/, "").slice(0, 40),
        });
        if (r && (r.id || r.nodeId)) created.push(r.id || r.nodeId);
        await sleep(120);
      }
    }
    if (created.length === old.length) {
      await mcp.call("delete_nodes", { nodeIds: old.map((o) => o.id) });
      console.log(`[${cloneId}] recreated ${created.length} at correct rows, old deleted`);
    } else {
      console.log(`[${cloneId}] created ${created.length}/${old.length} — old kept`);
    }
  }
  console.log("\nDONE");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

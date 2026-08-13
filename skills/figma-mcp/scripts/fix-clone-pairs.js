#!/usr/bin/env node
/**
 * fix-clone-pairs.js — rebuild the per-line pairs in every frame2 clone by
 * CONTENT (parse the leading number), not by sorted order. The previous
 * cleanup run scrambled clone pairs (sorted old nodes by y-ascending but
 * assigned rows by amount-ascending). Source is already correct.
 *
 * Pair rows (user ground truth): 12↔2880, 25↔2775, 100↔2670, 300↔2565,
 * 600↔2460, 1,200↔2355, 3,000↔2250 (Specialist..GM).
 */
const { connect } = require("./mcp-client.js");
const { execFileSync } = require("child_process");

const CLONES = ["923:9241", "923:9312", "923:9381", "923:9450", "923:9519", "923:9588"];
const PAIR_NUMS = [12, 25, 100, 300, 600, 1200, 3000];
const PAIR_YS = [2880, 2775, 2670, 2565, 2460, 2355, 2250]; // Specialist..GM
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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
const pairNum = (s) => { const n = parseInt(String(s).replace(/,/g, ""), 10); return n; };

(async () => {
  const port = Number(process.argv[2] || 1994);
  const mcp = await connect({ port, waitForPlugin: true });

  // colX from the (correct) source header
  const sInfo = await mcp.callJson("get_nodes_info", { nodeIds: ["921:347"] });
  const sRoot = (Array.isArray(sInfo) ? sInfo : [sInfo])[0];
  const sNodes = textNodes(sRoot);
  const headerRef = sNodes.find((t) => /Team Size Requirement/.test(t.characters));
  const colX = headerRef ? headerRef.bounds.x + headerRef.bounds.width / 2 : 2190.93;

  for (const cloneId of CLONES) {
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
    const members = old.filter((t) => /^\d/.test(t.name || ""));
    const subs = old.filter((t) => /^\(/.test(t.name || ""));
    if (members.length !== 7 || subs.length !== 7) { console.log(`[${cloneId}] unexpected counts (${members.length}+${subs.length}) — skip`); continue; }
    // pair each member with its sub (sub sits 32px above member in current layout)
    const pair = [];
    let ok = true;
    for (const m of members) {
      const n = pairNum(m.characters);
      const k = PAIR_NUMS.indexOf(n);
      if (k < 0) { console.log(`[${cloneId}] unknown member number ${n} — skip`); ok = false; break; }
      const sub = subs.find((s) => Math.abs(s.bounds.y - (m.bounds.y - 32)) < 10);
      if (!sub) { console.log(`[${cloneId}] no sub for ${m.characters.trim()}@${Math.round(m.bounds.y)} — skip`); ok = false; break; }
      pair.push({ k, m, sub });
    }
    if (!ok) continue;
    const mws = widths(pair.map((p) => p.m.characters), pair.map(() => 32));
    const sws = widths(pair.map((p) => p.sub.characters), pair.map(() => 24));
    const created = [];
    for (let i = 0; i < pair.length; i++) {
      const { k, m, sub } = pair[i];
      const ry = PAIR_YS[k];
      for (const [t, isSub, w] of [[m, false, mws[i]], [sub, true, sws[i]]]) {
        const r = await mcp.callJson("create_text", {
          parentId: gid, x: colX - w / 2, y: (isSub ? ry - 32 : ry),
          text: t.characters.replace(/\s+$/, ""), fontFamily: "Arial Unicode MS",
          fontSize: isSub ? 24 : 32, fontStyle: "Regular", name: t.characters.replace(/\s+$/, "").slice(0, 40),
        });
        if (r && (r.id || r.nodeId)) created.push(r.id || r.nodeId);
        await sleep(120);
      }
    }
    if (created.length === old.length) {
      await mcp.call("delete_nodes", { nodeIds: old.map((o) => o.id) });
      console.log(`[${cloneId}] rebuilt ${created.length} pairs by content at correct rows, old deleted`);
    } else {
      console.log(`[${cloneId}] created ${created.length}/${old.length} — old kept`);
    }
  }
  console.log("\nDONE");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

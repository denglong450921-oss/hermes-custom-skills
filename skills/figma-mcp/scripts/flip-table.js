#!/usr/bin/env node
/**
 * flip-table.js — fix the INVERTED salary table (header at bottom, rows
 * reversed) into a NORMAL table: header at top, Specialist/12 members first,
 * GM/3,000 last, sub-captions BELOW their member lines, all text fitted
 * within the column band (no overlap with the position column).
 *
 * Flip axis: block spans old_y ∈ [2218, 2985] → new_y = 2218 + 2985 - old_y.
 * Applying the flip to EVERYTHING (headers + rows + members + subs) keeps
 * each row's salary/position/members paired, puts 12 at the top, and moves
 * subs below their members automatically.
 *
 * Members/subs are recreated with width-fitted fonts (band 2027..2310,
 * center 2168.5, max width 283). Salary/position/headers are moved in place.
 * Source first, then the 6 frame-2 clones (per user: fix template first).
 */
const { connect } = require("./mcp-client.js");
const { execFileSync } = require("child_process");

const SOURCE = "921:347";
const CLONE_GROUPS = JSON.parse(process.env.CLONES || JSON.stringify(["923:9274", "923:9345", "923:9414", "923:9483", "923:9552", "923:9621"]));
const TOP = 2218, BOTTOM = 2985;
const BAND_L = 2027, BAND_R = 2310, CENTER = (2027 + 2310) / 2, MAXW = 283;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const PY = `
import json, sys
from PIL import ImageFont
F = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
d = json.load(sys.stdin)
out = []
for t, s in zip(d["texts"], d["sizes"]):
    f = ImageFont.truetype(F, int(round(s)))
    w = f.getlength(t)
    fit = s
    if w > MAXW:
        fit = max(round((s * MAXW / w) * 0.96 * 2) / 2, 8)
    out.append([round(w, 1), round(fit, 1)])
print(json.dumps(out))
`;
function measure(texts, sizes) {
  let out;
  try {
    out = execFileSync("/usr/bin/python3", ["-c", PY.replace(/MAXW/g, String(MAXW))], { input: JSON.stringify({ texts, sizes }), encoding: "utf-8", maxBuffer: 1 << 22 });
  } catch (e) {
    console.error("MEASURE ERR:", (e.stderr || e.message).slice(0, 2000));
    throw e;
  }
  return JSON.parse(out.trim());
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

  async function flipTable(gid, isSource) {
    const gInfo = await mcp.callJson("get_nodes_info", { nodeIds: [gid] });
    const gRoot = (Array.isArray(gInfo) ? gInfo : [gInfo])[0];
    const g = gRoot.id === gid ? gRoot : (function find(n) { if (n.id === gid) return n; for (const c of n.children || []) { const r = find(c); if (r) return r; } return null; })(gRoot);
    const nodes = textNodes(g);
    const flipY = (y) => Math.round(TOP + BOTTOM - y);

    // classify
    const headers = nodes.filter((t) => t.bounds.y > 2970);
    const salary = nodes.filter((t) => /INR/.test(t.characters || "") && t.bounds.x < 1700);
    const position = nodes.filter((t) => t.bounds.x > 2250 && !/INR/.test(t.characters || "") && t.bounds.y <= 2970);
    const perLine = nodes.filter(isPerLine).filter((t) => t.bounds.x >= 1950 && t.bounds.x <= 2150);
    console.log(`  [${gid}] headers=${headers.length} salary=${salary.length} position=${position.length} perLine=${perLine.length} total=${nodes.length}`);

    // 1. move headers/salary/position to flipped y (x unchanged) — skip for recovery runs
    let moved = 0;
    if (!process.env.SKIP_MOVE) {
      for (const t of [...headers, ...salary, ...position]) {
        try { await mcp.call("move_nodes", { nodeIds: [t.id], x: t.bounds.x, y: flipY(t.bounds.y) }); moved++; await sleep(80); }
        catch (e) { console.log(`    move ERR ${t.id}: ${e.message.slice(0, 80)}`); }
      }
    }
    console.log(`  moved ${moved} cells`);

    // 2. recreate per-line pairs at flipped positions, subs BELOW members, fitted widths
    const members = perLine.filter((t) => /^\d/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
    const subs = perLine.filter((t) => /^\(/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
    // pair by adjacency in CURRENT state (sub 32 above member)
    const pairs = [];
    const subOffset = process.env.NO_FLIP ? 32 : -32; // flipped: subs below (+32); pre-flip: above (-32)
    for (const m of members) {
      const sub = subs.find((s) => Math.abs(s.bounds.y - (m.bounds.y + subOffset)) < 10);
      if (sub) pairs.push([m, sub]);
    }
    console.log(`  pairs: ${pairs.length}`);
    const mTexts = pairs.map((p) => p[0].characters);
    const sTexts = pairs.map((p) => p[1].characters);
    const mMeas = measure(mTexts, mTexts.map(() => 32));
    const sMeas = measure(sTexts, sTexts.map(() => 24));
    const created = [];
    for (let k = 0; k < pairs.length; k++) {
      const my = process.env.NO_FLIP ? pairs[k][0].bounds.y : flipY(pairs[k][0].bounds.y); // refit keeps current y
      for (const [t, isSub] of [[pairs[k][0], false], [pairs[k][1], true]]) {
        const [w, fit] = isSub ? sMeas[k] : mMeas[k];
        const x = CENTER - w / 2;
        const y = isSub ? my + 32 : my; // sub BELOW member now
        const r = await mcp.callJson("create_text", {
          parentId: gid, x, y, text: t.characters.replace(/\s+$/, ""),
          fontFamily: isSource ? "Poppins" : "Arial Unicode MS",
          fontSize: fit, fontStyle: isSource ? "SemiBold" : "Regular",
          name: t.characters.replace(/\s+$/, "").slice(0, 40),
        });
        if (r && (r.id || r.nodeId)) created.push(r.id || r.nodeId);
        else console.log(`    create no-id k${k}${isSub ? "s" : ""}`);
        await sleep(120);
      }
    }
    if (created.length === perLine.length) {
      await mcp.call("delete_nodes", { nodeIds: perLine.map((o) => o.id) });
      console.log(`  recreated ${created.length} per-line at flipped rows (subs below), old deleted`);
    } else {
      console.log(`  created ${created.length}/${perLine.length} — old kept`);
    }
  }

  console.log("[src] flipping source table");
  if (!process.env.CLONES_ONLY) await flipTable(SOURCE, true);
  for (const gid of CLONE_GROUPS) {
    console.log(`[clone] ${gid}`);
    await flipTable(gid, gid === SOURCE);
  }
  console.log("\nDONE");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

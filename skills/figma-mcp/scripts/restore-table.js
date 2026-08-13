#!/usr/bin/env node
/**
 * restore-table.js — RESTORE the salary table (source 921:347 + the 6 frame-2
 * clone groups) to its ORIGINAL state, undoing the flip/per-line/split work:
 *   1. BACKUP current state to /tmp/table-backup-<ts>.json (get_nodes_info).
 *   2. Delete all per-line (members+sub) nodes.
 *   3. Move header/salary/position cells back to their original y
 *      (flipY(flipY(y)) = y — the flip was its own inverse).
 *   4. Recreate the ORIGINAL multi-line text nodes:
 *      - source: "12 members\n25 members\n…" (Poppins SemiBold 32/24, lh 104,
 *        at 2061,2926 and 2020,2894 — from the saved scan/styles/bounds JSONs)
 *      - clones: translated multi-line texts (translations2.json) with the
 *        auto-fit sizes (fit2.json), Arial Unicode MS.
 *   5. Verify and STOP — no further changes without user confirmation.
 *
 * Usage: node restore-table.js [port]
 */
const { connect } = require("./mcp-client.js");
const { execFileSync } = require("child_process");
const fs = require("fs");

const SOURCE = "921:347";
const CLONE_GROUPS = ["923:9274", "923:9345", "923:9414", "923:9483", "923:9552", "923:9621"];
const ALL = [SOURCE, ...CLONE_GROUPS];
const ORIG_MEMBERS = { x: 2061, y: 2926, w: 407, h: 728 };
const ORIG_SUBS = { x: 2020, y: 2894, w: 311, h: 728 };
const FLIP_TOP = 2218, FLIP_BOTTOM = 2985;
const flipY = (y) => FLIP_TOP + FLIP_BOTTOM - y;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const SCAN2 = JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes;
const STYLES = JSON.parse(fs.readFileSync("/tmp/source_styles_full.json", "utf-8"))["921:30"];
const TRANS2 = JSON.parse(fs.readFileSync("/tmp/translations2.json", "utf-8")).translations;
const FIT2 = JSON.parse(fs.readFileSync("/tmp/fit2.json", "utf-8"));

function textNodes(root) {
  const out = [];
  (function walk(n) { if (!n) return; if (n.type === "TEXT") out.push(n); for (const c of n.children || []) walk(c); })(root);
  return out;
}
function findNode(root, gid) {
  if (!root) return null;
  if (root.id === gid) return root;
  for (const c of root.children || []) { const r = findNode(c, gid); if (r) return r; }
  return null;
}
const isPerLine = (n) => (/^\d/.test(n.name || "") || /^\(/.test(n.name || "")) && !/INR/.test(n.name || "");

(async () => {
  const port = Number(process.argv[2] || 1994);
  const mcp = await connect({ port, waitForPlugin: true });

  // ---- 0. BACKUP current state ----
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const backup = {};
  for (const gid of ALL) {
    const info = await mcp.callJson("get_nodes_info", { nodeIds: [gid] });
    backup[gid] = Array.isArray(info) ? info : [info];
  }
  const bPath = `/tmp/table-backup-${ts}.json`;
  fs.writeFileSync(bPath, JSON.stringify(backup, null, 1));
  console.log(`BACKUP written: ${bPath}`);

  // ---- helper: recreate one multi-line node ----
  async function createMultiLine(gid, isSource, text, size, family, style, lh, box) {
    const lines = text.split("\n");
    const py = `
import json, sys
from PIL import ImageFont
F = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
d = json.load(sys.stdin)
f = ImageFont.truetype(F, int(round(${size})))
print(max(f.getlength(l) for l in d))
`;
    const maxW = JSON.parse(execFileSync("/usr/bin/python3", ["-c", py], { input: JSON.stringify(lines), encoding: "utf-8" }).trim());
    const x = box.x + (box.w - maxW) / 2; // LEFT-align, x adjusted so the widest line ≈ original CENTER position
    const r = await mcp.callJson("create_text", {
      parentId: gid, x, y: box.y, text, fontFamily: family, fontSize: size, fontStyle: style,
      name: text.split("\n")[0].slice(0, 40),
    });
    const nid = r && (r.id || r.nodeId);
    if (!nid) { console.log(`  create ERR for ${box.y}: ${JSON.stringify(r).slice(0, 90)}`); return null; }
    await sleep(150);
    // apply lineHeight via a text style
    try {
      const sr = await mcp.callJson("create_text_style", {
        name: `RestoreLH/${family}-${size}`, fontFamily: family, fontSize: size, fontStyle: style,
        lineHeightUnit: "PIXELS", lineHeightValue: lh,
      });
      const sid = sr && (sr.styleId || sr.id);
      if (sid) await mcp.call("apply_style_to_node", { nodeId: nid, styleId: sid });
    } catch (e) { console.log(`  lh style ERR: ${e.message.slice(0, 80)}`); }
    await sleep(150);
    return nid;
  }

  // ---- 1+2+3+4 per group ----
  for (const gid of ALL) {
    const isSource = gid === SOURCE;
    const info = await mcp.callJson("get_nodes_info", { nodeIds: [gid] });
    if (!Array.isArray(info) || !info[0] || typeof info[0] !== "object") { console.log(`[${gid}] unexpected get_nodes_info shape — SKIP`); continue; }
    const root = info[0];
    const g = findNode(root, gid) || root;

    // 2. delete per-line nodes
    const perLine = textNodes(g).filter(isPerLine).filter((t) => t.bounds.x >= 1950 && t.bounds.x <= 2150);
    if (perLine.length) { await mcp.call("delete_nodes", { nodeIds: perLine.map((n) => n.id) }); await sleep(400); }
    console.log(`[${gid}] deleted ${perLine.length} per-line nodes`);

    // 3. move cells back to original y (flip is self-inverse)
    const i2 = await mcp.callJson("get_nodes_info", { nodeIds: [gid] });
    const r2 = (Array.isArray(i2) && i2[0]) ? i2[0] : null;
    const g2 = r2 ? (findNode(r2, gid) || r2) : null;
    let moved = 0;
    if (g2) {
      for (const t of textNodes(g2)) {
        const isHeader = t.bounds.y > 2960 || /Team Size|Company Position|Monthly Salary/.test(t.characters || "");
        const isCell = /INR/.test(t.characters || "") || t.bounds.x > 2250 || isHeader;
        if (!isCell) continue;
        const ny = flipY(t.bounds.y);
        if (Math.abs(ny - t.bounds.y) > 1) {
          try { await mcp.call("move_nodes", { nodeIds: [t.id], x: t.bounds.x, y: ny }); moved++; await sleep(80); }
          catch (e) { console.log(`  move ERR ${t.id}: ${e.message.slice(0, 80)}`); }
        }
      }
    }
    console.log(`[${gid}] moved ${moved} cells back to original positions`);

    // 4. recreate multi-line members + subs
    if (isSource) {
      const m = SCAN2.find((n) => n.id === "921:381");
      const s = SCAN2.find((n) => n.id === "921:382");
      const mId = await createMultiLine(gid, true, m.characters, 32, "Poppins", "SemiBold", 104, ORIG_MEMBERS);
      const sId = await createMultiLine(gid, true, s.characters, 24, "Poppins", "SemiBold", 104, ORIG_SUBS);
      console.log(`[src] recreated multi-line members ${mId} + subs ${sId}`);
    } else {
      // find which clone this group belongs to → its language
      const langOf = { "923:9274": "kn", "923:9345": "ml", "923:9414": "mr", "923:9483": "lus", "923:9552": "ta", "923:9621": "te" };
      const lang = langOf[gid];
      const mText = TRANS2[lang][31];
      const sText = TRANS2[lang][32];
      const mSize = (FIT2[lang] && FIT2[lang]["31"]) || 32;
      const sSize = (FIT2[lang] && FIT2[lang]["32"]) || 24;
      const mId = await createMultiLine(gid, false, mText, mSize, "Arial Unicode MS", "Regular", 104, ORIG_MEMBERS);
      const sId = await createMultiLine(gid, false, sText, sSize, "Arial Unicode MS", "Regular", 104, ORIG_SUBS);
      console.log(`[${gid}] (${lang}) recreated multi-line members ${mId} + subs ${sId} (${mSize}/${sSize}px)`);
    }
  }
  console.log("\nRESTORE DONE — stopped, awaiting user confirmation before any further changes.");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

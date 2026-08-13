#!/usr/bin/env node
/**
 * restore-fonts.js — restore SOURCE fonts on passthrough (untranslated) nodes
 * of language clones. Translated nodes keep the FONT_FIX font (Arial Unicode MS).
 *
 * Root cause being fixed: FONT_FIX applied the fallback font to EVERY text node,
 * including pure-number/code/percentage table cells (Poppins/Calistoga etc.),
 * which changed font metrics and broke table alignment.
 *
 * Usage: node restore-fonts.js
 * Config below: pairs of [sourceFrame, cloneId] for all 12 clones.
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

// passthrough index set per source frame: translated[kn][i] == source text
function passthroughIdx(frameId) {
  const scan = SCAN[frameId];
  const kn = TRANS[frameId].translations["kn"];
  const out = new Set();
  for (let i = 0; i < scan.length; i++) {
    if (kn[i] === scan[i].characters) out.add(i);
  }
  return out;
}

// DFS collect styles for TEXT nodes IN ORDER (index = scan order; the source
// frame's node ids changed after the user restored the table, so id-keyed
// lookups against the saved scan JSON no longer match — index is stable)
function collect(node, arr) {
  if (node.type === "TEXT" && node.styles && typeof node.styles === "object") {
    arr.push(node.styles);
  }
  for (const c of node.children || []) collect(c, arr);
}

const normStyle = (s) =>
  (s || "").replace("Semi Bold", "SemiBold").replace("Display SemiBold", "SemiBold").replace("Bold Italic", "Italic");

(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // style cache: key -> styleId
  const styleCache = new Map();
  const existingStyles = (await mcp.callJson("get_styles")) || {};
  const textStyles = existingStyles.text || [];

  async function styleIdFor(fam, size, style, lhUnit, lhVal, lsUnit, lsVal) {
    const key = `${fam}|${size}|${style}|${lhUnit}|${lhVal}|${lsUnit}|${lsVal}`;
    if (styleCache.has(key)) return styleCache.get(key);
    // reuse existing style with same name convention if present
    const name = `Restore/${fam.replace(/\s/g, "")}-${size}-${style}`;
    let sid = null;
    for (const s of textStyles) {
      if (s.name === name) { sid = s.id; break; }
    }
    if (!sid) {
      const params = { name, fontFamily: fam, fontSize: size, fontStyle: style };
      if (lhVal != null && lhUnit) { params.lineHeightUnit = lhUnit; params.lineHeightValue = lhVal; }
      if (lsVal != null && lsUnit) { params.letterSpacingUnit = lsUnit; params.letterSpacingValue = lsVal; }
      try {
        const r = await mcp.callJson("create_text_style", params);
        sid = r && (r.styleId || r.id);
        if (sid) textStyles.push({ id: sid, name });
        await sleep(250);
      } catch (e) {
        console.log("   create_text_style ERR", name, e.message.slice(0, 120));
      }
    }
    styleCache.set(key, sid);
    return sid;
  }

  let totalRestored = 0, totalFail = 0;
  for (const [srcFrame, cloneId] of PAIRS) {
    const passthrough = passthroughIdx(srcFrame);
    if (passthrough.size === 0) { console.log(`[${cloneId}] no passthrough nodes`); continue; }

    // source styles map
    const srcInfo = await mcp.callJson("get_node", { nodeId: srcFrame });
    const srcRoot = srcInfo && srcInfo.node ? srcInfo.node : srcInfo;
    const srcStyles = [];
    collect(srcRoot, srcStyles);

    // clone text nodes (order = scan order)
    const scan = await mcp.callJson("scan_text_nodes", { nodeId: cloneId });
    const nodes = (scan && scan.textNodes) || [];
    const srcNodes = SCAN[srcFrame];

    let ok = 0, fail = 0;
    for (let i = 0; i < nodes.length; i++) {
      if (!passthrough.has(i)) continue;
      const st = srcStyles[i];
      if (!st || !st.fontFamily || st.fontFamily === "mixed") { fail++; continue; }
      const size = Number(st.fontSize);
      if (!Number.isFinite(size) || size <= 0) { fail++; continue; }
      const style = normStyle(st.fontStyle || "Regular");
      const lh = st.lineHeight || {};
      const ls = st.letterSpacing || {};
      const sid = await styleIdFor(
        st.fontFamily, size, style,
        lh.unit || null, lh.value != null ? lh.value : null,
        ls.unit || null, ls.value != null ? ls.value : null,
      );
      if (!sid) { fail++; continue; }
      try {
        await mcp.call("apply_style_to_node", { nodeId: nodes[i].id, styleId: sid });
        ok++;
        await sleep(120);
      } catch (e) { fail++; }
    }
    totalRestored += ok; totalFail += fail;
    console.log(`[${cloneId}] passthrough=${passthrough.size} restored=${ok} fail=${fail}`);
  }
  console.log(`\nDONE total restored=${totalRestored} fail=${totalFail}`);
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

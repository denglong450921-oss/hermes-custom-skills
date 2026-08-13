#!/usr/bin/env node
/**
 * apply-auto-fit.js — apply smaller font sizes (from text-fit.py) to translated
 * text nodes of language clones, so translated text fits its ORIGINAL box.
 *
 * Only touches translated nodes that need a smaller size; passthrough nodes and
 * nodes that already fit are left alone. lineHeight/letterSpacing of the
 * created style come from the SOURCE styles so row structure is preserved.
 *
 * Usage:
 *   node apply-auto-fit.js <fit-sizes.json> [port]
 * env: TARGET_FONT (default Arial Unicode MS), PAIRS (json, default the 12
 *      mattpocock-style pairs below — edit the file or pass PAIRS)
 */
const { connect } = require("./mcp-client.js");
const fs = require("fs");

const PAIRS = JSON.parse(process.env.PAIRS || JSON.stringify([
  ["921:7", "922:8397"], ["921:7", "923:8541"], ["921:7", "923:8681"],
  ["921:7", "923:8821"], ["921:7", "923:8961"], ["921:7", "923:9101"],
  ["921:30", "923:9241"], ["921:30", "923:9312"], ["921:30", "923:9381"],
  ["921:30", "923:9450"], ["921:30", "923:9519"], ["921:30", "923:9588"],
]));

const SCAN = {
  "921:7": JSON.parse(fs.readFileSync("/tmp/scan1.json", "utf-8")).textNodes,
  "921:30": JSON.parse(fs.readFileSync("/tmp/scan2.json", "utf-8")).textNodes,
};
const SRCSTYLES = JSON.parse(fs.readFileSync("/tmp/source_styles_full.json", "utf-8"));
const TARGET_FONT = process.env.TARGET_FONT || "Arial Unicode MS";
const normStyle = (s) =>
  (s || "").replace("Semi Bold", "SemiBold").replace("Display SemiBold", "SemiBold").replace("Bold Italic", "Italic");

(async () => {
  const fitPath = process.argv[2];
  if (!fitPath) { console.error("usage: apply-auto-fit.js <fit-sizes.json> [port]"); process.exit(1); }
  const fitSizes = JSON.parse(fs.readFileSync(fitPath, "utf-8"));
  const port = Number(process.argv[3] || 1994);
  const mcp = await connect({ port, waitForPlugin: true });
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const existing = (await mcp.callJson("get_styles")) || {};
  const textStyles = existing.text || [];
  const cache = new Map();

  async function styleIdFor(fam, size, style, lhVal, lhUnit) {
    const key = `${fam}|${size}|${style}|${lhVal}`;
    if (cache.has(key)) return cache.get(key);
    const name = `AutoFit/${fam.replace(/\s/g, "")}-${size}-${style}`;
    let sid = null;
    for (const s of textStyles) if (s.name === name) { sid = s.id; break; }
    if (!sid) {
      const p = { name, fontFamily: fam, fontSize: size, fontStyle: style };
      if (lhVal && lhVal > 0) { p.lineHeightUnit = lhUnit || "PIXELS"; p.lineHeightValue = lhVal; }
      try {
        const r = await mcp.callJson("create_text_style", p);
        if (!r || (!r.styleId && !r.id)) console.log("   CREATE no-id:", name, JSON.stringify(r).slice(0, 140));
        sid = r && (r.styleId || r.id);
        if (sid) textStyles.push({ id: sid, name });
        await sleep(250);
      } catch (e) { console.log("  create ERR", name, e.message.slice(0, 100)); }
    }
    cache.set(key, sid);
    return sid;
  }

  let totalApplied = 0, totalFail = 0;
  for (const [srcFrame, cloneId] of PAIRS) {
    const srcNodes = SCAN[srcFrame];
    const srcStyles = SRCSTYLES[srcFrame] || {};
    const scan = await mcp.callJson("scan_text_nodes", { nodeId: cloneId });
    const nodes = (scan && scan.textNodes) || [];
    // per-language fit sizes keyed by node INDEX
    const langCode = LANG_OF_CLONE[cloneId];
    const sizes = (fitSizes[langCode] || {});
    let applied = 0, fail = 0;
    for (let i = 0; i < nodes.length; i++) {
      const want = sizes[String(i)];
      if (!want) continue;
      const st = srcStyles[srcNodes[i].id] || {};
      const lh = st.lineHeight || {};
      // Arial Unicode MS ships Regular only — never request Bold/SemiBold/mixed
      const style = TARGET_FONT === "Arial Unicode MS" ? "Regular" : normStyle(st.fontStyle || "Regular");
      const sid = await styleIdFor(TARGET_FONT, want, style, lh.value || 0, lh.unit);
      if (!sid) { fail++; console.log("   no styleId for", i, want); continue; }
      try { await mcp.call("apply_style_to_node", { nodeId: nodes[i].id, styleId: sid }); applied++; await sleep(120); }
      catch (e) { fail++; console.log("   APPLY ERR", nodes[i].id, e.message.slice(0, 120)); }
    }
    totalApplied += applied; totalFail += fail;
    console.log(`[${cloneId}] (${langCode}) auto-fit applied=${applied} fail=${fail}`);
  }
  console.log(`\nDONE total applied=${totalApplied} fail=${totalFail}`);
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

// clone id -> language code (mirrors PAIRS order: 6 langs x 2 frames)
const LANGS = ["kn", "ml", "mr", "lus", "ta", "te"];
const LANG_OF_CLONE = {};
for (let i = 0; i < PAIRS.length; i++) LANG_OF_CLONE[PAIRS[i][1]] = LANGS[i % 6];

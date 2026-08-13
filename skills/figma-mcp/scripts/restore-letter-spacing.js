#!/usr/bin/env node
/**
 * restore-letter-spacing.js — second pass: re-apply passthrough-node styles
 * WITH letterSpacing (source styles from the cached get_selection log).
 * First pass (restore-fonts.js) used get_node styles, which omitted letterSpacing.
 */
const { connect } = require("./mcp-client.js");
const fs = require("fs");

const CLONES_F1 = ["922:8397","923:8541","923:8681","923:8821","923:8961","923:9101"];
const SCAN = JSON.parse(fs.readFileSync("/tmp/scan1.json", "utf-8")).textNodes;
const TRANS = JSON.parse(fs.readFileSync("/tmp/translations1.json", "utf-8"));
const SRCSTYLES = JSON.parse(fs.readFileSync("/tmp/source_styles_full.json", "utf-8"))["921:7"];

// passthrough indices (untranslated)
const passthrough = new Set();
for (let i = 0; i < SCAN.length; i++) {
  if (TRANS.translations.kn[i] === SCAN[i].characters) passthrough.add(i);
}

const normStyle = (s) => (s || "").replace("Semi Bold", "SemiBold").replace("Display SemiBold", "SemiBold");

(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const existing = (await mcp.callJson("get_styles")) || {};
  const textStyles = existing.text || [];
  const cache = new Map();

  async function styleIdFor(st) {
    const ls = st.letterSpacing || {};
    const key = `${st.fontFamily}|${st.fontSize}|${normStyle(st.fontStyle)}|${ls.unit}|${ls.value}`;
    if (cache.has(key)) return cache.get(key);
    const name = `RestoreLS/${st.fontFamily.replace(/\s/g, "")}-${st.fontSize}-${ls.value}${ls.unit === "PERCENT" ? "pct" : "px"}`;
    let sid = null;
    for (const s of textStyles) if (s.name === name) { sid = s.id; break; }
    if (!sid) {
      const p = { name, fontFamily: st.fontFamily, fontSize: Number(st.fontSize), fontStyle: normStyle(st.fontStyle) };
      if (ls.unit && ls.value != null) { p.letterSpacingUnit = ls.unit; p.letterSpacingValue = ls.value; }
      if (st.lineHeight && st.lineHeight.value != null) { p.lineHeightUnit = st.lineHeight.unit; p.lineHeightValue = st.lineHeight.value; }
      try {
        const r = await mcp.callJson("create_text_style", p);
        sid = r && (r.styleId || r.id);
        if (sid) textStyles.push({ id: sid, name });
        await sleep(250);
      } catch (e) { console.log("  create ERR", name, e.message.slice(0, 100)); }
    }
    cache.set(key, sid);
    return sid;
  }

  let total = 0, fail = 0;
  for (const cloneId of CLONES_F1) {
    const scan = await mcp.callJson("scan_text_nodes", { nodeId: cloneId });
    const nodes = (scan && scan.textNodes) || [];
    let ok = 0, f = 0;
    for (let i = 0; i < nodes.length; i++) {
      if (!passthrough.has(i)) continue;
      const srcId = SCAN[i].id;
      const st = SRCSTYLES[srcId];
      if (!st || !st.letterSpacing || !st.letterSpacing.value) continue;
      const sid = await styleIdFor(st);
      if (!sid) { f++; continue; }
      try { await mcp.call("apply_style_to_node", { nodeId: nodes[i].id, styleId: sid }); ok++; await sleep(120); }
      catch (e) { f++; }
    }
    total += ok; fail += f;
    console.log(`[${cloneId}] ls-restored=${ok} fail=${f}`);
  }
  console.log(`\nDONE total ls-restored=${total} fail=${fail}`);
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

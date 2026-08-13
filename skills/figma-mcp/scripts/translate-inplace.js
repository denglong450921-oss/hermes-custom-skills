#!/usr/bin/env node
/**
 * translate-inplace.js — translate an EXISTING frame's text nodes in place.
 * One bridge connection for the whole run: scan -> set_text -> byte-exact
 * verify -> screenshot ink-check. Use when the target frame already exists
 * (e.g. a language clone the user created/selected); use translate-frame.js
 * instead when clones must be created first.
 *
 * Translations JSON format (same as translate-frame.js):
 * {
 *   "languages": [ {"code":"fr-CA","name":"加拿大法语"} ],
 *   "translations": { "fr-CA": ["text0","text1",...] }   // index = scan order
 * }
 *
 * Usage: node translate-inplace.js <frameNodeId> <translations.json> [port]
 *
 * Options (env vars):
 *   SHOT=1        export a PNG screenshot of the frame after verify to
 *                 <frameNodeId>.png in CWD (default 0 — ink check needs it,
 *                 so set SHOT=1 for a visual check)
 *   PRINT_ALL=0   print every node's match status (default 1)
 *
 * Exit code 0 = all nodes byte-exact, 1 = any mismatch/error.
 */
const fs = require("fs");
const { connect } = require("./mcp-client.js");

(async () => {
  const src = process.argv[2];
  const transPath = process.argv[3];
  const port = Number(process.argv[4] || 1994);
  if (!src || !transPath) {
    console.error("usage: node translate-inplace.js <frameNodeId> <translations.json> [port]");
    process.exit(2);
  }
  const data = JSON.parse(fs.readFileSync(transPath, "utf-8"));
  const langs = data.languages;
  const translations = data.translations;

  const mcp = await connect({ port, waitForPlugin: true });
  const printAll = process.env.PRINT_ALL !== "0";

  const scan = await mcp.callJson("scan_text_nodes", { nodeId: src });
  const nodes = (scan && scan.textNodes) || [];
  if (!nodes.length) { console.error("FAIL: no text nodes under " + src); mcp.close(); process.exit(2); }

  // IRON RULE: translate TEXT nodes ONLY. Images/rectangles/vector nodes are
  // never translated — scan_text_nodes already returns only text, but double-
  // check the live types before mutating anything.
  const live = await mcp.callJson("get_nodes_info", { nodeIds: nodes.map((n) => n.id) });
  const liveById = {};
  for (const n of (Array.isArray(live) ? live : [])) liveById[n.id] = n;
  const nonText = nodes.filter((n) => liveById[n.id] && liveById[n.id].type !== "TEXT");
  if (nonText.length) {
    console.error(`FAIL: ${nonText.length} non-TEXT node(s) in scan — aborting, nothing was written:`);
    for (const n of nonText) console.error("  ", n.id, liveById[n.id] && liveById[n.id].type);
    mcp.close();
    process.exit(2);
  }

  let failures = 0;
  for (const lang of langs) {
    const texts = translations[lang.code] || [];
    if (texts.length !== nodes.length) {
      console.warn(`[${lang.code}] WARN: ${texts.length} translations for ${nodes.length} nodes`);
    }
    console.log(`--- ${lang.name} (${lang.code}) ${nodes.length} nodes ---`);

    // 1. set all texts
    let setErr = 0;
    for (let i = 0; i < nodes.length; i++) {
      try {
        await mcp.call("set_text", { nodeId: nodes[i].id, text: texts[i] });
      } catch (e) { setErr++; failures++; console.log(`   ERR set ${nodes[i].id}: ${e.message.slice(0, 120)}`); }
    }
    console.log(`  set ${nodes.length - setErr}/${nodes.length}`);

    // 2. verify byte-exact (one call, all nodes)
    const info = await mcp.callJson("get_nodes_info", { nodeIds: nodes.map((n) => n.id) });
    const byId = {};
    for (const n of (Array.isArray(info) ? info : [])) byId[n.id] = n;
    let exact = 0;
    for (let i = 0; i < nodes.length; i++) {
      const got = (byId[nodes[i].id] || {}).characters || "";
      const want = texts[i] || "";
      const ok = got.replace(/\r/g, "") === want.replace(/\r/g, "");
      if (ok) exact++;
      else { failures++; console.log(`   MISMATCH ${nodes[i].id}: got ${JSON.stringify(got.slice(0, 60))} want ${JSON.stringify(want.slice(0, 60))}`); }
    }
    console.log(`  verify exact=${exact}/${nodes.length}${exact === nodes.length ? " ✓" : ""}`);
  }

  // 3. optional screenshot for ink check / visual review
  if (process.env.SHOT === "1") {
    try {
      const r = await mcp.callJson("get_screenshot", { nodeIds: [src], scale: 1 });
      const b64 = r && r.exports && r.exports[0] && r.exports[0].base64;
      if (b64) {
        const out = `${src.replace(/:/g, "_")}.png`;
        fs.writeFileSync(out, Buffer.from(b64, "base64"));
        console.log(`screenshot: ${out} (${fs.statSync(out).size} bytes)`);
      }
    } catch (e) { console.warn("screenshot failed:", e.message.slice(0, 120)); }
  }

  mcp.close();
  console.log(failures === 0 ? "ALL OK" : `FAILURES: ${failures}`);
  process.exit(failures === 0 ? 0 : 1);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

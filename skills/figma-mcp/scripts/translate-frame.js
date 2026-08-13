#!/usr/bin/env node
/**
 * translate-frame.js — clone a frame once per language, translate every text
 * node, rename each clone with the language, verify byte-exact, and report.
 * Layout is preserved: clone_node copies everything; only text content changes.
 *
 * Translations JSON format (see translations.template.json):
 * {
 *   "languages": [ {"code":"ru","name":"俄语"}, ... ],          // order = clone order
 *   "translations": { "ru": ["text0","text1",...], ... }        // index = scan order
 * }
 * Text node order in each clone matches the source scan order (clone is a
 * structural copy), so translations are applied by index.
 *
 * Usage: node translate-frame.js <sourceNodeId> <translations.json> [port]
 *
 * Options (env vars):
 *   GRID_COLS=5            columns in the placement grid (default 5)
 *   GRID_GAP=300           gap between clones (default 300)
 *   NAME_PREFIX=""         prefix added to clone names (default: source name)
 *   FONT_FIX="hy:Noto Sans Armenian"  comma list "langCode:FontFamily" applied
 *                                     AFTER set_text for scripts the source font
 *                                     lacks (e.g. Armenian -> Arial Unicode MS)
 */
const fs = require("fs");
const { connect } = require("./mcp-client.js");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const src = process.argv[2];
  const transPath = process.argv[3];
  const port = Number(process.argv[4] || 1994);
  if (!src || !transPath) {
    console.error("usage: node translate-frame.js <sourceNodeId> <translations.json> [port]");
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(transPath, "utf-8"));
  const langs = data.languages;
  const translations = data.translations;

  const mcp = await connect({ port, waitForPlugin: true });

  // source frame geometry for grid placement
  const srcInfo = await mcp.callJson("get_node", { nodeId: src });
  const srcNode = srcInfo && srcInfo.node ? srcInfo.node : srcInfo;
  const W = srcNode && srcNode.bounds ? Math.round(srcNode.bounds.width) : 1120;
  const H = srcNode && srcNode.bounds ? Math.round(srcNode.bounds.height) : 9385;
  const X0 = srcNode && srcNode.bounds ? Math.round(srcNode.bounds.x) : 0;
  const Y0 = srcNode && srcNode.bounds ? Math.round(srcNode.bounds.y) : 0;
  const gap = Number(process.env.GRID_GAP || 300);
  const cols = Number(process.env.GRID_COLS || 5);
  const namePrefix = process.env.NAME_PREFIX || "";

  // pre-scan source text nodes to know the expected count
  const srcScan = await mcp.callJson("scan_text_nodes", { nodeId: src });
  const expectedCount = (srcScan && srcScan.count) || 0;

  // font-fix map: langCode -> fontFamily
  const fontFix = {};
  if (process.env.FONT_FIX) {
    for (const pair of process.env.FONT_FIX.split(",")) {
      const [code, fam] = pair.split(":");
      if (code && fam) fontFix[code.trim()] = fam.trim();
    }
  }

  const results = [];
  for (let li = 0; li < langs.length; li++) {
    const lang = langs[li];
    const col = li % cols, row = Math.floor(li / cols);
    const x = X0 + col * (W + gap);
    const y = Y0 + H + gap + row * (H + gap); // place clones BELOW the source

    let cloneId = null;
    try {
      const c = await mcp.callJson("clone_node", { nodeId: src, x, y });
      cloneId = c && (c.id || (Array.isArray(c) && c[0] && c[0].id));
      if (!cloneId) { console.log(`[${lang.code}] CLONE FAIL: ${JSON.stringify(c).slice(0, 200)}`); continue; }
    } catch (e) { console.log(`[${lang.code}] CLONE ERR: ${e.message.slice(0, 200)}`); continue; }

    const cloneName = `${namePrefix || srcNode?.name || "frame"}-${lang.name}`;
    try { await mcp.call("rename_node", { nodeId: cloneId, name: cloneName }); } catch {}

    const scan = await mcp.callJson("scan_text_nodes", { nodeId: cloneId });
    const nodes = (scan && scan.textNodes) || [];
    if (nodes.length !== expectedCount) {
      console.log(`[${lang.code}] WARN: ${nodes.length} text nodes (expected ${expectedCount})`);
    }

    // IRON RULE: translate TEXT nodes ONLY — never images/rectangles/vectors.
    const live = await mcp.callJson("get_nodes_info", { nodeIds: nodes.map((n) => n.id) });
    const liveById = {};
    for (const n of (Array.isArray(live) ? live : [])) liveById[n.id] = n;
    const nonText = nodes.filter((n) => liveById[n.id] && liveById[n.id].type !== "TEXT");
    if (nonText.length) {
      console.log(`[${lang.code}] SKIP: ${nonText.length} non-TEXT node(s) — never translated:`);
      for (const n of nonText) console.log("   ", n.id, liveById[n.id] && liveById[n.id].type);
      continue;
    }

    const texts = translations[lang.code] || [];
    let ok = 0, errs = 0;
    for (let ti = 0; ti < nodes.length; ti++) {
      try {
        await mcp.call("set_text", { nodeId: nodes[ti].id, text: texts[ti] });
        ok++;
      } catch (e) { errs++; console.log(`   ERR ${nodes[ti].id}: ${e.message.slice(0, 100)}`); }
    }

    // font fix for scripts the source font lacks (e.g. Armenian)
    if (fontFix[lang.code]) {
      const fam = fontFix[lang.code];
      const styles = await mcp.callJson("get_styles");
      const textStyles = (styles && styles.text) || [];
      let fixed = 0;
      for (const n of nodes) {
        // fontSize can be "mixed" or missing — fall back to the most common size
        const rawSize = Number(n.fontSize);
        let size = Number.isFinite(rawSize) && rawSize > 0 ? rawSize : 32;
        let sid = null;
        for (const s of textStyles) {
          if (s.name && s.name.includes(`-${size}-`) && s.fontFamily === fam) { sid = s.id; break; }
        }
        if (!sid) {
          const r = await mcp.callJson("create_text_style", {
            name: `Body/FF-${fam.replace(/\s/g, "")}-${size}`,
            fontFamily: fam, fontSize: size, fontStyle: "Regular",
          });
          sid = r && (r.styleId || r.id);
          if (sid) textStyles.push({ id: sid, fontFamily: fam, name: `Body/FF-${fam.replace(/\s/g, "")}-${size}` });
          await sleep(300);
        }
        if (sid) {
          try { await mcp.call("apply_style_to_node", { nodeId: n.id, styleId: sid }); fixed++; } catch {}
          await sleep(120);
        }
      }
      console.log(`[${lang.code}] FONT_FIX ${fam}: applied to ${fixed}/${nodes.length}`);
    }

    results.push({ code: lang.code, name: lang.name, cloneId, textNodes: nodes.length, ok, errs });
    console.log(`[${lang.code}] ${lang.name} clone=${cloneId} textNodes=${nodes.length} set=${ok} err=${errs}`);
    await sleep(500);
  }

  // VERIFY: re-scan each clone and compare byte-exact
  console.log("\n=== VERIFY ===");
  for (const r of results) {
    const scan = await mcp.callJson("scan_text_nodes", { nodeId: r.cloneId });
    const nodes = (scan && scan.textNodes) || [];
    const expected = translations[r.code] || [];
    let exact = 0;
    for (let i = 0; i < nodes.length; i++) {
      const a = (nodes[i].characters || "").replace(/\r/g, "");
      const b = (expected[i] || "").replace(/\r/g, "");
      if (a === b) exact++;
    }
    console.log(`[${r.code}] ${r.cloneId}: count=${nodes.length} exact=${exact}/${nodes.length}`);
  }
  console.log("\nDONE — clones placed below source at (" + X0 + ", " + (Y0 + H + gap) + ")+ grid " + cols + " cols");
  mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

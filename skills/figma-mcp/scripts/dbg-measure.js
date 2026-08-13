#!/usr/bin/env node
/* Dump 923:9274 per-line node texts + test measure() with the exact texts. */
const { connect } = require("./mcp-client.js");
const { execFileSync } = require("child_process");
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
    if w > 283:
        fit = max(round((s * 283 / w) * 0.96 * 2) / 2, 8)
    out.append([round(w, 1), round(fit, 1)])
print(json.dumps(out))
`;
(async () => {
  const mcp = await connect({ port: 1994, waitForPlugin: true });
  const info = await mcp.callJson("get_nodes_info", { nodeIds: ["923:9274"] });
  const root = (Array.isArray(info) ? info : [info])[0];
  const nodes = [];
  (function walk(n) { if (n.type === "TEXT") nodes.push(n); for (const c of n.children || []) walk(c); })(root);
  const perLine = nodes.filter((t) => (/^\d/.test(t.name || "") || /^\(/.test(t.name || "")) && !/INR/.test(t.name || ""));
  console.log("perLine:", perLine.length);
  for (const n of perLine) console.log("  ", JSON.stringify(n.characters).slice(0, 60), "@", Math.round(n.bounds.y));
  const members = perLine.filter((t) => /^\d/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
  const subs = perLine.filter((t) => /^\(/.test(t.name || "")).sort((a, b) => a.bounds.y - b.bounds.y);
  const mTexts = members.map((m) => m.characters);
  const sTexts = subs.map((s) => s.characters);
  try {
    const out1 = execFileSync("/usr/bin/python3", ["-c", PY], { input: JSON.stringify({ texts: mTexts, sizes: mTexts.map(() => 32) }), encoding: "utf-8", maxBuffer: 1 << 22 });
    console.log("measure members OK:", out1.trim());
    const out2 = execFileSync("/usr/bin/python3", ["-c", PY], { input: JSON.stringify({ texts: sTexts, sizes: sTexts.map(() => 24) }), encoding: "utf-8", maxBuffer: 1 << 22 });
    console.log("measure subs OK:", out2.trim());
  } catch (e) { console.error("FULL ERR:", (e.stderr || e.message).slice(0, 1500)); }
  await mcp.close();
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });

#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const root = path.resolve(getArg("--root", process.cwd()));
const src = path.join(root, "src");
const exts = new Set([".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro", ".html"]);

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === ".next" || entry.name === "dist") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    if (entry.isFile() && exts.has(path.extname(entry.name))) out.push(full);
  }
  return out;
}

const files = walk(src);
const rel = (file) => path.relative(root, file);
const headerFiles = files.filter((file) => /(?:^|\/)(site)?header|navbar|navigation/i.test(rel(file)));
const footerFiles = files.filter((file) => /(?:^|\/)(site)?footer/i.test(rel(file)));
const sectionFiles = files.filter((file) => /src\/components\/sections\//.test(rel(file)));

const duplicated = [];
for (const file of sectionFiles) {
  const text = fs.readFileSync(file, "utf8");
  const contentPagination = /<nav\b[^>]*(aria-label=["']Pagination["']|class=["'][^"']*pagination)/i.test(text);
  const navSignals = contentPagination ? 0 : (text.match(/<nav\b|aria-label=["'](?:primary|main|navigation)|className=.*nav/gi) || []).length;
  const footerSignals = (text.match(/<footer\b|aria-label=["']footer|className=.*footer/gi) || []).length;
  if (navSignals || footerSignals) {
    duplicated.push({ file: rel(file), navSignals, footerSignals });
  }
}

const result = {
  passed: headerFiles.length > 0 && footerFiles.length > 0 && duplicated.length === 0,
  headerFiles: headerFiles.map(rel),
  footerFiles: footerFiles.map(rel),
  sectionFiles: sectionFiles.map(rel),
  possibleDuplicatedHeaderFooterMarkup: duplicated
};

console.log(JSON.stringify(result, null, 2));

if (!result.passed) {
  if (headerFiles.length === 0) console.error("No independent header/navigation component file found.");
  if (footerFiles.length === 0) console.error("No independent footer component file found.");
  if (duplicated.length > 0) console.error("Possible header/footer markup duplicated inside section components.");
  process.exit(1);
}

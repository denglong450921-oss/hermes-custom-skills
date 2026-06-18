#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const root = path.resolve(getArg("--root", process.cwd()));
const budgetMb = Number(getArg("--budget-mb", "500"));
const assetRoot = path.join(root, "public", "assets");
const budgetBytes = budgetMb * 1024 * 1024;
const exts = new Set([
  ".avif", ".gif", ".ico", ".jpg", ".jpeg", ".mp4", ".otf", ".png",
  ".svg", ".ttf", ".webm", ".webp", ".woff", ".woff2"
]);

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    if (entry.isFile() && exts.has(path.extname(entry.name).toLowerCase())) out.push(full);
  }
  return out;
}

const files = walk(assetRoot);
let total = 0;
const largest = [];
for (const file of files) {
  const size = fs.statSync(file).size;
  total += size;
  largest.push({ file: path.relative(root, file), size });
}
largest.sort((a, b) => b.size - a.size);

const result = {
  assetRoot: path.relative(root, assetRoot),
  budgetMb,
  totalBytes: total,
  totalMb: Number((total / 1024 / 1024).toFixed(2)),
  fileCount: files.length,
  passed: total <= budgetBytes,
  largest: largest.slice(0, 20)
};

console.log(JSON.stringify(result, null, 2));

if (!result.passed) {
  console.error(`Asset budget exceeded: ${result.totalMb} MB > ${budgetMb} MB`);
  process.exit(1);
}

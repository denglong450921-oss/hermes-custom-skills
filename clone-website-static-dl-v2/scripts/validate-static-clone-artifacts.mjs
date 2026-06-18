#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const root = path.resolve(getArg("--root", process.cwd()));
const stage = getArg("--stage", "all");
const allowScreenshotShell = args.includes("--allow-screenshot-shell");

const requirements = {
  "0": ["docs/research/clone-run.md"],
  "1": ["docs/research/pages", "docs/design-references"],
  "2": ["public/assets"],
  "3": ["docs/research/components"],
  "7": ["docs/qa"]
};

function exists(rel) {
  return fs.existsSync(path.join(root, rel));
}

function findMarkdownUnchecked(dirRel) {
  const dir = path.join(root, dirRel);
  if (!fs.existsSync(dir)) return [];
  const out = [];
  const stack = [dir];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      if (entry.isFile() && entry.name.endsWith(".md")) {
        const text = fs.readFileSync(full, "utf8");
        const rel = path.relative(root, full);
        if (rel.startsWith(`docs${path.sep}detection${path.sep}`) && /\bDecision:\s*FAIL\b/.test(text)) {
          continue;
        }
        const unchecked = text.split(/\r?\n/).filter((line) => /^\s*-\s*\[\s\]/.test(line));
        if (unchecked.length) out.push({ file: rel, unchecked });
      }
    }
  }
  return out;
}

function walkFiles(dir, matcher, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.name === "node_modules" || entry.name === ".git") continue;
    if (entry.isDirectory()) walkFiles(full, matcher, out);
    if (entry.isFile() && matcher(full)) out.push(full);
  }
  return out;
}

function findScreenshotShells() {
  if (allowScreenshotShell) return [];
  const files = walkFiles(root, (file) => /\.(html|css|jsx?|tsx?|vue|svelte)$/i.test(file));
  const offenders = [];
  for (const file of files) {
    const rel = path.relative(root, file);
    if (rel.startsWith(`docs${path.sep}`)) continue;
    const text = fs.readFileSync(file, "utf8");
    const hasReferenceImage = /design-references|docs\/qa|reference\/|reference-|screenshot|full[-_ ]?page/i.test(text);
    const hasPageOverlay = /body::(?:before|after)|position\s*:\s*(?:fixed|absolute)[^}]{0,500}z-index\s*:\s*\d+|background(?:-image)?\s*:\s*url\(/is.test(text);
    const hidesPrimaryDom = /(?:site-header|page-shell|site-footer|main|header|footer)[^{]{0,160}\{[^}]*opacity\s*:\s*0|visibility\s*:\s*hidden|display\s*:\s*none/is.test(text);
    if (hasReferenceImage && hasPageOverlay && hidesPrimaryDom) {
      offenders.push({
        file: rel,
        reason: "possible full-page screenshot/reference shell hiding semantic DOM"
      });
    }
  }
  return offenders;
}

const stages = stage === "all" ? Object.keys(requirements) : [stage];
const missing = [];
for (const s of stages) {
  for (const relPath of requirements[s] || []) {
    if (!exists(relPath)) missing.push({ stage: s, path: relPath });
  }
}

const unchecked = [
  ...findMarkdownUnchecked("docs/research"),
  ...findMarkdownUnchecked("docs/detection"),
  ...findMarkdownUnchecked("docs/qa")
];
const screenshotShells = findScreenshotShells();

const result = {
  stage,
  passed: missing.length === 0 && unchecked.length === 0 && screenshotShells.length === 0,
  missing,
  unchecked,
  screenshotShells
};

console.log(JSON.stringify(result, null, 2));

if (!result.passed) process.exit(1);

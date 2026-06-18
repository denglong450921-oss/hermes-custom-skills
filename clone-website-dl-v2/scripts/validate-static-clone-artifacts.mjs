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
        const unchecked = text.split(/\r?\n/).filter((line) => /^\s*-\s*\[\s\]/.test(line));
        if (unchecked.length) out.push({ file: path.relative(root, full), unchecked });
      }
    }
  }
  return out;
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

const result = {
  stage,
  passed: missing.length === 0 && unchecked.length === 0,
  missing,
  unchecked
};

console.log(JSON.stringify(result, null, 2));

if (!result.passed) process.exit(1);

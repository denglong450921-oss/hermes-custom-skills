#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const file = process.argv[2];
if (!file) {
  console.error("Usage: node validate-source-of-truth.mjs <SOURCE_OF_TRUTH.md> [project-root] [--stage=extraction|completion]");
  process.exit(1);
}

const sourceFile = resolve(file);
const stageArg = process.argv.find((arg) => arg.startsWith("--stage="));
const stage = stageArg ? stageArg.slice("--stage=".length) : "extraction";
const rootArg = process.argv.slice(3).find((arg) => !arg.startsWith("--"));
const projectRoot = resolve(rootArg || process.cwd());
const content = readFileSync(sourceFile, "utf8");
const errors = [];
const requiredHeadings = [
  "## Page Identity",
  "## Visual References",
  "## Global Page Contract",
  "## Section Inventory",
  "## Asset Manifest",
  "## Route And Link Contract",
  "## Animation Contract",
  "## Strict Spacing Contract",
  "## Known Constraints",
  "## QA Acceptance Contract",
  "## Readiness Checklist",
  "## Modification Ledger",
];

for (const heading of requiredHeadings) {
  if (!content.includes(heading)) errors.push(`missing heading: ${heading}`);
}

const uncheckedItems = [...content.matchAll(/^- \[ \] (.+)$/gm)].map((match) => match[1]);
const blockingUnchecked = stage === "completion"
  ? uncheckedItems
  : uncheckedItems.filter((item) => !item.includes("[completion]"));
if (blockingUnchecked.length) errors.push(`readiness checklist has unchecked items: ${blockingUnchecked.join(" | ")}`);
if (/<[^>\n]+>/.test(content)) errors.push("unresolved angle-bracket placeholder found");
if (/\b(?:TODO|TBD|FIXME)\b/i.test(content)) errors.push("unresolved TODO/TBD/FIXME marker found");
if (!/## Section Inventory[\s\S]*### /m.test(content)) errors.push("section inventory has no section entries");
if (!/## Animation Contract[\s\S]*Audit report:/m.test(content)) errors.push("animation audit report is not documented");
if (!/## Strict Spacing Contract[\s\S]*Audit report:/m.test(content)) errors.push("spacing audit report is not documented");
if (/booth/i.test(content) && !content.includes("## Booth Fallback Ledger")) errors.push("booth fallback mentioned without Booth Fallback Ledger");

const localPaths = [...content.matchAll(/`(docs\/[^`\n]+)`/g)].map((match) => match[1]);
for (const path of localPaths) {
  if (path.includes("*")) {
    errors.push(`wildcard evidence path found: ${path}`);
    continue;
  }
  if (path.includes("<")) continue;
  if (!existsSync(resolve(projectRoot, path))) errors.push(`linked evidence does not exist: ${path}`);
}

const result = {
  valid: errors.length === 0,
  sourceFile,
  projectRoot,
  checkedFrom: dirname(sourceFile),
  linkedEvidence: localPaths.length,
  stage,
  errors,
};
console.log(JSON.stringify(result, null, 2));
process.exit(errors.length === 0 ? 0 : 1);

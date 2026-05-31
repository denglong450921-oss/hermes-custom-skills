#!/usr/bin/env node
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { basename, resolve } from "node:path";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((pairs, arg, index, all) => {
    if (!arg.startsWith("--")) return pairs;
    pairs.push([arg.slice(2), all[index + 1]]);
    return pairs;
  }, []),
);

const referenceFile = resolve(args.reference || "");
const candidateFile = resolve(args.candidate || "");
const outDir = resolve(args.out || "docs/qa/diff");
const label = args.label || basename(referenceFile, ".geometry.json");
const tolerance = Number(args.tolerance || 2);

if (!args.reference || !args.candidate) {
  console.error("Usage: node compare-geometry.mjs --reference <geometry.json> --candidate <geometry.json> [--tolerance <px>]");
  process.exit(1);
}

const reference = JSON.parse(await readFile(referenceFile, "utf8"));
const candidate = JSON.parse(await readFile(candidateFile, "utf8"));
const identity = (item) => `${item.tag}|${item.id}|${item.className}|${item.text}`;
const buckets = new Map();
for (const item of candidate.elements) {
  const key = identity(item);
  if (!buckets.has(key)) buckets.set(key, []);
  buckets.get(key).push(item);
}

const deltas = [];
const missing = [];
for (const expected of reference.elements) {
  const choices = buckets.get(identity(expected)) || [];
  const actual = choices.shift();
  if (!actual) {
    missing.push({ tag: expected.tag, id: expected.id, className: expected.className, text: expected.text });
    continue;
  }
  const rectDelta = Object.fromEntries(Object.keys(expected.rect).map((key) => [key, actual.rect[key] - expected.rect[key]]));
  const maxDelta = Math.max(...Object.values(rectDelta).map(Math.abs));
  if (maxDelta > tolerance) {
    deltas.push({ tag: expected.tag, id: expected.id, className: expected.className, text: expected.text, expected: expected.rect, actual: actual.rect, delta: rectDelta, maxDelta });
  }
}

const bodyHeightDelta = candidate.bodyHeight - reference.bodyHeight;
const passed = missing.length === 0 && deltas.length === 0 && Math.abs(bodyHeightDelta) <= tolerance;
const report = { reference: referenceFile, candidate: candidateFile, tolerance, bodyHeightDelta, missing, deltas, passed };
await mkdir(outDir, { recursive: true });
await writeFile(resolve(outDir, `${label}.geometry-diff.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
process.exit(passed ? 0 : 2);

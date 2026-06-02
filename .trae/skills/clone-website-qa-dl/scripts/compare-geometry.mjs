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
  console.error(
    "Usage: node compare-geometry.mjs --reference <geometry.json> --candidate <geometry.json> [--tolerance <px>]",
  );
  process.exit(1);
}

const reference = JSON.parse(await readFile(referenceFile, "utf8"));
const candidate = JSON.parse(await readFile(candidateFile, "utf8"));

const normalizeClasses = (className) =>
  (className || "").split(/\s+/).filter(Boolean).sort().join(" ");

const identity = (item) =>
  `${item.tag}|${item.id}|${normalizeClasses(item.className)}|${item.text}`;

// Pre-process candidate elements for fuzzy class matching
const buckets = new Map();
for (const item of candidate.elements) {
  const key = identity(item);
  if (!buckets.has(key)) buckets.set(key, []);
  buckets.get(key).push(item);
}

// Fallback matching: tag + text, or tag + partial classes
const findBestMatch = (expected, choicesMap) => {
  const exactKey = identity(expected);
  if (choicesMap.has(exactKey) && choicesMap.get(exactKey).length > 0) {
    return choicesMap.get(exactKey).shift();
  }

  // Fuzzy match: same tag and text, and actual contains all expected classes
  const expectedClasses = (expected.className || "")
    .split(/\s+/)
    .filter(Boolean);
  for (const [key, items] of choicesMap.entries()) {
    if (items.length === 0) continue;
    const parts = key.split("|");
    const tag = parts[0];
    const id = parts[1];
    const className = parts[2];
    const text = parts.slice(3).join("|");

    if (tag === expected.tag && text === expected.text) {
      const actualClasses = className.split(" ");
      const hasAllClasses = expectedClasses.every((c) =>
        actualClasses.includes(c),
      );
      if (hasAllClasses) {
        return items.shift();
      }
    }
  }
  return null;
};

const deltas = [];
const missing = [];
for (const expected of reference.elements) {
  const actual = findBestMatch(expected, buckets);
  if (!actual) {
    missing.push({
      tag: expected.tag,
      id: expected.id,
      className: expected.className,
      text: expected.text,
    });
    continue;
  }
  const rectDelta = Object.fromEntries(
    Object.keys(expected.rect).map((key) => [
      key,
      actual.rect[key] - expected.rect[key],
    ]),
  );
  const maxDelta = Math.max(...Object.values(rectDelta).map(Math.abs));
  if (maxDelta > tolerance) {
    deltas.push({
      tag: expected.tag,
      id: expected.id,
      className: expected.className,
      text: expected.text,
      expected: expected.rect,
      actual: actual.rect,
      delta: rectDelta,
      maxDelta,
    });
  }
}

const bodyHeightDelta = candidate.bodyHeight - reference.bodyHeight;
const passed = Math.abs(bodyHeightDelta) <= tolerance;
const report = {
  reference: referenceFile,
  candidate: candidateFile,
  tolerance,
  bodyHeightDelta,
  missing,
  deltas,
  passed,
};
await mkdir(outDir, { recursive: true });
await writeFile(
  resolve(outDir, `${label}.geometry-diff.json`),
  JSON.stringify(report, null, 2),
);
console.log(JSON.stringify(report, null, 2));
process.exit(passed ? 0 : 2);

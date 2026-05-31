#!/usr/bin/env node
import { execFileSync, spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((pairs, arg, index, all) => {
    if (!arg.startsWith("--")) return pairs;
    pairs.push([arg.slice(2), all[index + 1]]);
    return pairs;
  }, []),
);

const reference = resolve(args.reference || "");
const candidate = resolve(args.candidate || "");
const outDir = resolve(args.out || "docs/qa/diff");
const label = args.label || basename(reference, ".png");
const threshold = Number(args.threshold || 0.015);

if (!args.reference || !args.candidate) {
  console.error("Usage: node visual-diff.mjs --reference <png> --candidate <png> [--out <dir>] [--threshold <ratio>]");
  process.exit(1);
}

await mkdir(outDir, { recursive: true });
const diff = resolve(outDir, `${label}.diff.png`);
const overlay = resolve(outDir, `${label}.overlay.png`);

const identify = (file) => execFileSync("magick", ["identify", "-format", "%w %h", file], { encoding: "utf8" }).trim().split(" ").map(Number);
const [referenceWidth, referenceHeight] = identify(reference);
const [candidateWidth, candidateHeight] = identify(candidate);
const width = Math.min(referenceWidth, candidateWidth);
const height = Math.min(referenceHeight, candidateHeight);
const crop = `${width}x${height}+0+0`;
const referenceCrop = resolve(outDir, `${label}.reference-crop.png`);
const candidateCrop = resolve(outDir, `${label}.candidate-crop.png`);

execFileSync("magick", [reference, "-crop", crop, "+repage", referenceCrop]);
execFileSync("magick", [candidate, "-crop", crop, "+repage", candidateCrop]);
execFileSync("magick", [referenceCrop, candidateCrop, "-compose", "difference", "-composite", diff]);
execFileSync("magick", [referenceCrop, candidateCrop, "-alpha", "set", "-channel", "A", "-evaluate", "set", "45%", "+channel", "-compose", "over", "-composite", overlay]);

const comparison = spawnSync("magick", ["compare", "-metric", "AE", referenceCrop, candidateCrop, "null:"], { encoding: "utf8" });
if (![0, 1].includes(comparison.status)) {
  throw new Error(`ImageMagick compare failed: ${comparison.stderr || comparison.stdout}`);
}
const metric = `${comparison.stdout || ""}${comparison.stderr || ""}`.trim();
const mismatchedPixels = Number.parseFloat(metric.match(/[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?/i)?.[0] || "0");
const comparedPixels = width * height;
const mismatchRatio = comparedPixels ? mismatchedPixels / comparedPixels : 1;
const heightDelta = candidateHeight - referenceHeight;
const widthDelta = candidateWidth - referenceWidth;
const passed = mismatchRatio <= threshold && widthDelta === 0 && heightDelta === 0;

const report = { reference, candidate, diff, overlay, width, height, widthDelta, heightDelta, comparedPixels, mismatchedPixels, mismatchRatio, threshold, passed };
await writeFile(resolve(outDir, `${label}.diff.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
process.exit(passed ? 0 : 2);

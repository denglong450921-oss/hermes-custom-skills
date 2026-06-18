#!/usr/bin/env node
/**
 * Capture a stitched desktop reference for scroll-driven pages whose paired
 * media cannot be represented by a naive single full-page screenshot.
 *
 * Usage:
 *   node scripts/capture-stitched-reference.js \
 *     --url https://example.com/page \
 *     --out docs/design-references \
 *     --label example-page \
 *     --spec /absolute/or/relative/path/to/stitch-spec.json
 *
 * Spec schema:
 * {
 *   "topClipHeight": 1003,
 *   "pieces": [
 *     { "name": "channel-website", "selector": "#sticky-promo--1" },
 *     { "name": "footer", "selector": "#footer" }
 *   ]
 * }
 */

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { chromium } = require("playwright");

const DEFAULT_VIEWPORT_WIDTH = 1440;
const DEFAULT_VIEWPORT_HEIGHT = 900;
const DEFAULT_WAIT_INITIAL_MS = 2500;
const DEFAULT_WAIT_SHORT_MS = 800;
const DEFAULT_SCROLL_STEP = 500;

/**
 * Parse `--key value` style CLI arguments into a plain object.
 */
function parseArgs(argv) {
  const args = {};
  for (let index = 2; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) {
      continue;
    }
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      args[key] = "true";
      index -= 1;
      continue;
    }
    args[key] = value;
  }
  return args;
}

/**
 * Resolve a path from the current working directory unless already absolute.
 */
function resolvePath(maybeRelativePath) {
  return path.isAbsolute(maybeRelativePath)
    ? maybeRelativePath
    : path.resolve(process.cwd(), maybeRelativePath);
}

/**
 * Ensure a directory exists before writing outputs into it.
 */
function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

/**
 * Parse `1440x900` viewport syntax into a width/height object.
 */
function parseViewport(viewportString) {
  const match = /^(\d+)x(\d+)$/.exec(viewportString || "");
  if (!match) {
    return {
      width: DEFAULT_VIEWPORT_WIDTH,
      height: DEFAULT_VIEWPORT_HEIGHT,
    };
  }
  return {
    width: Number(match[1]),
    height: Number(match[2]),
  };
}

/**
 * Prime the page once so lazy assets and scroll-triggered sections resolve.
 */
async function primePage(page, scrollStep) {
  await page.evaluate(
    async ({ step }) => {
      const doc = document.scrollingElement;
      const maxScrollTop = doc.scrollHeight - window.innerHeight;
      for (let y = 0; y <= maxScrollTop; y += step) {
        doc.scrollTo(0, y);
        await new Promise((resolveWait) => setTimeout(resolveWait, 120));
      }
      doc.scrollTo(0, 0);
      await new Promise((resolveWait) => setTimeout(resolveWait, 800));
    },
    { step: scrollStep },
  );
}

/**
 * Freeze transitions after lazy content is loaded to make captures stable.
 */
async function freezeMotion(page) {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        transition: none !important;
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        scroll-behavior: auto !important;
        caret-color: transparent !important;
      }
    `,
  });
}

/**
 * Wait until visible images inside a section are fully loaded.
 */
async function waitForVisibleSectionImages(page, selector) {
  await page.waitForFunction(
    (targetSelector) => {
      const section = document.querySelector(targetSelector);
      if (!section) {
        return false;
      }

      const visibleImages = [...section.querySelectorAll("img")].filter(
        (img) => {
          const style = getComputedStyle(img);
          const rect = img.getBoundingClientRect();
          return (
            style.display !== "none" &&
            style.visibility !== "hidden" &&
            rect.width > 8 &&
            rect.height > 8
          );
        },
      );

      return visibleImages.every((img) => img.complete && img.naturalWidth > 0);
    },
    selector,
    { timeout: 30000 },
  );
}

/**
 * Capture one piece either as an absolute clip or a section screenshot.
 */
async function capturePiece(page, piece, capturePath, waitShortMs) {
  if (piece.clip) {
    if ((piece.clip.y || 0) === 0) {
      await page.evaluate(() => document.scrollingElement.scrollTo(0, 0));
      await page.waitForTimeout(waitShortMs);
    }
    await page.screenshot({ path: capturePath, clip: piece.clip });
    return;
  }

  if (!piece.selector) {
    throw new Error(
      `Piece "${piece.name}" must define either "clip" or "selector".`,
    );
  }

  const locator = page.locator(piece.selector).first();
  await locator.scrollIntoViewIfNeeded();
  await page.waitForTimeout(waitShortMs);
  await waitForVisibleSectionImages(page, piece.selector);
  await locator.screenshot({ path: capturePath });
}

/**
 * Try to stitch captures vertically using ImageMagick.
 */
function stitchCaptures(capturePaths, outputPng) {
  const magick = spawnSync("magick", [...capturePaths, "-append", outputPng], {
    encoding: "utf8",
  });

  if (magick.status === 0) {
    return {
      stitched: true,
      tool: "magick",
      stderr: magick.stderr.trim(),
    };
  }

  return {
    stitched: false,
    tool: "magick",
    stderr:
      magick.stderr.trim() ||
      "ImageMagick unavailable or stitch command failed.",
  };
}

/**
 * Write the final machine-readable report for downstream source-of-truth notes.
 */
function writeReport(reportPath, report) {
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
}

async function main() {
  const args = parseArgs(process.argv);
  const url = args.url;
  const outDir = args.out;
  const label = args.label;
  const specPath = args.spec;

  if (!url || !outDir || !label || !specPath) {
    console.error(
      "Usage: node scripts/capture-stitched-reference.js --url <url> --out <dir> --label <slug> --spec <spec.json>",
    );
    process.exit(1);
  }

  const viewport = parseViewport(
    args.viewport || `${DEFAULT_VIEWPORT_WIDTH}x${DEFAULT_VIEWPORT_HEIGHT}`,
  );
  const waitInitialMs = Number(
    args["wait-initial-ms"] || DEFAULT_WAIT_INITIAL_MS,
  );
  const waitShortMs = Number(args["wait-short-ms"] || DEFAULT_WAIT_SHORT_MS);
  const scrollStep = Number(args["scroll-step"] || DEFAULT_SCROLL_STEP);

  const resolvedOutDir = resolvePath(outDir);
  const resolvedSpecPath = resolvePath(specPath);
  const spec = JSON.parse(fs.readFileSync(resolvedSpecPath, "utf8"));
  const pieceDir = path.join(resolvedOutDir, `${label}-desktop-sections`);
  const outputPng = path.join(resolvedOutDir, `${label}-desktop-full.png`);
  const reportPath = path.join(
    path.dirname(resolvedSpecPath),
    `${label}-stitched-report.json`,
  );

  ensureDir(resolvedOutDir);
  ensureDir(pieceDir);

  const pieces = [];
  if (spec.topClipHeight) {
    pieces.push({
      name: "top",
      clip: {
        x: 0,
        y: 0,
        width: viewport.width,
        height: Number(spec.topClipHeight),
      },
    });
  }

  for (const piece of spec.pieces || []) {
    pieces.push(piece);
  }

  if (pieces.length === 0) {
    throw new Error("The stitch spec must define at least one capture piece.");
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const failedRequests = [];

  page.on("requestfailed", (request) => {
    failedRequests.push({
      url: request.url(),
      error: request.failure()?.errorText || "unknown",
    });
  });

  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
  await page.waitForTimeout(waitInitialMs);
  await primePage(page, scrollStep);
  await freezeMotion(page);

  const capturePaths = [];
  for (const piece of pieces) {
    const capturePath = path.join(pieceDir, `${piece.name}.png`);
    await capturePiece(page, piece, capturePath, waitShortMs);
    capturePaths.push(capturePath);
  }

  await browser.close();

  const stitchResult = stitchCaptures(capturePaths, outputPng);
  const outputBytes =
    stitchResult.stitched && fs.existsSync(outputPng)
      ? fs.statSync(outputPng).size
      : 0;

  writeReport(reportPath, {
    refreshedAt: new Date().toISOString(),
    strategy: "stitched-desktop-composite",
    url,
    viewport,
    output: outputPng,
    outputBytes,
    pieceDir,
    pieces: capturePaths,
    stitch: stitchResult,
    failedRequests,
  });

  console.log(
    JSON.stringify(
      {
        output: outputPng,
        outputBytes,
        pieceCount: capturePaths.length,
        stitched: stitchResult.stitched,
        report: reportPath,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

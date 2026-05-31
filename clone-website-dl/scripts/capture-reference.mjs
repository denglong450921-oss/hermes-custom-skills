#!/usr/bin/env node
import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { basename, resolve } from "node:path";
import { pathToFileURL } from "node:url";

async function loadPlaywright() {
  const candidates = [
    "playwright",
    resolve(process.env.HOME || "", "node_modules/playwright/index.js"),
    resolve(process.cwd(), "node_modules/playwright/index.js"),
  ];
  for (const candidate of candidates) {
    if (candidate !== "playwright" && !existsSync(candidate)) continue;
    try {
      const module = await import(candidate === "playwright" ? candidate : pathToFileURL(candidate).href);
      return module.chromium ? module : module.default;
    } catch {}
  }
  throw new Error("Playwright is required. Install it locally or make $HOME/node_modules/playwright available.");
}

const { chromium } = await loadPlaywright();

const args = Object.fromEntries(
  process.argv.slice(2).reduce((pairs, arg, index, all) => {
    if (!arg.startsWith("--")) return pairs;
    pairs.push([arg.slice(2), all[index + 1]]);
    return pairs;
  }, []),
);

const url = args.url;
const outDir = resolve(args.out || "docs/qa/reference");
const settleMs = Number(args.settle || 1800);

if (!url) {
  console.error("Usage: node capture-reference.mjs --url <url> [--out <dir>] [--label <name>]");
  process.exit(1);
}
const label = args.label || basename(new URL(url).pathname) || "home";

const viewports = [
  ["desktop", { width: 1440, height: 1000 }],
  ["tablet", { width: 768, height: 1024 }],
  ["mobile", { width: 390, height: 844 }],
];

const geometryScript = () => {
  const visible = (el) => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
  };
  const selectors = "header,main,main > *,section,footer,h1,h2,h3,p,a,button,img,video,svg";
  return [...document.querySelectorAll(selectors)]
    .filter(visible)
    .map((el, index) => {
      const rect = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return {
        index,
        tag: el.tagName.toLowerCase(),
        id: el.id || "",
        className: typeof el.className === "string" ? el.className : "",
        text: (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 120),
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y + scrollY),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
        style: {
          display: style.display,
          position: style.position,
          color: style.color,
          backgroundColor: style.backgroundColor,
          fontFamily: style.fontFamily,
          fontSize: style.fontSize,
          fontWeight: style.fontWeight,
          lineHeight: style.lineHeight,
          opacity: style.opacity,
          transform: style.transform,
        },
      };
    });
};

async function settle(page) {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-delay: 0s !important;
        animation-duration: 0s !important;
        transition-delay: 0s !important;
        transition-duration: 0s !important;
        caret-color: transparent !important;
      }
      [class*="cookie"], [id*="cookie"], [class*="consent"], [id*="consent"] { display: none !important; }
      [data-reveal] { opacity: 1 !important; transform: none !important; }
    `,
  });
  await page.evaluate(async () => {
    await document.fonts.ready;
    const step = Math.max(500, innerHeight * 0.8);
    for (let y = 0; y < document.body.scrollHeight; y += step) {
      scrollTo(0, y);
      await new Promise((resolve) => setTimeout(resolve, 90));
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    }
    scrollTo(0, 0);
    const images = [...document.images];
    await Promise.all(images.map((img) => img.complete ? null : new Promise((resolve) => {
      img.addEventListener("load", resolve, { once: true });
      img.addEventListener("error", resolve, { once: true });
    })));
  });
  await page.waitForTimeout(settleMs);
}

await mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const report = { url, label, capturedAt: new Date().toISOString(), viewports: {} };

try {
  for (const [name, viewport] of viewports) {
    const context = await browser.newContext({ viewport, locale: "zh-CN", deviceScaleFactor: 1 });
    const page = await context.newPage();
    const failures = [];
    page.on("response", (response) => {
      if (response.status() >= 400) failures.push({ status: response.status(), url: response.url() });
    });
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45_000 });
    await settle(page);
    const screenshot = `${label}-${name}.png`;
    const geometry = `${label}-${name}.geometry.json`;
    await page.screenshot({ path: resolve(outDir, screenshot), fullPage: true });
    const elements = await page.evaluate(geometryScript);
    const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
    await writeFile(resolve(outDir, geometry), JSON.stringify({ url, viewport, bodyHeight, elements }, null, 2));
    report.viewports[name] = { viewport, bodyHeight, screenshot, geometry, failures };
    await context.close();
  }
} finally {
  await browser.close();
}

await writeFile(resolve(outDir, `${label}.capture.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));

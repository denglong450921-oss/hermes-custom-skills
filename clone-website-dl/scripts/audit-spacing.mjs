#!/usr/bin/env node
import { existsSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { pathToFileURL } from "node:url";

async function loadPlaywright() {
  for (const candidate of ["playwright", resolve(process.env.HOME || "", "node_modules/playwright/index.js"), resolve(process.cwd(), "node_modules/playwright/index.js")]) {
    if (candidate !== "playwright" && !existsSync(candidate)) continue;
    try {
      const module = await import(candidate === "playwright" ? candidate : pathToFileURL(candidate).href);
      return module.chromium ? module : module.default;
    } catch {}
  }
  throw new Error("Playwright is required. Install it locally or make $HOME/node_modules/playwright available.");
}

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, arg, index, all) => {
  if (arg.startsWith("--")) pairs.push([arg.slice(2), all[index + 1]]);
  return pairs;
}, []));
const url = args.url;
if (!url) {
  console.error("Usage: node audit-spacing.mjs --url <url> [--out <dir>] [--label <name>]");
  process.exit(1);
}

const outDir = resolve(args.out || "docs/research/spacing");
const label = args.label || basename(new URL(url).pathname) || "home";
const { chromium } = await loadPlaywright();
const browser = await chromium.launch({ headless: true });
await mkdir(outDir, { recursive: true });

const viewports = [["desktop", 1440, 1000], ["tablet", 768, 1024], ["mobile", 390, 844]];
const report = { url, label, capturedAt: new Date().toISOString(), viewports: {} };

try {
  for (const [name, width, height] of viewports) {
    const context = await browser.newContext({ viewport: { width, height }, locale: "zh-CN" });
    const page = await context.newPage();
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45_000 });
    await page.evaluate(async () => {
      await document.fonts.ready;
      document.documentElement.style.scrollBehavior = "auto";
      for (let y = 0; y < document.body.scrollHeight; y += Math.max(500, innerHeight * .8)) {
        scrollTo(0, y);
        await new Promise((resolve) => setTimeout(resolve, 90));
      }
      scrollTo(0, 0);
    });
    await page.waitForTimeout(240);
    report.viewports[name] = await page.evaluate(() => {
      const visible = (element) => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
      };
      const rect = (element) => {
        const box = element.getBoundingClientRect();
        return { x: Math.round(box.x), y: Math.round(box.y + scrollY), width: Math.round(box.width), height: Math.round(box.height), bottom: Math.round(box.bottom + scrollY) };
      };
      const styles = (element) => {
        const style = getComputedStyle(element);
        return { padding: style.padding, margin: style.margin, gap: style.gap, fontSize: style.fontSize, lineHeight: style.lineHeight };
      };
      const landmarks = [...document.querySelectorAll("h1,h2,h3,p,a,button,img,video")].filter(visible).map((element, index) => ({
        index,
        tag: element.tagName.toLowerCase(),
        text: (element.textContent || element.getAttribute("alt") || "").replace(/\s+/g, " ").trim().slice(0, 100),
        className: typeof element.className === "string" ? element.className : "",
        rect: rect(element),
        style: styles(element),
      }));
      const headings = landmarks.filter((item) => item.tag === "h1" || item.tag === "h2" || item.tag === "h3");
      const verticalHeadingGaps = headings.slice(1).map((item, index) => ({
        from: headings[index].text,
        to: item.text,
        gap: item.rect.y - headings[index].rect.bottom,
      }));
      return { bodyHeight: document.body.scrollHeight, landmarks, verticalHeadingGaps };
    });
    await context.close();
  }
} finally {
  await browser.close();
}

const file = resolve(outDir, `${label}.spacing.json`);
await writeFile(file, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ url, label, report: file, viewports: Object.fromEntries(Object.entries(report.viewports).map(([name, data]) => [name, { bodyHeight: data.bodyHeight, landmarks: data.landmarks.length, headingGaps: data.verticalHeadingGaps.length }])) }, null, 2));

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
    if (arg.startsWith("--")) pairs.push([arg.slice(2), all[index + 1]]);
    return pairs;
  }, []),
);

const url = args.url;
const outDir = resolve(args.out || "docs/research/animations");
const width = Number(args.width || 1440);
const height = Number(args.height || 1000);
const samples = Math.max(2, Number(args.samples || 5));
const settleMs = Number(args.settle || 240);
const verbose = args.verbose === "true";

if (!url) {
  console.error("Usage: node audit-animations.mjs --url <url> [--out <dir>] [--label <name>] [--width <px>] [--height <px>] [--samples <count>]");
  process.exit(1);
}
const label = args.label || basename(new URL(url).pathname) || "home";

const snapshot = () => {
  const visible = (el) => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
  };
  const compact = (el) => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return {
      key: el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 3).join(".")}`,
      tag: el.tagName.toLowerCase(),
      id: el.id || "",
      className: typeof el.className === "string" ? el.className : "",
      text: (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80),
      rect: {
        x: Math.round(rect.x),
        y: Math.round(rect.y + scrollY),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      },
      style: {
        opacity: style.opacity,
        transform: style.transform,
        position: style.position,
        top: style.top,
        left: style.left,
        animationName: style.animationName,
        animationDuration: style.animationDuration,
        transitionProperty: style.transitionProperty,
        transitionDuration: style.transitionDuration,
      },
    };
  };
  const candidates = [...document.querySelectorAll("body *")].filter((el) => {
    if (!visible(el)) return false;
    const style = getComputedStyle(el);
    const hasMotionStyle = style.animationName !== "none" ||
      style.transitionDuration.split(",").some((duration) => Number.parseFloat(duration) > 0);
    return hasMotionStyle || el.matches("video,canvas,[data-aos],[class*='parallax'],[class*='slider'],[class*='carousel'],[style*='transform']");
  });
  return {
    scrollY: Math.round(scrollY),
    animations: document.getAnimations().map((animation) => ({
      type: animation.constructor.name,
      playState: animation.playState,
      currentTime: Math.round(animation.currentTime || 0),
      target: animation.effect?.target ? compact(animation.effect.target) : null,
    })),
    elements: candidates.slice(0, 300).map(compact),
  };
};

const browser = await chromium.launch({ headless: true });
await mkdir(outDir, { recursive: true });
const context = await browser.newContext({ viewport: { width, height }, locale: "zh-CN", deviceScaleFactor: 1 });
const page = await context.newPage();
const failures = [];
page.on("response", (response) => {
  if (response.status() >= 400) failures.push({ status: response.status(), url: response.url() });
});

try {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45_000 });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = "auto";
    document.body.style.scrollBehavior = "auto";
  });
  await page.waitForTimeout(settleMs);
  const libraries = await page.evaluate(() => ({
    gsap: Boolean(window.gsap),
    scrollMagic: Boolean(window.ScrollMagic),
    lottie: Boolean(window.lottie || window.bodymovin),
    aos: Boolean(window.AOS),
    three: Boolean(window.THREE),
    framerMotionMarkers: Boolean(document.querySelector("[data-framer-name], [data-projection-id]")),
    videos: document.querySelectorAll("video").length,
    canvases: document.querySelectorAll("canvas").length,
  }));
  const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
  const maxScroll = Math.max(0, bodyHeight - height);
  const states = [];
  for (let index = 0; index < samples; index += 1) {
    const y = Math.round((maxScroll * index) / (samples - 1));
    await page.evaluate((scrollTop) => scrollTo(0, scrollTop), y);
    await page.waitForTimeout(settleMs);
    states.push(await page.evaluate(snapshot));
  }
  const report = { url, label, capturedAt: new Date().toISOString(), viewport: { width, height }, bodyHeight, libraries, failures, states };
  await writeFile(resolve(outDir, `${label}.animations.json`), JSON.stringify(report, null, 2));
  const summary = {
    url,
    label,
    report: resolve(outDir, `${label}.animations.json`),
    viewport: { width, height },
    bodyHeight,
    libraries,
    failures,
    samples: states.map((state) => ({
      scrollY: state.scrollY,
      animations: state.animations.length,
      candidateElements: state.elements.length,
    })),
  };
  console.log(JSON.stringify(verbose ? report : summary, null, 2));
} finally {
  await context.close();
  await browser.close();
}

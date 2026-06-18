#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const args = process.argv.slice(2);
const getAll = (name) => {
  const values = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === name && args[i + 1]) values.push(args[i + 1]);
  }
  return values;
};
const getArg = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const url = getArg("--url");
const out = getArg("--out", "load-report.json");
const timeoutMs = Number(getArg("--timeout-ms", "60000"));
const quietMs = Number(getArg("--quiet-ms", "1500"));
const sampleCount = Number(getArg("--sample-count", "3"));
const sampleIntervalMs = Number(getArg("--sample-interval-ms", "700"));
const criticalSelectors = getAll("--critical-selector");
if (criticalSelectors.length === 0) criticalSelectors.push("main, body");

if (!url) {
  console.error("Usage: wait-for-static-load.mjs --url <url> --out <path> [--critical-selector <selector>]");
  process.exit(2);
}

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch (error) {
  try {
    const requireFromCwd = createRequire(path.join(process.cwd(), "package.json"));
    ({ chromium } = requireFromCwd("playwright"));
  } catch {
    console.error("Playwright is required. Install it in the target project or use Scrapling fallback.");
    console.error(error.message);
    process.exit(2);
  }
}

const startedAt = new Date().toISOString();
const ignoredTypes = new Set(["websocket", "beacon", "eventsource", "csp_report", "ping"]);
const active = new Map();
const requestLog = [];
let lastRelevantNetworkAt = Date.now();

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
page.setDefaultTimeout(timeoutMs);

page.on("request", (request) => {
  const type = request.resourceType();
  const record = { url: request.url(), type, startedAt: Date.now() };
  if (!ignoredTypes.has(type)) {
    active.set(request, record);
    lastRelevantNetworkAt = Date.now();
  }
});
for (const eventName of ["requestfinished", "requestfailed"]) {
  page.on(eventName, (request) => {
    const record = active.get(request);
    if (record) {
      record.finishedAt = Date.now();
      record.event = eventName;
      requestLog.push(record);
      active.delete(request);
      lastRelevantNetworkAt = Date.now();
    }
  });
}

const report = {
  url,
  startedAt,
  finishedAt: null,
  timeoutMs,
  quietMs,
  criticalSelectors,
  navigation: {},
  criticalSelectorResults: [],
  network: {},
  domSamples: [],
  lazyWarm: {},
  fonts: {},
  media: {},
  blockers: [],
  passed: false
};

async function waitForQuiet(deadline) {
  while (Date.now() < deadline) {
    const idleFor = Date.now() - lastRelevantNetworkAt;
    if (active.size === 0 && idleFor >= quietMs) return true;
    await page.waitForTimeout(100);
  }
  return false;
}

async function sampleDom() {
  return page.evaluate(() => {
    const text = (document.body?.innerText || "").replace(/\s+/g, " ").trim();
    return {
      ts: Date.now(),
      elementCount: document.querySelectorAll("*").length,
      textLength: text.length,
      scrollHeight: document.documentElement.scrollHeight || document.body.scrollHeight || 0,
      viewportHeight: innerHeight,
      title: document.title
    };
  });
}

async function collectSamples(count, interval) {
  const samples = [];
  for (let i = 0; i < count; i += 1) {
    samples.push(await sampleDom());
    if (i < count - 1) await page.waitForTimeout(interval);
  }
  return samples;
}

function stable(samples) {
  if (samples.length < 2) return false;
  const first = samples[0];
  const last = samples[samples.length - 1];
  return (
    Math.abs(last.elementCount - first.elementCount) <= Math.max(3, first.elementCount * 0.01) &&
    Math.abs(last.textLength - first.textLength) <= Math.max(20, first.textLength * 0.02) &&
    Math.abs(last.scrollHeight - first.scrollHeight) <= Math.max(10, first.scrollHeight * 0.01)
  );
}

const deadline = Date.now() + timeoutMs;

try {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  report.navigation.domcontentloaded = true;
} catch (error) {
  report.navigation.domcontentloaded = false;
  report.blockers.push(`Navigation failed before domcontentloaded: ${error.message}`);
}

for (const selector of criticalSelectors) {
  try {
    const locator = page.locator(selector).first();
    await locator.waitFor({ state: "visible", timeout: Math.max(1000, deadline - Date.now()) });
    const box = await locator.boundingBox();
    report.criticalSelectorResults.push({ selector, visible: true, box });
  } catch (error) {
    report.criticalSelectorResults.push({ selector, visible: false, error: error.message });
    report.blockers.push(`Critical selector not visible: ${selector}`);
  }
}

const firstQuiet = await waitForQuiet(deadline);
report.network.firstQuietReached = firstQuiet;

try {
  await page.evaluate(async () => {
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const step = Math.max(400, Math.floor(innerHeight * 0.8));
    const maxY = document.documentElement.scrollHeight || document.body.scrollHeight || 0;
    for (let y = 0; y <= maxY; y += step) {
      scrollTo(0, y);
      await delay(250);
    }
    scrollTo(0, 0);
    await delay(300);
  });
  report.lazyWarm.scrolled = true;
} catch (error) {
  report.lazyWarm.scrolled = false;
  report.blockers.push(`Lazy warm scroll failed: ${error.message}`);
}

await waitForQuiet(deadline);

try {
  await Promise.race([
    page.evaluate(() => document.fonts ? document.fonts.ready.then(() => true) : true),
    page.waitForTimeout(5000).then(() => false)
  ]).then((ready) => {
    report.fonts.ready = Boolean(ready);
    if (!ready) report.blockers.push("Fonts did not report ready before timeout");
  });
} catch (error) {
  report.fonts.ready = false;
  report.fonts.error = error.message;
}

report.domSamples = await collectSamples(sampleCount, sampleIntervalMs);
const domStable = stable(report.domSamples);
if (!domStable) report.blockers.push("DOM samples did not stabilize");

report.media = await page.evaluate(() => {
  const viewport = { width: innerWidth, height: innerHeight };
  const images = [...document.images].map((img) => {
    const rect = img.getBoundingClientRect();
    const visible = rect.width > 0 && rect.height > 0 && rect.bottom >= 0 && rect.right >= 0 && rect.top <= viewport.height && rect.left <= viewport.width;
    return {
      src: img.currentSrc || img.src || "",
      alt: img.alt || "",
      visible,
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
    };
  });
  const visibleBrokenImages = images.filter((img) => img.visible && (!img.complete || img.naturalWidth === 0 || img.naturalHeight === 0));
  const spinners = [...document.querySelectorAll('[class*="spinner" i], [class*="skeleton" i], [aria-busy="true"], progress')].map((el) => {
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return {
      selector: el.tagName.toLowerCase(),
      text: (el.textContent || "").trim().slice(0, 80),
      visible: rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none",
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
    };
  }).filter((item) => item.visible);
  return { images, visibleBrokenImages, visibleLoadingIndicators: spinners };
});

if (report.media.visibleBrokenImages.length > 0) report.blockers.push("Visible broken/unresolved images remain");
if (report.media.visibleLoadingIndicators.length > 0) report.blockers.push("Visible loading indicators remain");

report.network.activeRelevantRequests = [...active.values()].map((item) => ({ url: item.url, type: item.type, ageMs: Date.now() - item.startedAt }));
report.network.recentRelevantRequests = requestLog.slice(-30).map((item) => ({
  url: item.url,
  type: item.type,
  durationMs: item.finishedAt ? item.finishedAt - item.startedAt : null,
  event: item.event
}));
report.network.finalQuietReached = active.size === 0 && Date.now() - lastRelevantNetworkAt >= quietMs;
if (!report.network.finalQuietReached) report.blockers.push("Network quiet window not reached");

report.finishedAt = new Date().toISOString();
report.passed = (
  report.navigation.domcontentloaded === true &&
  report.criticalSelectorResults.some((item) => item.visible) &&
  report.network.finalQuietReached &&
  domStable &&
  report.media.visibleBrokenImages.length === 0 &&
  report.media.visibleLoadingIndicators.length === 0
);

if (!report.passed && report.blockers.length === 0) report.blockers.push("Readiness signals did not pass");

fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
fs.writeFileSync(out, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({
  passed: report.passed,
  out,
  blockers: report.blockers,
  criticalSelectorResults: report.criticalSelectorResults
}, null, 2));

await browser.close();
process.exit(report.passed ? 0 : 1);

#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..");
const assets = path.join(root, "assets");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function loadCourse() {
  const sandbox = { window: {} };
  vm.runInNewContext(read("assets/course-data.js"), sandbox);
  return sandbox.window.COURSE_DATA;
}

function localReferenceExists(page, reference) {
  if (/^(?:#|mailto:|tel:)/.test(reference)) return true;
  assert(!/^https?:\/\//.test(reference), `${page}: runtime network reference ${reference}`);
  const clean = reference.split("#")[0].split("?")[0];
  return fs.existsSync(path.resolve(root, clean));
}

function pngDimensions(filePath) {
  const buffer = fs.readFileSync(filePath);
  const pngSignature = "89504e470d0a1a0a";
  assert(buffer.subarray(0, 8).toString("hex") === pngSignature, `${filePath}: invalid PNG signature`);
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20)
  };
}

function loadAtlasRatios(relativePath) {
  const source = read(relativePath);
  const match = source.match(/const ATLAS_RATIOS\s*=\s*(\{[\s\S]*?\});/);
  assert(match, `${relativePath}: missing ATLAS_RATIOS`);
  return vm.runInNewContext(`(${match[1]})`);
}

const course = loadCourse();
const template = JSON.parse(read("template.json"));
const style = JSON.parse(read("ui-style.json"));
const words = course.flatMap(day => day.words);
const dayPages = fs.readdirSync(root).filter(file => /^day\d\d\.html$/.test(file)).sort();
const appRatios = loadAtlasRatios("assets/app.js");
const homeRatios = loadAtlasRatios("assets/home.js");

assert(course.length === 15, `expected 15 course days, found ${course.length}`);
assert(dayPages.length === 15, `expected 15 daily HTML pages, found ${dayPages.length}`);
assert(words.length === 100, `expected 100 learning items, found ${words.length}`);
assert(new Set(words.map(item => item.w.toLowerCase())).size === 100, "learning words must be unique");
assert(template.styleManifest === "ui-style.json", "template.json must route agents to ui-style.json");
assert(style.name === "Unified Paradigm UI", "style manifest has the wrong design-system name");
assert(
  /Visual appeal is the first learner-facing design principle/.test(style.primaryPrinciple),
  "style manifest must make visual appeal the primary learner-facing principle"
);
assert(style.canonicalFiles.stylesheet === "assets/styles.css", "style manifest must identify the canonical stylesheet");

const pageFiles = ["index.html", ...dayPages];
for (const page of pageFiles) {
  const html = read(page);
  for (const match of html.matchAll(/\b(?:src|href)="([^"]+)"/g)) {
    assert(localReferenceExists(page, match[1]), `${page}: missing local reference ${match[1]}`);
  }
  assert(
    /assets\/styles\.css\?v=[^"]+/.test(html),
    `${page}: stylesheet must use a versioned local URL to prevent stale UI fixes`
  );
}

const css = read("assets/styles.css");
for (const [token, value] of Object.entries(style.tokens.color)) {
  const cssName = token.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`);
  assert(
    new RegExp(`--${cssName}:\\s*${value.replace("#", "\\#")}\\s*;`, "i").test(css),
    `style token ${token} (${value}) is not synchronized with assets/styles.css`
  );
}
const atlasRule = css.match(/^\.atlas-art\s*\{([\s\S]*?)\}/m);
assert(atlasRule, "missing .atlas-art rule");
assert(/\bdisplay\s*:\s*block\s*;/.test(atlasRule[1]), ".atlas-art must be a measurable block box");
assert(/\bbackground-size\s*:\s*400%\s+200%\s*;/.test(atlasRule[1]), ".atlas-art crop geometry is missing");

for (const selector of [".choice .atlas-art", ".flip-card .atlas-art"]) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const rule = css.match(new RegExp(`^${escaped}\\s*\\{([\\s\\S]*?)\\}`, "m"));
  assert(rule, `missing ${selector} rule`);
  assert(/\bheight\s*:\s*auto\s*;/.test(rule[1]), `${selector}: do not force atlas art to a fixed height`);
  assert(
    /\baspect-ratio\s*:\s*var\(--art-ratio,\s*1\)\s*;/.test(rule[1]),
    `${selector}: preserve each atlas cell's source ratio`
  );
  assert(!/\bheight\s*:\s*100%\s*;/.test(rule[1]), `${selector}: height:100% squashes mixed-ratio art`);
}

for (const renderer of ["assets/app.js", "assets/home.js"]) {
  const source = read(renderer);
  assert(
    /background-image:url\('\$\{item\.atlas\}'\)/.test(source),
    `${renderer}: render each atlas with a direct local background-image URL`
  );
}
assert(
  (read("assets/app.js").match(/image-choice-grid/g) || []).length >= 3,
  "image-answer rounds must use the responsive image-choice grid"
);

const imageFiles = [];
for (const day of course) {
  const relativePath = `assets/images/day${String(day.day).padStart(2, "0")}-atlas.png`;
  const absolutePath = path.join(root, relativePath);
  assert(fs.existsSync(absolutePath), `missing ${relativePath}`);
  const dimensions = pngDimensions(absolutePath);
  assert(dimensions.width > 0 && dimensions.height > 0, `${relativePath}: collapsed image dimensions`);
  const nativeCellRatio = dimensions.width / (dimensions.height * 2);
  assert(
    Math.abs(appRatios[day.day] - nativeCellRatio) < .01,
    `${relativePath}: app ratio ${appRatios[day.day]} does not match native cell ratio ${nativeCellRatio.toFixed(3)}`
  );
  assert(
    Math.abs(homeRatios[day.day] - nativeCellRatio) < .01,
    `${relativePath}: home ratio ${homeRatios[day.day]} does not match native cell ratio ${nativeCellRatio.toFixed(3)}`
  );
  imageFiles.push(relativePath);
}

const audioFiles = [];
for (const item of words) {
  const key = item.w.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  for (const suffix of ["word", "phrase"]) {
    const relativePath = `assets/audio/${key}-${suffix}.mp3`;
    const absolutePath = path.join(root, relativePath);
    assert(fs.existsSync(absolutePath), `missing ${relativePath}`);
    assert(fs.statSync(absolutePath).size > 0, `${relativePath}: empty MP3`);
    audioFiles.push(relativePath);
  }
}
const completionAudio = path.join(assets, "audio", "course-complete.mp3");
assert(fs.existsSync(completionAudio) && fs.statSync(completionAudio).size > 0, "missing course-complete.mp3");
audioFiles.push("assets/audio/course-complete.mp3");

const result = {
  template: "Unified Paradigm UI",
  pages: pageFiles.length,
  dailyPages: dayPages.length,
  learningItems: words.length,
  imageAtlases: imageFiles.length,
  audioFiles: audioFiles.length,
  imageSurface: "block + direct URL",
  aspectRatioContract: "native atlas cell ratio",
  styleManifest: "pass",
  offlineReferences: "pass"
};

console.log(JSON.stringify(result, null, 2));

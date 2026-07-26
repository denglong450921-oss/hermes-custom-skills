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

const course = loadCourse();
const words = course.flatMap(day => day.words);
const dayPages = fs.readdirSync(root).filter(file => /^day\d\d\.html$/.test(file)).sort();

assert(course.length === 15, `expected 15 course days, found ${course.length}`);
assert(dayPages.length === 15, `expected 15 daily HTML pages, found ${dayPages.length}`);
assert(words.length === 100, `expected 100 learning items, found ${words.length}`);
assert(new Set(words.map(item => item.w.toLowerCase())).size === 100, "learning words must be unique");

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
const atlasRule = css.match(/^\.atlas-art\s*\{([\s\S]*?)\}/m);
assert(atlasRule, "missing .atlas-art rule");
assert(/\bdisplay\s*:\s*block\s*;/.test(atlasRule[1]), ".atlas-art must be a measurable block box");
assert(/\bbackground-size\s*:\s*400%\s+200%\s*;/.test(atlasRule[1]), ".atlas-art crop geometry is missing");

for (const renderer of ["assets/app.js", "assets/home.js"]) {
  const source = read(renderer);
  assert(
    /background-image:url\('\$\{item\.atlas\}'\)/.test(source),
    `${renderer}: render each atlas with a direct local background-image URL`
  );
}

const imageFiles = [];
for (const day of course) {
  const relativePath = `assets/images/day${String(day.day).padStart(2, "0")}-atlas.png`;
  const absolutePath = path.join(root, relativePath);
  assert(fs.existsSync(absolutePath), `missing ${relativePath}`);
  const dimensions = pngDimensions(absolutePath);
  assert(dimensions.width > 0 && dimensions.height > 0, `${relativePath}: collapsed image dimensions`);
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
  offlineReferences: "pass"
};

console.log(JSON.stringify(result, null, 2));

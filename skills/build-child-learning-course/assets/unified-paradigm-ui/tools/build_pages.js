#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const assets = path.join(root, "assets");
const sourcePath = path.join(root, "index.html");
const dataPath = path.join(assets, "course-data.js");

function loadCourse() {
  if (fs.existsSync(dataPath)) {
    const source = fs.readFileSync(dataPath, "utf8");
    const match = source.match(/window\.COURSE_DATA\s*=\s*(\[[\s\S]*\]);?\s*$/);
    if (!match) throw new Error("Cannot parse assets/course-data.js");
    return JSON.parse(match[1]);
  }
  const source = fs.readFileSync(sourcePath, "utf8");
  const match = source.match(
    /<script id="course-data" type="application\/json">([\s\S]*?)<\/script>/
  );
  if (!match) throw new Error("Cannot find the embedded course data.");
  return JSON.parse(match[1]);
}

const course = loadCourse();
fs.mkdirSync(assets, { recursive: true });
fs.writeFileSync(
  dataPath,
  `window.COURSE_DATA = ${JSON.stringify(course, null, 2)};\n`,
  "utf8"
);

const pageHead = title => `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#ff7b97">
  <meta name="color-scheme" content="light">
  <title>${title}</title>
  <link rel="stylesheet" href="assets/styles.css?v=20260726-aspect-fix">
</head>`;

const home = `${pageHead("100词声音邮局｜15天可爱英语课")}
<body class="home-page">
  <a class="skip-link" href="#course-map">跳到课程地图</a>
  <header class="home-nav">
    <a class="mini-brand" href="index.html" aria-label="100词声音邮局首页">
      <span class="brand-bird" aria-hidden="true"><i></i></span>
      <span><strong>100词声音邮局</strong><small>一本可以玩的英语绘本</small></span>
    </a>
    <div class="home-nav-actions">
      <span class="offline-pill">本地图片 · Edge MP3 · 离线上课</span>
      <button class="soft-button" id="reset-course" type="button">重置进度</button>
    </div>
  </header>

  <main>
    <section class="home-hero">
      <div class="hero-copy">
        <p class="kicker">15 DAYS · 100 WORDS · AGE 6</p>
        <h1>把每个单词<br>装进<span>会发光的故事</span></h1>
        <p class="hero-lede">每天打开一封声音来信：看绘本、听发音、翻卡片、说短句。15 天后，孩子能听、能认、能说，也会把词放进生活。</p>
        <div class="hero-buttons">
          <a class="candy-button primary" id="continue-link" href="day01.html">打开今天的来信</a>
          <button class="candy-button secondary" id="sample-audio" type="button">听一听声音</button>
        </div>
        <div class="trust-row" aria-label="课程特点">
          <span>100 个真实词图</span><span>201 个本地 MP3</span><span>15 个独立日课</span>
        </div>
      </div>
      <div class="hero-book" aria-label="软陶绘本词汇示例">
        <div class="book-ring ring-one"></div>
        <div class="book-ring ring-two"></div>
        <div class="book-page">
          <div class="atlas-art hero-art" data-home-art="6:0" role="img" aria-label="软陶绘本小猫"></div>
          <div class="book-caption"><small>今天的声音</small><strong>cat</strong><span>/kæt/</span></div>
        </div>
        <div class="floating-note note-one">听</div>
        <div class="floating-note note-two">说</div>
        <div class="floating-star">★</div>
      </div>
    </section>

    <section class="map-section" id="course-map" aria-labelledby="map-title">
      <header class="section-heading">
        <div><p class="kicker">STORY ROUTE</p><h2 id="map-title">15 封声音来信</h2></div>
        <p>每一天都是独立 HTML，点开就能上课。完成出口挑战，信封会盖上闪亮邮戳。</p>
      </header>
      <div class="day-card-grid" id="home-day-grid"></div>
    </section>

    <section class="parent-note">
      <div class="note-sticker">给大人</div>
      <div><h2>每天约 30 分钟，先让孩子自己想</h2><p>课程按照 30% 学习、70% 提取练习设计。答错不扣星，先重听、再尝试；出口挑战达到 80 分即可点亮当天。</p></div>
      <a class="text-link" href="使用说明.txt">查看使用说明 →</a>
    </section>
  </main>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script src="assets/course-data.js?v=20260726-aspect-fix"></script>
  <script src="assets/home.js?v=20260726-aspect-fix"></script>
</body>
</html>`;

fs.writeFileSync(path.join(root, "index.html"), home, "utf8");

for (const day of course) {
  const n = String(day.day).padStart(2, "0");
  const prev = day.day > 1 ? `day${String(day.day - 1).padStart(2, "0")}.html` : "index.html";
  const next = day.day < 15 ? `day${String(day.day + 1).padStart(2, "0")}.html` : "index.html";
  const html = `${pageHead(`第${day.day}天｜${day.theme}｜100词声音邮局`)}
<body class="lesson-page" data-day="${day.day}">
  <a class="skip-link" href="#lesson-panel">跳到今日任务</a>
  <header class="lesson-topbar">
    <a class="mini-brand" href="index.html" aria-label="返回课程首页">
      <span class="brand-bird" aria-hidden="true"><i></i></span>
      <span><strong>声音邮局</strong><small>第 ${day.day} 封来信</small></span>
    </a>
    <div class="audio-controls" aria-label="发音设置">
      <span class="edge-label">Edge MP3</span>
      <label>语速
        <select id="speech-rate">
          <option value="0.7">慢速</option>
          <option value="0.85" selected>标准</option>
          <option value="1">稍快</option>
        </select>
      </label>
      <label>重复
        <select id="speech-repeat">
          <option value="1">1遍</option>
          <option value="2">2遍</option>
          <option value="3">3遍</option>
        </select>
      </label>
      <button class="soft-button" id="motion-toggle" type="button" aria-pressed="false">动效开</button>
    </div>
  </header>

  <div class="lesson-layout">
    <aside class="day-drawer" aria-label="15天课程目录">
      <div class="drawer-top"><a href="index.html">← 全部来信</a><strong>课程路线</strong></div>
      <nav class="day-links" id="day-list"></nav>
      <button class="soft-button reset-day" id="reset-day" type="button">重玩今天</button>
    </aside>

    <main class="lesson-main">
      <section class="daily-cover" id="day-hero"></section>
      <div class="learning-balance" aria-label="学习与提取练习比例">
        <span class="balance-learn"><b>30%</b> 学一学</span>
        <span class="balance-test"><b>70%</b> 想一想、玩一玩</span>
      </div>
      <nav class="mission-tabs" id="stage-tabs" aria-label="今日六段任务"></nav>
      <section class="mission-panel" id="lesson-panel" tabindex="-1"></section>
      <nav class="page-turner" aria-label="前后日课">
        <a href="${prev}">← ${day.day > 1 ? `第 ${day.day - 1} 天` : "课程首页"}</a>
        <a href="${next}">${day.day < 15 ? `第 ${day.day + 1} 天` : "回到首页"} →</a>
      </nav>
    </main>
  </div>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script src="assets/course-data.js?v=20260726-aspect-fix"></script>
  <script src="assets/app.js?v=20260726-aspect-fix"></script>
</body>
</html>`;
  fs.writeFileSync(path.join(root, `day${n}.html`), html, "utf8");
}

console.log(`Built index.html and ${course.length} daily HTML pages.`);

"use strict";

(() => {
  const COURSE = window.COURSE_DATA || [];
  const dayNumber = Number(document.body.dataset.day);
  const dayIndex = Math.max(0, Math.min(COURSE.length - 1, dayNumber - 1));
  const day = COURSE[dayIndex];
  const STORE_KEY = "sound-post-office-v3";
  const LEGACY_KEY = "sound-post-office-v1";
  const STAGES = [
    { short: "热身", name: "旧词热身", mode: "提取" },
    { short: "新词", name: "新词投递", mode: "学习" },
    { short: "渐隐", name: "渐隐练习", mode: "学习" },
    { short: "翻卡", name: "翻卡配对", mode: "提取" },
    { short: "游戏", name: "变化游戏", mode: "提取" },
    { short: "出口", name: "出口挑战", mode: "提取" }
  ];
  const GAME_NAMES = {
    sound: "声音侦探",
    recall: "看图说词",
    sort: "分类邮筒",
    phrase: "短句拼装",
    clue: "线索寻词"
  };
  const DAY_COLORS = [
    "#83d8ff", "#ffb8c9", "#9ee1cb", "#ffd65c", "#b8a9ef",
    "#8edbd1", "#ffbd8e", "#a9d9ff", "#ffd079", "#a8e49c",
    "#99d8f3", "#d3bdff", "#ffabc0", "#a8ddef", "#ffd774"
  ];
  const ATLAS_RATIOS = {
    1: 1, 2: 1, 3: 1, 4: .888, 5: .75,
    6: 1, 7: .75, 8: .75, 9: .75, 10: .75,
    11: .75, 12: .75, 13: .75, 14: .75, 15: .75
  };
  const POSITIONS = [
    ["0%", "0%"], ["33.333%", "0%"], ["66.667%", "0%"], ["100%", "0%"],
    ["0%", "100%"], ["33.333%", "100%"], ["66.667%", "100%"], ["100%", "100%"]
  ];
  const CATEGORY = {
    hello: "交流", hi: "交流", name: "人物", I: "人物", you: "人物", yes: "交流", no: "交流",
    mom: "人物", dad: "人物", baby: "人物", brother: "人物", sister: "人物", family: "人物", love: "感受",
    head: "身体", eye: "身体", ear: "身体", nose: "身体", mouth: "身体", hand: "身体", foot: "身体",
    red: "颜色", blue: "颜色", yellow: "颜色", green: "颜色", black: "颜色", white: "颜色", pink: "颜色",
    one: "数字", two: "数字", three: "数字", four: "数字", five: "数字", six: "数字", seven: "数字",
    cat: "动物", dog: "动物", bird: "动物", fish: "动物", rabbit: "动物", bear: "动物", duck: "动物",
    apple: "食物", banana: "食物", milk: "食物", bread: "食物", egg: "食物", rice: "食物", cake: "食物",
    home: "家", door: "家", window: "家", bed: "家", chair: "家", table: "家", room: "家",
    book: "学校", pen: "学校", bag: "学校", desk: "学校", teacher: "人物", school: "学校", read: "动作",
    run: "动作", jump: "动作", sit: "动作", stand: "动作", look: "动作", listen: "动作", clap: "动作",
    sun: "自然", moon: "自然", star: "自然", tree: "自然", flower: "自然", rain: "自然",
    ball: "玩具", doll: "玩具", car: "玩具", kite: "玩具", box: "物品", round: "形状",
    happy: "感受", sad: "感受", tired: "感受", hungry: "感受", good: "感受", okay: "感受",
    shirt: "衣服", shoes: "衣服", hat: "衣服", coat: "衣服", hot: "天气", cold: "天气",
    go: "动作", come: "动作", help: "动作", please: "交流", thank: "交流", bye: "交流"
  };

  let stageIndex = 0;
  let wordIndex = 0;
  let quizState = null;
  let fadeReveals = new Set();
  let flipState = null;
  let gameState = null;
  let exitState = null;
  let toastTimer = null;
  let currentAudio = null;
  let audioRun = 0;
  const state = readState();
  const $ = (selector, root = document) => root.querySelector(selector);

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    })[character]);
  }

  function shuffle(items) {
    const copy = [...items];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const swap = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[swap]] = [copy[swap], copy[index]];
    }
    return copy;
  }

  function unique(items) {
    const seen = new Set();
    return items.filter(item => {
      const key = item.w.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function sample(items, count, excluded = "") {
    return shuffle(items.filter(item => item.w !== excluded)).slice(0, count);
  }

  function readState() {
    const defaults = {
      currentDay: 0,
      completedDays: [],
      stages: {},
      scores: {},
      rate: .85,
      repeat: 1,
      reducedMotion: false
    };
    try {
      const current = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
      if (current) return Object.assign(defaults, current);
      const legacy = JSON.parse(localStorage.getItem(LEGACY_KEY) || "null");
      if (legacy) {
        const migrated = Object.assign(defaults, legacy);
        localStorage.setItem(STORE_KEY, JSON.stringify(migrated));
        return migrated;
      }
    } catch {
      // Keep teaching even if a private browser blocks localStorage.
    }
    return defaults;
  }

  function saveState() {
    state.currentDay = dayIndex;
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(state));
    } catch {
      // Progress saving is helpful, but never required to use the course.
    }
    renderDayList();
    renderStageTabs();
  }

  function prepareCourse() {
    COURSE.forEach(courseDay => courseDay.words.forEach((item, slot) => {
      const key = item.w.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      item.day = courseDay.day;
      item.slot = slot;
      item.audioWord = `assets/audio/${key}-word.mp3`;
      item.audioPhrase = `assets/audio/${key}-phrase.mp3`;
      item.atlas = `assets/images/day${String(courseDay.day).padStart(2, "0")}-atlas.png`;
      item.artRatio = ATLAS_RATIOS[courseDay.day] || .75;
    }));
  }

  function art(item, extraClass = "") {
    const [x, y] = POSITIONS[item.slot] || POSITIONS[0];
    return `<span class="atlas-art ${extraClass}" role="img" aria-label="${escapeHTML(item.zh)}的软陶绘本插画" style="background-image:url('${item.atlas}');--x:${x};--y:${y};--art-ratio:${item.artRatio}"></span>`;
  }

  function phraseWords(phrase) {
    return phrase.replace(/[.,!?']/g, "").trim().split(/\s+/).filter(Boolean);
  }

  function cumulativePool(index = dayIndex) {
    return unique(COURSE.slice(0, index + 1).flatMap(courseDay => courseDay.words));
  }

  function reviewPool() {
    if (dayIndex === 0) return day.words;
    const previous = COURSE[dayIndex - 1].words;
    const older = dayIndex > 1 ? COURSE[dayIndex - 2].words.slice(0, 3) : [];
    return unique([...previous, ...older, ...day.words.slice(0, 2)]);
  }

  function showToast(message) {
    const toast = $("#toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2400);
  }

  function stopAudio() {
    audioRun += 1;
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      currentAudio = null;
    }
    if ("speechSynthesis" in window) speechSynthesis.cancel();
    document.querySelectorAll("[data-speak][aria-pressed='true']").forEach(button => {
      button.setAttribute("aria-pressed", "false");
    });
  }

  function speechFallback(text, button) {
    if (!("speechSynthesis" in window)) {
      showToast("本地 MP3 无法播放，请检查 assets/audio 文件夹。");
      return;
    }
    showToast("本地 MP3 暂时无法播放，已启用系统备用朗读。");
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = Number($("#speech-rate").value);
    utterance.pitch = 1.05;
    if (button) button.setAttribute("aria-pressed", "true");
    utterance.onend = utterance.onerror = () => {
      if (button) button.setAttribute("aria-pressed", "false");
    };
    speechSynthesis.speak(utterance);
  }

  function speak(text, button) {
    stopAudio();
    const match = COURSE.flatMap(courseDay => courseDay.words).find(item => item.w === text || item.p === text);
    const src = match ? (match.w === text ? match.audioWord : match.audioPhrase)
      : text === "You did it! One hundred words!" ? "assets/audio/course-complete.mp3"
        : "";
    if (!src) {
      speechFallback(text, button);
      return;
    }
    const repeats = Number($("#speech-repeat").value);
    const rate = Number($("#speech-rate").value);
    const runId = audioRun;
    let played = 0;
    let fallbackUsed = false;
    const fallback = () => {
      if (fallbackUsed || runId !== audioRun) return;
      fallbackUsed = true;
      speechFallback(text, button);
    };
    const play = () => {
      if (runId !== audioRun) return;
      currentAudio = new Audio(src);
      currentAudio.preload = "auto";
      currentAudio.playbackRate = rate;
      if (button) button.setAttribute("aria-pressed", "true");
      currentAudio.onended = () => {
        played += 1;
        if (played < repeats && runId === audioRun) {
          setTimeout(play, 360);
        } else if (button) {
          button.setAttribute("aria-pressed", "false");
        }
      };
      currentAudio.onerror = fallback;
      const request = currentAudio.play();
      if (request && request.catch) request.catch(fallback);
    };
    play();
  }

  function celebrate() {
    if (state.reducedMotion || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const colors = ["#ff7895", "#83d8ff", "#ffd65c", "#8de2bf", "#9480df"];
    for (let index = 0; index < 28; index += 1) {
      const piece = document.createElement("i");
      piece.className = "confetti";
      piece.style.left = `${Math.random() * 100}vw`;
      piece.style.background = colors[index % colors.length];
      piece.style.setProperty("--drift", `${(Math.random() - .5) * 220}px`);
      piece.style.animationDelay = `${Math.random() * .35}s`;
      document.body.appendChild(piece);
      setTimeout(() => piece.remove(), 1900);
    }
  }

  function completeStage(index = stageIndex) {
    const key = `d${dayNumber}`;
    state.stages[key] = [...new Set([...(state.stages[key] || []), index])];
    saveState();
  }

  function renderHero() {
    const item = day.words[0];
    $("#day-hero").style.setProperty("--day-color", DAY_COLORS[dayIndex]);
    $("#day-hero").innerHTML = `
      <div class="daily-copy">
        <p class="kicker">DAY ${String(dayNumber).padStart(2, "0")} · ${escapeHTML(day.district)}</p>
        <h1>${escapeHTML(day.theme)}</h1>
        <p><strong>今日任务：</strong>${escapeHTML(day.mission)}。先看绘本猜意思，再用声音和游戏把词找回来。</p>
        <div class="daily-meta">
          <span>${day.words.length} 个新词</span>
          <span>${escapeHTML(GAME_NAMES[day.game])}</span>
          <span>出口挑战 80 分过关</span>
        </div>
      </div>
      <div class="daily-art-wrap">${art(item, "daily-art")}</div>`;
  }

  function renderDayList() {
    $("#day-list").innerHTML = COURSE.map(courseDay => {
      const current = courseDay.day === dayNumber;
      const done = state.completedDays.includes(courseDay.day);
      const n = String(courseDay.day).padStart(2, "0");
      return `<a class="day-link${current ? " current" : ""}" href="day${n}.html"${current ? ' aria-current="page"' : ""}>
        <span class="day-number">${n}</span>
        <span><strong>${escapeHTML(courseDay.theme)}</strong><small>${courseDay.words.length}词 · ${escapeHTML(GAME_NAMES[courseDay.game])}</small></span>
        <span class="day-status" aria-label="${done ? "已完成" : "未完成"}">${done ? "✓" : "·"}</span>
      </a>`;
    }).join("");
  }

  function renderStageTabs() {
    const completed = state.stages[`d${dayNumber}`] || [];
    $("#stage-tabs").innerHTML = STAGES.map((stage, index) => `
      <button type="button" role="tab" class="mission-tab${completed.includes(index) ? " done" : ""}"
        data-stage="${index}" aria-selected="${index === stageIndex}" aria-controls="lesson-panel">
        <span class="tab-dot">${completed.includes(index) ? "✓" : index + 1}</span>${stage.short}
      </button>`).join("");
  }

  function panelHeading(title, description, mode = STAGES[stageIndex].mode) {
    return `<header class="panel-heading">
      <div><h2>${title}</h2><p>${description}</p></div>
      <span class="mode-chip">${mode}</span>
    </header>`;
  }

  function instruction(text) {
    return `<div class="instruction"><strong>孩子怎么做</strong><span>${text}</span></div>`;
  }

  function stageFooter(nextLabel = "进入下一段") {
    return `<footer class="stage-footer">
      <button type="button" class="action-button ghost" data-prev-stage ${stageIndex === 0 ? "disabled" : ""}>← 上一步</button>
      <button type="button" class="action-button primary" data-next-stage>${nextLabel} →</button>
    </footer>`;
  }

  function makeQuestion(item, type, pool) {
    return {
      item,
      type,
      choices: shuffle([item, ...sample(pool, 3, item.w)])
    };
  }

  function createQuiz(mode = "review") {
    const source = mode === "review" ? reviewPool() : unique([...day.words, ...reviewPool()]);
    const questions = sample(source, Math.min(5, source.length)).map((item, index) => {
      return makeQuestion(item, ["listen", "picture", "meaning"][index % 3], cumulativePool());
    });
    return { mode, questions, index: 0, score: 0, answered: false, selected: "" };
  }

  function quizChoice(choice, question, model, attribute) {
    const correct = model.answered && choice.w === question.item.w;
    const wrong = model.answered && choice.w === model.selected && choice.w !== question.item.w;
    const imageChoice = question.type === "listen";
    const content = imageChoice ? art(choice) : question.type === "picture"
      ? `<span class="word-face">${escapeHTML(choice.w)}</span>`
      : `<span class="word-face">${escapeHTML(choice.zh)}</span>`;
    return `<button type="button" class="choice${imageChoice ? " image-choice" : ""}${correct ? " correct" : ""}${wrong ? " wrong" : ""}"
      ${attribute}="${escapeHTML(choice.w)}" ${model.answered ? "disabled" : ""}>${content}</button>`;
  }

  function renderQuiz() {
    if (!quizState) quizState = createQuiz();
    if (quizState.index >= quizState.questions.length) {
      completeStage(0);
      const percent = Math.round(quizState.score / quizState.questions.length * 100);
      $("#lesson-panel").innerHTML = panelHeading("热身完成", "记忆已经醒来，答错的词会在后面重新出现。") + `
        <div class="activity-card result-copy">
          <div class="score-badge" style="--score:${percent}%"><strong>${percent}分</strong></div>
          <h3>${percent >= 80 ? "声音信号很亮！" : "旧词正在醒来！"}</h3>
          <p>答对 ${quizState.score} / ${quizState.questions.length}。第一天只是轻松摸底，不知道也没关系。</p>
        </div>${stageFooter("去认识新词")}`;
      return;
    }
    const question = quizState.questions[quizState.index];
    const prompt = question.type === "listen" ? "听一听，哪一张图是这个词？"
      : question.type === "picture" ? `看图说词：${question.item.zh}`
        : `“${question.item.w}” 是什么意思？`;
    $("#lesson-panel").innerHTML = panelHeading(dayIndex === 0 ? "声音热身" : "旧词热身", "先自己想 5 秒，再点答案。") +
      instruction(question.type === "listen" ? "先按播放，再从四张无文字图片里选答案。" : "先说出答案，再点击验证；大人暂时不提示。") + `
      <div class="activity-card">
        <p class="question-count">QUESTION ${quizState.index + 1} / ${quizState.questions.length}</p>
        <h3 class="question-title">${escapeHTML(prompt)}</h3>
        ${question.type === "listen" ? `<button class="action-button audio" type="button" data-speak="${escapeHTML(question.item.w)}">♪ 播放单词</button>` : ""}
        ${question.type === "picture" ? `<div class="recall-picture">${art(question.item)}</div>` : ""}
        <div class="choice-grid${question.type === "listen" ? " image-choice-grid" : ""}">${question.choices.map(choice => quizChoice(choice, question, quizState, "data-quiz-answer")).join("")}</div>
        <div class="feedback${quizState.answered ? (quizState.selected === question.item.w ? " good" : " retry") : ""}">
          ${quizState.answered ? (quizState.selected === question.item.w
            ? `答对啦！${question.item.w} ${question.item.ipa}，${question.item.zh}。`
            : `再听一次：${question.item.w} ${question.item.ipa}，意思是“${question.item.zh}”。`) : "点选后，这里会给你即时反馈。"}
        </div>
        ${quizState.answered ? `<div class="button-row">
          <button type="button" class="action-button primary" data-quiz-next>${quizState.index === quizState.questions.length - 1 ? "查看结果" : "下一题"} →</button>
          <button type="button" class="action-button audio" data-speak="${escapeHTML(question.item.p)}">♪ 听短句</button>
        </div>` : ""}
      </div>
      <details class="teacher-note"><summary>给带课大人的提示</summary><p>每题最多等待 5 秒。答错时只说“我们再听一次”，不要直接报答案。</p></details>
      ${stageFooter("去认识新词")}`;
  }

  function renderWords() {
    const item = day.words[wordIndex];
    $("#lesson-panel").innerHTML = panelHeading("新词投递", "声音、图像、意思和短句一起进入记忆。") +
      instruction("先看高清绘本图猜意思；听单词两遍，再跟读单词和短句各一次。") + `
      <div class="word-spread">
        <div class="word-picture">${art(item)}</div>
        <article class="word-copy">
          <small>今日第 ${wordIndex + 1} / ${day.words.length} 词</small>
          <h3>${escapeHTML(item.w)}</h3>
          <span class="ipa">${escapeHTML(item.ipa)}</span>
          <p class="meaning">${escapeHTML(item.zh)}</p>
          <div class="phrase-paper"><small>记忆短句 · ${phraseWords(item.p).length} 个词</small><strong>${escapeHTML(item.p)}</strong></div>
          <div class="word-controls">
            <button class="action-button audio" type="button" data-speak="${escapeHTML(item.w)}">♪ 听单词</button>
            <button class="action-button audio" type="button" data-speak="${escapeHTML(item.p)}">♪ 听短句</button>
          </div>
        </article>
      </div>
      <div class="word-dots">${day.words.map((word, index) => `
        <button type="button" class="word-dot${index === wordIndex ? " current" : ""}" data-word-index="${index}">${escapeHTML(word.w)}</button>`).join("")}
      </div>
      <footer class="stage-footer">
        <button class="action-button ghost" type="button" data-word-prev ${wordIndex === 0 ? "disabled" : ""}>← 上一个词</button>
        <button class="action-button primary" type="button" data-word-next>${wordIndex === day.words.length - 1 ? "完成新词投递" : "下一个词"} →</button>
      </footer>`;
  }

  function fadeItems() {
    return [day.words[0], day.words[Math.floor(day.words.length / 2)], day.words.at(-1)];
  }

  function renderFade() {
    const items = fadeItems();
    $("#lesson-panel").innerHTML = panelHeading("渐隐练习", "提示一层层变少，让孩子主动把词说出来。") +
      instruction("从上到下完成三张卡：第一张读，第二张补词，第三张只看图回忆。说完再揭晓。") + `
      <div class="fade-list">${items.map((item, index) => {
        const revealed = fadeReveals.has(index);
        const prompt = index === 0 ? `<h3>${escapeHTML(item.w)}</h3><p>${escapeHTML(item.p)}</p>`
          : index === 1 ? `<h3>${revealed ? escapeHTML(item.w) : "____"}</h3><p>${escapeHTML(item.p.replace(new RegExp(item.w, "i"), "____"))}</p>`
            : `<h3>${revealed ? escapeHTML(item.w) : "只看图，说英文"}</h3><p>${revealed ? escapeHTML(item.p) : "说完以后再揭晓"}</p>`;
        return `<article class="fade-step">
          ${art(item)}
          <div><small>提示等级 ${index + 1}</small>${prompt}</div>
          <button class="action-button ${revealed ? "audio" : "ghost"}" type="button" data-fade="${index}">
            ${revealed ? "♪ 再听一次" : "揭晓答案"}
          </button>
        </article>`;
      }).join("")}</div>
      <details class="teacher-note"><summary>难度为什么会增加？</summary><p>第一张保留完整文字，第二张挖空目标词，第三张只留图片。提示减少，就是一次温和的提取练习。</p></details>
      ${stageFooter("去玩翻卡配对")}`;
  }

  function flipLevel() {
    if (dayNumber <= 3) return { pairs: 3, sides: ["visual", "word"], label: "3 对 · 看图找词" };
    if (dayNumber <= 6) return { pairs: 4, sides: ["visual", "word"], label: "4 对 · 扩大图词配对" };
    if (dayNumber <= 9) return { pairs: 5, sides: ["sound", "visual"], label: "5 对 · 听音找图" };
    if (dayNumber <= 12) return { pairs: 6, sides: ["word", "phrase"], label: "6 对 · 词语找短句" };
    if (dayNumber <= 14) return { pairs: 7, sides: ["phrase", "visual"], label: "7 对 · 短句找场景" };
    return { pairs: 8, sides: ["mixed", "mixed"], label: "8 对 · 图、音、词、句混合" };
  }

  function createFlip() {
    const level = flipLevel();
    const pool = unique([...day.words, ...shuffle(cumulativePool()).slice(0, level.pairs)]);
    const items = sample(pool, level.pairs);
    const combinations = [["sound", "visual"], ["word", "phrase"], ["phrase", "visual"], ["visual", "word"]];
    const cards = items.flatMap((item, index) => {
      const sides = level.sides[0] === "mixed" ? combinations[index % combinations.length] : level.sides;
      return sides.map((side, sideIndex) => ({
        key: `${index}-${sideIndex}`,
        pairId: `pair-${index}`,
        item,
        side
      }));
    });
    return {
      level,
      cards: shuffle(cards),
      open: [],
      matched: new Set(),
      attempts: 0,
      wrong: 0,
      locked: false,
      complete: false
    };
  }

  function flipContent(card) {
    if (card.side === "visual") return art(card.item);
    if (card.side === "sound") return `<span class="sound-face">♪<small style="display:block;font-size:12px">点开听声音</small></span>`;
    if (card.side === "phrase") return `<span class="phrase-face">${escapeHTML(card.item.p)}</span>`;
    return `<span class="word-face">${escapeHTML(card.item.w)}<small style="display:block">${escapeHTML(card.item.ipa)}</small></span>`;
  }

  function renderFlip() {
    if (!flipState) flipState = createFlip();
    const level = flipState.level;
    const accuracy = flipState.attempts ? Math.round(flipState.matched.size / flipState.attempts * 100) : 100;
    $("#lesson-panel").innerHTML = panelHeading("翻卡配对", "每天都增加工作记忆负荷，并逐步撤掉文字提示。", "重点游戏") +
      instruction(`今天是“${level.label}”。一次只翻两张；配错会自动盖回，先记位置，不抢快。`) + `
      <div class="flip-stats">
        <div class="tiny-stat"><strong>${level.pairs}</strong><small>配对数</small></div>
        <div class="tiny-stat"><strong>${flipState.matched.size}</strong><small>已找到</small></div>
        <div class="tiny-stat"><strong>${flipState.attempts}</strong><small>尝试</small></div>
        <div class="tiny-stat"><strong>${accuracy}%</strong><small>当前准确率</small></div>
      </div>
      <div class="flip-grid" role="grid" aria-label="${escapeHTML(level.label)}">
        ${flipState.cards.map((card, index) => {
          const open = flipState.open.includes(card.key);
          const matched = flipState.matched.has(card.pairId);
          return `<button type="button" role="gridcell" class="flip-card${open ? " open" : ""}${matched ? " matched" : ""}"
            data-flip="${index}" aria-pressed="${open || matched}" ${flipState.locked || matched ? "disabled" : ""}>
            <span class="card-front" aria-hidden="true">✦</span>
            <span class="card-back">${flipContent(card)}</span>
          </button>`;
        }).join("")}
      </div>
      <div class="feedback${flipState.complete ? " good" : ""}">
        ${flipState.complete ? `全部找到！今天用 ${flipState.attempts} 次完成 ${level.pairs} 对配对。` : "翻开两张卡，寻找属于同一个词的两种线索。"}
      </div>
      <div class="button-row">
        <button type="button" class="action-button ghost" data-flip-reset>重新洗牌</button>
      </div>
      <details class="teacher-note" open><summary>今天怎样比昨天更难？</summary><p>${escapeHTML(level.label)}。第 1–6 天建立图词连接；第 7 天起加入无文字音频；第 10 天起用短句；第 15 天做 8 对混合迁移。</p></details>
      ${stageFooter("去玩变化游戏")}`;
  }

  function handleFlip(index) {
    if (!flipState || flipState.locked) return;
    const card = flipState.cards[index];
    if (flipState.open.includes(card.key) || flipState.matched.has(card.pairId)) return;
    flipState.open.push(card.key);
    if (card.side === "sound") speak(card.item.w);
    renderFlip();
    if (flipState.open.length < 2) return;
    flipState.locked = true;
    flipState.attempts += 1;
    const [firstKey, secondKey] = flipState.open;
    const first = flipState.cards.find(item => item.key === firstKey);
    const second = flipState.cards.find(item => item.key === secondKey);
    const isMatch = first.pairId === second.pairId;
    setTimeout(() => {
      if (isMatch) {
        flipState.matched.add(first.pairId);
        speak(first.item.p);
      } else {
        flipState.wrong += 1;
      }
      flipState.open = [];
      flipState.locked = false;
      if (flipState.matched.size === flipState.level.pairs) {
        flipState.complete = true;
        completeStage(3);
        celebrate();
      }
      renderFlip();
    }, state.reducedMotion ? 80 : 650);
  }

  function createGame() {
    const currentItems = sample(day.words, 3);
    const currentKeys = new Set(currentItems.map(item => item.w));
    const reviewItems = shuffle(unique([...reviewPool(), ...cumulativePool()]))
      .filter(item => !currentKeys.has(item.w))
      .slice(0, 2);
    const items = [...currentItems, ...reviewItems];
    return {
      type: day.game,
      items,
      index: 0,
      score: 0,
      answered: false,
      selected: "",
      revealed: false,
      choices: null,
      tiles: null,
      built: []
    };
  }

  function gameFeedback(item, expected = item.w) {
    if (!gameState.answered) return `<div class="feedback">完成后这里会给你即时反馈。</div>`;
    const correct = gameState.selected === expected;
    return `<div class="feedback ${correct ? "good" : "retry"}">${correct
      ? `送对啦！${escapeHTML(item.w)} · ${escapeHTML(item.p)}`
      : `这次应该是 ${escapeHTML(item.w)}。听一遍，再大声说一次。`}</div>
      <div class="button-row">
        <button type="button" class="action-button primary" data-game-next>${gameState.index === gameState.items.length - 1 ? "查看成绩" : "下一题"} →</button>
        <button type="button" class="action-button audio" data-speak="${escapeHTML(item.p)}">♪ 听短句</button>
      </div>`;
  }

  function renderSoundGame(item) {
    if (!gameState.choices) gameState.choices = shuffle([item, ...sample(cumulativePool(), 3, item.w)]);
    return instruction("按播放键，只凭声音从四张无文字绘本图中找到答案。") + `
      <div class="activity-card">
        <p class="question-count">声音侦探 ${gameState.index + 1} / ${gameState.items.length}</p>
        <h3 class="question-title">哪个画面属于这个声音？</h3>
        <button type="button" class="action-button audio" data-speak="${escapeHTML(item.w)}">♪ 播放声音</button>
        <div class="choice-grid image-choice-grid">${gameState.choices.map(choice => `
          <button type="button" class="choice image-choice${gameState.answered && choice.w === item.w ? " correct" : ""}${gameState.answered && choice.w === gameState.selected && choice.w !== item.w ? " wrong" : ""}"
            data-game-answer="${escapeHTML(choice.w)}" ${gameState.answered ? "disabled" : ""}>${art(choice)}</button>`).join("")}
        </div>${gameFeedback(item)}
      </div>`;
  }

  function renderRecallGame(item) {
    return instruction("看图后先把英文词和短句说出来；说完才揭晓，自主判断是否说对。") + `
      <div class="activity-card">
        <p class="question-count">看图说词 ${gameState.index + 1} / ${gameState.items.length}</p>
        <div class="recall-picture">${art(item)}</div>
        ${gameState.revealed ? `<div class="result-copy"><h3>${escapeHTML(item.w)} <small>${escapeHTML(item.ipa)}</small></h3><p>${escapeHTML(item.p)}</p></div>
          <div class="button-row" style="justify-content:center">
            <button type="button" class="action-button primary" data-self-score="yes">我说对了</button>
            <button type="button" class="action-button ghost" data-self-score="no">我再练一次</button>
            <button type="button" class="action-button audio" data-speak="${escapeHTML(item.p)}">♪ 听短句</button>
          </div>` : `<div class="button-row" style="justify-content:center"><button type="button" class="action-button primary" data-reveal-recall>说好了，揭晓答案</button></div>`}
      </div>`;
  }

  function sortBuckets(item) {
    const correct = CATEGORY[item.w] || "物品";
    const all = [...new Set(Object.values(CATEGORY))].map(w => ({ w }));
    return shuffle([correct, ...sample(all, 3, correct).map(entry => entry.w)]);
  }

  function renderSortGame(item) {
    if (!gameState.choices) gameState.choices = sortBuckets(item);
    const correct = CATEGORY[item.w] || "物品";
    return instruction("先大声说词，再把它投入最合适的分类邮筒。") + `
      <div class="activity-card">
        <p class="question-count">分类邮筒 ${gameState.index + 1} / ${gameState.items.length}</p>
        <div class="recall-picture">${art(item)}</div>
        <h3 class="question-title" style="text-align:center">${escapeHTML(item.w)}</h3>
        <div class="bucket-grid">${gameState.choices.map(name => `
          <button type="button" class="bucket${gameState.answered && name === correct ? " correct" : ""}${gameState.answered && name === gameState.selected && name !== correct ? " wrong" : ""}"
            data-game-answer="${escapeHTML(name)}" ${gameState.answered ? "disabled" : ""}>${escapeHTML(name)}邮筒</button>`).join("")}
        </div>${gameFeedback(item, correct)}
      </div>`;
  }

  function renderPhraseGame(item) {
    if (!gameState.tiles) gameState.tiles = shuffle(phraseWords(item.p));
    const builtText = gameState.built.map(index => gameState.tiles[index]);
    return instruction("先听短句，再按顺序点击词块；拼好后检查。") + `
      <div class="activity-card">
        <p class="question-count">短句拼装 ${gameState.index + 1} / ${gameState.items.length}</p>
        <div class="recall-picture">${art(item)}</div>
        <button type="button" class="action-button audio" data-speak="${escapeHTML(item.p)}">♪ 先听短句</button>
        <div class="builder-zone">${builtText.length ? builtText.map((word, index) => `
          <button type="button" class="built-tile" data-unbuild="${index}">${escapeHTML(word)}</button>`).join("") : "词块会放在这里……"}</div>
        <div class="tile-row">${gameState.tiles.map((word, index) => `
          <button type="button" class="word-tile${gameState.built.includes(index) ? " used" : ""}" data-build="${index}">${escapeHTML(word)}</button>`).join("")}</div>
        <div class="button-row">
          <button type="button" class="action-button primary" data-check-phrase ${builtText.length !== gameState.tiles.length ? "disabled" : ""}>检查短句</button>
          <button type="button" class="action-button ghost" data-clear-phrase>清空</button>
        </div>
        ${gameState.answered ? gameFeedback(item, phraseWords(item.p).join(" ").toLowerCase()) : `<div class="feedback">每个记忆短句不超过 4 个词，慢慢排，不计时。</div>`}
      </div>`;
  }

  function renderClueGame(item) {
    if (!gameState.choices) gameState.choices = shuffle([item, ...sample(cumulativePool(), 3, item.w)]);
    return instruction("读中文线索和首字母，从四个英文词中找到答案。") + `
      <div class="activity-card">
        <p class="question-count">线索寻词 ${gameState.index + 1} / ${gameState.items.length}</p>
        <h3 class="question-title">线索：${escapeHTML(item.zh)} · 开头是 “${escapeHTML(item.w[0].toUpperCase())}”</h3>
        <div class="choice-grid">${gameState.choices.map(choice => `
          <button type="button" class="choice${gameState.answered && choice.w === item.w ? " correct" : ""}${gameState.answered && choice.w === gameState.selected && choice.w !== item.w ? " wrong" : ""}"
            data-game-answer="${escapeHTML(choice.w)}" ${gameState.answered ? "disabled" : ""}>${escapeHTML(choice.w)}</button>`).join("")}
        </div>${gameFeedback(item)}
      </div>`;
  }

  function renderGame() {
    if (!gameState) gameState = createGame();
    const name = GAME_NAMES[gameState.type];
    if (gameState.index >= gameState.items.length) {
      completeStage(4);
      const percent = Math.round(gameState.score / gameState.items.length * 100);
      $("#lesson-panel").innerHTML = panelHeading(name, "今天的变化游戏完成。") + `
        <div class="activity-card result-copy">
          <div class="score-badge" style="--score:${percent}%"><strong>${percent}分</strong></div>
          <h3>找回了 ${gameState.score} / ${gameState.items.length} 个词</h3>
          <p>游戏结果只用来安排复习，不给孩子贴标签。</p>
          <button type="button" class="action-button ghost" data-game-replay>再玩一局</button>
        </div>${stageFooter("去出口挑战")}`;
      return;
    }
    const item = gameState.items[gameState.index];
    const markup = gameState.type === "sound" ? renderSoundGame(item)
      : gameState.type === "recall" ? renderRecallGame(item)
        : gameState.type === "sort" ? renderSortGame(item)
          : gameState.type === "phrase" ? renderPhraseGame(item)
            : renderClueGame(item);
    $("#lesson-panel").innerHTML = panelHeading(name, "同一个词换一种玩法，再从记忆里取出来。") + markup +
      `<details class="teacher-note"><summary>给带课大人的提示</summary><p>这关做 5 次提取，混合今天和旧词。第一次讲清规则，后面只给最小提示。</p></details>${stageFooter("去出口挑战")}`;
  }

  function answerGame(value) {
    if (!gameState || gameState.answered) return;
    const item = gameState.items[gameState.index];
    const expected = gameState.type === "sort" ? (CATEGORY[item.w] || "物品") : item.w;
    gameState.selected = value;
    gameState.answered = true;
    if (value === expected) gameState.score += 1;
    renderGame();
    speak(item.w);
  }

  function nextGame() {
    gameState.index += 1;
    gameState.answered = false;
    gameState.selected = "";
    gameState.revealed = false;
    gameState.choices = null;
    gameState.tiles = null;
    gameState.built = [];
    renderGame();
  }

  function createExit() {
    const pool = unique([...day.words, ...reviewPool()]);
    const questions = sample(pool, 5).map((item, index) => makeQuestion(item, index % 2 ? "phrase" : "listen", cumulativePool()));
    return { questions, index: 0, score: 0, answered: false, selected: "", recorded: false };
  }

  function renderExit() {
    if (!exitState) exitState = createExit();
    if (exitState.index >= exitState.questions.length) {
      const percent = Math.round(exitState.score / exitState.questions.length * 100);
      const passed = percent >= 80;
      if (!exitState.recorded) {
        exitState.recorded = true;
        state.scores[`d${dayNumber}`] = Math.max(percent, state.scores[`d${dayNumber}`] || 0);
        if (passed && !state.completedDays.includes(dayNumber)) state.completedDays.push(dayNumber);
        if (passed) {
          completeStage(5);
          celebrate();
        } else {
          saveState();
        }
      }
      $("#lesson-panel").innerHTML = panelHeading("出口挑战", "5 题独立提取，80 分点亮今日邮戳。") + `
        <div class="activity-card result-copy">
          <div class="score-badge" style="--score:${percent}%"><strong>${percent}分</strong></div>
          <h3>${passed ? "今日邮站已点亮！" : "还差一点点信号"}</h3>
          <p>${passed ? `答对 ${exitState.score} / 5，可以打开下一封来信。` : `答对 ${exitState.score} / 5。先回到翻卡重练，再挑战一次。`}</p>
          <div class="button-row" style="justify-content:center">
            <button type="button" class="action-button ghost" data-exit-replay>再挑战一次</button>
            ${passed && dayNumber < 15 ? `<button type="button" class="action-button primary" data-next-day>前往第 ${dayNumber + 1} 天 →</button>` : ""}
            ${passed && dayNumber === 15 ? `<button type="button" class="action-button primary" data-speak="You did it! One hundred words!">播放毕业祝贺</button>` : ""}
          </div>
        </div>
        <details class="teacher-note" open><summary>给带课大人的提示</summary><p>${passed ? "今天到这里就好。离开屏幕后，请孩子再说一个最喜欢的短句。" : "不要马上重考。先回到翻卡，只练配错的线索，再做第二次出口挑战。"}</p></details>`;
      return;
    }
    const question = exitState.questions[exitState.index];
    const prompt = question.type === "listen" ? "听单词，选择正确图片"
      : `哪一个词能补进短句？“${question.item.p.replace(new RegExp(question.item.w, "i"), "____")}”`;
    $("#lesson-panel").innerHTML = panelHeading("出口挑战", "独立完成 5 题，达到 80 分即可过关。") +
      instruction("大人不提示、不翻回去；每题答完都大声读一次正确短句。") + `
      <div class="activity-card">
        <p class="question-count">EXIT ${exitState.index + 1} / 5</p>
        <h3 class="question-title">${escapeHTML(prompt)}</h3>
        ${question.type === "listen" ? `<button type="button" class="action-button audio" data-speak="${escapeHTML(question.item.w)}">♪ 播放单词</button>` : ""}
        <div class="choice-grid${question.type === "listen" ? " image-choice-grid" : ""}">${question.choices.map(choice => {
          const correct = exitState.answered && choice.w === question.item.w;
          const wrong = exitState.answered && choice.w === exitState.selected && choice.w !== question.item.w;
          return `<button type="button" class="choice${question.type === "listen" ? " image-choice" : ""}${correct ? " correct" : ""}${wrong ? " wrong" : ""}"
            data-exit-answer="${escapeHTML(choice.w)}" ${exitState.answered ? "disabled" : ""}>${question.type === "listen" ? art(choice) : escapeHTML(choice.w)}</button>`;
        }).join("")}</div>
        <div class="feedback${exitState.answered ? (exitState.selected === question.item.w ? " good" : " retry") : ""}">
          ${exitState.answered ? (exitState.selected === question.item.w ? `正确！${escapeHTML(question.item.p)}` : `正确答案是 ${escapeHTML(question.item.w)}。${escapeHTML(question.item.p)}`) : "独立完成，不看提示。"}
        </div>
        ${exitState.answered ? `<div class="button-row">
          <button type="button" class="action-button primary" data-exit-next>${exitState.index === 4 ? "查看今日成绩" : "下一题"} →</button>
          <button type="button" class="action-button audio" data-speak="${escapeHTML(question.item.p)}">♪ 听正确短句</button>
        </div>` : ""}
      </div>`;
  }

  function renderPanel() {
    if (stageIndex === 0) renderQuiz();
    else if (stageIndex === 1) renderWords();
    else if (stageIndex === 2) renderFade();
    else if (stageIndex === 3) renderFlip();
    else if (stageIndex === 4) renderGame();
    else renderExit();
  }

  function switchStage(next) {
    stageIndex = Math.max(0, Math.min(5, next));
    if (stageIndex === 0) quizState = null;
    if (stageIndex === 3) flipState = null;
    if (stageIndex === 4) gameState = null;
    if (stageIndex === 5) exitState = null;
    renderStageTabs();
    renderPanel();
    $("#lesson-panel").focus({ preventScroll: true });
  }

  document.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!button) return;
    if (button.matches("[data-stage]")) switchStage(Number(button.dataset.stage));
    else if (button.matches("[data-prev-stage]")) switchStage(stageIndex - 1);
    else if (button.matches("[data-next-stage]")) {
      if (stageIndex < 5) {
        completeStage(stageIndex);
        switchStage(stageIndex + 1);
      } else {
        showToast("先完成出口挑战，达到 80 分就会点亮今天。");
      }
    } else if (button.matches("[data-speak]")) speak(button.dataset.speak, button);
    else if (button.matches("[data-word-index]")) {
      wordIndex = Number(button.dataset.wordIndex);
      renderWords();
    } else if (button.matches("[data-word-prev]")) {
      wordIndex = Math.max(0, wordIndex - 1);
      renderWords();
    } else if (button.matches("[data-word-next]")) {
      if (wordIndex < day.words.length - 1) {
        wordIndex += 1;
        renderWords();
      } else {
        completeStage(1);
        switchStage(2);
      }
    } else if (button.matches("[data-fade]")) {
      const index = Number(button.dataset.fade);
      fadeReveals.add(index);
      speak(fadeItems()[index].p, button);
      if (fadeReveals.size === 3) completeStage(2);
      renderFade();
    } else if (button.matches("[data-quiz-answer]")) {
      if (quizState.answered) return;
      quizState.selected = button.dataset.quizAnswer;
      quizState.answered = true;
      const question = quizState.questions[quizState.index];
      if (quizState.selected === question.item.w) quizState.score += 1;
      renderQuiz();
      speak(question.item.w);
    } else if (button.matches("[data-quiz-next]")) {
      quizState.index += 1;
      quizState.answered = false;
      quizState.selected = "";
      renderQuiz();
    } else if (button.matches("[data-flip]")) handleFlip(Number(button.dataset.flip));
    else if (button.matches("[data-flip-reset]")) {
      flipState = createFlip();
      renderFlip();
    } else if (button.matches("[data-game-answer]")) answerGame(button.dataset.gameAnswer);
    else if (button.matches("[data-game-next]")) nextGame();
    else if (button.matches("[data-reveal-recall]")) {
      gameState.revealed = true;
      renderGame();
    } else if (button.matches("[data-self-score]")) {
      if (button.dataset.selfScore === "yes") gameState.score += 1;
      nextGame();
    } else if (button.matches("[data-build]")) {
      const index = Number(button.dataset.build);
      if (!gameState.built.includes(index)) gameState.built.push(index);
      renderGame();
    } else if (button.matches("[data-unbuild]")) {
      gameState.built.splice(Number(button.dataset.unbuild), 1);
      renderGame();
    } else if (button.matches("[data-clear-phrase]")) {
      gameState.built = [];
      renderGame();
    } else if (button.matches("[data-check-phrase]")) {
      const item = gameState.items[gameState.index];
      const built = gameState.built.map(index => gameState.tiles[index]).join(" ").toLowerCase();
      const expected = phraseWords(item.p).join(" ").toLowerCase();
      gameState.selected = built;
      gameState.answered = true;
      if (built === expected) gameState.score += 1;
      renderGame();
    } else if (button.matches("[data-game-replay]")) {
      gameState = null;
      renderGame();
    } else if (button.matches("[data-exit-answer]")) {
      if (exitState.answered) return;
      exitState.selected = button.dataset.exitAnswer;
      exitState.answered = true;
      const question = exitState.questions[exitState.index];
      if (exitState.selected === question.item.w) exitState.score += 1;
      renderExit();
      speak(question.item.w);
    } else if (button.matches("[data-exit-next]")) {
      exitState.index += 1;
      exitState.answered = false;
      exitState.selected = "";
      renderExit();
    } else if (button.matches("[data-exit-replay]")) {
      exitState = null;
      renderExit();
    } else if (button.matches("[data-next-day]")) {
      location.href = `day${String(dayNumber + 1).padStart(2, "0")}.html`;
    }
  });

  $("#speech-rate").value = String(state.rate);
  $("#speech-repeat").value = String(state.repeat);
  $("#speech-rate").addEventListener("change", event => {
    state.rate = Number(event.target.value);
    saveState();
    showToast("语速已保存。");
  });
  $("#speech-repeat").addEventListener("change", event => {
    state.repeat = Number(event.target.value);
    saveState();
    showToast("重复次数已保存。");
  });
  $("#motion-toggle").addEventListener("click", () => {
    state.reducedMotion = !state.reducedMotion;
    document.body.classList.toggle("reduce-motion", state.reducedMotion);
    $("#motion-toggle").textContent = state.reducedMotion ? "动效关" : "动效开";
    $("#motion-toggle").setAttribute("aria-pressed", String(state.reducedMotion));
    saveState();
    showToast(state.reducedMotion ? "已减少动效。" : "已开启动效。");
  });
  $("#reset-day").addEventListener("click", () => {
    if (!confirm(`要重玩第 ${dayNumber} 天吗？会清除今天的阶段记录和成绩。`)) return;
    delete state.stages[`d${dayNumber}`];
    delete state.scores[`d${dayNumber}`];
    state.completedDays = state.completedDays.filter(number => number !== dayNumber);
    saveState();
    location.reload();
  });

  prepareCourse();
  document.body.classList.toggle("reduce-motion", state.reducedMotion);
  $("#motion-toggle").textContent = state.reducedMotion ? "动效关" : "动效开";
  $("#motion-toggle").setAttribute("aria-pressed", String(state.reducedMotion));
  renderHero();
  renderDayList();
  renderStageTabs();
  renderPanel();

  window.courseQA = {
    days: COURSE.length,
    totalWords: COURSE.flatMap(courseDay => courseDay.words).length,
    uniqueWords: new Set(COURSE.flatMap(courseDay => courseDay.words.map(item => item.w.toLowerCase()))).size,
    maxPhraseWords: Math.max(...COURSE.flatMap(courseDay => courseDay.words.map(item => phraseWords(item.p).length))),
    distinctDailyPages: COURSE.length,
    imageAtlases: COURSE.length,
    imageMappings: COURSE.flatMap(courseDay => courseDay.words).filter(item => item.atlas).length,
    localAudioFilesExpected: COURSE.flatMap(courseDay => courseDay.words).length * 2 + 1,
    flipLevels: COURSE.map(courseDay => {
      const originalDay = document.body.dataset.day;
      document.body.dataset.day = courseDay.day;
      const level = courseDay.day <= 3 ? { pairs: 3, mode: "visual-word" }
        : courseDay.day <= 6 ? { pairs: 4, mode: "visual-word" }
          : courseDay.day <= 9 ? { pairs: 5, mode: "sound-visual" }
            : courseDay.day <= 12 ? { pairs: 6, mode: "word-phrase" }
              : courseDay.day <= 14 ? { pairs: 7, mode: "phrase-visual" }
                : { pairs: 8, mode: "mixed" };
      document.body.dataset.day = originalDay;
      return level;
    })
  };
})();

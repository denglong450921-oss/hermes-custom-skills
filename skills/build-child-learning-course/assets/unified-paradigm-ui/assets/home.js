"use strict";

(() => {
  const COURSE = window.COURSE_DATA || [];
  const STORE_KEY = "sound-post-office-v3";
  const LEGACY_KEY = "sound-post-office-v1";
  const GAME_NAMES = {
    sound: "声音侦探",
    recall: "看图说词",
    sort: "分类邮筒",
    phrase: "短句拼装",
    clue: "线索寻词"
  };
  const ATLAS_RATIOS = {
    1: 1, 2: 1, 3: 1, 4: .888, 5: .75,
    6: 1, 7: .75, 8: .75, 9: .75, 10: .75,
    11: .75, 12: .75, 13: .75, 14: .75, 15: .75
  };
  const POSITIONS = [
    ["0%", "0%"], ["33.333%", "0%"], ["66.667%", "0%"], ["100%", "0%"],
    ["0%", "100%"], ["33.333%", "100%"], ["66.667%", "100%"], ["100%", "100%"]
  ];

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    })[character]);
  }

  function readState() {
    const defaults = { currentDay: 0, completedDays: [], scores: {}, rate: .85, repeat: 1 };
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
      // A blocked storage area should never prevent the local course from opening.
    }
    return defaults;
  }

  function prepareCourse() {
    COURSE.forEach(day => day.words.forEach((item, slot) => {
      const key = item.w.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      item.day = day.day;
      item.slot = slot;
      item.audioWord = `assets/audio/${key}-word.mp3`;
      item.audioPhrase = `assets/audio/${key}-phrase.mp3`;
      item.atlas = `assets/images/day${String(day.day).padStart(2, "0")}-atlas.png`;
      item.artRatio = ATLAS_RATIOS[day.day] || .75;
    }));
  }

  function artStyle(item) {
    const [x, y] = POSITIONS[item.slot] || POSITIONS[0];
    return `background-image:url('${item.atlas}');--x:${x};--y:${y};--art-ratio:${item.artRatio}`;
  }

  function setHeroArt() {
    const target = document.querySelector("[data-home-art]");
    const [day, slot] = (target.dataset.homeArt || "6:0").split(":").map(Number);
    const item = COURSE[day - 1].words[slot];
    target.setAttribute("style", artStyle(item));
    target.setAttribute("aria-label", `${item.zh}的软陶绘本插画`);
  }

  function renderDayCards(state) {
    document.querySelector("#home-day-grid").innerHTML = COURSE.map(day => {
      const item = day.words[0];
      const completed = state.completedDays.includes(day.day);
      const n = String(day.day).padStart(2, "0");
      return `<a class="home-day-card${completed ? " done" : ""}" href="day${n}.html">
        <span class="atlas-art home-day-art" role="img" aria-label="${escapeHTML(item.zh)}绘本插画" style="${artStyle(item)}"></span>
        <span class="home-day-copy">
          <small>DAY ${n}${completed ? " · 已完成" : ""}</small>
          <h3>${escapeHTML(day.theme)}</h3>
          <p>${day.words.length} 个词 · ${escapeHTML(GAME_NAMES[day.game])}</p>
        </span>
      </a>`;
    }).join("");
  }

  let sampleAudio = null;
  function playSample(button) {
    if (sampleAudio) {
      sampleAudio.pause();
      sampleAudio.currentTime = 0;
    }
    sampleAudio = new Audio("assets/audio/hello-phrase.mp3");
    sampleAudio.playbackRate = .85;
    button.textContent = "正在播放…";
    sampleAudio.onended = () => { button.textContent = "听一听声音"; };
    sampleAudio.onerror = () => {
      button.textContent = "听一听声音";
      showToast("没有找到本地 MP3，请检查 assets/audio 文件夹。");
    };
    const request = sampleAudio.play();
    if (request && request.catch) request.catch(() => {
      button.textContent = "听一听声音";
      showToast("浏览器等待你再次点击播放。");
    });
  }

  let toastTimer;
  function showToast(message) {
    const toast = document.querySelector("#toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2400);
  }

  prepareCourse();
  const state = readState();
  renderDayCards(state);
  setHeroArt();

  const nextDay = COURSE.find(day => !state.completedDays.includes(day.day))?.day || 15;
  document.querySelector("#continue-link").href = `day${String(nextDay).padStart(2, "0")}.html`;
  document.querySelector("#continue-link").textContent = state.completedDays.length
    ? `继续第 ${nextDay} 天`
    : "打开今天的来信";
  document.querySelector("#sample-audio").addEventListener("click", event => playSample(event.currentTarget));
  document.querySelector("#reset-course").addEventListener("click", () => {
    if (!confirm("要清除 15 天的课程进度吗？图片、声音和课程内容不会删除。")) return;
    localStorage.removeItem(STORE_KEY);
    localStorage.removeItem(LEGACY_KEY);
    location.reload();
  });

  window.courseQA = {
    days: COURSE.length,
    totalWords: COURSE.flatMap(day => day.words).length,
    distinctDailyPages: COURSE.length,
    imageAtlases: COURSE.length,
    imageMappings: COURSE.flatMap(day => day.words).filter(item => item.atlas).length,
    localAudioFilesExpected: COURSE.flatMap(day => day.words).length * 2 + 1
  };
})();

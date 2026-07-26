#!/usr/bin/env python3
"""Create a safe, offline, multi-day HTML course skeleton."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{page_title}</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body data-page="{page}"{day_attr}>
  <a class="skip-link" href="#app">跳到学习内容</a>
  <div class="scene" aria-hidden="true">
    <span class="shape shape-one">★</span>
    <span class="shape shape-two">●</span>
    <span class="shape shape-three">▲</span>
  </div>
  <button id="mobile-toggle" class="mobile-toggle" aria-label="打开目录">☰ 目录</button>
  <button id="motion-toggle" class="motion-toggle" aria-pressed="false">✨ 动效</button>
  <div class="shell">
    <aside id="sidebar" class="sidebar"></aside>
    <main id="app" class="content"></main>
  </div>
  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <script src="assets/course-data.js"></script>
  <script src="assets/app.js"></script>
</body>
</html>
"""


CSS = """\
:root{--navy:#24304a;--sun:#ffd84d;--coral:#ff6b6b;--sky:#59c8ff;--grape:#8c6ff7;--mint:#62d6a7;--cream:#fffaf0;--card:#fff;--line:#24304a;--pop-shadow:0 8px 0 rgba(36,48,74,.16)}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at 90% 8%,#ffe993 0 8%,transparent 9%),linear-gradient(135deg,#eaf9ff,var(--cream));color:var(--navy);font-family:"Arial Rounded MT Bold","PingFang SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.6}
button,a{font:inherit}
button:focus-visible,a:focus-visible{outline:4px solid #ffd166;outline-offset:3px}
.skip-link{position:fixed;z-index:100;left:12px;top:-70px;padding:10px 14px;border-radius:12px;background:white;color:var(--navy)}
.skip-link:focus{top:12px}
.scene{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none}
.shape{position:absolute;display:grid;place-items:center;width:70px;height:70px;border:3px solid var(--navy);border-radius:24px;background:var(--sun);box-shadow:var(--pop-shadow);animation:float 4s ease-in-out infinite paused}
.shape-one{right:5%;top:18%;transform:rotate(12deg)}
.shape-two{right:11%;bottom:12%;background:var(--mint);animation-delay:-1.2s}
.shape-three{left:300px;bottom:7%;background:var(--sky);animation-delay:-2s}
.motion-on .shape{animation-play-state:running}
@keyframes float{50%{translate:0 -14px;rotate:5deg}}
.sidebar{position:fixed;inset:0 auto 0 0;width:280px;padding:24px 18px;background:linear-gradient(180deg,var(--navy),#3e356e);color:white;overflow:auto;border-right:4px solid var(--navy)}
.brand{margin:0 8px 18px;font-size:20px}
.toc{display:grid;gap:5px}
.toc a{padding:10px 12px;border-radius:12px;color:#d8edf3;text-decoration:none}
.toc a:hover,.toc a.active{background:#ffffff18;color:white}
.content{margin-left:280px;padding:38px clamp(20px,5vw,72px) 80px}
.hero,.section,.mission-card{padding:30px;border:3px solid var(--navy);border-radius:28px;background:#fffffff2;box-shadow:var(--pop-shadow)}
.hero h1{margin:0 0 10px;font-size:clamp(34px,5vw,62px);line-height:1.05}
.section{margin-top:24px}
.section h2{margin-top:0}
.day-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.day-card,.activity{min-width:0;padding:18px;border:3px solid var(--line);border-radius:20px;background:white;box-shadow:0 5px 0 rgba(36,48,74,.12)}
.day-card{color:inherit;text-decoration:none}
.day-card:hover{translate:0 -3px;background:#fef7d8}
.mission-list{display:grid;gap:20px;margin-top:24px}
.mission-card{position:relative;min-width:0}
.mission-card[data-mode="learning"]{background:linear-gradient(135deg,#fff9d8,#ecfaff)}
.mission-card[data-mode="testing"]{background:linear-gradient(135deg,#f6efff,#fff0f0)}
.mission-card.done{border-color:#218c61;background:#eafff6}
.mission-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.mode-chip,.percent-chip,.stage-chip{display:inline-flex;align-items:center;padding:4px 10px;border:2px solid var(--navy);border-radius:999px;font-weight:800;font-size:14px;background:white}
.mode-chip.learning{background:var(--sun)}
.mode-chip.testing{background:var(--grape);color:white}
.ratio-meter{display:grid;grid-template-columns:3fr 7fr;height:22px;margin-top:18px;border:3px solid var(--navy);border-radius:999px;overflow:hidden;background:white}
.ratio-learning{background:linear-gradient(90deg,var(--sun),var(--sky))}
.ratio-testing{background:linear-gradient(90deg,var(--grape),var(--coral))}
.ratio-labels{display:flex;justify-content:space-between;gap:12px;margin-top:7px;font-weight:800}
.progress-track{height:18px;margin:18px 0 6px;border:3px solid var(--navy);border-radius:999px;background:white;overflow:hidden}
.progress-fill{width:0;height:100%;background:linear-gradient(90deg,var(--mint),var(--sky),var(--grape));transition:width .35s ease}
.placeholder{padding:22px;border:3px dashed #88b9c9;border-radius:18px;background:#ffffffb8}
.game-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.game-card{min-width:0;padding:20px;border:3px solid var(--navy);border-radius:22px;background:white;box-shadow:0 6px 0 #d9d2ff;transition:translate .16s,transform .16s}
.motion-on .game-card:hover{translate:0 -5px;transform:rotate(-1deg)}
.game-id{display:inline-block;padding:3px 9px;border-radius:999px;background:var(--grape);color:white;font-size:14px}
.action-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.action-btn,.reset-btn{min-height:46px;padding:10px 16px;border:3px solid var(--navy);border-radius:16px;background:var(--coral);color:white;font-weight:900;box-shadow:0 4px 0 var(--navy);cursor:pointer}
.action-btn:active,.reset-btn:active{translate:0 3px;box-shadow:0 1px 0 var(--navy)}
.reset-btn{background:white;color:var(--navy)}
.mobile-toggle,.motion-toggle{position:fixed;z-index:30;top:12px;padding:10px 13px;border:3px solid var(--navy);border-radius:14px;background:var(--sun);color:var(--navy);font-weight:900}
.mobile-toggle{display:none;left:12px}
.motion-toggle{right:16px}
.toast{position:fixed;z-index:40;right:20px;bottom:20px;padding:12px 16px;border:3px solid var(--navy);border-radius:16px;background:var(--navy);color:white;transform:translateY(140px);transition:transform .2s}
.toast.show{transform:none}
@media(max-width:800px){.sidebar{transform:translateX(-102%);transition:transform .2s;z-index:25}.sidebar.open{transform:none}.content{margin-left:0;padding:76px 16px}.mobile-toggle{display:block}.motion-toggle{right:12px}.shape-three{left:5%}.hero,.section,.mission-card{padding:22px}.ratio-labels{font-size:14px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""


APP_JS = r"""
(function(){
  const data=window.COURSE_DATA;
  const page=document.body.dataset.page;
  const dayNumber=Number(document.body.dataset.day||0);
  const storageKey='child-course-progress-v3';
  let state={days:{},motion:false};
  try{state={...state,...JSON.parse(localStorage.getItem(storageKey)||'{}')};}catch(error){}

  function save(){
    try{localStorage.setItem(storageKey,JSON.stringify(state));}catch(error){}
  }

  function showToast(message){
    const toast=document.querySelector('#toast');
    toast.textContent=message;
    toast.classList.add('show');
    window.setTimeout(()=>toast.classList.remove('show'),1400);
  }

  function dayState(){
    state.days=state.days||{};
    state.days[dayNumber]=state.days[dayNumber]||{blocks:{},attempts:{}};
    return state.days[dayNumber];
  }

  function shell(active){
    document.querySelector('#sidebar').innerHTML=`<h1 class="brand">${data.title}</h1><nav class="toc"><a class="${active===0?'active':''}" href="index.html">课程总览</a>${data.days.map(d=>`<a class="${active===d.day?'active':''}" href="day${String(d.day).padStart(2,'0')}.html">第${d.day}天 · ${d.title}</a>`).join('')}</nav>`;
    document.querySelector('#mobile-toggle').onclick=()=>document.querySelector('#sidebar').classList.toggle('open');
    const motion=document.querySelector('#motion-toggle');
    document.body.classList.toggle('motion-on',Boolean(state.motion));
    motion.setAttribute('aria-pressed',String(Boolean(state.motion)));
    motion.onclick=()=>{
      state.motion=!state.motion;
      document.body.classList.toggle('motion-on',state.motion);
      motion.setAttribute('aria-pressed',String(state.motion));
      save();
    };
  }

  function outline(){
    shell(0);
    document.querySelector('#app').innerHTML=`<header class="hero"><p>${data.audience}</p><h1>${data.title}</h1><p>${data.masteryGoal}</p><div class="ratio-meter" aria-label="30%学习，70%测试"><span class="ratio-learning"></span><span class="ratio-testing"></span></div><div class="ratio-labels"><span>🌞 学习 30%</span><span>🎮 测试 70%</span></div><p><strong>${data.coreGames.length} 个核心游戏引擎</strong>，通过上手、巩固和迁移跨日深化。</p></header><section class="section"><h2>课程地图</h2><div class="day-grid">${data.days.map(d=>`<a class="day-card" href="day${String(d.day).padStart(2,'0')}.html"><strong>第${d.day}天</strong><h3>${d.title}</h3><p>${d.objective}</p><small>${(d.games||[]).map(g=>`${g.name} · ${g.stageLabel}`).join(' / ')}</small></a>`).join('')}</div></section>`;
  }

  function missionCard(block,d){
    const complete=Boolean(dayState().blocks[block.id]);
    const labels={learning:'学习',testing:'测试'};
    let body='';
    if(block.id==='previous-review')body=`<div class="placeholder">${d.review}</div>`;
    if(block.id==='micro-lesson')body=`<div class="placeholder">${d.model}</div>`;
    if(block.id==='worked-example')body=`<div class="placeholder">${d.guidedPractice}</div>`;
    if(block.id==='exit-challenge')body=`<div class="placeholder">${d.exitCheck}</div>`;
    if(block.gameIndex!==undefined){
      const g=d.games[block.gameIndex];
      const attempts=dayState().attempts[g.id]||0;
      body=`<article class="game-card"><span class="game-id">${g.id}</span><span class="stage-chip">${g.stageLabel}</span><h3>${g.name}</h3><p>${g.adaptation}</p><p>已记录作答：<strong data-attempt-count="${g.id}">${attempts}</strong> 次</p><div class="action-row"><button class="action-btn" data-game-action="${g.id}">记录一次作答</button></div></article>`;
    }
    return `<section class="mission-card ${complete?'done':''}" data-mode="${block.mode}" data-block="${block.id}"><div class="mission-head"><span class="mode-chip ${block.mode}">${labels[block.mode]}</span><span class="percent-chip">${block.percent}%</span><h2>${block.title}</h2></div>${body}<div class="action-row"><button class="action-btn" data-complete-block="${block.id}">${complete?'✓ 已完成':'完成这一关'}</button></div></section>`;
  }

  function updateProgress(){
    const d=window.COURSE_DATA.days[dayNumber-1];
    const completeCount=d.timePlan.filter(b=>dayState().blocks[b.id]).length;
    const percent=Math.round(completeCount/d.timePlan.length*100);
    const fill=document.querySelector('#progress-fill');
    if(fill)fill.style.width=`${percent}%`;
    const label=document.querySelector('#progress-label');
    if(label)label.textContent=`今日任务 ${completeCount}/${d.timePlan.length}`;
  }

  function bindDaily(d){
    document.querySelectorAll('[data-complete-block]').forEach(button=>{
      button.onclick=()=>{
        const id=button.dataset.completeBlock;
        dayState().blocks[id]=!dayState().blocks[id];
        save();
        daily();
        showToast(dayState().blocks[id]?'任务完成，继续闯关！':'已恢复这一关');
      };
    });
    document.querySelectorAll('[data-game-action]').forEach(button=>{
      button.onclick=()=>{
        const id=button.dataset.gameAction;
        dayState().attempts[id]=(dayState().attempts[id]||0)+1;
        save();
        const counter=document.querySelector(`[data-attempt-count="${id}"]`);
        if(counter)counter.textContent=dayState().attempts[id];
        showToast('已记录一次作答，先想再看反馈！');
      };
    });
    document.querySelector('#reset-day').onclick=()=>{
      state.days[dayNumber]={blocks:{},attempts:{}};
      save();
      daily();
      showToast('今天的进度已重置');
    };
    updateProgress();
  }

  function daily(){
    shell(dayNumber);
    const d=data.days[dayNumber-1];
    const reviewLabel=d.reviewSourceDay==='prerequisites'?'入学基础':`第 ${d.reviewSourceDay} 天`;
    document.querySelector('#app').innerHTML=`<header class="hero"><p>DAY ${String(d.day).padStart(2,'0')} · 先复习 ${reviewLabel}</p><h1>${d.title}</h1><p>${d.objective}</p><div class="ratio-meter" aria-label="30%学习，70%测试"><span class="ratio-learning"></span><span class="ratio-testing"></span></div><div class="ratio-labels"><span>🌞 学习 30%</span><span>🎮 测试 70%</span></div><div class="progress-track" aria-hidden="true"><div id="progress-fill" class="progress-fill"></div></div><p id="progress-label">今日任务 0/6</p><button id="reset-day" class="reset-btn">重置今天</button></header><div class="mission-list">${d.timePlan.map(block=>missionCard(block,d)).join('')}</div><div class="toast-copy" aria-live="polite"></div>`;
    bindDaily(d);
  }

  if(page==='outline')outline();else daily();
})();
"""


GAME_LIBRARY = (
    ("G01", "翻牌配对"),
    ("G02", "听音侦探"),
    ("G03", "看图开口"),
    ("G06", "拼搭工坊"),
    ("G08", "错误小医生"),
    ("G15", "小老师挑战"),
)

STAGE_LABELS = {
    "onboarding": "上手",
    "consolidation": "巩固",
    "transfer": "迁移",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an offline child-learning course skeleton."
    )
    parser.add_argument("--slug", required=True, help="Lowercase hyphenated folder name")
    parser.add_argument("--title", required=True, help="Course title")
    parser.add_argument("--days", type=int, default=15, help="Number of daily pages")
    parser.add_argument(
        "--output-dir", type=Path, default=Path.cwd(), help="Parent output directory"
    )
    parser.add_argument("--language", default="zh-CN", help="HTML language tag")
    parser.add_argument(
        "--audience", default="请填写学习者年龄、基础和每日学习时间。"
    )
    parser.add_argument(
        "--mastery-goal", default="请填写完成课程后可以观察到的学习成果。"
    )
    return parser.parse_args()


def validate(args: argparse.Namespace) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        raise SystemExit("--slug must contain lowercase letters, digits, and hyphens only")
    if not 1 <= args.days <= 60:
        raise SystemExit("--days must be between 1 and 60")


def core_game_count(total_days: int) -> int:
    if total_days >= 15:
        return 6
    if total_days >= 12:
        return 5
    if total_days >= 4:
        return 4
    return max(2, total_days)


def selected_games(total_days: int, day: int) -> tuple[tuple[str, str], tuple[str, str]]:
    core = GAME_LIBRARY[: core_game_count(total_days)]
    primary_index = ((day - 1) // 3) % len(core)
    offset = 1 + ((day - 1) % min(3, len(core) - 1))
    secondary_index = (primary_index + offset) % len(core)
    return core[primary_index], core[secondary_index]


def stage_for_occurrence(occurrence: int) -> str:
    if occurrence == 1:
        return "onboarding"
    if occurrence == 2:
        return "consolidation"
    return "transfer"


def time_plan() -> list[dict[str, object]]:
    return [
        {
            "id": "previous-review",
            "title": "① 昨日回忆挑战",
            "mode": "testing",
            "percent": 15,
        },
        {
            "id": "micro-lesson",
            "title": "② 新知识微课堂",
            "mode": "learning",
            "percent": 20,
        },
        {
            "id": "worked-example",
            "title": "③ 一起看一个例子",
            "mode": "learning",
            "percent": 10,
        },
        {
            "id": "game-round-a",
            "title": "④ 核心游戏测试 A",
            "mode": "testing",
            "percent": 20,
            "gameIndex": 0,
        },
        {
            "id": "game-round-b",
            "title": "⑤ 核心游戏测试 B",
            "mode": "testing",
            "percent": 20,
            "gameIndex": 1,
        },
        {
            "id": "exit-challenge",
            "title": "⑥ 离堂挑战",
            "mode": "testing",
            "percent": 15,
        },
    ]


def day_record(
    day: int, games: tuple[dict[str, str], dict[str, str]]
) -> dict[str, object]:
    return {
        "day": day,
        "title": f"待设计主题 {day}",
        "objective": "填写一个可观察、可测试的当天目标。",
        "reviewSourceDay": "prerequisites" if day == 1 else day - 1,
        "review": (
            "用不显示答案的任务检查入学基础。"
            if day == 1
            else f"先提取第 {day - 1} 天的核心内容，再进入新知识。"
        ),
        "model": "用一张关键图、一个声音、一个动作或一个具体模型讲清新知识。",
        "guidedPractice": "演示一个例子，随后淡出提示，让孩子完成最后一步。",
        "games": list(games),
        "exitCheck": "隐藏答案，要求孩子独立选择、说出、构建或解释。",
        "timePlan": time_plan(),
    }


def build_days(total_days: int) -> list[dict[str, object]]:
    occurrences: dict[str, int] = {}
    days: list[dict[str, object]] = []
    for day in range(1, total_days + 1):
        records: list[dict[str, str]] = []
        for game_id, name in selected_games(total_days, day):
            occurrences[game_id] = occurrences.get(game_id, 0) + 1
            stage = stage_for_occurrence(occurrences[game_id])
            records.append(
                {
                    "id": game_id,
                    "name": name,
                    "stage": stage,
                    "stageLabel": STAGE_LABELS[stage],
                    "adaptation": (
                        "填写本轮真实题目、作答方式、反馈规则与可观察成功证据。"
                    ),
                }
            )
        days.append(day_record(day, (records[0], records[1])))
    return days


def write_course(args: argparse.Namespace) -> Path:
    target = args.output_dir.expanduser().resolve() / args.slug
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing target: {target}")

    assets = target / "assets"
    (assets / "audio").mkdir(parents=True)
    (assets / "images").mkdir()
    (assets / "audio" / ".gitkeep").write_text("", encoding="utf-8")
    (assets / "images" / ".gitkeep").write_text("", encoding="utf-8")

    course = {
        "title": args.title,
        "audience": args.audience,
        "masteryGoal": args.mastery_goal,
        "timeSplit": {"learning": 30, "testing": 70},
        "coreGames": [
            game_id for game_id, _ in GAME_LIBRARY[: core_game_count(args.days)]
        ],
        "days": build_days(args.days),
    }
    data_js = "window.COURSE_DATA = " + json.dumps(
        course, ensure_ascii=False, indent=2
    ) + ";\n"
    (assets / "course-data.js").write_text(data_js, encoding="utf-8")
    (assets / "styles.css").write_text(CSS, encoding="utf-8")
    (assets / "app.js").write_text(APP_JS, encoding="utf-8")

    index = HTML_TEMPLATE.format(
        language=args.language,
        page_title=args.title,
        page="outline",
        day_attr="",
    )
    (target / "index.html").write_text(index, encoding="utf-8")

    for day in range(1, args.days + 1):
        html = HTML_TEMPLATE.format(
            language=args.language,
            page_title=f"第{day}天｜{args.title}",
            page="day",
            day_attr=f' data-day="{day}"',
        )
        (target / f"day{day:02}.html").write_text(html, encoding="utf-8")

    return target


def main() -> None:
    args = parse_args()
    validate(args)
    target = write_course(args)
    print(f"Created {args.days}-day offline course skeleton: {target}")


if __name__ == "__main__":
    main()

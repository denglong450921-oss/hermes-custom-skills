#!/usr/bin/env python3
"""Create a focused WeChat article writing brief from Markdown."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PROFILES: dict[str, dict[str, Any]] = {
    "explainer": {
        "label": "清晰科普",
        "best_for": "把复杂概念讲给普通读者",
        "theme": "minimal",
        "opening": "先指出读者常见误解，再给一句清晰判断。",
        "structure": ["误区或问题", "核心概念", "为什么重要", "怎么判断", "行动清单"],
        "tone": "准确、克制、少术语、每段只推进一个信息点",
    },
    "opinion": {
        "label": "观点专栏",
        "best_for": "认知、趋势、价值判断和反常识观点",
        "theme": "cognition",
        "opening": "用一个反常识判断开场，但必须马上解释边界。",
        "structure": ["核心判断", "反面误区", "判断依据", "迁移框架", "结尾金句"],
        "tone": "有锋芒但不喊口号，观点必须有推理链",
    },
    "story": {
        "label": "故事叙事",
        "best_for": "人物、案例、经历复盘和品牌故事",
        "theme": "minimal",
        "opening": "用一个具体场景开场，第二段点出主题。",
        "structure": ["场景", "冲突", "转折", "方法", "读者可带走的启发"],
        "tone": "具体、画面感强、少抽象总结，多动作和细节",
    },
    "framework": {
        "label": "方法框架",
        "best_for": "工具、流程、学习方法和可执行指南",
        "theme": "cognition",
        "opening": "先说读者会得到什么结果，再给框架总览。",
        "structure": ["适用问题", "框架总览", "步骤一", "步骤二", "常见误区", "复盘清单"],
        "tone": "清楚、有步骤、少抒情、强调可执行",
    },
    "business": {
        "label": "商业分析",
        "best_for": "商业、增长、财富、组织和战略判断",
        "theme": "wealth",
        "opening": "先给结论，再说明关键假设和风险。",
        "structure": ["结论", "背景变量", "机会", "风险", "执行路径", "判断清单"],
        "tone": "可信、现实、重假设，不许承诺确定收益",
    },
    "technical": {
        "label": "技术深度",
        "best_for": "AI、软件、架构、工程实践和工具链",
        "theme": "tech",
        "opening": "先说明工程问题和读者收益，再进入实现逻辑。",
        "structure": ["问题", "设计目标", "核心机制", "实现步骤", "边界条件", "迁移建议"],
        "tone": "精确、分层、避免炫技，代码服务于理解",
    },
    "health": {
        "label": "健康科普",
        "best_for": "健康、医学、运动、睡眠、营养和心理恢复",
        "theme": "health",
        "opening": "先安抚焦虑，再澄清误区和适用边界。",
        "structure": ["常见误区", "事实边界", "风险信号", "日常建议", "何时求助"],
        "tone": "温和、审慎、基于证据，不制造恐慌",
    },
}


PROFILE_KEYWORDS = {
    "health": ("健康", "医学", "睡眠", "营养", "疾病", "冥想", "wellness", "health"),
    "technical": ("ai", "api", "代码", "架构", "模型", "工程", "技术", "software", "tech"),
    "business": (
        "个人商业",
        "商业闭环",
        "闭环",
        "mvp",
        "商业",
        "增长",
        "投资",
        "财富",
        "战略",
        "组织",
        "finance",
        "business",
    ),
    "framework": ("方法", "步骤", "指南", "清单", "流程", "怎么做", "framework", "guide"),
    "story": ("故事", "复盘", "案例", "经历", "人物", "转折", "case", "story"),
    "opinion": ("观点", "认知", "趋势", "长期主义", "判断", "反常识", "opinion"),
}


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)(.*)\Z", text, re.S)
    if not match:
        return {}, text
    metadata: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, match.group(2)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_title(metadata: dict[str, Any], body: str, path: Path) -> str:
    if metadata.get("title"):
        return str(metadata["title"]).strip()
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").strip() or "未命名文章"


def headings(body: str) -> list[str]:
    return [
        match.group(2).strip()
        for match in re.finditer(r"^(#{2,3})\s+(.+)$", body, flags=re.M)
    ]


def paragraphs(body: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", body)
    return [
        compact(re.sub(r"^#+\s+", "", block))
        for block in blocks
        if compact(block) and not block.lstrip().startswith(("```", "|"))
    ]


def choose_profile(text: str, requested: str) -> str:
    if requested != "auto":
        return requested
    signal = text.lower()
    scores = {
        profile: sum(signal.count(keyword) for keyword in keywords)
        for profile, keywords in PROFILE_KEYWORDS.items()
    }
    winner = max(scores, key=scores.get)
    return winner if scores[winner] > 0 else "explainer"


def reader_promise(title: str, profile: str) -> str:
    if profile == "framework":
        return f"读完能拿到一套处理“{title}”的可执行方法。"
    if profile == "technical":
        return f"读完能理解“{title}”背后的关键机制和落地边界。"
    if profile == "business":
        return f"读完能判断“{title}”里的机会、假设和风险。"
    if profile == "health":
        return f"读完能更稳妥地理解“{title}”，知道哪些事能做、哪些情况要谨慎。"
    if profile == "story":
        return f"读完能从一个具体故事里带走关于“{title}”的可复用启发。"
    if profile == "opinion":
        return f"读完能获得一个关于“{title}”的清晰判断和推理框架。"
    return f"读完能用更简单的话理解“{title}”，并知道下一步怎么做。"


def title_options(title: str, profile: str) -> list[str]:
    clean = title.strip(" #")
    patterns = {
        "explainer": [f"一文讲透：{clean}", f"{clean}，到底该怎么理解？", f"别再误解{clean}"],
        "opinion": [f"关于{clean}，我最想说的一句话", f"{clean}真正改变的是什么？", f"多数人低估了{clean}"],
        "story": [f"我从{clean}里学到的一件事", f"一个关于{clean}的真实转折", f"{clean}背后的那次选择"],
        "framework": [f"{clean}的实用框架", f"处理{clean}，先抓住这几步", f"把{clean}做成闭环"],
        "business": [f"{clean}：机会、假设与风险", f"重新判断{clean}的商业价值", f"{clean}不是趋势，而是执行题"],
        "technical": [f"{clean}的核心机制", f"理解{clean}，先看这套架构", f"{clean}从原理到落地"],
        "health": [f"{clean}：别焦虑，先看边界", f"关于{clean}，更稳妥的理解", f"{clean}的日常建议与风险信号"],
    }
    return patterns.get(profile, patterns["explainer"])


def quality_findings(body: str, para_list: list[str], heading_list: list[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if len(heading_list) < 2:
        findings.append({"level": "major", "issue": "缺少可扫读的二级标题", "fix": "补 3-5 个以问题或动作开头的 H2。"})
    if para_list:
        opening = para_list[0]
        if len(opening) > 180:
            findings.append({"level": "major", "issue": "开头太长", "fix": "前两段压到 80-140 字，先给读者收益或核心判断。"})
        if not re.search(r"[？?]|为什么|怎么|如何|真正|误区|核心|结论", opening):
            findings.append({"level": "minor", "issue": "开头缺少抓手", "fix": "加入问题、反常识判断、具体场景或读者痛点。"})
    long_count = sum(1 for paragraph in para_list if len(paragraph) > 260)
    if long_count:
        findings.append({"level": "major", "issue": f"存在 {long_count} 个过长段落", "fix": "移动端每段控制在 1-3 句，长解释拆成列表或小标题。"})
    if not re.search(r"例如|比如|案例|数据|研究|因为|所以|这意味着|换句话说", body):
        findings.append({"level": "major", "issue": "论证偏抽象", "fix": "每个关键判断至少补一个例子、数据、场景或因果解释。"})
    if not re.search(r"总结|最后|行动|清单|建议|下一步|可以这样做", body):
        findings.append({"level": "minor", "issue": "结尾行动感不足", "fix": "结尾给 3 条读者可执行动作或一个判断清单。"})
    return findings


def build_brief(path: Path, profile: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    title = extract_title(metadata, body, path)
    heading_list = headings(body)
    para_list = paragraphs(body)
    selected = choose_profile(" ".join([title, str(metadata), body[:5000]]), profile)
    spec = PROFILES[selected]
    findings = quality_findings(body, para_list, heading_list)
    return {
        "status": "ready",
        "source": str(path.resolve()),
        "title": title,
        "recommended_profile": selected,
        "profile_label": spec["label"],
        "recommended_theme": spec["theme"],
        "reader_promise": reader_promise(title, selected),
        "style_positioning": {
            "best_for": spec["best_for"],
            "opening": spec["opening"],
            "tone": spec["tone"],
            "structure": spec["structure"],
        },
        "copywriting_focus": [
            "只保留一个核心论点，删掉旁支观点。",
            "开头 150 字内说清读者收益、问题或反常识判断。",
            "每个 H2 解决一个读者问题，不写泛泛口号。",
            "用例子、数据、场景或因果链支撑判断。",
            "段落短、句子准、少形容词，避免 AI 腔和空泛励志。",
            "结尾给行动清单、判断标准或可复用框架。",
        ],
        "title_options": title_options(title, selected),
        "suggested_openings": [
            f"{spec['opening']} 这篇文章的读者承诺是：{reader_promise(title, selected)}",
            f"如果只能带走一句话：请先把“{title}”写成一个具体问题，而不是一个宏大概念。",
        ],
        "suggested_outline": spec["structure"],
        "quality_findings": findings,
        "metrics": {
            "source_chars": len(body),
            "paragraphs": len(para_list),
            "headings": len(heading_list),
            "long_paragraphs": sum(1 for paragraph in para_list if len(paragraph) > 260),
        },
    }


def write_markdown_brief(brief: dict[str, Any], output: Path) -> None:
    lines = [
        f"# 写作风格 Brief：{brief['title']}",
        "",
        f"- 推荐风格：{brief['profile_label']} (`{brief['recommended_profile']}`)",
        f"- 推荐排版主题：`{brief['recommended_theme']}`",
        f"- 读者承诺：{brief['reader_promise']}",
        "",
        "## 标题备选",
        *[f"- {item}" for item in brief["title_options"]],
        "",
        "## 改写重点",
        *[f"- {item}" for item in brief["copywriting_focus"]],
        "",
        "## 推荐结构",
        *[f"{index}. {item}" for index, item in enumerate(brief["suggested_outline"], start=1)],
        "",
        "## 需要修正的问题",
    ]
    findings = brief["quality_findings"]
    if findings:
        lines.extend(f"- [{item['level']}] {item['issue']}：{item['fix']}" for item in findings)
    else:
        lines.append("- 暂无明显结构问题，继续压缩表达并增强例证。")
    lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a WeChat article writing style brief.")
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--profile",
        default="auto",
        choices=["auto", *PROFILES.keys()],
        help="Writing profile to force, or auto to infer from the article.",
    )
    parser.add_argument("--output", type=Path, help="Write JSON brief to this path.")
    parser.add_argument("--md-output", type=Path, help="Write a Markdown brief to this path.")
    args = parser.parse_args()

    if not args.input.is_file():
        print(json.dumps({"status": "error", "message": f"Input file not found: {args.input}"}, ensure_ascii=False))
        return 2
    try:
        brief = build_brief(args.input, args.profile)
    except (OSError, UnicodeError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False))
        return 2
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.md_output:
        write_markdown_brief(brief, args.md_output)
    print(json.dumps(brief, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

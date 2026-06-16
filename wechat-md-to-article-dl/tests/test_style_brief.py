from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from style_brief import build_brief, choose_profile  # noqa: E402


class StyleBriefTests(unittest.TestCase):
    def test_choose_profile_detects_business_and_health(self) -> None:
        self.assertEqual("business", choose_profile("商业 增长 战略 风险", "auto"))
        self.assertEqual("health", choose_profile("睡眠 健康 营养 建议", "auto"))

    def test_build_brief_generates_focused_public_article_guidance(self) -> None:
        markdown = """---
title: OPC：AI 时代的个人商业系统
---

# OPC：AI 时代的个人商业系统

很多人都在谈 AI 工具，但真正的问题是商业闭环。

## 为什么不是工具问题

因为没有需求验证，工具越多越容易分散。

## 如何开始

可以先做一个 MVP，用真实反馈验证下一步。
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "article.md"
            source.write_text(markdown, encoding="utf-8")
            brief = build_brief(source, "auto")

        self.assertEqual("business", brief["recommended_profile"])
        self.assertEqual("wealth", brief["recommended_theme"])
        self.assertIn("读完能判断", brief["reader_promise"])
        self.assertGreaterEqual(len(brief["title_options"]), 3)
        self.assertTrue(
            any("开头" in item or "核心" in item for item in brief["copywriting_focus"])
        )

    def test_cli_writes_json_and_markdown_brief(self) -> None:
        markdown = """# 健康冥想与日常恢复

冥想不是万能药，但它能帮助一部分人建立稳定节律。
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "health.md"
            output = root / "brief.json"
            md_output = root / "brief.md"
            source.write_text(markdown, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "style_brief.py"),
                    str(source),
                    "--output",
                    str(output),
                    "--md-output",
                    str(md_output),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            stdout = json.loads(result.stdout)
            saved = json.loads(output.read_text(encoding="utf-8"))
            markdown_brief = md_output.read_text(encoding="utf-8")

        self.assertEqual("health", stdout["recommended_profile"])
        self.assertEqual(stdout["recommended_profile"], saved["recommended_profile"])
        self.assertIn("写作风格 Brief", markdown_brief)
        self.assertIn("读者承诺", markdown_brief)


if __name__ == "__main__":
    unittest.main()

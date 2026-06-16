from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]

try:
    from PIL import Image
except ModuleNotFoundError:
    bundled_python = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    )
    if bundled_python.exists() and Path(sys.executable).resolve() != bundled_python.resolve():
        os.execv(
            str(bundled_python),
            [str(bundled_python), "-m", "unittest", "discover", "-s", str(SKILL_ROOT / "tests")],
        )
    raise


sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from gen_cover import CANVAS_H, CANVAS_W, render  # noqa: E402


class GenCoverTests(unittest.TestCase):
    def test_render_generates_sharp_png_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "cover.png"
            report = root / "cover.json"
            result = render(
                title="AI 时代的 OPC",
                subtitle="一个人如何用最小成本跑通自己的商业闭环",
                tagline="决策者 + AI 工具链 · 可验证需求 · 商业闭环系统",
                label="AI ERA · ONE PERSON COMPANY",
                output=str(output),
                report=str(report),
                template="business",
                align="left",
                no_image=True,
            )

            with Image.open(output) as img:
                size = img.size
                fmt = img.format
            saved = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual("passed", result["status"])
        self.assertEqual((CANVAS_W, CANVAS_H), size)
        self.assertEqual("PNG", fmt)
        self.assertGreaterEqual(saved["render_scale"], 3)
        self.assertGreaterEqual(saved["text_sharpness_score"], 7.0)
        self.assertTrue(saved["safe_zone_left_ok"])
        self.assertTrue(saved["safe_zone_right_ok"])

    def test_long_title_wraps_to_at_most_two_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "long.png"
            result = render(
                title="从零开始构建你的第一个 AI 自动化工作流：完整入门指南",
                subtitle="无需编程基础，利用现成工具组合出高效的自动化系统",
                tagline="自动化 · AI 工具 · 工作流设计",
                label="TUTORIAL · AI",
                output=str(output),
                template="tech",
                align="center",
                no_image=True,
            )

        self.assertEqual("passed", result["status"])
        self.assertLessEqual(result["title_line_count"], 2)
        self.assertGreaterEqual(result["text_sharpness_score"], 7.0)
        self.assertTrue(result["safe_zone_left_ok"])
        self.assertTrue(result["safe_zone_right_ok"])


if __name__ == "__main__":
    unittest.main()

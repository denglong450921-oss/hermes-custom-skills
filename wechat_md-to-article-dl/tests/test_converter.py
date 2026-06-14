from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from convert import convert, infer_theme, parse_frontmatter  # noqa: E402
from official_verify import verify_article_structure  # noqa: E402
from quality import audit_html  # noqa: E402


class ConverterTests(unittest.TestCase):
    def test_frontmatter_uses_safe_yaml(self) -> None:
        metadata, body = parse_frontmatter(
            "---\ntitle: 测试\ntags:\n  - AI\n  - 架构\n---\n正文"
        )
        self.assertEqual("测试", metadata["title"])
        self.assertEqual(["AI", "架构"], metadata["tags"])
        self.assertEqual("正文", body)

    def test_theme_inference_prefers_health_language(self) -> None:
        self.assertEqual("health", infer_theme({}, "儿童健康、运动、睡眠与营养建议"))

    def test_conversion_sanitizes_and_passes_quality_gate(self) -> None:
        markdown = """---
title: 安全测试
summary: 验证危险 HTML 会被清理
type: tech
---

> 核心判断必须清楚。

## 第一部分

正文包含 [危险链接](javascript:alert(1))。

<script>alert(1)</script>

<p onclick="alert(2)" style="color:red">原始段落</p>

## 第二部分

- 清单一
- 清单二
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            output = root / "article.html"
            report = root / "report.json"
            source.write_text(markdown, encoding="utf-8")
            result = convert(
                source,
                output,
                theme_name="auto",
                title=None,
                threshold=90,
                report_path=report,
            )
            html = output.read_text(encoding="utf-8")
            saved_report = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual("passed", result["status"])
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("javascript:", html.lower())
        self.assertNotIn("onclick", html.lower())
        self.assertNotIn("class=", html.lower())
        self.assertNotIn("<style", html.lower())
        self.assertNotIn("font-family", html.lower())
        self.assertTrue(all(score >= 90 for score in saved_report["scores"].values()))

    def test_audit_blocks_loud_fragile_html(self) -> None:
        result = audit_html(
            '<style>.x{display:grid}</style><script>x()</script>'
            '<section class="x" style="padding:2px;background:linear-gradient(red,blue)">'
            '<h1 style="font-size:42px">Title</h1><p style="font-size:11px;line-height:1.1;'
            'color:#000">Body</p></section>'
        )
        self.assertEqual("blocked", result["status"])
        self.assertIn("wechat_compatibility", result["failed_dimensions"])
        self.assertIn("readability", result["failed_dimensions"])

    def test_audit_blocks_official_editor_spec_violations(self) -> None:
        nested = "<section>" * 16 + "deep" + "</section>" * 16
        content = (
            '<section style="width:640px;height:80px;line-height:0;'
            'text-align:start;position:absolute;transform:translateX(2px);'
            'font-family:Arial!important">'
            '<h1 style="font-size:26px">Title</h1>'
            '<pre style="font-size:16px">ordinary paragraph</pre>'
            f"{nested}</section>"
        )
        result = audit_html(content)
        failed_checks = {
            check["name"] for check in result["checks"] if not check["passed"]
        }
        self.assertEqual("blocked", result["status"])
        self.assertTrue(
            {
                "no_fixed_dimensions",
                "positive_line_height",
                "portable_text_alignment",
                "no_pre_elements",
                "same_tag_nesting_limit",
                "platform_default_font",
                "dark_mode_safe_css",
            }
            <= failed_checks
        )

    def test_official_verifier_posts_json_and_normalizes_violations(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps(
                    {
                        "isValid": False,
                        "inValidInfo": {
                            "width": {
                                "violateRules": "Fixed width is not responsive.",
                                "items": [
                                    {
                                        "outerHTML": (
                                            '<section style="width:640px">x</section>'
                                        )
                                    }
                                ],
                            }
                        },
                    }
                ).encode()

        with patch("official_verify.urlopen", return_value=FakeResponse()) as mocked:
            result = verify_article_structure("<section>test</section>")

        self.assertEqual("blocked", result["status"])
        self.assertFalse(result["is_valid"])
        self.assertEqual(1, result["violation_count"])
        self.assertEqual("width", result["violations"][0]["rule"])
        self.assertEqual(
            '<section style="width:640px">x</section>',
            result["violations"][0]["items"][0]["outer_html"],
        )
        request = mocked.call_args.args[0]
        self.assertEqual("POST", request.method)
        self.assertEqual("application/json", request.headers["Content-type"])
        self.assertEqual(
            {"content": "<section>test</section>"},
            json.loads(request.data.decode("utf-8")),
        )

    def test_dark_mode_audit_distinguishes_decorative_and_text_gradients(self) -> None:
        decorative = audit_html(
            '<section style="max-width:680px;padding:18px;background:#fff">'
            '<h1 style="font-size:26px;color:#111827">Title</h1>'
            '<p style="font-size:16px;line-height:1.82;color:#374151">Body</p>'
            '<section style="background-image:linear-gradient(#fff,#ddd)"><br></section>'
            "</section>"
        )
        text_gradient = audit_html(
            '<section style="max-width:680px;padding:18px;background:#fff">'
            '<h1 style="font-size:26px;color:#111827">Title</h1>'
            '<p style="font-size:16px;line-height:1.82;color:#374151;'
            'background-image:linear-gradient(#fff,#ddd)">Body</p>'
            "</section>"
        )
        decorative_checks = {
            check["name"]: check["passed"] for check in decorative["checks"]
        }
        text_checks = {
            check["name"]: check["passed"] for check in text_gradient["checks"]
        }
        self.assertTrue(decorative_checks["no_text_over_gradients"])
        self.assertFalse(text_checks["no_text_over_gradients"])

    def test_dark_mode_audit_flags_scoped_opt_out_and_fixed_svg_colors(self) -> None:
        result = audit_html(
            '<section style="max-width:680px;padding:18px;background:#fff">'
            '<h1 style="font-size:26px;color:#111827">Title</h1>'
            '<p style="font-size:16px;line-height:1.82;color:#374151">Body</p>'
            '<ul data-no-dark style="color:#111827">'
            '<li style="color:#000">Styled descendant still converts</li></ul>'
            '<svg viewBox="0 0 10 10"><path fill="black" d="M0 0h10v10z"></path></svg>'
            "</section>"
        )
        failed_checks = {
            check["name"] for check in result["checks"] if not check["passed"]
        }
        self.assertIn("data_no_dark_scope", failed_checks)
        self.assertIn("svg_uses_adaptive_color", failed_checks)

    def test_dark_mode_audit_flags_severely_low_text_contrast(self) -> None:
        result = audit_html(
            '<section style="max-width:680px;padding:18px;background:#fff">'
            '<h1 style="font-size:26px;color:#111827">Title</h1>'
            '<p style="font-size:16px;line-height:1.82;color:#494429;'
            'background-color:#c22b4c">Low contrast body</p>'
            "</section>"
        )
        failed_checks = {
            check["name"] for check in result["checks"] if not check["passed"]
        }
        self.assertIn("moderate_text_contrast", failed_checks)

    def test_audit_uses_prose_container_when_decorative_section_follows(self) -> None:
        result = audit_html(
            '<section style="max-width:680px;padding:18px;background:#fff">'
            '<h1 style="font-size:26px;color:#111827">Title</h1>'
            '<section><p style="font-size:16px;line-height:1.82;color:#374151">'
            "Readable body</p></section>"
            '<section style="background-image:linear-gradient(#fff,#ddd)">'
            "<br></section></section>"
        )
        checks = {check["name"]: check["passed"] for check in result["checks"]}
        self.assertTrue(checks["comfortable_line_height"])
        self.assertTrue(checks["soft_text_contrast"])

    def test_image_content_is_reported_for_manual_dark_mode_review(self) -> None:
        result = audit_html(
            '<section style="max-width:680px;padding:18px;background:#fff">'
            '<h1 style="font-size:26px;color:#111827">Title</h1>'
            '<p style="font-size:16px;line-height:1.82;color:#374151">Body</p>'
            '<img src="https://example.com/text.png" alt="A text diagram" '
            'style="width:100%;height:auto">'
            "</section>"
        )
        self.assertTrue(result["manual_review"])
        self.assertIn("transparent", " ".join(result["manual_review"]).lower())

    def test_fenced_code_uses_wrapping_section_instead_of_pre(self) -> None:
        markdown = """---
title: 代码兼容性
type: tech
---

## 示例

下面的代码演示移动端长行自动换行。

```python
print("a very long line that should wrap on a narrow mobile screen")
```
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "article.md"
            output = root / "article.html"
            source.write_text(markdown, encoding="utf-8")
            result = convert(
                source,
                output,
                theme_name="auto",
                title=None,
                threshold=90,
                report_path=root / "report.json",
            )
            content = output.read_text(encoding="utf-8")

        self.assertEqual("passed", result["status"])
        self.assertNotIn("<pre", content.lower())
        self.assertIn("<code", content.lower())
        self.assertIn("white-space:pre-wrap", content.lower())


if __name__ == "__main__":
    unittest.main()

# WeChat 发布完整工作流

此用户（dennon）的标准发布流程：写文 → 转HTML → 封面 → 推草稿箱。

## 流程

```
Step 1: 写文 ── dennon-perspective skill
         → ~/Downloads/<标题20字>.md 自动保存并打开

Step 2: 转WeChat HTML ── wechat_md-to-article-dl skill
         → python3 <skill>/scripts/convert.py <input.md> --output /tmp/<name>.html --theme cognition
         → open /tmp/<name>.html

Step 3: 生成封面 ── wechat-cover-generator-dl + wechat_article_cover_image_gen
         → python3 <fetch>/scripts/fetch_image.py --query "<3-5 English keywords>" --min-width 800
         → python3 <gen_cover>/scripts/gen_cover.py \
             --title "<短标题>" \
             --image-url "<from fetch>" \
             --output /tmp/<name>-cover.png
         → open /tmp/<name>-cover.png

Step 4: 推草稿箱 ── wechat_article_push_dl skill
         → cd ~/Documents （.env 文件在此目录）
         → md2wechat --html /tmp/<name>.html --title "<标题>" --author "dennon" --style academic_gray --cover /tmp/<name>-cover.png
```

## 关键路径

| 文件 | 路径 |
|------|------|
| .env 凭证 | `~/Documents/.env` |
| 封面脚本（主目录） | `~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py` |
| 封面脚本（冲突副本） | `~/.hermes/skills/dennon-perspective/wechat_article_cover_image_gen/scripts/gen_cover.py` |
| 图片获取脚本（主目录） | `~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py` |
| WeChat转换器 | `~/.hermes/skills/wechat_md-to-article-dl/scripts/convert.py` |

## 陷阱

- **凭证目录**：`md2wechat` 的 `.env` 必须在当前工作目录，不是 home。`cd ~/Documents` 后再执行。
- **封面标题截断**：900×383 封面最多容纳约20字（分两行）。超长标题必须在 `--title` 参数中手动缩短，完整标题写在文章正文中。
- **图片获取**：`fetch_image.py` 输出 JSON 到 stdout，不写文件。从 stdout 提取 `image_url` 字段作为 `--image-url` 的值。
- **封面脚本路径冲突**：`gen_cover.py` 存在于两个路径（主目录 + dennon-perspective 子目录）。优先使用主目录版本。

## 质量门

| 门 | 通过条件 |
|----|---------|
| WeChat HTML | 5项评分均 ≥ 90 |
| 封面 | 900×383, 标题无截断, Safe zone ≥ 60px, Sharpness ≥ 7.0 |
| 推稿 | `"success": true` + `media_id` |

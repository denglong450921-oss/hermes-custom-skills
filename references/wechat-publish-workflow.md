# WeChat 发布完整工作流

dennon 的标准发布流程：写文 → 转HTML → 封面 → 推草稿箱。每个步骤由独立 skill 执行，本文件记录端到端路径和实践中发现的陷阱。

## 流程

```
Step 1: 写文 ── dennon-perspective（本 skill）
         ↓  ~/Downloads/<标题前20字>.md 自动保存并打开

Step 2: 转WeChat HTML ── wechat_md-to-article-dl
         ↓  /tmp/<name>.html

Step 3: 生成封面 ── wechat-cover-generator-dl + wechat_article_cover_image_gen
         ↓  /tmp/<name>-cover.png

Step 4: 推草稿箱 ── wechat_article_push_dl（cd ~/Documents 后执行）
```

## 各步骤命令

### Step 1: 写文
由 dennon-perspective 的写作助手模式自动执行。完成后：
```bash
# 自动完成（skill 内部逻辑）
open ~/Downloads/<标题前20字>.md
```

### Step 2: 转 WeChat HTML
```bash
python3 ~/.hermes/skills/wechat_md-to-article-dl/scripts/convert.py \
  "~/Downloads/<input.md>" \
  --output /tmp/<name>.wechat.html \
  --theme cognition \
  --title "<完整标题>"
open /tmp/<name>.wechat.html
```

### Step 3: 生成封面
```bash
# 3a. 取图
python3 ~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py \
  --query "<3-5 English keywords>" --min-width 800
# 从 stdout JSON 提取 image_url

# 3b. 渲染（优先主目录脚本，避免子目录冲突版本）
python3 ~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py \
  --title "<短标题（≤20字）>" \
  --subtitle "<副标题>" \
  --image-url "<from fetch>" \
  --output /tmp/<name>-cover.png
open /tmp/<name>-cover.png
```

### Step 4: 推草稿箱
```bash
cd ~/Documents       # ← 必须：md2wechat 从 CWD 读取 .env
md2wechat --html /tmp/<name>.wechat.html \
  --title "<标题>" \
  --author "dennon" \
  --style academic_gray \
  --cover /tmp/<name>-cover.png
```

🔴 **推送前必须展示完整命令让用户确认**，不可静默执行。

## 关键文件路径

| 文件 | 路径 |
|------|------|
| .env 凭证 | `~/Documents/.env` |
| 封面渲染脚本（主目录，优先） | `~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py` |
| 封面脚本（冲突副本） | `~/.hermes/skills/dennon-perspective/wechat_article_cover_image_gen/scripts/gen_cover.py` |
| 图片获取脚本 | `~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py` |
| WeChat转换器 | `~/.hermes/skills/wechat_md-to-article-dl/scripts/convert.py` |

## 陷阱

| 陷阱 | 表现 | 修复 |
|------|------|------|
| 凭证目录错误 | `40164` / 认证失败 | `cd ~/Documents`（.env 所在目录）后再执行 md2wechat |
| 封面标题截断 | 标题只显示一半 | 900×383 最多容纳 ~20字。超长标题在 `--title` 参数中手动缩短，完整标题写在文章正文中 |
| 图片获取输出位置 | fetch_image.py 输出 JSON 到 stdout，不写文件 | 从 stdout 解析 `image_url`，不假设文件路径 |
| 封面脚本路径冲突 | gen_cover.py 在两个路径都存在 | 优先使用主目录版本：`~/.hermes/skills/wechat_article_cover_image_gen/` |
| 文章文件名含Unicode引号 | `" "` 导致 Python 找不到文件 | 先用 shell glob 复制到 `/tmp/` 的 ASCII 名文件，再转换 |
| HTML 来源选择 | 推文时用 `--html` 还是 `--markdown` | 已由 wechat_md-to-article-dl 转换的 HTML（inline CSS only）用 `--html`；原始 Markdown 用 `--markdown`（MD2WeChat 自动生成兼容 CSS） |
| 章节密度失控 | 文章被过度裁剪失去深度 | 遵循「深度保留」原则：保留案例、类比展开、分步推导、背景说明 |
| 多个skill衔接中断 | 上一个步骤的产出文件找不到 | 步骤间传递明确的绝对路径，不依赖假设的临时目录状态 |

## 质量门

| 门 | 通过条件 | 验证方式 |
|----|---------|---------|
| WeChat HTML | 5项评分均 ≥ 90 | 读取 convert.py 输出的 report JSON |
| 封面 | 900×383, 标题无截断, Safe zone ≥ 60px, Sharpness ≥ 7.0 | gen_cover.py 输出的 TDD Checklist |
| 推稿 | `"success": true` + `media_id` | md2wechat 输出的 JSON 中的 `data.media_id` |

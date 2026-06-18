# WeChat 发布完整工作流

dennon 的标准发布流程：写文 → 转HTML → 封面 → 推草稿箱。每个步骤由独立 skill 执行，本文件记录端到端路径和实践中发现的陷阱。

## 流程

```
Step 0: 视频转写（可选──当素材是视频时）── video-transcribe
         ↓  转录文本保存到 ~/Downloads/<name>_transcript.md

Step 0.5: Auto Article 裁剪件处理（可选──用户提供 vault 裁剪件路径时）
         ↓  dennon-perspective Step 2 自动处理：
            剥离 AI 元框架 → 保留学术素材和实验数据 → 按破→立→重构→收束重建

Step 1: 写文 ── dennon-perspective（本 skill）
         ↓  ~/Downloads/<标题前20字>.md 自动保存并打开

Step 2: 转WeChat HTML ── wechat_md-to-article-dl
         ↓  /tmp/<name>.html

Step 3: 生成封面 ── wechat-cover-generator-dl + wechat_article_cover_image_gen
         ↓  /tmp/<name>-cover.png

Step 4: 推草稿箱 ── wechat_article_push_dl（cd ~/Documents 后执行）
```

**典型工作流**（本 session 重复 3 次的模式）：
```
用户提供 .mp4 路径
  → video-transcribe 转写
  → 用户提供 vault 裁剪件路径 (Clippings/Auto Article/)
  → dennon-perspective 按破→立→重构→收束写文
  → wechat_md-to-article-dl 转 WeChat HTML
  → wechat-cover-generator-dl 生成封面
  → wechat_article_push_dl 推草稿箱
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
# 3a. 取图（Picsum 图片无 Unsplash ID，无需检查 used-images.txt）
python3 ~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py \
  --query "<3-5 English keywords>" --min-width 800
# 从 stdout JSON 提取 image_url

# 3b. 渲染
python3 ~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py \
  --title "<短标题（≤20字，如"努力通货膨胀"）>" \
  --subtitle "<副标题（长句后半段）>" \
  --image-url "<from fetch>" \
  --template auto \
  --align center \
  --output "~/Downloads/<短文件名>-cover.png"
open "~/Downloads/<短文件名>-cover.png"
```

### Step 4: 推草稿箱
```bash
cd ~/Documents       # ← 必须：md2wechat 从 CWD 读取 .env
md2wechat --html /tmp/<name>.wechat.html \
  --author "dennon" \
  --cover ~/Downloads/<短文件名>-cover.png
```
- 不需要 `--style`：HTML 已由 wechat_md-to-article-dl 内联样式预处理，加 `--style` 会重复叠加
- 不需要 `--title`：HTML 中已有完整 H1 标题，md2wechat 自动提取

🔴 **推送前必须展示完整命令让用户确认**，不可静默执行。

## 关键文件路径

| 文件 | 路径 |
|------|------|
| .env 凭证 | `~/Documents/.env` |
| 封面渲染脚本 | `~/.hermes/skills/wechat_article_cover_image_gen/scripts/gen_cover.py` |
| 图片获取脚本 | `~/.hermes/skills/open-source-image-fetch-dl/scripts/fetch_image.py` |
| WeChat转换器 | `~/.hermes/skills/wechat_md-to-article-dl/scripts/convert.py` |

## 陷阱

| 陷阱 | 表现 | 修复 |
|------|------|------|
| 凭证目录错误 | `40164` / 认证失败 | `cd ~/Documents`（.env 所在目录）后再执行 md2wechat |
| 封面标题截断 | 标题只显示一半 | 900×383 最多容纳 ~20字。超长标题在 `--title` 参数中手动缩短，完整标题写在文章正文中 |
| 图片获取输出位置 | fetch_image.py 输出 JSON 到 stdout，不写文件 | 从 stdout 解析 `image_url`，不假设文件路径 |
| 文章文件名含Unicode引号 | `" "` 导致 Python 找不到文件 | 先用 shell glob 复制到 `/tmp/` 的 ASCII 名文件，再转换 |
| HTML 来源选择 | 推文时用 `--html` 还是 `--markdown` | 已由 wechat_md-to-article-dl 转换的 HTML（inline CSS only）用 `--html`；原始 Markdown 用 `--markdown`（MD2WeChat 自动生成兼容 CSS） |
| 重复叠加 `--style` | 推文后格式异常 | HTML 已内联样式预处理时，不加 `--style` |
| 图片来源追踪 | 重复使用同一张 Picsum 图片 | Picsum 图片（fastly.picsum.photos）无 Unsplash ID，不写入 used-images.txt，无需检查 |
| 封面输出路径 | 用户找不到封面 | 封面从 `/tmp/` 复制到 `~/Downloads/` 并用 `open` 展示 |

## 质量门

| 门 | 通过条件 | 验证方式 |
|----|---------|---------|
| WeChat HTML | 5项评分均 ≥ 90 | 读取 convert.py 输出的 report JSON |
| 封面 | 900×383, 标题无截断, Safe zone ≥ 60px, Sharpness ≥ 7.0 | gen_cover.py 输出的 TDD Checklist |
| 推稿 | `"success": true` + `media_id` | md2wechat 输出的 JSON 中的 `data.media_id` |

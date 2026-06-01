# 抖音博主数据采集 — 原子化 + 编排实战案例

> 这个案例来自用户 real-world 分享：输入一个抖音博主主页链接，agent 自动采集全部作品数据、内容分析、打标签、出报告。

## 流程概述

输入：抖音博主主页 URL + "采集他的所有作品"
输出：数据库表（每作品一行，含元数据）+ 本地原文件 + 转写文稿

## 原子 Skill 清单

| Skill | 职责 | 是否通用 |
|-------|------|---------|
| `health-check` | 检查远程 Windows 连接、CUDA 可用性、依赖完整性 | 通用 |
| `parse-author` | 解析抖音博主主页，提取概况信息 | 平台特定 |
| `collect-works` | 采集全部历史作品（基础数据 + 音视频/封面原文件） | 平台特定 |
| `image-ocr` | 图文作品 → 图片理解 → 提取文字 | 通用 |
| `audio-transcribe` | 视频作品 → 抽取音频 → 转写文字 | 通用 |
| `remote-cuda-transcribe` | 远程 Windows GPU CUDA 加速转写（Whisper） | 通用 |
| `llm-polish` | Whisper 转写后大模型润色（纠正专业术语） | 通用 |
| `gen-author-tags` | 基于全部作品内容归纳作者级别标签（需用户协商确认） | 通用 |
| `tag-works` | 为每一条作品打对应标签 | 通用 |
| `generate-report` | 汇总所有数据输出总结报告（数据库表 + 本地文件） | 通用 |

## 编排 Skill（orchestrator）

编排 skill 的 SKILL.md 只包含以下内容结构：

### 步骤 0: 健康检查
调用 `health-check` → 确认 Windows 可达、CUDA 就绪、依赖完整。

### 步骤 1: 解析作者
调用 `parse-author` → 输入 `{url: "..."}` → 输出 `{author_name, author_id, ...}`。

### 步骤 2: 采集作品
调用 `collect-works` → 输入 `{author_id, count}` → 输出 `[{work_id, type, url, ...}]`。

### 步骤 3: 条件分支（作品处理）
- 若作品类型为 "image" → 调用 `image-ocr`
- 若作品类型为 "video" → 调用 `audio-transcribe`（经 `remote-cuda-transcribe` 推送到 Windows GPU 转写）→ 调用 `llm-polish`

### 步骤 4: 标签归纳
调用 `gen-author-tags` → 输入全部作品内容 → 输出标签列表 → **暂停等待用户确认**。

### 步骤 5: 逐条打标
调用 `tag-works` → 输入 `{works: [...], tags: [...]}` → 输出标注完成的作品列表。

### 步骤 6: 输出报告
调用 `generate-report` → 输入全部数据 → 输出数据库表 + 本地文件。

## 关键设计特征

1. **编排 skill 不含任何业务逻辑** — 只声明步骤顺序、条件分支、数据流向
2. **10 个原子 skill 中 8 个是通用能力** — 换平台（小红书/B站/视频号）只需改 2 个平台特定 skill + 新编排
3. **用户交互点明确标注** — 第 4 步标签归纳后需用户协商确认
4. **原子 skill 可独立测试** — 每个 skill 几分钟就能验证一个环节

## 复用矩阵

| 平台 | 需新建的 skill | 可直接复用 |
|------|---------------|-----------|
| 抖音 | `parse-author` (抖音), `collect-works` (抖音) | OCR、转写、润色、打标、报告、健康检查 |
| 小红书 | `parse-author` (小红书), `collect-works` (小红书) | 同上 |
| B站 | `parse-author` (B站), `collect-works` (B站) | 同上 |
| 视频号 | `parse-author` (视频号), `collect-works` (视频号) | 同上 |

## 运行表现

一次完整运行（约 50-100 条作品）：
- 全自动执行，无需人工干预（除标签确认）
- 最终产出两个交付物：
  1. 数据库表 — 每条作品一行：标题、正文、标签、发布时间、互动数据、原文件路径
  2. 本地文件夹 — 每个作品的音视频文件、封面图、转写文稿

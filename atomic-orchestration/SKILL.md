---
name: atomic-orchestration
description: >
  Use when designing or refactoring multi-step agent workflows. This skill teaches the "atomic + orchestration" pattern: break complex workflows into small, single-responsibility atomic skills, then chain them with a lightweight orchestration skill that has no business logic — only a step sequence. Trigger on: "设计工作流", "编排skill", "原子化", "拆skill", "multi-step workflow", "orchestrate", "workflow design", "pipeline", "chain skills", "workflow refactor", "reusable workflow", "将工作流拆分为skill". Prefer this skill whenever the user describes a multi-step data pipeline, content processing pipeline, or any task that involves 3+ sequential operations that could be independently maintained.
compatibility:
  - hermes-agent
---

# Atomic + Orchestration Skill Design

> **核心思想**：把复杂工作流拆成多个"原子 skill"（每个只做一件事），再用一个"编排 skill"（只有流程声明，没有业务逻辑）把它们串起来。

## Why This Works

| 问题 | 原子化 + 编排的解法 |
|------|-------------------|
| 长链条工作流一次性写通很难 | 每个原子 skill 只需几分钟验证，逐个击破 |
| 改一个环节怕破坏整条链路 | 只改出问题的那个原子 skill，编排不动 |
| 换个平台要重写大部分逻辑 | 通用能力（OCR/转写/打标）复用，只写新编排 |

## When to Use

**适合场景** — 具备以下 2+ 特征的工作流：
- 有 3 个以上可独立测试的步骤
- 涉及不同类型的处理（如解析 → 采集 → 转写 → 分析 → 输出）
- 需要支持多个平台/数据源的变体（抖音、小红书、B 站等）
- 未来可能需要单独优化或替换某个环节
- 多个工作流共享部分能力（OCR、转写、打标签）

**不适合场景**：
- 2-3 步的简单线性操作（直接写一个 skill 就够了）
- 不可拆分的原子操作（如"读取文件并返回内容"）
- 一次性脚本（用完即弃的临时任务）

## Workflow Design Process

### Step 1: 识别步骤（任务分解）

拿到用户需求后，先画出完整流程。把所有操作列出来，不要考虑"这是不是一个 skill"——先列动作。

> 例：采集抖音博主数据
> 1. 检查远程连接和依赖
> 2. 解析博主主页信息
> 3. 采集所有历史作品（数据 + 原文件）
> 4. 判断作品类型
> 5. 图文 → OCR 提取文字
> 6. 视频 → 抽取音频 → 转写文字 → LLM 润色
> 7. 归纳内容标签
> 8. 每条作品打标
> 9. 输出汇总报告

### Step 2: 界定边界（聚合为原子 skill）

把相邻的、逻辑上必须在一起的步骤合并，形成原子 skill。判断标准：

✅ **原子 skill 的黄金法则**：
- 只有一个职责（Single Responsibility）
- 输入输出清晰可预期
- 可以独立测试和验证
- 不依赖上下游的具体实现（只依赖输入格式）

> 上例的原子 skill 划分：
> - `health-check` — 第 1 步
> - `parse-author` — 第 2 步
> - `collect-works` — 第 3 步
> - `image-ocr` — 第 5 步（只判断图文）
> - `audio-transcribe` — 第 6 步中的音频抽取 + 转写
> - `llm-polish` — 第 6 步中的润色（可拆分是因为可能选用不同模型/策略）
> - `gen-author-tags` — 第 8 步中的标签归纳
> - `tag-works` — 第 8 步中的逐条打标
> - `generate-report` — 第 9 步

### Step 3: 识别通用能力（标记跨平台复用）

找出跟具体平台无关的 skill。这些以后做新平台可以直接复用：

| 通用（平台无关） | 平台特定 |
|----------------|---------|
| OCR 图片文字提取 | 抖音作者解析 |
| 音频转写（Whisper） | 抖音作品采集 |
| LLM 润色 | B 站作者解析 |
| 内容打标签 | 小红书作品采集 |
| 汇总报告生成 | |

### Step 4: 编排 skill 设计

编排 skill 的唯一职责是声明"按什么顺序执行哪些步骤"。它**不包含任何业务逻辑**。

编排 skill 的结构：
```
## 工作流
1. [原子 skill A] → 输入 X → 输出 Y
2. [原子 skill B] → 输入 Y → 输出 Z
3. [原子 skill C] → 输入 Z → 输出 W
...
N. [汇总报告]
```

编排 skill 可以做条件分支（if/else 根据作品类型走不同路径），但分支逻辑也只描述"什么条件下调用哪个 skill"，不重复 skill 内部的细节。

## Atomic Skill Template

每个原子 skill 的 SKILL.md 应该包含：

```markdown
---
name: my-atomic-skill
description: 一句话说明这个 skill 的唯一职责
---

# My Atomic Skill

## Input
期望的输入格式说明（如：JSON 对象 / 文件路径 / 文本片段）

示例：
```json
{
  "author_id": "douyin_12345678",
  "max_works": 50,
  "include_media": true
}
```

## Process
具体的执行步骤。必须包含：工具调用、参数、判定条件。

示例：
1. 用浏览器工具访问 `https://www.douyin.com/user/{author_id}`
2. 解析页面 JSON-LD 数据提取作者名、粉丝数、签名文案
3. 如果粉丝数页面上不可见，改用移动端 API 兜底
4. 输出结构化的 author_info JSON

## Output
明确的输出格式说明（如：JSON / 文件 / 打印结果）。下游 skill 依赖这个格式。

示例：
```json
{
  "author_name": "张三",
  "follower_count": 125000,
  "signature": "分享日常...",
  "avatar_url": "https://...",
  "collected_at": "2026-06-01T09:00:00Z"
}
```
```

## Orchestration Skill Template

```markdown
---
name: my-workflow-orchestrator
description: 编排 [平台/业务] 的完整工作流。按顺序调用原子 skill 完成数据采集、处理、分析、输出。
---

# [平台/业务名] 工作流编排

## 解析指令
从用户输入中提取：
- 目标 URL / 用户名
- 需要采集的数量

## 工作流步骤

### Step 0: 环境检查
调用 `health-check` 确认依赖环境就绪。
→ 输入: 无
→ 输出: 检查结果

### Step 1: [原子 skill A]
调用 `parse-author` 获取概况。
→ 输入: {url: "..."}
→ 输出: {author_name, author_id, ...}

### Step 2: [原子 skill B]
调用 `collect-works` 采集作品。
→ 输入: {author_id, count}
→ 输出: [{work_id, type, url, ...}]

### Step 3: 条件分支
- 若作品类型为 "image" → 调用 `image-ocr`
- 若作品类型为 "video" → 调用 `audio-transcribe` → `llm-polish`

🔴 CHECKPOINT: 确认所有作品处理完毕后再进入打标阶段。

### Step 4: [原子 skill C]
调用 `gen-author-tags` 归纳标签。
→ 输入: 全部作品内容
→ 输出: [tag1, tag2, ...]

🛑 STOP: 此步骤必须等待用户协商确认标签后再继续。如果用户长时间不确认（5分钟后自动采用 AI 建议标签）。

### Step 5: [原子 skill D]
调用 `tag-works` 逐条打标。
→ 输入: {works: [...], tags: [...]}
→ 输出: 标注完成的作品列表

### Step 6: 输出报告
调用 `generate-report` 汇总。
→ 输入: 全部数据
→ 输出: 报告（文件 / 数据库 / 控制台）
```

## 编排 skill 的关键原则

- ⚠️ **不写业务逻辑** — 每一行都应该是"调用哪个 skill"，不是"怎么做"
- ✅ **明确输入输出契约** — 每一步注明输入来自上一步的什么输出
- ✅ **条件分支只描述路由** — "如果 A 则调用 skill X，如果 B 则调用 skill Y"
- ✅ **用户交互点要标注** — 哪些步骤需要用户确认/协商（用 🔴 CHECKPOINT 标记）
- 🛑 **强制停止点** — 涉及用户决策（如标签协商、数据审核）的步骤前加 🛑 STOP，等待人工确认再继续
- ✅ **可独立跳转** — 编排 skill 应支持指定从某一步开始（断点续跑）

## Pitfalls / Anti-Patterns

| 错误做法 | 为什么 | 正确做法 |
|---------|--------|---------|
| 编排 skill 里写业务逻辑 | 改流程时必须同时改编排和原子 skill，失去分离意义 | 编排只声明步骤顺序和调用关系 |
| 原子 skill 太大 | 测试、调试、复用的粒度都变差 | 坚持单一职责，一个 skill 只做一个事 |
| 原子 skill 之间紧耦合 | 改一个影响另一个，复用困难 | 通过明确的输入/输出契约解耦 |
| 不定义输入输出格式 | 下游 skill 不知道期望什么数据 | 每个原子 skill 顶部标注 Input/Output |
| 把配置硬编码在 skill 里 | 换平台要改 skill 内部 | 配置由编排传入，原子 skill 只关心处理逻辑 |
| 编排不处理任何失败 | 一步失败整个流程中断，无降级方案 | 每个步骤预配 fallback（见 Failure Recovery 章节） |
| 原子 skill 内部隐式调用其他 skill | 产生不可见的隐式依赖链，破坏编排的可观测性 | 原子 skill 只做自己的事，跨 skill 调用都在编排层声明 |
| 缺少中间输出检查 | 跑到最后才发现某一步产出不对，返工成本高 | 关键步骤后加 🔴 CHECKPOINT 检查输出质量再继续 |

## Failure Recovery（运行时失败处理）

编排工作流时，每个步骤都可能失败。必须在编排 skill 中为每一步预定义 fallback 路径，而不是 error 一路冒泡到顶。

### 三段式 Fallback 表

| 步骤 | 触发条件 | 一线修复 | 仍失败兜底 |
|------|---------|---------|-----------|
| 环境检查 | 远程连接超时 / CUDA 不可用 | 重试 1 次，等待 5 秒 | 跳过 GPU 转写，降级到 CPU whisper（换用 `transcribe-cpu` skill）或提示用户手动检查环境 |
| 作者解析 | HTTP 404 / 页面结构变更 | 换用备用 API endpoint（如从 Web 端 fallback 到移动端接口） | 提示用户提供作者 ID 的另一来源（如搜索后手动复制 ID） |
| 作品采集 | 单条作品抓取失败 | 跳过该条，记录到失败列表，继续下一条 | 全部抓完后再重试失败的，最多 2 轮 |
| 图片 OCR | OCR 返回空/置信度 < 0.6 | 调大图片分辨率重新 OCR | 标记为"OCR 失败"，保留原始图片路径供人工审查 |
| 音频转写 | Whisper 转写出错 | 检查音频文件是否损坏，尝试 ffmpeg 修复 | 标记为"转写失败"，保留原始音频路径 |
| LLM 润色 | API 调用超时 / 返回空 | 用截断后的文本重试（去掉末段） | 保留 Whisper 原始输出（附注：未润色） |
| 打标签 | 协商标签时用户不确认 | 使用当前 work-in-progress 标签 | 使用默认标签（"未分类"），标记待办 |
| 报告生成 | 数据不完整 | 生成部分报告，标注缺失的数据条目 | 输出原始数据 JSON 兜底，确保结果不丢 |

### 超时与重试策略

- 网络请求类步骤：超时 30 秒，最多重试 2 次，间隔递增（2s, 5s）
- 本地处理类步骤（OCR/转写）：超时 5 分钟，重试 1 次
- LLM 调用类步骤：超时 60 秒，重试 1 次，换备用模型/降 prompt size
- 所有重试耗尽后：执行兜底路径，工作流不中断

## Verification Checklist

产出前逐条检查：

- [ ] 每个原子 skill 是否只做一件事？
- [ ] 编排 skill 是否只包含步骤声明，没有业务逻辑？
- [ ] 每个原子 skill 的输入输出格式是否明确标注？
- [ ] 通用能力是否已被提取为独立 skill？
- [ ] 是否能在不修改原子 skill 的前提下，通过换编排来支持新平台？
- [ ] 所有步骤是否有明确的失败处理策略？
- [ ] 每个步骤是否都有 Fallback 路径（触发条件 → 一线修复 → 兜底）？

## 实例参考

`references/douyin-case-study.md` 中收录了一个完整的抖音博主数据采集工作流案例（来自真实用户分享）。包含：10 个原子 skill 的职责定义、编排 skill 的 7 步流程、跨平台复用矩阵、以及运行表现。如果你正在设计一个新的工作流，可以参考这个案例做对比。

你之前分享的抖音博主数据采集工作流就是这个模式的完整案例。如果你正在设计一个新的工作流，可以参考上述步骤重新走一遍流程。

# Anti-Patterns Checklist: Is Your SKILL.md Well-Structured?

Run every skill through this 8-node anti-pattern gate before publishing. These are the 6 most common structural mistakes.

```
START
  |
  v
[准备编写 / 审查一个 Skill]
  |
  v
+------------------------------------------------+
| 1. 这个 Skill 是否塞了多件不相关的事？          |
|    例：初始化 + 数据处理 + 导出 + 测试全写一起   |
+------------------------------------------------+
  |-- YES --> [反模式 1：大杂烩 Skill]
  |            |
  |            v
  |         [拆分 Skill]
  |            |
  |            +--> [主 Skill：负责串联流程]
  |            +--> [子 Skill A：只负责初始化]
  |            +--> [子 Skill B：只负责数据处理]
  |            +--> [子 Skill C：只负责导出 / 验证]
  |            |
  |            v
  |         [原则：一个 Skill 只管一件事]
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 2. Description 是否写成内部黑话？               |
|    例：description: 处理 TCC 的 v3 迁移          |
+------------------------------------------------+
  |-- YES --> [反模式 2：Description 太黑话]
  |            |
  |            v
  |         [改成通用语言 + 具体技术关键词]
  |            |
  |            v
  |         示例：
  |         ❌ 处理 TCC 的 v3 迁移
  |         ✅ 将旧版支付事务客户端迁移到 v3 API，
  |            替换 import 路径并更新初始化方式
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 3. 是否只有指令，没有示例？                     |
|    例：只写"替换旧路径"，但没给 Before/After     |
+------------------------------------------------+
  |-- YES --> [反模式 3：AI 输出全靠猜]
  |            |
  |            v
  |         [每个关键操作至少补一个 Before/After]
  |            |
  |            v
  |         示例：
  |         Before:
  |           import old/client
  |
  |         After:
  |           import new/client/v3
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 4. 步骤之间是否没有验证点？                     |
|    例：全部做完才测试，中间错了也不知道          |
+------------------------------------------------+
  |-- YES --> [反模式 4：没有中间检查点]
  |            |
  |            v
  |         [在关键步骤之间插入验证命令]
  |            |
  |            +--> [替换 import 后：go vet ./...]
  |            +--> [添加模块后：go build ./...]
  |            +--> [接口改完后：运行核心请求测试]
  |            |
  |            v
  |         [避免最后才发现全白干]
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 5. 判断规则是否写死具体数值？                   |
|    例：文件必须小于 128KB / 超时固定 3 秒        |
+------------------------------------------------+
  |-- YES --> [反模式 5：硬编码数值]
  |            |
  |            v
  |         [改成判断规则 + 参考范围]
  |            |
  |            v
  |         示例：
  |         ❌ 超时时间必须是 3 秒
  |         ✅ 根据接口复杂度设置合理超时，
  |            通常建议 3-10 秒，长任务可单独配置
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 6. SKILL.md 是否像 Wiki？                       |
|    背景 300 行，真正执行方法只有 50 行           |
+------------------------------------------------+
  |-- YES --> [反模式 6：SKILL.md 过度堆背景]
  |            |
  |            v
  |         [拆分文档内容]
  |            |
  |            +--> [SKILL.md：只保留做什么、怎么做]
  |            +--> [references/：放背景、原理、长说明]
  |            +--> [examples/：放 Before/After 示例]
  |            |
  |            v
  |         [让 AI 快速找到执行规则]
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 7. 是否通过反模式检查？                         |
+------------------------------------------------+
  |
  +--> [ ] 不是大杂烩 Skill
  +--> [ ] Description 用通用语言写清楚
  +--> [ ] 关键操作有 Before/After 示例
  +--> [ ] 关键步骤之间有验证点
  +--> [ ] 判断规则没有写死具体数值
  +--> [ ] SKILL.md 没有写成 Wiki
  |
  v
+------------------------------------------------+
| 8. 是否全部通过？                               |
+------------------------------------------------+
  |-- NO --> [返回对应反模式继续修改]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| FINAL: Skill 结构清晰，可以进入测试 / 发布      |
+------------------------------------------------+
```

## Mapping to Darwin Rubric

| Tree Node | Darwin Dim | What it catches |
|-----------|-----------|-----------------|
| 1. 大杂烩 | dim2 (workflow clarity) | Multiple responsibilities in one skill |
| 2. 黑话 | dim1 (frontmatter) | Description too domain-specific |
| 3. 无示例 | dim5 (actionable specificity) | Instructions without Before/After |
| 4. 无验证点 | dim4 (checkpoints) | No verification between steps |
| 5. 硬编码 | dim5 (actionable specificity) | Fixed values instead of ranges |
| 6. Wiki化 | dim7 (architecture) | SKILL.md is a reference doc, not a procedure |

## When to Apply

Run this tree BEFORE harness injection. Fix structural issues first, then add evals. A skill that fails this tree will produce a harness that tests the wrong things.

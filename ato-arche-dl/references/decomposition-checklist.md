# Decomposition Checklist: Is Your Skill Ready?
# 拆分检查清单：你的 Skill 准备好了吗？

Run each sub-skill through this 4-node decision tree before finalizing the workflow design.
在确定工作流设计前，将每个子 Skill 通过这棵 4 节点决策树验证。

```
START
  |
  v
[Prepare to Split Skill / 准备拆分 Skill]
  |
  v
+------------------------------------------------------------------------+
| 1. Does this skill do ONE thing only?                                  |
|    这个 Skill 是否只做一件事？                                           |
|    Principle: Single Responsibility / 原则：单一职责                    |
+------------------------------------------------------------------------+
  |-- NO / 否 --> [Continue splitting / 继续拆分]
  |           |
  |           +--> [Extract initialization as a skill / 把初始化拆成一个 Skill]
  |           +--> [Extract data processing as a skill / 把数据处理拆成一个 Skill]
  |           +--> [Extract generation/export as a skill / 把生成/导出拆成一个 Skill]
  |           |
  |           v
  |        [Each sub-skill has one clear task / 每个子 Skill 只保留一个明确任务]
  |
  |-- YES / 是
        |
        v
+------------------------------------------------------------------------+
| 2. Do sub-skills have dependencies (ordering)?                         |
|    子 Skill 之间是否有先后顺序？                                         |
|    Principle: Explicit Dependencies / 原则：依赖明确                    |
+------------------------------------------------------------------------+
  |-- YES / 有 --> [Document dependency chain / 在文档中写清楚依赖关系]
  |            |
  |            v
  |         [Example / 示例]
  |         ## Prerequisites / 前置条件
  |         Must complete environment init first / 必须先完成环境初始化
  |
  |-- NO / 无 --> [Mark as no strong dependency / 标记为无强依赖]
        |
        v
+------------------------------------------------------------------------+
| 3. Can this sub-skill run independently of the main workflow?          |
|    当前子 Skill 是否依赖主流程才能运行？                                  |
|    Principle: Independent Usability / 原则：可独立使用                   |
+------------------------------------------------------------------------+
  |-- YES (depends on main) / 是（依赖主流程） --> [Add standalone support / 补齐独立运行条件]
  |            |
  |            +--> [Input requirements / 输入要求]
  |            +--> [Execution steps / 运行步骤]
  |            +--> [Output result / 输出结果]
  |            +--> [Failure handling / 失败处理]
  |            |
  |            v
  |         [Make it runnable without the main workflow / 让它脱离主流程也能单独跑]
  |
  |-- NO (independent) / 否（可独立运行）
        |
        v
+------------------------------------------------------------------------+
| 4. Does the sub-skill pass all three split principles?                 |
|    子 Skill 是否满足三条拆分原则？                                       |
|                                                                        |
|    [ ] Single responsibility / 单一职责: one job only / 只管一件事      |
|    [ ] Explicit dependencies / 依赖明确: preconditions + order          |
|        写清楚前置条件和顺序                                             |
|    [ ] Independent usability / 可独立使用: runs without main workflow   |
|        脱离主流程也能运行                                               |
+------------------------------------------------------------------------+
  |-- NO / 否 --> [Return to relevant step / 返回对应步骤继续调整]
  |
  |-- YES / 是
        |
        v
+------------------------------------------------------------------------+
| FINAL: Ready to use as independent sub-skill                           |
| 可以作为独立子 Skill 使用                                              |
+------------------------------------------------------------------------+
```

## Mapping to ato-arche-dl Design Steps / 对应 ato-arche-dl 设计步骤

| Tree Node / 节点 | Maps to / 对应 | What to check / 检查内容 |
|-----------|-------------------|---------------|
| 1. Single Responsibility / 单一职责 | Step 3: Choose atomic boundaries | One clear responsibility, distinct I/O contract |
| 2. Explicit Dependencies / 依赖明确 | Step 5: Define contracts | Preconditions, input source, failure behavior documented |
| 3. Independent Usability / 可独立使用 | Step 4: Classify + Step 8: Verify | Can it be tested without the full workflow? |
| 4. Three Principles / 三条原则 | Step 8: Verify the architecture | All three gates passed / 三个门槛全部通过 |

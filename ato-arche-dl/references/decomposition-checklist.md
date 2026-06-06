# Decomposition Checklist: Is Your Skill Ready?

Run each sub-skill through this 4-node decision tree before finalizing the workflow design.

```
START
  |
  v
[准备拆分 Skill]
  |
  v
+------------------------------------------------+
| 1. 这个 Skill 是否只做一件事？                  |
|    原则：单一职责                               |
+------------------------------------------------+
  |-- NO --> [继续拆分]
  |           |
  |           +--> [把初始化拆成一个 Skill]
  |           +--> [把数据处理拆成一个 Skill]
  |           +--> [把生成/导出拆成一个 Skill]
  |           |
  |           v
  |        [每个子 Skill 只保留一个明确任务]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 2. 子 Skill 之间是否有先后顺序？                |
|    原则：依赖明确                               |
+------------------------------------------------+
  |-- YES --> [在文档中写清楚依赖关系]
  |            |
  |            v
  |         [示例]
  |         ## 前置条件
  |         必须先完成环境初始化
  |
  |-- NO --> [标记为无强依赖]
        |
        v
+------------------------------------------------+
| 3. 当前子 Skill 是否依赖主流程才能运行？        |
|    原则：可独立使用                             |
+------------------------------------------------+
  |-- YES --> [补齐独立运行条件]
  |            |
  |            +--> [输入要求]
  |            +--> [运行步骤]
  |            +--> [输出结果]
  |            +--> [失败处理]
  |            |
  |            v
  |         [让它脱离主流程也能单独跑]
  |
  |-- NO
        |
        v
+------------------------------------------------+
| 4. 子 Skill 是否满足三条拆分原则？              |
|                                                |
|    [ ] 单一职责：只管一件事                    |
|    [ ] 依赖明确：写清楚前置条件和顺序          |
|    [ ] 可独立使用：脱离主流程也能运行          |
+------------------------------------------------+
  |-- NO --> [返回对应步骤继续调整]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| FINAL: 可以作为独立子 Skill 使用               |
+------------------------------------------------+
```

## Mapping to ato-arche-dl Design Steps

| Tree Node | Maps to Design Step | What to check |
|-----------|-------------------|---------------|
| 1. 单一职责 | Step 3: Choose atomic boundaries | One clear responsibility, distinct I/O contract |
| 2. 依赖明确 | Step 5: Define contracts | Preconditions, input source, failure behavior documented |
| 3. 可独立使用 | Step 4: Classify + Step 8: Verify | Can it be tested without the full workflow? |
| 4. 三条原则 | Step 8: Verify the architecture | All three gates passed |

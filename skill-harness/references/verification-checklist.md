# Skill Verification Checklist: Is Your Skill Ready to Ship?

Run every skill through this 11-node verification gate before publishing. Covers functional, build, and runtime validation plus quantitative quality metrics.

```
START
  |
  v
[准备验证一个 Skill]
  |
  v
+------------------------------------------------+
| 1. 这个 Skill 是否有验证清单？                  |
|    原则：每个 Skill 都应该可验证                |
+------------------------------------------------+
  |-- NO --> [先补充验证清单]
  |            |
  |            +--> [功能验证]
  |            +--> [构建验证]
  |            +--> [运行验证]
  |            +--> [度量指标]
  |            |
  |            v
  |         [补齐后再继续]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 2. 功能验证是否通过？                           |
+------------------------------------------------+
  |
  +--> [ ] 所有旧版 import 路径已替换
  +--> [ ] 新版客户端模块已添加
  |
  v
+------------------------------------------------+
| 功能验证是否全部通过？                          |
+------------------------------------------------+
  |-- NO --> [返回修改 Skill 功能逻辑]
  |            |
  |            v
  |         [修复 import / 模块 / 功能缺口]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 3. 构建验证是否通过？                           |
+------------------------------------------------+
  |
  +--> [ ] go vet ./... 无警告
  +--> [ ] go build ./... 正常
  |
  v
+------------------------------------------------+
| 构建验证是否全部通过？                          |
+------------------------------------------------+
  |-- NO --> [返回修复构建问题]
  |            |
  |            +--> [修复 vet 警告]
  |            +--> [修复 build error]
  |            +--> [重新执行构建验证]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 4. 运行验证是否通过？                           |
+------------------------------------------------+
  |
  +--> [ ] 核心接口请求正常
  +--> [ ] 错误处理逻辑正常
  |
  v
+------------------------------------------------+
| 运行验证是否全部通过？                          |
+------------------------------------------------+
  |-- NO --> [返回修复运行问题]
  |            |
  |            +--> [检查接口请求]
  |            +--> [检查异常分支]
  |            +--> [检查错误处理]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 5. 是否有推荐度量指标？                         |
|    用于判断 Skill 是否真的有效                  |
+------------------------------------------------+
  |-- NO --> [补充量化指标]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 6. 触发准确率是否 > 90%？                       |
+------------------------------------------------+
  |-- NO --> [优化触发条件]
  |            |
  |            v
  |         [减少漏触发]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 7. 触发误报率是否 < 5%？                        |
+------------------------------------------------+
  |-- NO --> [收紧触发条件]
  |            |
  |            v
  |         [减少不该触发时误触发]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 8. 输出一致性是否 > 85%？                       |
+------------------------------------------------+
  |-- NO --> [统一输出格式和规则]
  |            |
  |            v
  |         [补充模板 / 示例 / 边界条件]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 9. Token 效率是否比无 Skill 减少 30%+？         |
+------------------------------------------------+
  |-- NO --> [压缩 Skill 内容]
  |            |
  |            +--> [删除冗余说明]
  |            +--> [保留关键规则]
  |            +--> [减少重复示例]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 10. 完成准确率是否 > 80%？                      |
+------------------------------------------------+
  |-- NO --> [优化 Skill 指令和验证逻辑]
  |            |
  |            +--> [补充失败处理]
  |            +--> [补充验收标准]
  |            +--> [补充反例]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| 11. 三层验证 + 指标是否全部达标？               |
+------------------------------------------------+
  |-- NO --> [不要发布]
  |            |
  |            v
  |         [回到失败项继续修正]
  |
  |-- YES
        |
        v
+------------------------------------------------+
| FINAL: Skill 验证通过，可以发布 / 复用          |
+------------------------------------------------+
```

## Mapping to Harness Concepts

| Tree Node | Harness Equivalent | How to Measure |
|-----------|-------------------|----------------|
| 1-4 (functional/build/runtime) | `check_harness.py` REQUIRED tier | Run `python3 scripts/check_harness.py <skill> --json` |
| 5 (metrics) | `evals/evals.json` + `run_harness.py` | Run full harness against test outputs |
| 6 (trigger rate) | Description optimization | Run `python -m scripts.run_loop` from skill-creator |
| 7 (false positive) | Description optimization | Same as above — FP rate from held-out test set |
| 8 (output consistency) | `grader.py` assertion pass rate | Run 3+ harness runs, measure stddev of pass rate |
| 9 (token efficiency) | Baseline comparison | Compare tokens with-skill vs without-skill |
| 10 (completion rate) | FTPR tracking | Run `python3 feedback/ftpr.py` |
| 11 (final gate) | Check all above | Aggregate all metrics before publishing |

## When to Apply

Run this tree after completing harness injection (skill-harness Step 1-4). The harness verifies format — this tree verifies quality. A skill can pass `check_harness.py` (format OK) but fail this tree (effectiveness poor). Both gates are required before publishing.

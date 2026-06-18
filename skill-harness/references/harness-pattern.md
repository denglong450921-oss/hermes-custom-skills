# Harness Pattern Reference

Based on the Agent Harness article by 陈思州 (Datawhale).

## The 5 Modules

```
Task         — 任务输入，评估的内容
Environment  — 可操作环境（文件、配置、工具链）
Tools        — Agent 能使用的工具（API、命令、CSS类）
Trace        — 每一步的记录：工具、参数、结果
Grader       — 结果判断（规则、脚本、断言）
```

## Eval Case Format

```json
{
  "id": "case_001",
  "task": "任务描述，必须具体",
  "environment": {
    "files": {"filename": "content"},
    "tools_available": ["tool1", "tool2"]
  },
  "tools": ["必需使用的工具"],
  "grader": {
    "must_use": ["必须检查的元素"],
    "must_have": ["必须包含的内容"],
    "must_not_have": ["必须避免的错误"]
  }
}
```

## Trace Format

```json
{
  "case_id": "case_001",
  "trace": [
    {"tool": "tool_name", "arguments": {}, "result": "output"}
  ],
  "answer": "最终结果",
  "grade": {
    "success": true,
    "reason": "评分理由"
  }
}
```

## Working Example

The `html-output` skill has a complete harness at `~/.hermes/skills/html-output/evals/`.
Study it when adding harness to a new skill.

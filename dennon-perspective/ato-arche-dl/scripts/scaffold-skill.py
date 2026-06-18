#!/usr/bin/env python3
"""Scaffold an atomic skill or orchestration skill from a template.

Usage:
    python3 scaffold-skill.py atomic --name parse-author --dir ./skills/
    python3 scaffold-skill.py orchestration --name content-collection --dir ./skills/

Creates:
    <dir>/<name>/SKILL.md
    <dir>/<name>/references/   (empty, ready for docs)
    <dir>/<name>/scripts/      (empty, ready for scripts)
"""

import sys
import os
from pathlib import Path


ATOMIC_TEMPLATE = """---
name: {name}
description: >
  {description}
  Use when {trigger_context}.
compatibility: Hermes Agent and Codex-style skill environments.
---

# {name}

## Responsibility

{responsibility}

## Input

```json
{{
  "required_field": "value",
  "optional_field": "value"
}}
```

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `required_field` | string | Yes | - |
| `optional_field` | string | No | "default" |

## Preconditions

- List required tools, credentials, files, or prior state here.

## Process

1. Validate preconditions.
2. Perform the core capability.
3. Validate the result.
4. Return structured output or a documented failure state.

## Output

```json
{{
  "status": "success",
  "result": {{
    "field_1": "value",
    "field_2": "value"
  }}
}}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success", "partial", or "failed" |
| `result` | object | Skill-specific output data |

## Failure Handling

| Signal | Response | Fallback |
|--------|----------|----------|
| `timeout` | Retry 2x with exponential backoff | Return partial result |
| `invalid_input` | Return error immediately | - |
| `network_error` | Retry 3x | Stop and report |

## Verification

- How to confirm the result is usable (schema check, file exists, API responds).

## Contract Version

- v1.0: Initial contract.
"""

ORCHESTRATION_TEMPLATE = """---
name: {name}
description: >
  Orchestrate {workflow_outcome} by routing data through atomic skills.
  Use when {trigger_context}.
compatibility: Hermes Agent and Codex-style skill environments.
---

# {name}

## Inputs

- `input_name`: description of user input

## Workflow

| Step | Invoke | Input source | Output | Next route |
|------|--------|-------------|--------|------------|
| `0` | `health-check` | Runtime context | `health_status` | Continue or stop |
| `1` | `first-skill` | User input | `result_1` | Step 2 |
| `2` | `second-skill` | `result_1` | `result_2` | Step 3 |
| `3` | `final-skill` | `result_2` | Final artifact | Complete |

## Conditional Branches

- If condition A → invoke `skill-a`
- If condition B → invoke `skill-b`
- If neither → invoke `default-skill`

## Recovery

| Step | Failure signal | First response | Final fallback |
|------|---------------|----------------|----------------|
| `1` | `timeout` | Retry | Stop and report |
| `2` | `empty_output` | Use fallback skill | Partial result |
| `3` | `api_error` | Retry with backoff | Manual review |

## Human Review Points

- **Step N**: STOP — wait for user confirmation before proceeding.
  - Input to human: what they review
  - Expected decision: approve / reject / modify

## Resume

Persist these fields for resume capability:

- `run_id`
- `step_status` (per step: pending / completed / failed / partial)
- `completed_items`
- `failed_items`
- `artifact_paths`
- `resume_from` (step name to continue from)

## Cost Budget

| Resource | Limit | On exceeded |
|----------|-------|-------------|
| API calls | 100 | Stop and report |
| Model tokens | 50000 | Switch to cheaper model |
| Wall time | 300s | Partial result |
"""


def scaffold(skill_type: str, name: str, base_dir: str):
    skill_dir = os.path.join(base_dir, name)
    Path(skill_dir).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(skill_dir, "references")).mkdir(exist_ok=True)
    Path(os.path.join(skill_dir, "scripts")).mkdir(exist_ok=True)
    
    skill_path = os.path.join(skill_dir, "SKILL.md")
    
    if os.path.exists(skill_path):
        print(f"Error: {skill_path} already exists. Refusing to overwrite.")
        sys.exit(1)
    
    if skill_type == "atomic":
        content = ATOMIC_TEMPLATE.format(
            name=name,
            description=f"Perform {name.replace('-', ' ')} capability.",
            trigger_context=f"the workflow needs {name.replace('-', ' ')}",
            responsibility=f"One capability: {name.replace('-', ' ')}."
        )
    elif skill_type == "orchestration":
        content = ORCHESTRATION_TEMPLATE.format(
            name=name,
            workflow_outcome=name.replace("-", " "),
            trigger_context=f"the user needs to run the {name.replace('-', ' ')} workflow"
        )
    else:
        print(f"Error: Unknown skill type '{skill_type}'. Use 'atomic' or 'orchestration'.")
        sys.exit(1)
    
    with open(skill_path, "w") as f:
        f.write(content)
    
    print(f"Created: {skill_path}")
    print(f"Created: {skill_dir}/references/")
    print(f"Created: {skill_dir}/scripts/")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_path} — fill in responsibility, input/output contracts, process steps")
    print(f"  2. Add reference docs to {skill_dir}/references/")
    print(f"  3. Add helper scripts to {skill_dir}/scripts/")
    print(f"  4. Test in isolation (see references/testing-procedures.md)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    skill_type = sys.argv[1]
    
    name = None
    base_dir = "."
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--name" and i + 1 < len(sys.argv):
            name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--dir" and i + 1 < len(sys.argv):
            base_dir = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            sys.exit(1)
    
    if not name:
        print("Error: --name is required")
        sys.exit(1)
    
    scaffold(skill_type, name, base_dir)


if __name__ == "__main__":
    main()

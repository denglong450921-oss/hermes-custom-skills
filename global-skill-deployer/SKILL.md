---
name: global-skill-deployer
description: Turn any locally created skill into a globally shared skill with one source of truth plus multi-client symlinks. Use this whenever the user asks to globally install a skill, sync a skill across Trae, Claude Code, Hermes Agent, Cursor, or create a reusable deployment workflow for a custom skill. Trigger on requests like "全局化这个 skill", "把技能软链接到 Hermes", "一处更新到处可用", "install this skill everywhere", or "make this local skill available in all agents".
---

# Global Skill Deployer

Use this skill to standardize a custom skill so it lives in one global registry and can be used across multiple AI clients.

## What This Skill Does

- Moves a local skill into `~/.agents/skills` as the canonical source
- Creates symlinks into `~/.trae/skills`, `~/.trae-cn/skills`, `~/.claude/skills`, `~/.hermes/skills`, and optionally `~/.cursor/skills`
- Optionally creates a runnable CLI wrapper in `~/.local/bin`
- Preserves safety by backing up conflicting directories instead of deleting them
- Supports batch deployment for multiple custom skills
- Generates JSON and Markdown inventory reports so the user can audit global skill health
- Supports `custom-only` reporting so the user sees only self-created skills
- Supports `auto-fix` so the tool can repair missing links, broken links, and detectable wrappers for custom skills
- Supports baseline refresh so the official baseline file can be rebuilt safely over time
- Supports per-skill custom manifests to track deployment metadata for self-created skills

## Inputs To Gather

Collect or infer:

- Skill name
- Optional source directory
- Optional entry script relative path, if the user wants a CLI wrapper
- Optional target IDE groups if the user does not want all defaults

Reasonable defaults:

- Global registry: `~/.agents/skills`
- Link targets: `Trae, Trae CN, Claude Code, Hermes, Cursor`
- CLI wrapper directory: `~/.local/bin`

## Handling Conflicts

Before deploying, check if the skill already exists in the global registry (e.g. `~/.agents/skills/<skill-name>`). If a naming conflict is detected (the target directory exists but is a different skill or differs from the source), **do not assume the action**. 
Instead, use the `AskUserQuestion` tool (or ask the user conversationally) to provide a choice:
1. **Overwrite**: Replace the existing global skill with the new one (`--on-conflict overwrite`).
2. **Keep Both (Rename)**: Keep the existing skill and rename the new one automatically with a suffix like `-local1` (`--on-conflict rename`).
3. **Skip**: Abort deploying this specific skill (`--on-conflict skip`).

Only proceed with the chosen `--on-conflict` argument once the user decides.

## Execution

Run the bundled installer for single-skill deployment:

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/install_global_skill.py \
  --skill-name "<skill-name>" \
  --source-dir "<optional-source-dir>" \
  --entry-script "<optional-relative-script-path>"
```

Examples:

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/install_global_skill.py \
  --skill-name multilingual-video-voice-workflow \
  --entry-script scripts/multilingual_video_workflow.py
```

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/install_global_skill.py \
  --skill-name my-custom-skill \
  --source-dir /Users/name/.trae/skills/my-custom-skill \
  --skip-wrapper
```

For batch deployment and reporting, run:

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/manage_global_skills.py \
  --scan-local-skills
```

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/manage_global_skills.py \
  --skill-names skill-a,skill-b \
  --create-wrappers
```

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/manage_global_skills.py \
  --report-only
```

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/manage_global_skills.py \
  --report-only \
  --custom-only
```

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/manage_global_skills.py \
  --custom-only \
  --auto-fix
```

```bash
python3 /Users/f/.agents/skills/global-skill-deployer/scripts/manage_global_skills.py \
  --refresh-baseline
```

## Safety Rules

- Do not delete an existing non-matching skill directory outright.
- If a link target already contains a different directory or file, back it up with a timestamp suffix before linking.
- If the requested skill is already in the global registry, reuse it and only refresh the symlinks and wrapper as needed.
- In `custom-only` mode, determine custom skills by comparing against `references/official-skills.txt`
- In `auto-fix` mode, only repair custom skills unless the user explicitly asks for a wider repair scope
- In `refresh-baseline` mode, first backfill manifests for currently detected custom skills, then rebuild the official baseline from global skills that do not carry a custom manifest

## Verify After Running

Check these things after the installer finishes:

1. The global source directory exists under `~/.agents/skills/<skill-name>`
2. The requested IDE paths point to that same directory
3. The CLI wrapper resolves from `PATH` if one was requested
4. For batch mode, inspect the generated inventory report for any `needs_attention` skills
5. For `custom-only`, verify the report only contains user-created skills
6. For `refresh-baseline`, verify that custom skills now carry `.custom-skill-manifest.json`

## Response Format

When reporting completion:

- Show the global source directory
- List each created or refreshed symlink
- Mention any backups that were created
- Mention the wrapper path if one was created
- In batch mode, include paths to `global_skill_inventory.json` and `global_skill_inventory.md`
- In `custom-only` mode, include paths to `custom_skill_inventory.json` and `custom_skill_inventory.md`
- When `refresh-baseline` runs, mention the refreshed baseline file and any manifests that were backfilled

## Harness (Self-Eval)

This skill has a built-in eval harness following the Agent Harness 5-module pattern to verify deployment correctness.

### Task (what to test)
3 eval cases in `evals/evals.json`:
- **case_001**: Single skill global deployment → must create global source + symlinks + verify
- **case_002**: Skill deployment without CLI wrapper → must skip wrapper creation
- **case_003**: Batch scan + deploy + inventory report → must generate JSON and MD reports

### Environment
- `scripts/install_global_skill.py` — single-skill installer
- `scripts/manage_global_skills.py` — batch manager + reporter
- `references/official-skills.txt` — official baseline for custom-only filtering

### Tools
`install_global_skill.py` `manage_global_skills.py`

### Grader
Run the harness on any deployment output:

```bash
# Full harness run
python3 evals/run_harness.py <output-file>

# Individual checks
python3 evals/grader.py <output-file> '<checks-json>'
```

### Checks

| Check | Detects |
|-------|---------|
| `global_source_exists` | Global registry path referenced in output |
| `symlinks_created` | Symlink creation mentioned |
| `cli_wrapper_created` | CLI wrapper path referenced |
| `inventory_reports_generated` | JSON + MD report files mentioned |
| `backup_on_conflict` | Backup/rename handling mentioned |
| `custom_only` | Custom-only filtering active |
| `needs_attention` | Health/attention flags reported |
| `manifest_created` | Custom skill manifest created |
| `refresh_baseline` | Baseline file rebuilt |
| `verify_results` | Verification steps included |
| `skip_cli_wrapper` | Wrapper correctly skipped |

### Eval flow
1. Pick a case from `evals/evals.json`
2. Follow instructions above
3. Save output
4. Run `run_harness.py` to grade
5. Fix failures, re-deploy, re-check

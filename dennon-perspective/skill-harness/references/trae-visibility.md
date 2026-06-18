# Making Skills Visible to Trae

Trae (字节跳动 AI IDE) reads skills from `~/.agents/skills/` with symlinks in `~/.trae/skills/`.

## Setup

```bash
# 1. Copy skill to agent skills dir
cp -r ~/.hermes/skills/<skill-name> ~/.agents/skills/<skill-name>

# 2. Symlink from Trae's skills dir
cd ~/.trae/skills && ln -sf ../../.agents/skills/<skill-name> <skill-name>
```

After this, Trae will discover the skill on next restart.

## Verification

Check that both locations are correct:

```bash
ls ~/.agents/skills/<skill-name>/SKILL.md       # should exist
ls -la ~/.trae/skills/<skill-name>                # should be a symlink
readlink ~/.trae/skills/<skill-name>              # → ../../.agents/skills/<skill-name>
```

## Pattern details

| Path | Purpose |
|------|---------|
| `~/.agents/skills/<name>/` | Actual skill content (SKILL.md + evals + scripts + references) |
| `~/.trae/skills/<name>` | Symlink → `../../.agents/skills/<name>` |
| `~/.trae/skill-config.json` | Optional: disable built-in skills, manage extra settings |

The `skill-config.json` can disable built-in skills the user doesn't want:

```json
{
  "disabledSkills": [],
  "builtinSkillStatus": {
    "TRAE-dynamic-ui": false
  },
  "managedSkills": {}
}
```

## When to use

Apply this after:
- Creating a new skill that should be available in Trae
- Running darwin-optimization on a skill and wanting the updated version visible
- Debugging why Trae isn't picking up a skill (check the symlink first)

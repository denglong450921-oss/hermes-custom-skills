# Skill Loading Troubleshooting

## Symptom

A slash command like `/html-output` fails with:

```
Failed to load skill for /html-output
```

## Root Cause

Duplicate `name:` YAML frontmatter values across different SKILL.md files in `~/.hermes/skills/`. The system's `scan_skill_commands()` function registers the first one it finds, then silently skips later duplicates. If a stale or incomplete copy is scanned first, the slash command points to a broken skill.

## Common Trigger

The **Darwin skill-optimizer** (`darwin-skill`) can create workspace directories with snapshot copies:

```
~/.hermes/skills/html-output/                      # ← real skill
~/.hermes/skills/html-output-workspace/
  └── skill-snapshot/
      └── SKILL.md            # ← copy with same name: "html-output"
```

The workspace snapshot is typically older or stripped compared to the real skill. If the filesystem scan finds it first, `/html-output` registers against the broken copy.

## Detection

```bash
# Search for all SKILL.md files using a specific name
grep -rl '^name: "html-output"' ~/.hermes/skills/*/SKILL.md ~/.hermes/skills/*/**/SKILL.md 2>/dev/null

# Or list the category in hermes skills list
hermes skills list | grep "html-output"
# Check if the category column shows a workspace directory
```

## Fix

1. **Remove the conflicting SKILL.md** that isn't the real skill:
   ```bash
   rm ~/.hermes/skills/<workspace-dir>/skill-snapshot/SKILL.md
   ```

2. **Reload the skill registry** so the real skill is picked up:
   - Restart gateway: `hermes gateway run --replace`
   - Or just invoke the slash command again — the system rescans on cache miss

## Prevention

When creating or modifying skills, avoid placing SKILL.md files with the same `name:` frontmatter in multiple subdirectories. The scan excludes `.git`, `.github`, `.hub`, and `.archive` directories, but NOT `*-workspace/`, `skill-snapshot/`, or `darwin/` subdirectories.

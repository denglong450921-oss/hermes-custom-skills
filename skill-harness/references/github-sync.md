# GitHub Auto-Sync for Custom Skills

Back up your Hermes custom skills to GitHub with automatic periodic sync.

## Setup

### 1. Create Repo

```bash
mkdir -p ~/Documents/hermes-skills
cd ~/Documents/hermes-skills
git init
gh repo create hermes-custom-skills --public --source .
```

### 2. Add Skills

```bash
rsync -a --exclude=__pycache__ ~/.hermes/skills/html-output/ html-output/
rsync -a --exclude=__pycache__ ~/.hermes/skills/skill-harness/ skill-harness/
# ... add all custom skills
git add -A
git commit -m "init custom skills"
git push origin main
```

### 3. Auto-Sync Cron Job

Use a Hermes cron job that runs every 30 min:

```bash
hermes cronjob create --name auto-push-skills --schedule 30m --workdir ~/Documents/hermes-skills
```

The cron job rsyncs each skill, git add+commit+push.

## Identifying User-Created Skills

| Type | Identify by | Sync? |
|------|-------------|-------|
| User-created | Real dir in `~/.hermes/skills/`, no matching `openclaw-imports/` | Yes |
| Customized import | Symlink with `.custom-skill-manifest.json` | Check with user |
| Imported | Has matching `openclaw-imports/` entry | No |
| Official bundled | Under category dir like `apple/`, `autonomous-ai-agents/` | No |

## Cron Details

Schedule `30m` = every 30 minutes. Silent on no-changes. Uses `workdir` to run from repo.

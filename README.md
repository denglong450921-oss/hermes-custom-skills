# Hermes Custom Skills

Personal Hermes Agent skills collection — auto-synced to GitHub every 30 min.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| **html-output** | 🛠️ 自建 v4.1 | Beautiful HTML output with harness + feedback loop + honesty constraint |
| **skill-harness** | 🛠️ 自建 | 5-module Agent Harness injector with distill/ftpr/honesty |
| **skill-creator** | 🛠️ 自建 | Meta skill for creating, editing, and evaluating skills |
| **swihub-ppt-template** | 🛠️ 自建 | PPT template (gold #D4AF37, Playfair+Open Sans) |
| **web-video-presentation-dev** | 🛠️ 自建 | Video presentation engineering companion |
| **camofox-browser** | 🛠️ 自建 | Stealth browser config for AI agents |
| **mao-zedong-perspective** | 🛠️ 自建 | Mao Zedong thinking framework |
| **global-skill-deployer** | 📦 自定义导入 | Deploy skills across Hermes, Trae, Claude Code, Cursor |
| **multilingual-video-voice-workflow** | 📦 自定义导入 | TTS + SRT multilingual voice pipeline |

## Auto-Sync

A cron job runs every 30 minutes: rsyncs local changes from `~/.hermes/skills/` and `~/.agents/skills/` into this repo, then commits + pushes to GitHub.

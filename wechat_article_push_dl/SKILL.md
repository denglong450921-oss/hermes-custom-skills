---
name: wechat_article_push_dl
description: Push pre-formatted HTML or Markdown content to WeChat Official Account drafts via the WeChat API. Use whenever the user wants to create WeChat article drafts (standard article or 小绿书 image post) from HTML or Markdown. Handles credentials, cover image upload, draft creation, and all WeChat API error codes.
contract_version: "1.0"
---

# wechat_article_push_dl

Push content to WeChat Official Account drafts. This skill handles ALL WeChat API interactions: auth, cover upload, content image processing, draft creation, error handling. It does NOT convert modern CSS to WeChat-compatible styles — input HTML must already be WeChat-compatible (inline styles only).

## ⚠️ Critical Pitfall: `--html` Strips Modern CSS

This is the #1 failure mode. **If you push raw HTML via `--html` and the CSS
looks broken in WeChat, the fix is to use `--markdown` instead.**

Read `references/wechat-html-css-stripped.md` for full diagnosis + fix.
Symptom: "my card's CSS is not working", "backgrounds disappeared",
"gradients are gone", "layout collapsed" — always check whether the user
used `--html` vs `--markdown`.

**Rule of thumb: Always prefer `--markdown`. Only use `--html` when the
HTML is already minimal inline-style (no style blocks, no CSS vars, no
gradients, no flex/grid).**

## Quick Reference

```bash
# Push HTML file
md2wechat --html article.html --title "Title" --style tech --author "Name" --cover <url>

# Push Markdown file (MD2WeChat converter auto-generates WeChat-compatible HTML)
md2wechat --markdown article.md --style tech --author "Name" --cover <url>

# Push as 小绿书 (image post)
md2wechat --markdown article.md --type newspic --cover <url>
```

## Input Contract

| Field | CLI Flag | Required | Default | Max |
|-------|----------|----------|---------|-----|
| HTML file path | `--html` | Yes (or `--markdown` / `--content`) | - | - |
| Markdown file path | `--markdown` | Yes (or `--html` / `--content`) | - | - |
| Content string | `--content` | Yes (or `--html` / `--markdown`) | - | - |
| Title | `--title` | No (extracted from frontmatter or filename) | Filename | 64 chars |
| Summary | `--summary` | No | Auto | 120 chars |
| Cover | `--cover` | **YES — REQUIRED** | - | URL or local path |
| Author | `--author` | No | - | - |
| Style | `--style` | No | `academic_gray` | One of: academic_gray, festival, tech, announcement |
| Type | `--type` | No | `news` | `news` or `newspic` |
| Comments | `--comment` | No (flag) | Disabled | - |
| Fans-only comments | `--fans-only-comment` | No (requires `--comment`) | Everyone can comment | - |

At least one of `--html`, `--markdown`, or `--content` is required.

## Preconditions

### 1. Credentials — `.env` file in CWD

```
WECHAT_APPID=wx...
WECHAT_APP_SECRET=***
```

The CLI reads `.env` from the current working directory, not home. For this user, credentials are in `~/Documents/.env` — always `cd ~/Documents` before running md2wechat. If credentials are missing or wrong, the API returns:

| Error | Meaning |
|-------|---------|
| `40001` | AppSecret invalid — regenerate at mp.weixin.qq.com |
| `40013` | AppID invalid — should start with `wx` |

**To set up credentials:**
```bash
cat > .env << EOF
WECHAT_APPID=your_appid
WECHAT_APP_SECRET=your_appsecret
EOF
```

### 2. IP Whitelist

WeChat requires your outbound IP to be whitelisted. The actual IP can differ from `api.ipify.org` due to VPN/proxy. Run the push command once — if it fails with `40164`, the error message contains the real IP:

```
Error code: 40164, message: invalid ip <ACTUAL_IP>, not in whitelist
```

Add that IP at [mp.weixin.qq.com](https://mp.weixin.qq.com) → Settings → Development → Basic Configuration → IP Whitelist.

### 3. md2wechat CLI installed

```bash
pip3 install md2wechat
# If not on PATH:
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
```

### 4. Cover image

Every draft requires a cover. Provide via `--cover <url_or_path>`. Accepts remote URLs or local file paths.

## Process

1. **Verify preconditions** — check CLI available, .env exists, cover provided.
2. **Verify HTML is WeChat-compatible** (if using `--html`):
   - All styles must be inline (`style=""`)
   - No `<style>` blocks, no CSS vars, no gradients/flex/grid/pseudo-elements
   - See `WeChat CSS → works/doesn't work` tables below
3. **Build command** with appropriate flags.
4. 🔴 **STOP — Show user the exact command and wait for confirmation.** Do NOT execute without user approval. Present the full command in a code block and explain what it will do.
5. **Execute** `md2wechat` command (only after user confirms).
6. **Check result:**
   - `"success": true` → return media_id
   - Error → decode error code, report fix to user.

## Output Contract

```json
{
  "success": true,
  "data": {
    "media_id": "kJHuVqQ0oAIrl9gfF0SY...",
    "status": "published",
    "message": "文章已成功发布到公众号草稿箱"
  }
}
```

On success, the draft is saved to WeChat 草稿箱 (drafts). It does NOT auto-publish. The user must review and publish manually at mp.weixin.qq.com.

## Failure Handling

| 触发条件 | 一线修复 | 仍失败兜底 |
|-----------|---------|-----------|
| `40001` — invalid AppSecret | Regenerate at mp.weixin.qq.com, update .env | Report to user: check AppSecret matches exactly |
| `40013` — invalid AppID | Verify AppID starts with `wx` | Report to user: check mp.weixin.qq.com settings |
| `40164` — IP not whitelisted | Read `<ACTUAL_IP>` from error, add to whitelist | Ask user to add IP at mp.weixin.qq.com |
| `MISSING_COVER_IMAGE` — no cover | Pass `--cover <url_or_path>` | Check if cover URL is accessible |
| `45004` — body too long | Check digest/summary/description length | Shorten article or split into multiple drafts |
| `404` — API unavailable | Must be verified (认证号) account | Tell user to verify their WeChat account |
| `45166` — content violation | HTML format error | Convert to Markdown and retry with `--markdown` |
| CLI not found | `pip3 install md2wechat` | Add to PATH: `export PATH="$HOME/Library/Python/3.9/bin:$PATH"` |
| CLI error | Run `md2wechat --help` to verify flags | Correct the flag syntax and retry |

**First response:** Retry with corrected input.
**Final fallback:** Report the exact error code and fix to the user.

## WeChat HTML Compatibility

WeChat's article renderer supports only inline styles. `<style>` blocks, CSS variables, gradients, flex/grid, `::before`/`::after`, counters, `@media`, `box-shadow`, `transform`, and `opacity` are all **stripped or broken**.

> See `references/wechat-css-compatibility.md` for the full ✅ works / ❌ doesn't-work tables and HTML strategy guide. Load this file when the user's HTML has formatting issues in WeChat.

### Quick rule of thumb

**Prefer `--markdown` over `--html`.** The MD2WeChat converter built into the CLI generates proper WeChat-compatible HTML from Markdown. Only use `--html` when you have pre-formatted HTML that already uses only inline styles.

## Verification

1. Run a push with `--markdown` on a test article → confirm `"success": true` with `media_id`
2. Check mp.weixin.qq.com → 草稿箱 → article appears with correct title, cover, content
3. For cover image: confirm it uploaded (look for `Cover uploaded:` in output)
4. For error 40164: add IP, retry → should succeed

## Harness (Self-Eval)

The harness validates that an agent following the skill builds correct `md2wechat` CLI commands and handles WeChat API errors properly. 3 test cases cover HTML push, markdown/newspic push, and error handling.

### Cases

| ID | Principle Tested | Scenario |
|----|-----------------|----------|
| `case_001` | HTML article push | User provides HTML file, title, style=tech, cover, comments enabled — must build `--html` command with all flags |
| `case_002` | 小绿书 image post | User provides markdown file for image-post format — must build `--markdown --type newspic` command |
| `case_003` | Missing cover error | User forgets cover image — must guide user to add `--cover` flag |

### Checks

| Check | What it detects |
|-------|----------------|
| `builds_html_command` | Output uses `--html` flag |
| `builds_markdown_command` | Output uses `--markdown` flag |
| `includes_cover` | Output includes `--cover` flag |
| `includes_style` | Output includes `--style` with valid value |
| `includes_type_newspic` | Output includes `--type newspic` |
| `includes_comment` | Output includes `--comment` flag |
| `handles_missing_cover` | Output mentions cover is required / missing |
| `handles_ip_whitelist` | Output references 40164 / IP whitelist |
| `handles_auth_error` | Output references 40001/40013 auth errors |
| `verifies_preconditions` | Output checks .env / credentials / CLI install |
| `returns_media_id` | Output references media_id / draft created |

### Run

```bash
# Full harness
python3 evals/run_harness.py <output-file>

# Or individual check
python3 evals/grader.py <output-file> '[{"text":"Uses --html","check":"builds_html_command"}]'
```

### Honesty & Truthfulness

Report results exactly as they are:
- API call succeeded → report media_id, don't add disclaimers
- API call failed → report exact error code and fix, don't hide it
- Precondition missing → say what's missing, don't silently skip
- If actual push isn't possible (no live credentials) → test command construction only, don't claim the draft was created

---

## Anti-Patterns & What NOT to Do

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|--------------|------------------|
| 1 | Pushing raw HTML with `<style>` blocks | WeChat strips all `<style>` — content becomes unformatted | Convert to Markdown and use `--markdown`, or rewrite with inline styles only |
| 2 | Pushing without a cover | API returns `MISSING_COVER_IMAGE` | Always provide `--cover <url_or_path>` |
| 3 | Forgetting IP whitelist | API returns `40164` — outbound IP not recognized | Run once, read the actual IP from error, add to WeChat whitelist |
| 4 | Using `--html` when source is Markdown | Misses MD2WeChat's automatic CSS conversion | Always prefer `--markdown` over `--html` |
| 5 | Silently executing the push without showing the user | User may not expect a real API call creating a draft | 🔴 STOP and show command before executing |
| 6 | Claiming "draft created" when you only tested command construction | Without live credentials, no draft was actually created | Report honestly: "command built correctly" not "draft published" |
| 7 | Passing a local image path that doesn't exist | CLI will error trying to upload | Verify the path exists, or use a remote URL |

---

## Related Skills

- `md2wechat` — Convert Markdown to WeChat-compatible HTML (CSS formatting, layout modules)
- `wechat_article_css_dl` — Check/fix HTML for WeChat CSS compatibility
- `ato-arche-dl` — Atomic skill workflow design pattern

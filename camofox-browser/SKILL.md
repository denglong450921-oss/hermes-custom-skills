---
name: camofox-browser
description: >
  Configure and use CamoFox (jo-inc) stealth browser for AI agents.
  Bypasses Cloudflare, bot detection, and CAPTCHAs by spoofing Firefox fingerprints.
---

# CamoFox Stealth Browser

High-stealth browser backend for AI agents. Modification of Firefox (Camoufox) with a REST/MCP wrapper.

## Installation

### Docker (Recommended)
```yaml
services:
  camofox:
    image: ghcr.io/jo-inc/camofox-browser:latest
    ports: ["9377:9377"]
    environment:
      - CAMOFOX_PORT=9377
    shm_size: '2gb'
    restart: always
```

### NPM
```bash
npm install -g camofox-browser
camofox-browser # Starts on 9377
```

## Configuration

Set environment variables in `.env`:
- `CAMOFOX_URL=http://localhost:9377`

## Verification

Check health:
```bash
curl http://localhost:9377/health
# Expected: {"ok":true,"browserConnected":true}
```

## Persistence Patterns: The "Backpack" Analogy

For Cloudflare-protected sites, the most reliable strategy is session persistence using a **User Data Dir** (User Profile).

- **Principle**: Think of the browser as having a "backpack" (the profile folder). If you visit a site, pass the verification, and save the cookies/tokens in the backpack, next time you go back with the same backpack, the site remembers you and lets you in without asking for verification again.
- **Manual Setup (Manual "打底")**: 
  1. Run a script with `headless=False` and a designated `user_data_dir`.
  2. Manually click the "Verify you are human" box in the visible window.
  3. Wait for the page to load/save state, then close.
- **Agent Execution**: Run the script with `headless=True` using the *same* `user_data_dir`.

### Correct API for Persistent Context with user_data_dir

**CRITICAL**: `user_data_dir` cannot be passed directly to `Camoufox()` — it is a Playwright `launch_persistent_context` parameter and will raise `TypeError: BrowserType.launch() got an unexpected keyword argument 'user_data_dir'` if passed to the regular launch path.

Always use this pattern instead:

```python
from camoufox.utils import launch_options
from camoufox import DefaultAddons
from playwright.sync_api import sync_playwright

PROFILE_DIR = "/path/to/profile"
STORAGE_STATE = "/path/to/profile/storage_state.json"

with sync_playwright() as playwright:
    opts = launch_options(
        headless=False,          # or True for agent execution
        geoip=True,              # requires: pip install camoufox[geoip]
        exclude_addons=[DefaultAddons.UBO],  # see pitfalls below
        user_data_dir=PROFILE_DIR,
    )
    context = playwright.firefox.launch_persistent_context(**opts)
    page = context.new_page()
    page.goto("https://target.site")
    # ... do work ...
    # Save cookies/localStorage for later reuse:
    context.storage_state(path=STORAGE_STATE)
    context.close()
```

To reuse saved state in a subsequent run, pass `storage_state=STORAGE_STATE` when creating a non-persistent context, OR just reuse the same `user_data_dir` with persistent context (cookies are already baked in).

## Templates

- `templates/persistent_login.py` — Phase 1 manual login script (run in interactive terminal, saves cookies to profile dir)
- `templates/headless_agent.py` — Phase 2 headless automation script (safe to run from agent terminal)

## References

- `references/macos-env-notes.md` — macOS-specific env facts: confirmed package versions, UBO fix, DOM inspection JS, nohup/zsh patterns

## Button Detection in Dynamic SPAs (Vue/React)

Playwright's `locator("button", has_text="...")` can silently return 0 results in Camoufox even when buttons exist in the DOM. The accessible tree differs from the real DOM.

**Always prefer CSS class selectors or JS evaluation over text-based locators:**

```python
# UNRELIABLE in Camoufox — may return empty even when button exists
page.locator("button", has_text="特惠订阅")

# RELIABLE — use CSS class unique to target button
btn = page.locator("button.buy-btn.special")
if btn.count() > 0:
    return btn.first

# RELIABLE fallback — nth by position among a CSS class group
btns = page.locator("button.buy-btn")
if btns.count() >= 2:
    return btns.nth(1)  # index 0=first plan, 1=second plan, etc.
```

**How to discover the right CSS class:** use `browser_console` with JS to inspect real DOM:

```javascript
Array.from(document.querySelectorAll('button'))
  .filter(b => b.innerText.includes('目标文字'))
  .map(b => ({text: b.innerText.trim(), disabled: b.disabled, className: b.className}))
```

This reveals actual class names, disabled state, and aria attributes — much more reliable than screenshot analysis.

## Reload Timeout Pattern for Polling Loops

`page.reload()` with a tight timeout will fail repeatedly on slow/rate-limited sites. Use this pattern:

```python
try:
    page.reload(wait_until="domcontentloaded", timeout=15000)
except Exception:
    # fallback: full navigation is more reliable than reload
    page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=20000)
page.wait_for_timeout(1200)  # wait for JS framework to render
```

## Stealth Alternatives: nodriver

If Camoufox or Playwright still get detected, use **`nodriver`**. It is a high-stealth automation library that does not use the standard WebDriver protocol, making it nearly invisible to bot detectors like Cloudflare Turnstile.

```python
import nodriver as uc
browser = await uc.start()
page = await browser.get('https://target.site')
# nodriver often passes verification automatically without user intervention
```

## Installation Notes

```bash
pip install camoufox           # base install
pip install "camoufox[geoip]"  # required if you pass geoip=True
python -m camoufox fetch       # downloads the Camoufox Firefox binary
```

## Pitfalls

- **Port Conflict**: If 9377 taken, check `lsof -i :9377`.
- **Proxy Interference**: If global proxy is active, local requests to 9377 may fail. Add `no_proxy=localhost,127.0.0.1` to `.env`.
- **Memory**: Docker requires `shm_size: '2gb'` to prevent rendering crashes on heavy sites.
- **GUI Errors (EPIPE)**: In terminal-only environments (SSH/headless containers), attempting `headless=False` will crash with `EPIPE` or display errors. Use `nodriver` or remote debugging if manual intervention is required.
- **File Locking**: A `user_data_dir` can only be used by one browser instance at a time. Close all "Manual Setup" windows before starting the Agent.
- **UBO Addon Download Failure (macOS)**: The default UBO (uBlock Origin) addon often fails to download silently, leaving an empty directory at `~/Library/Caches/camoufox/*/addons/UBO/`. This causes `InvalidAddonPath: manifest.json is missing`. Fix: always pass `exclude_addons=[DefaultAddons.UBO]` unless you specifically need it. If you see the error, delete the empty dir (`rm -rf ~/Library/Caches/camoufox/*/addons/UBO`) and re-run with the exclusion.
- **user_data_dir TypeError**: Passing `user_data_dir` to `Camoufox()` directly raises `TypeError: BrowserType.launch() got an unexpected keyword argument 'user_data_dir'`. Must use `launch_options()` + `playwright.firefox.launch_persistent_context()` instead — see the Persistence Patterns section above.
- **geoip Extra Required**: `geoip=True` raises `NotInstalledGeoIPExtra` unless you `pip install camoufox[geoip]`. On first run it downloads a ~65 MB GeoIP database.
- **input() EOF in Agent Context**: Scripts that call `input()` to wait for human interaction will raise `EOFError: EOF when reading a line` when run via an agent's terminal tool. The user must run such scripts in their own interactive terminal session.

# Camoufox on macOS — Environment Notes

## Confirmed working environment (May 2026)

- Python: /opt/anaconda3/bin/python (3.12)
- camoufox: 0.4.11
- camoufox[geoip]: required separately — downloads ~65 MB MaxMind DB on first use
- Camoufox Firefox binary: v135.0.1-beta.24 (fetched via `python -m camoufox fetch`)
- GeoIP DB cache: ~/Library/Caches/camoufox/

## UBO Addon Problem

Default UBO addon fails silently on macOS — download creates empty dir:
  ~/Library/Caches/camoufox/Camoufox.app/Contents/Resources/addons/UBO/

Symptom: `InvalidAddonPath: manifest.json is missing`
Fix: `rm -rf ~/Library/Caches/camoufox/*/addons/UBO` + always pass `exclude_addons=[DefaultAddons.UBO]`

## user_data_dir API

- `Camoufox(user_data_dir=...)` → TypeError (wrong API)
- `launch_options(..., user_data_dir=...) + playwright.firefox.launch_persistent_context(**opts)` → correct

## DOM Inspection for Button Detection

bigmodel.cn GLM Coding page button structure (verified May 2026):
- All plan buttons: `button.el-button.el-tooltip.buy-btn.el-button--primary`
- Pro (middle plan) only: adds class `special` → `button.buy-btn.special`
- Disabled state: `button.disabled` attribute or `is-disabled` CSS class
- Text-based locator (`has_text="特惠订阅"`) unreliable in Camoufox Firefox accessible tree

JS to inspect buttons:
```javascript
Array.from(document.querySelectorAll('button'))
  .filter(b => b.innerText.includes('订阅'))
  .map(b => ({text: b.innerText.trim(), disabled: b.disabled, className: b.className}))
```

## nohup Background Pattern (zsh)

```bash
# Run in background, log to file
nohup /opt/anaconda3/bin/python /path/to/script.py --at 14:00 > /tmp/script.log 2>&1 &
# Note PID:
echo $!
# Watch log:
tail -f /tmp/script.log
# Stop:
kill <PID>
# or:
pkill -f "script.py"
```

Note: `echo "PID: $!"` with quotes triggers zsh history expansion (`!`). Use `echo $!` instead.

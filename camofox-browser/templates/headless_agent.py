#!/usr/bin/env python3
"""
Phase 2: Headless polling/snipe agent — safe to run from agent terminal.
Loads saved profile + cookies, polls for a target button, clicks when active.

Usage:
    python headless_agent.py --at 14:00   # wait until 14:00 then snipe
    python headless_agent.py              # start polling immediately
    python headless_agent.py --visible    # show browser window (debug)
"""
import sys
import time
import argparse
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from camoufox.utils import launch_options
from camoufox import DefaultAddons
from playwright.sync_api import sync_playwright

# ── CONFIG ─────────────────────────────────────────────────────────────────
PROFILE_DIR    = str(Path.home() / ".camoufox_profile")
STORAGE_STATE  = str(Path(PROFILE_DIR) / "storage_state.json")
TARGET_URL     = "https://example.com"       # CHANGE THIS
SCREENSHOT_DIR = str(Path(PROFILE_DIR) / "screenshots")

# Button selector — use CSS class, NOT text (text unreliable in Camoufox)
# Discover with: document.querySelectorAll('button').forEach(b=>console.log(b.className, b.innerText))
TARGET_BTN_SELECTOR = "button.target-class"  # CHANGE THIS

INTERVAL_NORMAL = 3.0   # seconds between polls
INTERVAL_HOT    = 0.8   # seconds in hot window
HOT_WINDOW_SECS = 30    # how many seconds before target time to go hot
# ───────────────────────────────────────────────────────────────────────────


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}", flush=True)


def parse_target_time(s):
    parts = s.split(":")
    h, m = int(parts[0]), int(parts[1])
    sec = int(parts[2]) if len(parts) > 2 else 0
    t = datetime.now().replace(hour=h, minute=m, second=sec, microsecond=0)
    if t < datetime.now():
        t += timedelta(days=1)
    return t


def find_button(page):
    try:
        btn = page.locator(TARGET_BTN_SELECTOR)
        if btn.count() > 0:
            return btn.first
    except Exception as e:
        log(f"find_button error: {e}")
    return None


def is_enabled(btn):
    try:
        if btn.get_attribute("disabled") is not None:
            return False
        cls = btn.get_attribute("class") or ""
        if "disabled" in cls or "is-disabled" in cls:
            return False
        return True
    except Exception:
        return False


def snipe(page, target_time=None):
    interval = INTERVAL_NORMAL
    attempt = 0
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

    while True:
        attempt += 1
        try:
            if target_time:
                remaining = (target_time - datetime.now()).total_seconds()
                if remaining <= HOT_WINDOW_SECS:
                    interval = INTERVAL_HOT
                if remaining < -120:
                    log("120s past target time — stopping")
                    break

            log(f"Attempt {attempt} — reloading...")
            try:
                page.reload(wait_until="domcontentloaded", timeout=15000)
            except Exception:
                page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1200)

            btn = find_button(page)
            if btn is None:
                log("Button not found")
            elif not is_enabled(btn):
                log("Button disabled (sold out / not yet on sale)")
            else:
                log("!!! BUTTON ACTIVE — clicking !!!")
                page.screenshot(path=f"{SCREENSHOT_DIR}/before_{attempt}.png")
                btn.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=f"{SCREENSHOT_DIR}/after_{attempt}.png")
                log(f"Clicked. URL: {page.url}")
                log("Check browser. Press Enter to continue polling or Ctrl+C to stop: ")
                # NOTE: input() only works if running in interactive terminal
                # If running from agent: remove this line and just break or loop
                input()

        except KeyboardInterrupt:
            log("Stopped by user")
            break
        except Exception as e:
            log(f"Error: {e}")
            traceback.print_exc()

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--at", default=None, help="Target time HH:MM")
    parser.add_argument("--visible", action="store_true", help="Show browser")
    args = parser.parse_args()

    headless = not args.visible
    target_time = None

    if args.at:
        target_time = parse_target_time(args.at)
        log(f"Target time: {target_time}")
        hot_start = target_time - timedelta(seconds=HOT_WINDOW_SECS)
        now = datetime.now()
        if now < hot_start:
            wait = (hot_start - now).total_seconds()
            log(f"Waiting {wait:.0f}s until hot window...")
            time.sleep(wait)
        log("Entering hot mode")

    if not Path(STORAGE_STATE).exists():
        log(f"ERROR: No storage state at {STORAGE_STATE}. Run persistent_login.py first.")
        sys.exit(1)

    with sync_playwright() as playwright:
        opts = launch_options(
            headless=headless,
            geoip=True,
            exclude_addons=[DefaultAddons.UBO],
            user_data_dir=PROFILE_DIR,
        )
        context = playwright.firefox.launch_persistent_context(**opts)
        page = context.new_page()
        log(f"Navigating to {TARGET_URL}")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=20000)
        log("Page loaded. Starting poll loop...")
        snipe(page, target_time=target_time)
        context.close()

    log("Done")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Phase 1: Manual login script — run in YOUR OWN interactive terminal.
NOT via agent terminal (input() will EOF).

Usage:
    python persistent_login.py

Opens Camoufox browser, you log in manually, press Enter, cookies saved.
"""
import os
from pathlib import Path
from camoufox.utils import launch_options
from camoufox import DefaultAddons
from playwright.sync_api import sync_playwright

PROFILE_DIR = str(Path.home() / ".camoufox_profile")
STORAGE_STATE = str(Path(PROFILE_DIR) / "storage_state.json")
TARGET_URL = "https://example.com"  # CHANGE THIS

os.makedirs(PROFILE_DIR, exist_ok=True)

print(f"Profile dir: {PROFILE_DIR}")
print("Browser opening — log in, then press Enter here to save cookies.")

with sync_playwright() as playwright:
    opts = launch_options(
        headless=False,
        geoip=True,                          # pip install camoufox[geoip]
        exclude_addons=[DefaultAddons.UBO],  # avoids InvalidAddonPath on macOS
        user_data_dir=PROFILE_DIR,
    )
    context = playwright.firefox.launch_persistent_context(**opts)
    page = context.new_page()
    page.goto(TARGET_URL)
    print("Complete login in browser, then press Enter: ", end="", flush=True)
    input()
    context.storage_state(path=STORAGE_STATE)
    context.close()

print(f"Cookies saved to: {STORAGE_STATE}")

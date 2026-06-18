# Load Completion And Slow Element Extraction

Slow sites fail clone workflows in two opposite ways: capturing too early misses content, while waiting forever kills speed. Use a multi-signal readiness contract instead of a fixed sleep.

## Readiness Rule

A page is ready for static extraction when all applicable signals pass or unresolved items are recorded as blockers/placeholders:

1. Navigation reaches `domcontentloaded` or `load`.
2. Critical selectors are visible, not merely attached. Prefer `main`, `header`, `footer`, a known hero selector, and any user-requested section.
3. Relevant network requests are quiet for a stable window such as `1000-2000ms`. Ignore long-lived websockets, analytics, beacons, tracking pixels, and known telemetry.
4. DOM stability holds for at least 3 samples spaced `500-1000ms`: element count, visible text length, and `document.body.scrollHeight` stop changing beyond small tolerances.
5. Fonts are ready through `document.fonts.ready`, or the timeout is recorded.
6. Lazy content is warmed: scroll down in viewport-sized steps, pause for network/DOM stability, then return to the capture position.
7. Visible media is resolved: in-viewport images have `currentSrc` and non-zero natural dimensions, or a placeholder/fallback is recorded.
8. Loading overlays, skeletons, and spinners are hidden, dismissed, or recorded as unresolved.

Do not advance Stage 1 from a single `networkidle` event. Some sites keep background requests open; others render important sections after network quiet.

## Playwright Helper

Run:

```bash
node <skill-dir>/scripts/wait-for-static-load.mjs \
  --url "$URL" \
  --out docs/research/pages/<page-slug>/load-report.json \
  --critical-selector "main" \
  --critical-selector "footer"
```

Use `--timeout-ms`, `--quiet-ms`, and `--sample-count` when a target is unusually slow. The report is evidence; link it in `SOURCE_OF_TRUTH.md`.

## Scrapling Fallback

Use Scrapling when browser extraction is slow, flaky, anti-bot-sensitive, or when elements relocate/change structure. Prefer it as an evidence assistant, not as a screenshot replacement.

Useful Scrapling controls:

- `DynamicFetcher` or `DynamicSession` for browser-backed extraction.
- `network_idle=True` for a network quiet wait.
- `wait_selector` with `wait_selector_state="visible"` for slow elements.
- `timeout` and `wait` to separate maximum wait from a small final settle window.
- `page_action` to scroll and warm lazy-loaded sections after navigation.
- `page_setup` to register listeners/routes before navigation.
- `capture_xhr` to inspect API data behind slow-rendered sections.
- `StealthyFetcher` or `real_chrome=True` only when ordinary browser extraction is blocked.

Example pattern:

```python
from scrapling.fetchers import DynamicFetcher

def warm_page(page):
    page.evaluate("""
      async () => {
        const delay = ms => new Promise(r => setTimeout(r, ms));
        for (let y = 0; y < document.body.scrollHeight; y += Math.max(400, innerHeight * 0.8)) {
          scrollTo(0, y);
          await delay(350);
        }
        scrollTo(0, 0);
        await delay(800);
      }
    """)

response = DynamicFetcher.fetch(
    url,
    network_idle=True,
    wait_selector="main",
    wait_selector_state="visible",
    timeout=60000,
    wait=1000,
    page_action=warm_page,
)
```

Avoid `disable_resources=True` during fidelity extraction because blocking fonts, images, media, or stylesheets can change layout or prevent a page from finishing. Use it only for a separate fast text reconnaissance pass and label the evidence accordingly.

## Blocker Policy

If readiness does not pass by the timeout:

1. Save the partial load report.
2. Identify missing selectors/media and likely causes.
3. Try one focused fallback: longer timeout, different critical selector, Scrapling, or user-provided access.
4. If still unresolved, stop Stage 1 and ask for access, screenshots, or permission to use placeholders.

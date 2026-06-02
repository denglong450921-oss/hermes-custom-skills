# Playwright Extraction Mode

When Camofox browser MCP is unavailable but Playwright (`python3 -c "import playwright"` succeeds), use Playwright Python scripts as a **full extraction alternative** — renders JS, extracts computed styles, and captures design tokens, all without needing the Camofox server.

## When to Use

- Camofox not running at `localhost:9377`
- Playwright installed (`python3 -c "import playwright"` passes)
- SPA or JS-heavy sites (curl returns empty HTML)
- Need pixel-accurate CSS values (unlike Firecrawl heuristic mode)

## Capabilities vs Other Modes

| Capability | Camofox | Playwright | Firecrawl |
|---|---|---|---|
| JS rendering | ✅ | ✅ | ❌ |
| getComputedStyle() | ✅ | ✅ via `page.evaluate()` | ❌ |
| Interaction sweep | ✅ click/hover/scroll | ⚠️ manual scripting needed | ❌ |
| Multi-state extraction | ✅ | ⚠️ manual scripting needed | ❌ |
| CSS precision | Pixel-perfect | Pixel-perfect | Heuristic |
| Speed | Fast (MCP) | Medium (launch browser) | Fastest |

## Usage Pattern

### Pattern A: Full-Page Reconnaissance (Phase 1)

Write a Python script like this, adapt for each project:

```python
import asyncio
from playwright.async_api import async_playwright
import json, os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Desktop viewport
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="zh-CN"  # match site locale
        )
        page = await context.new_page()
        await page.goto("TARGET_URL", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)  # let animations settle
        
        base = "/path/to/project"
        
        # --- Screenshots ---
        await page.screenshot(path=f"{base}/docs/design-references/desktop-full.png", full_page=True)
        
        # Mobile
        await context.close()
        context = await browser.new_context(viewport={"width": 390, "height": 844})
        # ... repeat
        
        # --- Page Structure ---
        structure = await page.evaluate("""
            () => {
                const sections = [];
                document.querySelectorAll('section, div[id], header, footer, main, nav').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width < 100 || rect.height < 50) return;
                    sections.push({
                        tag: el.tagName.toLowerCase(),
                        id: el.id || '',
                        class: (el.className || '').toString().slice(0, 80),
                        rect: {top: Math.round(rect.top), width: Math.round(rect.width), height: Math.round(rect.height)},
                        text: (el.textContent || '').trim().slice(0, 120)
                    });
                });
                return sections.slice(0, 60);
            }
        """)
        with open(f"{base}/docs/design-references/page-structure.json", "w") as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
        
        # --- CSS Variables (design tokens) ---
        cssVars = await page.evaluate("""
            () => {
                const style = getComputedStyle(document.documentElement);
                const vars = {};
                for (let i = 0; i < style.length; i++) {
                    const prop = style[i];
                    if (prop.startsWith('--')) vars[prop] = style.getPropertyValue(prop).trim();
                }
                return vars;
            }
        """)
        with open(f"{base}/docs/design-references/css-vars.json", "w") as f:
            json.dump(cssVars, f, ensure_ascii=False, indent=2)
        
        await browser.close()

asyncio.run(main())
```

### Pattern B: Design Token Extraction (all key elements)

```python
tokens = await page.evaluate("""
    () => {
        const elements = {
            'body': document.body,
            'h1': document.querySelector('h1'),
            'h2': document.querySelector('h2'),
            'p': document.querySelector('p'),
            'btn': document.querySelector('a.btn, button.btn'),
            'link': document.querySelector('a')
        };
        const result = {};
        for (const [name, el] of Object.entries(elements)) {
            if (!el) continue;
            const cs = getComputedStyle(el);
            result[name] = {
                color: cs.color,
                bg: cs.backgroundColor,
                font: cs.fontFamily,
                size: cs.fontSize,
                weight: cs.fontWeight,
                lineHeight: cs.lineHeight,
            };
        }
        return result;
    }
""")
```

### Pattern C: Section HTML & Text Extraction

```python
# Extract each major section's innerHTML and text
sections_data = await page.evaluate("""
    () => {
        const results = {};
        const sections = ['#tile-1', '#tile-3', '#footer', ...];
        // ... or find by content
        const found = document.querySelectorAll('section');
        found.forEach(s => {
            if (s.textContent.includes('KEY_TEXT')) {
                results['section_name'] = {
                    html: s.innerHTML.slice(0, 3000),
                    text: s.textContent.trim().slice(0, 1000)
                };
            }
        });
        return results;
    }
""")
```

### Pattern D: Image & Asset Discovery

```python
images = await page.evaluate("""
    () => {
        const imgs = [];
        document.querySelectorAll('img').forEach(img => {
            if (img.src) imgs.push({
                src: (img.currentSrc || img.src).slice(0, 200),
                lazySrc: img.dataset.src || img.dataset.lazy || null,
                srcset: img.dataset.srcset || img.srcset || null,
                alt: (img.alt || '').slice(0, 100),
                w: img.naturalWidth,
                h: img.naturalHeight
            });
        });
        return imgs;
    }
""")
```

### Pattern E: Nav/Header Detection

Some sites have header elements that are hard to find with standard selectors. Use this to probe:

```python
nav_info = await page.evaluate("""
    () => {
        const candidates = [];
        const selectors = ['nav', '.navbar', '.header', 'header', 
                           '[role="navigation"]', '.nav-bar'];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) candidates.push({
                selector: sel, tag: el.tagName, id: el.id,
                class: el.className.slice(0, 60),
                has_links: el.querySelectorAll('a').length
            });
        }
        // Also find sticky/fixed elements at top
        const all = document.querySelectorAll('div, header');
        for (const el of all) {
            const cs = getComputedStyle(el);
            if ((cs.position === 'fixed' || cs.position === 'sticky') && 
                parseInt(cs.top) === 0 && el.children.length > 3) {
                candidates.push({
                    selector: 'sticky/fixed find', tag: el.tagName,
                    id: el.id, class: el.className.slice(0, 60),
                    has_links: el.querySelectorAll('a').length
                });
                break;
            }
        }
        return candidates;
    }
""")
```

## Pipeline Adaptations

### Phase 1: Reconnaissance (Playwright Mode)

1. **Full page navigation & screenshots** — see Pattern A
2. **Design token extraction** — see Pattern B (CSS variables, font stack, color palette)
3. **Section structure** — see Pattern A (page-structure.json gives component boundaries)
4. **Content extraction** — see Pattern C (per-section HTML for spec files)
5. **Asset discovery** — see Pattern D (image URLs, alt texts, dimensions)
6. **Mark interaction model** as "partial — Playwright mode (no click/hover sweep built-in)"
7. **Write PAGE_TOPOLOGY.md** with actual CSS values (they are pixel-accurate, unlike Firecrawl)
8. **Handle lazy-loading:** Scan for `data-src`, `data-lazy` via page.evaluate (can resolve lazy images since Playwright waits for networkidle)

### Phase 2-5: Same as Camofox mode

Foundation → Component Spec → Dispatch Builders → Assembly → QA.
CSS values are pixel-accurate (getComputedStyle via page.evaluate).
Builder prompts can use exact CSS values — no need for "approximate" disclaimer.

### Limitations

- **No built-in interaction sweep** — you can add click/hover/page.evaluate() calls to the Python script, but the extraction script doesn't include them by default. Add `await page.click()` / `await page.hover()` calls for multi-state extraction as needed.
- **Browser startup overhead** — Playwright launches headless Chromium (~2-3s). For small sites this is slower than curl-only.
- **Lazy images may still resolve to placeholder** — `networkidle` wait helps, but some images load after scrolling. Add `await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))` before image discovery.
- **Rapid context close/open causes EPIPE crash** — When extracting multiple pages sequentially, repeatedly calling `await context.close()` + `await browser.new_context()` in a loop can trigger Node.js EPIPE errors (`write EPIPE`, `write after end`). The Playwright driver process gets overwhelmed by the rapid start/stop cycle.
  **Fix:** Reuse a single context for the entire extraction session, or batch all page extractions into a single browser instance with one context per extraction phase. Reduce context create/close to ~3 cycles max. If extracting 5+ pages, create all contexts upfront:

## When to Choose Playwright vs Firecrawl

Choose **Playwright** when:
- The site has JS rendering (SPA, React, Vue)
- You need pixel-accurate CSS values for the clone
- You have Playwright installed (common in AI agent environments)
- Camofox is unavailable

Choose **Firecrawl** when:
- The site is HTML-only (WordPress, static sites with rendered HTML)
- Speed matters more than CSS precision
- Playwright is not installed
- You only need layout structure and content

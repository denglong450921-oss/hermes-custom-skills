#!/usr/bin/env python3
"""
extract-playwright.py — Full Phase 1 website extraction via Playwright.

Usage:
  python3 scripts/extract-playwright.py <url> [output_dir]

Extracts:
  - Desktop (1440px) + Mobile (390px) screenshots
  - Page structure (sections, positions, classes)
  - Design tokens (CSS vars, fonts, colors)
  - Key element styles (h1, h2, p, CTA buttons)
  - Section HTML + text content
  - Image/asset manifest
  - Nav/header detection
  - Dark mode presence
  - Interaction sweep (clickable elements, hover states)
  - Lazy image resolution (scrolls to bottom)

Output: <output_dir>/docs/design-references/*.json + *.png
"""

import asyncio, json, os, sys, re
from playwright.async_api import async_playwright

async def extract_url(url: str, output_dir: str):
    """Run full extraction pipeline on a single URL."""
    os.makedirs(f"{output_dir}/docs/design-references", exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        # ── Desktop (1440px) ───────────────────────────────────
        print("[1/9] Desktop extraction (1440px)...")
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()
        await page.goto(url, wait_until="networkidle", timeout=45000)
        await page.wait_for_timeout(2000)

        # Screenshot
        await page.screenshot(path=f"{output_dir}/docs/design-references/desktop-full.png", full_page=True)

        # Page structure
        structure = await page.evaluate("""
            () => {
                const sections = [];
                const selectors = ['section', 'div[id]', 'header', 'footer', 'main', 'nav',
                    '[class*="hero"]', '[class*="banner"]', '[class*="section"]'];
                const seen = new Set();
                document.querySelectorAll(selectors.join(',')).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width < 200 || rect.height < 30) return;
                    const key = Math.round(rect.top / 10) * 10;
                    if (seen.has(key)) return; seen.add(key);
                    sections.push({
                        tag: el.tagName.toLowerCase(), id: el.id || '',
                        cls: (el.className || '').toString().slice(0, 120),
                        rect: {t: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height)},
                        text: (el.textContent || '').trim().slice(0, 150).replace(/\\s+/g, ' ')
                    });
                });
                sections.sort((a,b) => a.rect.t - b.rect.t);
                return sections;
            }
        """)
        write_json(f"{output_dir}/docs/design-references/page-structure.json", structure)

        # CSS variables
        css_vars = await page.evaluate("""
            () => {
                const s = getComputedStyle(document.documentElement);
                const vars = {};
                for (let i = 0; i < s.length; i++) {
                    const p = s[i];
                    if (p.startsWith('--')) vars[p] = s.getPropertyValue(p).trim();
                }
                return vars;
            }
        """)
        write_json(f"{output_dir}/docs/design-references/css-vars.json", css_vars)

        # Font detection
        fonts = await page.evaluate("""
            () => {
                const links = [];
                document.querySelectorAll('link[rel="stylesheet"]').forEach(l => { if (l.href) links.push(l.href); });
                const cs = getComputedStyle(document.body);
                return { fontLinks: links, bodyFont: cs.fontFamily, bodySize: cs.fontSize };
            }
        """)
        write_json(f"{output_dir}/docs/design-references/fonts.json", fonts)

        # Design tokens (key element styles)
        tokens = await page.evaluate("""
            () => {
                const get = (sel) => {
                    const el = document.querySelector(sel);
                    if (!el) return null;
                    const cs = getComputedStyle(el);
                    return {
                        color: cs.color, bg: cs.backgroundColor, font: cs.fontFamily,
                        size: cs.fontSize, weight: cs.fontWeight, lh: cs.lineHeight,
                        padding: cs.padding, borderRadius: cs.borderRadius
                    };
                };
                const result = {};
                document.querySelectorAll('h1, h2:first-of-type').forEach(el => {
                    const r = el.getBoundingClientRect();
                    if (r.top < 800 && r.top > 0) {
                        result['hero_heading'] = { text: el.textContent.trim().slice(0, 100), ...(cs => ({color: cs.color, size: cs.fontSize, weight: cs.fontWeight, font: cs.fontFamily}))(getComputedStyle(el)) };
                    }
                });
                document.querySelectorAll('a, button').forEach(el => {
                    const r = el.getBoundingClientRect();
                    if (r.top < 800 && r.top > 0 && r.height > 30 && r.width > 80) {
                        const cs = getComputedStyle(el);
                        if (cs.cursor === 'pointer' || el.textContent.toLowerCase().includes('start') || el.textContent.toLowerCase().includes('free') || el.textContent.toLowerCase().includes('sign')) {
                            result['cta_button'] = { text: el.textContent.trim().slice(0, 60), color: cs.color, bg: cs.backgroundColor, size: cs.fontSize, weight: cs.fontWeight, padding: cs.padding, borderRadius: cs.borderRadius };
                        }
                    }
                });
                for (const sel of ['h1','h2','h3','p','body','header','footer']){ const s = get(sel); if(s) result[sel] = s; }
                return result;
            }
        """)
        write_json(f"{output_dir}/docs/design-references/design-tokens.json", tokens)

        # Images
        images = await page.evaluate("""
            () => {
                const imgs = [];
                document.querySelectorAll('img').forEach(img => {
                    if (img.src) imgs.push({
                        src: (img.currentSrc || img.src).slice(0, 300),
                        lazySrc: img.dataset.src || img.dataset.lazy || null,
                        alt: (img.alt || '').slice(0, 150),
                        w: img.naturalWidth || img.width, h: img.naturalHeight || img.height
                    });
                });
                return imgs;
            }
        """)
        write_json(f"{output_dir}/docs/design-references/assets.json", images)

        # Section HTML
        sections_html = await page.evaluate("""
            () => {
                const sections = {};
                document.querySelectorAll('section, header, footer, main > div').forEach(s => {
                    const r = s.getBoundingClientRect();
                    if (r.height < 30) return;
                    const id = s.id || (s.className || '').toString().slice(0, 40).replace(/[^a-zA-Z0-9_-]/g, '_');
                    sections[id] = { html: s.outerHTML.slice(0, 5000), text: (s.textContent || '').trim().slice(0, 2000), tag: s.tagName };
                });
                return sections;
            }
        """)
        write_json(f"{output_dir}/docs/design-references/section-html.json", sections_html)

        # Nav/header detection
        nav = await page.evaluate("""
            () => {
                const candidates = [];
                const selectors = ['nav', '.navbar', '.header', 'header', '[role="navigation"]'];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) candidates.push({ selector: sel, tag: el.tagName, id: el.id, cls: (el.className || '').slice(0, 60), has_links: el.querySelectorAll('a').length });
                }
                const all = document.querySelectorAll('div, header');
                for (const el of all) {
                    const cs = getComputedStyle(el);
                    if ((cs.position === 'fixed' || cs.position === 'sticky') && parseInt(cs.top) === 0 && el.children.length > 3) {
                        candidates.push({ selector: 'sticky/fixed', tag: el.tagName, id: el.id, cls: (el.className || '').slice(0, 60), has_links: el.querySelectorAll('a').length });
                        break;
                    }
                }
                if (candidates.length > 0) {
                    const navEl = document.querySelector(candidates[0].selector);
                    if (navEl) {
                        const navCs = getComputedStyle(navEl);
                        const links = Array.from(navEl.querySelectorAll('a')).slice(0, 20).map(a => ({ text: a.textContent.trim().slice(0, 40), href: a.getAttribute('href') || '' }));
                        return { tag: navEl.tagName, h: navEl.offsetHeight, bg: navCs.backgroundColor, position: navCs.position, links };
                    }
                }
                return null;
            }
        """)
        if nav:
            write_json(f"{output_dir}/docs/design-references/nav-detail.json", nav)

        # Dark mode detection
        dark = await page.evaluate("""
            () => {
                const html = document.documentElement.outerHTML;
                const hasMedia = html.includes('prefers-color-scheme');
                const hasDarkClass = html.includes('class=\"dark\"') || html.includes('class=\\'dark\\'');
                const hasDataTheme = html.includes('data-theme=\"dark\"');
                return { media_query: hasMedia, dark_class: hasDarkClass, data_theme: hasDataTheme, detected: hasMedia || hasDarkClass || hasDataTheme };
            }
        """)
        write_json(f"{output_dir}/docs/design-references/dark-mode.json", dark)

        await ctx.close()

        # ── Mobile (390px) ──────────────────────────────────────
        print("[8/9] Mobile screenshot (390px)...")
        ctx_m = await browser.new_context(viewport={"width": 390, "height": 844})
        page_m = await ctx_m.new_page()
        await page_m.goto(url, wait_until="networkidle", timeout=45000)
        await page_m.wait_for_timeout(2000)
        await page_m.screenshot(path=f"{output_dir}/docs/design-references/mobile-full.png", full_page=True)
        await ctx_m.close()

        # ── Scroll for lazy images ──────────────────────────────
        print("[9/9] Lazy image resolution (scroll)...")
        ctx_l = await browser.new_context(viewport={"width": 1440, "height": 900})
        page_l = await ctx_l.new_page()
        await page_l.goto(url, wait_until="networkidle", timeout=45000)
        await page_l.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page_l.wait_for_timeout(3000)
        lazy_images = await page_l.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('img')).filter(i => i.src).map(i => ({
                    src: (i.currentSrc || i.src).slice(0, 300),
                    lazySrc: i.dataset.src || i.dataset.lazy || null,
                    loaded: i.complete && i.naturalWidth > 0
                }));
            }
        """)
        write_json(f"{output_dir}/docs/design-references/lazy-images-resolved.json", lazy_images)
        await ctx_l.close()

        await browser.close()
        print(f"✓ Full extraction complete → {output_dir}/docs/design-references/")


def write_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "docs", "research", re.sub(r'[^a-zA-Z0-9]', '-', url.replace('https://', '').replace('http://', '').rstrip('/')))

    await extract_url(url, output_dir)


if __name__ == "__main__":
    asyncio.run(main())

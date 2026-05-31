# Batch Site Testing Methodology

Empirical approach developed during clone-website-dl v2 development to validate edge case coverage across diverse sites.

## Purpose

When developing or updating a web extraction/clone skill, batch-testing 50+ diverse sites reveals edge cases that single-site testing misses. 3 rounds of 150 total tests uncovered 8 problems the skill didn't address.

## Methodology

### Site Selection (50 per round)
Pick diverse categories:
- Chinese tech (10): deepseek, zhipu, juejin, csdn, etc.
- Global SaaS (10): linear, notion, figma, vercel, etc.
- E-commerce/Travel (10): amazon, shopify, booking, agoda, etc.
- News/Media (10): wired, arstechnica, techcrunch, etc.
- Government/Education (10): whitehouse, gov.uk, mit, harvard, etc.
- Dev tools / UI libraries (10): vite, eslint, mantine, radix, etc.
- International variety (10): aljazeera, straitstimes, yonhap, etc.

### Extraction Test
```bash
curl -sL --max-time 8 "$URL" | head -c 30000
```

### Analysis Dimensions
For each site, check:
1. **HTML bytes received** — blocked/timeout marker
2. **Body content blocks** — `grep -Eo '>[^<]{200,}' | wc -l` (SPA vs SSR; portable on macOS and Linux)
3. **JS bundles** — `<script src="*.js">` count (>20 = heavy)
4. **CSS files** — external + local count, hashed filenames
5. **CSS variables** — `--var:` pattern count (design system indicator)
6. **Third-party services** — analytics, social, CDN count
7. **Cookie banners** — `cookie-consent|gdpr|ccpa|CookieNotice`
8. **Resource hints** — preconnect, preload, dns-prefetch
9. **Lazy images** — data-src, data-lazy, loading="lazy"
10. **Inline SVGs** — count (>30 = dedup needed)
11. **Google Fonts** — fonts.googleapis.com, fonts.gstatic.com
12. **Viewport meta** — `<meta name="viewport">` presence
13. **Frameworks** — Tailwind, Bootstrap, FontAwesome presence
14. **Image formats** — webp, avif usage
15. **Inline styles** — `<style>` block count
16. **Preconnects** — total resource hints

### Problem Aggregation
Collect all problems across sites, aggregate by frequency. Sort descending — the top problems at 30-40% frequency are the ones to address first.

### Script
Use `scripts/preflight-audit.sh <url>` for single-site analysis.
Use `execute_code` with the batch loop pattern for multi-site runs (see code in session transcripts).

# Real-World Extraction Knowledge Bank

> 50-site batch test (2026-05-31) — empirical failure modes and repair patterns.

## SPA Detection Thresholds

```
Content blocks (">[^<]{100,}") < 3   AND   Script tags > 5   → SPA
```

**Example results:** Linear (42 bundles, 0 content blocks), Figma (28 bundles, 0 blocks), Vercel (28 bundles, 1 block), Cursor (6 bundles, 0 blocks)

**Causes:** Next.js app router shell pages, React SPAs, Vite-built pages.

**Fix:** Fall back to Playwright headless browser → `page.content()` after `wait_until="networkidle"`.

## Sites That Work With Plain Curl

These return server-rendered HTML with actual content:

| Site | Type | Characteristics |
|------|------|----------------|
| nextjs.org | Docs | Static site generation |
| tailwindcss.com | Docs | Static site generation |
| github.com | Platform | Server-rendered |
| notion.so | SaaS | Hybrid rendering |
| html5up.net | Static | Plain HTML templates |

## Third-Party Embed Prevalence

32% of sites tested had third-party embeds. Watch for these URL patterns:

| Pattern | Type | Action |
|---------|------|--------|
| `facebook.com`, `twitter.com`, `linkedin.com` | Social widgets | Replace with static link |
| `google-analytics`, `gtag`, `googletagmanager` | Analytics | Skip entirely |
| `cloudflare`, `cdn.*`, `unpkg.com`, `cdnjs` | CDN assets | Download to local |
| `googleadservices`, `doubleclick` | Ads | Skip (not needed) |
| `hotjar`, `mixpanel`, `amplitude` | User analytics | Skip |

## Hash-Based CSS Filenames

Sites using build tools (Next.js, Vite, Webpack) emit CSS with content hashes:

```
4ed2fe305fed57cc.css    → Next.js CSS module hash
806c3349eef96975.css    → Next.js global CSS hash
```

These change on every deploy. Save as `main.css`, keep the original hash as a comment:
```css
/* Source: https://example.com/_next/static/css/4ed2fe305fed57cc.css */
```

## Design Token Extraction Verification

After downloading external CSS, verify you have real design tokens:

```bash
# Quick color palette
grep -Eo '#[0-9a-fA-F]{6}' *.css | sort -u
# Font families  
grep -Eo 'font-family:[[:space:]]*[^;]+' *.css | sort -u
# CSS custom properties
grep -Eo -- '--[[:alnum:]_-]+:[[:space:]]*[^;]+' *.css | sort -u
```

Common false positives to filter: `#000`, `#fff`, `#fff`, `transparent`, `inherit`, `initial`.

## Lazy-Loaded Image Detection

Patterns to scan for:
```bash
grep -Eo 'data-src="[^"]+"' page.html    # data-src attribute
grep -Eo 'data-lazy="[^"]+"' page.html   # data-lazy attribute
grep -Eo 'loading="lazy"' page.html      # loading=lazy native
grep -Eo 'data-srcset="[^"]+"' page.html # responsive images
```

Always use `data-src` (not `src`) for the real image URL when both exist.

## Inline SVG Dedup Strategy

Sites with many inline SVGs (Squarespace: 85, Supabase: 53): SVGs tend to be repeated icons with minor differences. Strategy:

1. Extract all `<svg>...</svg>` blocks
2. Group by `viewBox` attribute (same viewBox ≈ same icon)
3. Per group: pick the most complete version as the icon component
4. Name by visual function, not the rendered page section
5. Merge into ONE `src/components/icons.tsx` file

## Batch Test Pattern

To validate extraction on many sites at once:
```bash
sites=("url1" "url2" ...)
for url in "${sites[@]}"; do
  html=$(curl -sL --max-time 6 "$url" 2>/dev/null)
  blocks=$(printf '%s' "$html" | grep -Eo '>[^<]{100,}' | wc -l | tr -d ' ')
  scripts=$(printf '%s' "$html" | grep -Eo '<script[^>]*src=' | wc -l | tr -d ' ')
  echo "$url → content=$blocks scripts=$scripts"
done
```

This catches: rate limiting, SPA detection, redirect chains, and empty responses in one pass.

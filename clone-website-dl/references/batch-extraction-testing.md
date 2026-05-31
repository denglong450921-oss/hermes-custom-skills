# Batch Extraction Testing Methodology

> Developed through 5 rounds of testing on 250 websites (2026-05-31).
> Goal: systematically discover edge cases in website extraction/cloning by testing at scale.

## Why Batch Test

Single-site testing misses patterns that only emerge at scale. Batch testing reveals:
- Which edge cases affect 1% vs 40% of sites (prioritize fixes)
- Which sites make good extraction targets (server-rendered, clean HTML)
- Which extraction methods work for different site types (SPA vs static vs SSR)

## Target Selection

Pick 50 diverse sites covering these categories:

| Category | Sites | Examples |
|----------|-------|----------|
| Chinese tech | 8-10 | deepseek, zhipu, juejin, csdn |
| SaaS/Startup | 8-10 | linear, notion, vercel, sentry |
| E-commerce | 5-8 | shopify, amazon, nike |
| Framework docs | 5-8 | react.dev, vuejs.org, nextjs.org |
| UI libraries | 5-8 | mantine, chakra, radix-ui, ant.design |
| News/Media | 5-8 | techcrunch, wired, arstechnica |
| Government/Education | 3-5 | mit.edu, gov.uk, canada.ca |
| Creative/Design | 3-5 | behance, awwwards, codrops |

## Extraction Script

```bash
# Single-site extraction test
URL="https://example.com"
HTML=$(curl -sL --max-time 6 "$URL" 2>/dev/null | head -c 40000)
SIZE=${#HTML}

if [ "$SIZE" -lt 200 ]; then
  echo "BLOCKED or empty ($SIZE bytes)"
  exit 1
fi

# Analysis checks
echo "=== Size: $SIZE bytes ==="
echo "JS bundles: $(printf '%s' "$HTML" | grep -Ec '<script[^>]*src="[^"]*\.(js|mjs)')"
echo "CSS files: $(printf '%s' "$HTML" | grep -Ec '<link[^>]*rel="stylesheet"')"
echo "Lazy images: $(printf '%s' "$HTML" | grep -Ec 'data-src|data-lazy|loading="lazy"')"
echo "Inline SVGs: $(printf '%s' "$HTML" | grep -Ec '<svg[^>]*>')"
echo "Third-party: $(printf '%s' "$HTML" | grep -Ec '(facebook|twitter|google-analytics|gtag|cloudflare)')"
echo "Cookie banner: $(printf '%s' "$HTML" | grep -Eic '(cookie-consent|gdpr|ccpa)')"
echo "CSS variables: $(printf '%s' "$HTML" | grep -Ec -- '--[[:alnum:]_-]+:')"
echo "Viewport meta: $(printf '%s' "$HTML" | grep -Ec '<meta[^>]*name="viewport"')"
echo "Dark mode: $(printf '%s' "$HTML" | grep -Ec '(prefers-color-scheme|\.dark[[:space:]]*\{)')"
echo "Anim libs: $(printf '%s' "$HTML" | grep -Ec '(gsap|framer-motion|lottie|three\.)')"
echo "Inline events: $(printf '%s' "$HTML" | grep -Ec '[[:space:]]on[[:alnum:]_]+[[:space:]]*=')"
echo "!important: $(printf '%s' "$HTML" | grep -Ec '!important')"
```

## Data Recording

For each batch, record results in a TSV:

```tsv
site_id	status	size	js	css	lazy	svg	3rd_party	problems
01-deepseek	ISSUES	48518	11	0	2	6	12	3rd-party=12
```

## Pattern Analysis

After each batch, aggregate problem frequencies:

```python
from collections import Counter
problem_counts = Counter()
for site in results:
    for problem in site['problems']:
        cat = problem.split('=')[0]
        problem_counts[cat] += 1

print(f"Problem frequency (across {N} accessible sites):")
for cat, count in problem_counts.most_common():
    pct = count / accessible * 100
    bar = '█' * max(1, count // 2)
    print(f"  {cat:<30} {count:3d}/{N:2d} ({pct:3.0f}%) {bar}")
```

## Known Findings (250-site aggregate)

| Problem | Rate | Priority |
|---------|------|----------|
| Third-party embeds | 19% | HIGH — detect & skip |
| Cookie banners | 16% | HIGH — detect & remove |
| No viewport meta | 14% | MEDIUM — safe default |
| Google Fonts | 12% | MEDIUM — next/font conversion |
| SPA / JS-rendered | 12% | HIGH — headless browser required |
| Dark/light mode | 26% | HIGH — dual CSS variable blocks |
| Animation libraries | 16% | MEDIUM — extract + convert to CSS |
| !important usage | 28% | LOW — Tailwind ! modifier |
| Preconnect hints | 9% | LOW — keep first-party only |
| Hash CSS filenames | 10% | LOW — save as main.css |
| CSS vars (100+) | 4% | LOW — automated grep extraction |
| Inline style blocks | 13% | LOW — extract and merge |

## Cleanest Clone Targets (server-rendered, minimal deps)

nextjs.org, tailwindcss.com, github.com, getbootstrap.com, bulma.io, svelte.dev, solidjs.com, primevue.org, getbootstrap.com, agoda.com, expedia.com, wired.com, mit.edu, gov.sg, amazon.com, ibm.com, sendgrid.com, pocketbase.io, fly.io, appwrite.io

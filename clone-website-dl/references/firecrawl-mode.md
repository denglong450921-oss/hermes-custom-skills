# Firecrawl Extraction Mode

When Camofox browser MCP is unavailable, use Firecrawl MCP as fallback extraction.

## When to Use
- Camofox server not running / unreachable
- URL is accessible but browser MCP tools fail
- User explicitly requests Firecrawl for speed

## Limitations
- No getComputedStyle() — CSS values are inferred (less precise)
- No interaction sweep — behaviors must be described generically
- No multi-state extraction — only the default loaded state is captured
- **SPA sites will fail** — sites rendered entirely by JS (Linear, Figma, Vercel) return empty HTML with curl. Must use Camofox or Playwright for these.
- Best for: layout structure, content, assets. NOT for pixel-perfect CSS or SPAs.

## SPA Detection (Run First)
If the target is a modern JS-heavy site, curl/HTML extraction will return empty HTML:
```bash
HTML=$(curl -sL --max-time 5 "$URL")
BODY_BLOCKS=$(printf '%s' "$HTML" | grep -Eo '>[^<]{100,}' | wc -l | tr -d ' ')
SCRIPT_TAGS=$(printf '%s' "$HTML" | grep -Eo '<script[^>]*src=' | wc -l | tr -d ' ')
if [ "$BODY_BLOCKS" -lt 3 ] && [ "$SCRIPT_TAGS" -gt 5 ]; then
  echo "SPA detected — Firecrawl mode cannot extract content. Use Camofox or Playwright."
  exit 1
fi
```

## Pipeline Adaptations

### Phase 1: Reconnaissance (Firecrawl Mode)
1. **Scrape HTML:** `curl -sL <URL>` or Firecrawl MCP — save raw HTML
2. **Extract inline styles:** Parse `<style>` blocks for CSS variables and rules
3. **Download external CSS:** For each `<link rel="stylesheet">`, download the file and extract:
   - CSS custom properties (`--color-*`, `--font-*`, `--spacing-*`)
   - Color values (`#hex`, `rgb()`, `rgba()`) from `.body`, `h1`, `a` selectors
   - Font families from `font-family` declarations
   - **Hash-based filenames:** If CSS filename contains a hash (e.g., `4ed2fe305fed57cc.css`), it's likely a build artifact. Save as `main.css` instead and note the hash in a comment for traceability.
   ```bash
   curl -sL "https://example.com/assets/css/main.css" > docs/research/external.css
   grep -E "(color|font-family|--)" docs/research/external.css | head -40
   ```
4. **Take screenshots** via screenshot.py (Playwright) — for layout reference:
   ```bash
   python3 ~/.hermes/skills/web/html-to-png/scripts/screenshot.py page.html --output docs/design-references/fullpage.png
   ```
5. **Mark interaction model** as "unknown — Firecrawl mode (no behavior data)"
6. **Write PAGE_TOPOLOGY.md** with caveat: "CSS values are heuristic — verify with browser DevTools"
7. **Handle lazy-loading:** Scan for `data-src`, `data-lazy`, `loading="lazy"` attributes. Build a separate asset list for download.

### Phase 2-5: Same as Camofox mode
Foundation → Component Spec → Dispatch Builders → Assembly → QA
CSS values will use the heuristic values from Firecrawl extraction.
Builder prompts must note: "CSS values are approximate — verify with original site."

## Decision
After Phase 1 (Firecrawl mode), ask user: "Firecrawl mode used — CSS values are approximate. Proceed with best-effort clone? (y/n)"

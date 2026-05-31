#!/bin/bash
# preflight-audit.sh — Analyze a target URL before cloning
# Usage: bash scripts/preflight-audit.sh <url>
# Returns JSON with extraction mode recommendation and problem list
# Based on 150-site empirical testing

URL="$1"
if [ -z "$URL" ]; then
  echo '{"error":"Usage: preflight-audit.sh <url>","status":"error"}'
  exit 1
fi

URL=$(echo "$URL" | sed 's|^//|https://|; s|^http:|https:|')

echo "{\"url\":\"$URL\",\"checks\":{"

# Fetch HTML
HTML=$(curl -sL --max-time 8 "$URL" 2>/dev/null)
BYTES=$(echo "$HTML" | wc -c | tr -d ' ')
echo "\"html_bytes\":$BYTES,"

# SPA detection: body content blocks vs script bundles
BODY_BLOCKS=$(printf '%s' "$HTML" | grep -Eo '>[^<]{200,}' | wc -l | tr -d ' ')
SCRIPT_BUNDLES=$(printf '%s' "$HTML" | grep -Eo '<script[^>]*src="[^"]*\.(js|mjs)' | wc -l | tr -d ' ')
SPA=0
if [ "$BODY_BLOCKS" -lt 2 ] && [ "$SCRIPT_BUNDLES" -gt 5 ]; then SPA=1; fi
echo "\"spa_detected\":$SPA,"
echo "\"body_content_blocks\":$BODY_BLOCKS,"
echo "\"js_bundles\":$SCRIPT_BUNDLES,"

# CSS analysis
CSS_EXTERNAL=$(printf '%s' "$HTML" | grep -Eo '<link[^>]*rel="stylesheet"[^>]*href="https?://' | wc -l | tr -d ' ')
CSS_LOCAL=$(printf '%s' "$HTML" | grep -Eo '<link[^>]*rel="stylesheet"[^>]*href="/[^"]+' | wc -l | tr -d ' ')
CSS_HASHED=$(printf '%s' "$HTML" | grep -Eo '<link[^>]*href="[^"]*\.[a-f0-9]{8,}\.css"' | wc -l | tr -d ' ')
CSS_VARS=$(printf '%s' "$HTML" | grep -Eo -- '--[[:alnum:]_-]+:[[:space:]]' | wc -l | tr -d ' ')
echo "\"css_external\":$CSS_EXTERNAL,"
echo "\"css_local\":$CSS_LOCAL,"
echo "\"css_hashed\":$CSS_HASHED,"
echo "\"css_variables\":$CSS_VARS,"

# Third-party detection
THIRD_PARTY=$(printf '%s' "$HTML" | grep -Eo '(facebook\.com|twitter\.com|x\.com|google-analytics|gtag|googletagmanager|cloudflare|unpkg\.com|cdnjs|hotjar|intercom|segment\.com|amplitude|doubleclick|googlesyndication)' | sort -u | wc -l | tr -d ' ')
echo "\"third_party_services\":$THIRD_PARTY,"

# Cookie banner
COOKIE=$(printf '%s' "$HTML" | grep -Eio '(cookie-consent|gdpr|ccpa|cookie-banner|CookieNotice)' | wc -l | tr -d ' ')
COOKIE_PRESENT=0
if [ "$COOKIE" -gt 0 ]; then COOKIE_PRESENT=1; fi
echo "\"cookie_banner\":$COOKIE_PRESENT,"

# Resource hints
PRECONNECTS=$(printf '%s' "$HTML" | grep -Eo 'rel="(preconnect|preload|dns-prefetch)"' | wc -l | tr -d ' ')
echo "\"resource_hints\":$PRECONNECTS,"

# Lazy images
LAZY=$(printf '%s' "$HTML" | grep -Eo 'data-src|data-lazy|loading="lazy"' | wc -l | tr -d ' ')
echo "\"lazy_images\":$LAZY,"

# Inline SVGs
INLINE_SVG=$(printf '%s' "$HTML" | grep -Eo '<svg[^>]*>' | wc -l | tr -d ' ')
echo "\"inline_svgs\":$INLINE_SVG,"

# Google Fonts
GF=$(printf '%s' "$HTML" | grep -Eo 'fonts\.(googleapis|gstatic)' | wc -l | tr -d ' ')
echo "\"google_fonts\":$GF,"

# Viewport meta
HAS_VIEWPORT=$(printf '%s' "$HTML" | grep -Eq '<meta[^>]*name="viewport"' && echo 1 || echo 0)
echo "\"has_viewport_meta\":$HAS_VIEWPORT,"

# Frameworks
echo -n "\"frameworks\":{"
FW=()
echo "$HTML" | grep -qi 'tailwind' && FW+=('"tailwind":true') || FW+=('"tailwind":false')
echo -n "${FW[0]}"
FW2=$(echo "$HTML" | grep -qi 'bootstrap' && echo ', "bootstrap":true' || echo ', "bootstrap":false')
echo -n "$FW2"
FW3=$(printf '%s' "$HTML" | grep -Eqi '(font-awesome|fontawesome)' && echo ', "fontawesome":true' || echo ', "fontawesome":false')
echo -n "$FW3"
echo "},"

# Image formats
echo -n "\"image_formats\":{"
echo "$HTML" | grep -q '\.webp' && echo -n '"webp":true' || echo -n '"webp":false'
echo "$HTML" | grep -q '\.avif' && echo -n ', "avif":true' || echo -n ', "avif":false'
echo "},"

# Recommendation
echo -n "\"recommendation\":"
if [ "$SPA" -eq 1 ]; then
  echo -n '"SPA — Use Camofox or Playwright headless browser. curl-only extraction will return empty HTML."'
elif [ "$BYTES" -gt 5000 ] && [ "$SCRIPT_BUNDLES" -lt 10 ]; then
  echo -n '"HTML-only extraction OK. Use Firecrawl fallback or curl."'
else
  echo -n '"Mixed — prefer Camofox for best results, curl for content structure."'
fi

echo ",\"problems\":["
FIRST=1
if [ "$SPA" -eq 1 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"SPA: $SCRIPT_BUNDLES bundles, $BODY_BLOCKS content blocks\""
fi
if [ "$THIRD_PARTY" -gt 3 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"$THIRD_PARTY third-party services\""
fi
if [ "$COOKIE_PRESENT" -eq 1 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"cookie consent banner detected\""
fi
if [ "$CSS_HASHED" -gt 0 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"$CSS_HASHED hashed CSS files\""
fi
if [ "$CSS_VARS" -gt 100 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"$CSS_VARS CSS variables (design system)\""
fi
if [ "$LAZY" -gt 5 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"$LAZY lazy-loaded images\""
fi
echo "]}}"

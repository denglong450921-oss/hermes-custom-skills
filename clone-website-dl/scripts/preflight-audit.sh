#!/bin/bash
# preflight-audit.sh — Analyze a target URL before cloning
# Usage: bash scripts/preflight-audit.sh <url>
# Returns JSON with extraction mode recommendation and problem list
# Based on 300-site empirical testing

URL="$1"
if [ -z "$URL" ]; then
  echo '{"error":"Usage: preflight-audit.sh <url>","status":"error"}'
  exit 1
fi

URL=$(echo "$URL" | sed 's|^//|https://|')

echo "{\"url\":\"$URL\",\"checks\":{"

# Fetch HTML with retry for rate-limited/blocked sites
TMP_BODY=$(mktemp)
trap 'rm -f "$TMP_BODY"' EXIT
CURL_META=$(curl -sSL --max-time 8 -o "$TMP_BODY" -w '%{http_code}\\t%{url_effective}\\t%{content_type}' "$URL" 2>/dev/null)
CURL_RC=$?
HTTP_CODE=$(printf '%s' "$CURL_META" | cut -f1)

# Retry with different user-agent on 403/503/429 or empty
if [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "503" ] || [ "$HTTP_CODE" = "429" ] || [ -z "$HTTP_CODE" ]; then
  CURL_META=$(curl -sSL --max-time 8 -o "$TMP_BODY" \
    -A 'Mozilla/5.0 (compatible; PreflightBot/1.0; +https://hermes-agent.ai)' \
    -w '%{http_code}\\t%{url_effective}\\t%{content_type}' "$URL" 2>/dev/null)
  CURL_RC=$?
  HTTP_CODE=$(printf '%s' "$CURL_META" | cut -f1)
fi
EFFECTIVE_URL=$(printf '%s' "$CURL_META" | cut -f2)
CONTENT_TYPE=$(printf '%s' "$CURL_META" | cut -f3-)
HTML=$(cat "$TMP_BODY")
BYTES=$(wc -c < "$TMP_BODY" | tr -d ' ')
FETCH_OK=1
if [ -z "$HTTP_CODE" ] || [ "$HTTP_CODE" -lt 200 ] || [ "$HTTP_CODE" -ge 400 ] || [ "$BYTES" -lt 200 ]; then
  FETCH_OK=0
fi
PARTIAL_FETCH=0
if [ "$FETCH_OK" -eq 1 ] && [ "$CURL_RC" -ne 0 ]; then
  PARTIAL_FETCH=1
fi
echo "\"fetch_ok\":$FETCH_OK,"
echo "\"partial_fetch\":$PARTIAL_FETCH,"
echo "\"curl_exit_code\":$CURL_RC,"
echo "\"http_status\":\"${HTTP_CODE:-000}\","
echo "\"html_bytes\":$BYTES,"

# SPA detection: body content blocks vs script bundles
BODY_BLOCKS=$(printf '%s' "$HTML" | grep -Eo '>[^<]{200,}' | wc -l | tr -d ' ')
SCRIPT_BUNDLES=$(printf '%s' "$HTML" | grep -Eio '<script[^>]*src[[:space:]]*=[[:space:]]*[^[:space:]>]*\.(js|mjs)' | wc -l | tr -d ' ')
SPA=0
if [ "$BODY_BLOCKS" -lt 2 ] && [ "$SCRIPT_BUNDLES" -gt 5 ]; then SPA=1; fi
echo "\"spa_detected\":$SPA,"
echo "\"body_content_blocks\":$BODY_BLOCKS,"
echo "\"js_bundles\":$SCRIPT_BUNDLES,"

# CSS analysis
STYLESHEET_LINKS=$(printf '%s' "$HTML" | grep -Eio '<link[^>]*>' | grep -Ei 'rel[[:space:]]*=[[:space:]]*[^[:space:]>]*stylesheet' || true)
CSS_EXTERNAL=$(printf '%s' "$STYLESHEET_LINKS" | grep -Eic 'href[[:space:]]*=[[:space:]]*[^[:space:]>]*https?://' || true)
CSS_LOCAL=$(printf '%s' "$STYLESHEET_LINKS" | grep -Eic 'href[[:space:]]*=[[:space:]]*[^[:space:]>]*/' || true)
CSS_HASHED=$(printf '%s' "$STYLESHEET_LINKS" | grep -Eic '\.[a-f0-9]{8,}\.css' || true)
CSS_VARS=$(printf '%s' "$HTML" | grep -Eo -- '--[[:alnum:]_-]+:[[:space:]]' | wc -l | tr -d ' ')
INLINE_STYLES=$(printf '%s' "$HTML" | grep -Eio '<style([[:space:]>])' | wc -l | tr -d ' ')
echo "\"css_external\":$CSS_EXTERNAL,"
echo "\"css_local\":$CSS_LOCAL,"
echo "\"css_hashed\":$CSS_HASHED,"
echo "\"css_variables\":$CSS_VARS,"
echo "\"inline_style_blocks\":$INLINE_STYLES,"

# Third-party detection
THIRD_PARTY=$(printf '%s' "$HTML" | grep -Eio '(facebook\.com|twitter\.com|x\.com|google-analytics|gtag|googletagmanager|cloudflare|unpkg\.com|cdnjs|hotjar|intercom|segment\.com|amplitude|doubleclick|googlesyndication)' | sort -u | wc -l | tr -d ' ')
echo "\"third_party_services\":$THIRD_PARTY,"

# Cookie banner
COOKIE=$(printf '%s' "$HTML" | grep -Eio '(cookie-consent|gdpr|ccpa|cookie-banner|CookieNotice)' | wc -l | tr -d ' ')
COOKIE_PRESENT=0
if [ "$COOKIE" -gt 0 ]; then COOKIE_PRESENT=1; fi
echo "\"cookie_banner\":$COOKIE_PRESENT,"

# Resource hints
PRECONNECTS=$(printf '%s' "$HTML" | grep -Eio 'rel[[:space:]]*=[[:space:]]*[^[:space:]>]*(preconnect|preload|dns-prefetch)' | wc -l | tr -d ' ')
echo "\"resource_hints\":$PRECONNECTS,"

# Lazy images
LAZY=$(printf '%s' "$HTML" | grep -Eio 'data-src|data-lazy|loading[[:space:]]*=[[:space:]]*[^[:space:]>]*lazy' | wc -l | tr -d ' ')
echo "\"lazy_images\":$LAZY,"

# Inline SVGs
INLINE_SVG=$(printf '%s' "$HTML" | grep -Eio '<svg[^>]*>' | wc -l | tr -d ' ')
echo "\"inline_svgs\":$INLINE_SVG,"

# Google Fonts
GF=$(printf '%s' "$HTML" | grep -Eio 'fonts\.(googleapis|gstatic)' | wc -l | tr -d ' ')
echo "\"google_fonts\":$GF,"

# Viewport meta
HAS_VIEWPORT=$(printf '%s' "$HTML" | grep -Ei '<meta[^>]*name[[:space:]]*=[[:space:]]*[^[:space:]>]*viewport' >/dev/null && echo 1 || echo 0)
echo "\"has_viewport_meta\":$HAS_VIEWPORT,"

# Global UI patterns
DARK_MODE=$(printf '%s' "$HTML" | grep -Eio '(prefers-color-scheme|\.dark[[:space:]]*\{|data-theme[[:space:]]*=[[:space:]]*[^[:space:]>]*dark)' | wc -l | tr -d ' ')
ANIM_LIBS=$(printf '%s' "$HTML" | grep -Eio '(gsap|framer-motion|lottie|three\.js|data-aos)' | wc -l | tr -d ' ')
IMPORTANT=$(printf '%s' "$HTML" | grep -Eio '!important' | wc -l | tr -d ' ')
echo "\"dark_mode_markers\":$DARK_MODE,"
echo "\"animation_library_markers\":$ANIM_LIBS,"
echo "\"important_rules\":$IMPORTANT,"

# Frameworks
echo -n "\"frameworks\":{"
FW=()
printf '%s' "$HTML" | grep -i 'tailwind' >/dev/null && FW+=('"tailwind":true') || FW+=('"tailwind":false')
echo -n "${FW[0]}"
FW2=$(printf '%s' "$HTML" | grep -i 'bootstrap' >/dev/null && echo ', "bootstrap":true' || echo ', "bootstrap":false')
echo -n "$FW2"
FW3=$(printf '%s' "$HTML" | grep -Ei '(font-awesome|fontawesome)' >/dev/null && echo ', "fontawesome":true' || echo ', "fontawesome":false')
echo -n "$FW3"
echo "},"

# Image formats
echo -n "\"image_formats\":{"
printf '%s' "$HTML" | grep -i '\.webp' >/dev/null && echo -n '"webp":true' || echo -n '"webp":false'
printf '%s' "$HTML" | grep -i '\.avif' >/dev/null && echo -n ', "avif":true' || echo -n ', "avif":false'
echo "},"

# Recommendation
echo -n "\"recommendation\":"
if [ "$FETCH_OK" -eq 0 ]; then
  echo -n '"Fetch failed or returned an empty response. Check URL accessibility before selecting an extraction mode."'
elif [ "$SPA" -eq 1 ]; then
  echo -n '"SPA — Use Camofox or Playwright headless browser. curl-only extraction will return empty HTML."'
elif [ "$BYTES" -gt 5000 ] && [ "$SCRIPT_BUNDLES" -lt 10 ]; then
  echo -n '"HTML-only extraction OK. Use Firecrawl fallback or curl."'
else
  echo -n '"Mixed — prefer Camofox for best results, curl for content structure."'
fi

echo ",\"problems\":["
FIRST=1
if [ "$FETCH_OK" -eq 0 ] && [ "$CURL_RC" -ne 0 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"curl failed with exit code $CURL_RC\""
fi
if [ "$PARTIAL_FETCH" -eq 1 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"partial HTML response: curl exit code $CURL_RC after $BYTES bytes\""
fi
if [ "$CURL_RC" -eq 0 ] && [ -n "$HTTP_CODE" ] && { [ "$HTTP_CODE" -lt 200 ] || [ "$HTTP_CODE" -ge 400 ]; }; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"HTTP status $HTTP_CODE\""
fi
if [ "$BYTES" -lt 200 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"empty or tiny HTML response: $BYTES bytes\""
fi
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
if [ "$INLINE_SVG" -gt 30 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"$INLINE_SVG inline SVGs (deduplicate icons)\""
fi
if [ "$FETCH_OK" -eq 1 ] && [ "$HAS_VIEWPORT" -eq 0 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"viewport meta missing\""
fi
if [ "$DARK_MODE" -gt 0 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"dark mode markers detected\""
fi
if [ "$ANIM_LIBS" -gt 0 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"animation library markers detected\""
fi
if [ "$IMPORTANT" -gt 10 ]; then
  [ "$FIRST" -eq 1 ] || echo ","; FIRST=0
  echo -n "\"$IMPORTANT !important rules\""
fi
echo "]}}"

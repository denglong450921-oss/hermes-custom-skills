# Web Content Sourcing — Chinese Platforms

When the user provides a URL to a Chinese platform (WeChat, Zhihu, etc.) and asks you to render it as HTML, you often hit an anti-bot wall. This reference captures tested extraction techniques.

## WeChat Official Account (mp.weixin.qq.com)

### The Problem

WeChat articles serve a verification page when accessed directly via curl or browser automation. The page shows "环境异常" (environment anomaly) and requires a CAPTCHA.

### The Workaround

**curl with MicroMessenger User-Agent + Python regex extraction:**

```bash
curl -sL -A "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43" "https://mp.weixin.qq.com/s/<ARTICLE_ID>" | python3 -c "
import sys, re
html = sys.stdin.read()
match = re.search(r'id=\"js_content\"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if match:
    content = match.group(1)
    text = re.sub(r'<[^>]+>', '\n', content)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    print(text)
"
```

### Key details

- **User-Agent must mimic iPhone + MicroMessenger** — desktop UAs trigger the verification page
- **Alternative: plain iPhone Safari UA also works** — `Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1` has also been proven to bypass the wall. Try MicroMessenger first, fall back to plain Safari.
- **The article content is in `id="js_content"`** — a hidden div that's injected server-side even behind the verification wall
- **The regex searches for `</div>\s*<script`** as the closing boundary, because a trailing `<script>` block follows the content div
- The fetched page is ~3.5MB (includes CSS/JS/framework), but the article text extract is ~260KB of HTML

### Pitfalls

- `grep -P` does NOT work on macOS (use Python regex instead)
- Some WeChat articles use additional encoding (HTML entities) that need decoding
- The `id="js_content"` might have additional attributes — use `id=\"js_content\"[^>]*>` in the regex to handle this
- Rate limiting: multiple rapid requests may trigger stricter CAPTCHA

## General principle for Chinese content platforms

1. Try mobile User-Agent first — many anti-bot checks are relaxed for mobile browsers
2. For WeChat specifically, the MicroMessenger UA string is the key to bypassing the verification wall
3. The content is often in the HTML even when the verification page is shown — search for content-bearing elements by ID rather than trying to render the page
4. Consider using `https://archive.is/` or similar caching services as a fallback if direct extraction fails
5. **For very long articles, use a two-pass strategy**: first pipe through `head -500` to confirm the extraction pattern matches and to get OG metadata (title/description), then do a full extraction targeting `js_content` specifically. This prevents truncated output from overwhelming analysis.

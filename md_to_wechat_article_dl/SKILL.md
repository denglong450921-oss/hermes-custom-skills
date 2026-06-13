---
name: md_to_wechat_article_dl
description: Convert Markdown files to beautifully formatted, WeChat-compatible HTML articles. Follows Chinese typography best practices for WeChat Official Account articles. Use when you have a Markdown file (especially long-form Chinese content) that needs to become a WeChat article with professional formatting. Handles YAML frontmatter, headings, lists, blockquotes, code blocks, tables, images, and bold/italic text. Output is pure inline CSS — ready for wechat_article_push_dl.
contract_version: "1.0"
---

# md_to_wechat_article_dl

Convert Markdown → WeChat-compatible HTML with professional Chinese typography. This skill automates the formatting principles described in the reference article (6000-char WeChat formatting guide).

## Quick Start

```bash
# Convert a markdown file to WeChat HTML
python3 scripts/convert.py /path/to/article.md -o /path/to/output.html

# Convert and show the output path
python3 scripts/convert.py article.md -o article.html
echo "Output: article.html"
```

## Design Principles (from reference article)

This skill follows the WeChat typography rules from the 6000-char guide:

| Principle | Implementation |
|-----------|---------------|
| Body font size | 15px (comfortable reading) |
| Body text color | #595959 (soft black, not pure #000) |
| Line height | 1.75 (breathing room) |
| Letter spacing | 0.5px (not too dense) |
| Side margins | 16px padding on mobile |
| Section spacing | 24px between sections |
| Heading color | #1a1a2e (dark, distinct from body) |
| Accent color | #e8633a (for emphasis) |
| Image spacing | 12px margin top/bottom |
| Blockquote style | Left border accent + light background |
| Code blocks | Monospace + light gray background |
| Max width | 680px centered |

## Input Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Markdown file path | `string` | Yes | Path to .md file |
| Output path | `string` | Yes | Where to save the .html file |
| Title/override | `string` | No | Override YAML frontmatter title |
| Cover image | `string` | No | Auto-extract first image as cover hint |

## Preconditions

- Python 3 available with `markdown` library:
  ```bash
  pip3 install markdown
  ```
- Input .md file exists and is readable
- Output directory exists

## Process

1. **Read** the markdown file and parse YAML frontmatter (title, author, date, tags).
2. **Convert** markdown body to HTML using the Python markdown library with `fenced_code` and `tables` extensions.
3. **Wrap** the HTML in a WeChat-compatible template with inline CSS (never `<style>` blocks).
4. **Apply** Chinese typography: proper font sizes, colors, spacing per the reference article.
5. **Save** the output to the specified path.
6. **Report** the output path and extracted metadata.

## Bundled Script

The `scripts/convert.py` script handles the deterministic conversion:

```python
# Usage: python3 scripts/convert.py <input.md> -o <output.html> [--title TITLE]

import re, json, sys, os
from markdown import markdown as md_convert

def parse_frontmatter(text):
    \"\"\"Extract YAML frontmatter and body.\"\"\"
    m = re.match(r'^---\\s*\\n(.*?)\\n---\\s*\\n(.*)', text, re.DOTALL)
    if not m:
        return {}, text
    yaml_text, body = m.group(1), m.group(2)
    meta = {}
    for line in yaml_text.split('\\n'):
        kv = re.match(r'^(\\w+):\\s*(.+)$', line)
        if kv:
            meta[kv.group(1)] = kv.group(2).strip('\\"\\'')
    return meta, body

def wechat_html(body_html, meta, title_override=None):
    \"\"\"Wrap HTML body in WeChat-compatible template with inline CSS.\"\"\"
    title = title_override or meta.get('title', 'Article')
    author = meta.get('author', '')
    date = meta.get('date', '')
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;font-family:-apple-system,'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans SC',sans-serif;background:#f8f6f3;color:#595959;line-height:1.75;font-size:15px;letter-spacing:0.5px;">

<div style="max-width:680px;margin:0 auto;padding:24px 16px;background:#fff;">

<!-- Header -->
<div style="margin-bottom:24px;">
  <h1 style="font-size:22px;font-weight:700;color:#1a1a2e;margin:0 0 8px 0;line-height:1.4;">{title}</h1>
  {('<p style="color:#999;font-size:13px;margin:0;">' + author + (' · ' + date if date else '') + '</p>') if author else ''}
</div>

<!-- Body -->
{body_html}

<!-- Footer -->
<p style="text-align:center;color:#ccc;font-size:12px;margin-top:32px;padding-top:16px;border-top:1px solid #eee;">
  {'© ' + author if author else ''}
</p>

</div>
</body>
</html>'''

def convert_markdown_to_wechat(md_text):
    \"\"\"Convert markdown to WeChat-safe HTML.\"\"\"
    # Markdown extensions
    extensions = ['fenced_code', 'tables', 'codehilite', 'nl2br']
    
    # Convert
    html = md_convert(md_text, extensions=extensions)
    
    # Post-process: ensure all styles are inline-safe
    # Replace any <style> tags with inline alternatives
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # Style tags inline
    style_map = {
        'h1': 'font-size:22px;font-weight:700;color:#1a1a2e;margin:20px 0 12px 0;line-height:1.4;',
        'h2': 'font-size:18px;font-weight:700;color:#1a1a2e;margin:24px 0 12px 0;line-height:1.4;',
        'h3': 'font-size:16px;font-weight:600;color:#333;margin:18px 0 8px 0;',
        'p': 'margin:0 0 12px 0;color:#595959;',
        'strong': 'font-weight:700;color:#1a1a2e;',
        'em': 'font-style:italic;',
        'ul': 'padding-left:20px;margin:0 0 12px 0;',
        'ol': 'padding-left:20px;margin:0 0 12px 0;',
        'li': 'margin-bottom:6px;color:#595959;line-height:1.6;',
        'blockquote': 'margin:12px 0;padding:12px 16px;background:#f8f6f3;border-left:4px solid #e8633a;color:#666;font-size:14px;line-height:1.6;',
        'code': 'font-family:"SF Mono","Fira Code","Consolas",monospace;background:#f0eee8;padding:2px 6px;border-radius:3px;font-size:13px;color:#c8406a;',
        'pre': 'margin:12px 0;padding:14px 16px;background:#f8f6f3;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.5;',
        'pre code': 'background:none;padding:0;border-radius:0;color:#333;font-size:13px;',
        'img': 'max-width:100%;height:auto;display:block;margin:16px auto;border-radius:6px;',
        'table': 'width:100%;border-collapse:collapse;margin:12px 0;font-size:14px;',
        'th': 'background:#f0eee8;padding:8px 10px;text-align:left;font-weight:600;color:#1a1a2e;border-bottom:2px solid #e0ddd8;',
        'td': 'padding:8px 10px;border-bottom:1px solid #e0ddd8;color:#595959;',
        'hr': 'border:none;border-top:1px solid #e0ddd8;margin:24px 0;',
        'a': 'color:#e8633a;text-decoration:none;',
    }
    
    for tag, style in style_map.items():
        # Apply to opening tags without existing style
        html = re.sub(
            f'<{tag}(\\s[^>]*?)?>',
            lambda m: f'<{tag}{m.group(1) or ""} style="{style}">',
            html
        )
    
    return html

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', required=True, help='Output HTML file')
    parser.add_argument('--title', help='Override title')
    args = parser.parse_args()
    
    with open(args.input) as f:
        text = f.read()
    
    meta, body = parse_frontmatter(text)
    body_html = convert_markdown_to_wechat(body)
    output_html = wechat_html(body_html, meta, args.title)
    
    with open(args.output, 'w') as f:
        f.write(output_html)
    
    result = {
        'status': 'success',
        'output': args.output,
        'title': args.title or meta.get('title', ''),
        'author': meta.get('author', ''),
        'char_count': len(body)
    }
    print(json.dumps(result, ensure_ascii=False))
```

## Output Contract

```json
{
  "status": "success",
  "output": "/path/to/output.html",
  "title": "Article Title",
  "author": "Author Name",
  "char_count": 6000
}
```

## Failure Handling

| 触发条件 | 一线修复 | 仍失败兜底 |
|-----------|---------|-----------|
| Input file not found | Check path: `ls -la <path>` | Ask user for correct path |
| `markdown` library not installed | `pip3 install markdown` | Use `python3 -c` with regex fallback |
| YAML frontmatter parsing error | Ignore frontmatter, use file title | Use filename as title |
| Output directory not writable | Save to `/tmp/<basename>.html` | Ask user for writable path |
| No content in file | Report empty file | Create minimal HTML with title only |

## Verification

1. Run `python3 scripts/convert.py sample.md -o sample.html`
2. Open `sample.html` in browser → verify typography matches reference
3. Inspect HTML → confirm no `<style>` blocks, all inline styles
4. Push with `wechat_article_push_dl` → confirm renders correctly in WeChat

## Related Skills

- `wechat_article_push_dl` — Push formatted HTML to WeChat drafts
- `wechat_article_css_dl` — Check/fix HTML for WeChat CSS compatibility
- `md2wechat` — Alternative: MD2WeChat converter (built into CLI)

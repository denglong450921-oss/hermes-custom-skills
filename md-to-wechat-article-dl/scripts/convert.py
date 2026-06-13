#!/usr/bin/env python3
"""
Convert Markdown to WeChat-compatible HTML with Chinese typography.
Usage: python3 scripts/convert.py <input.md> -o <output.html> [--title TITLE]
"""

import re, json, sys, os, argparse

# Try importing markdown
try:
    from markdown import markdown as md_convert
except ImportError:
    print(json.dumps({"status": "error", "message": "pip3 install markdown first"}, ensure_ascii=False))
    sys.exit(1)


def parse_frontmatter(text):
    """Extract YAML frontmatter and body."""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if not m:
        return {}, text
    yaml_text, body = m.group(1), m.group(2)
    meta = {}
    for line in yaml_text.split('\n'):
        kv = re.match(r'^(\w+):\s*(.+)$', line)
        if kv:
            meta[kv.group(1)] = kv.group(2).strip('"\'')
    return meta, body


def wechat_html(body_html, meta, title_override=None):
    """Wrap HTML body in WeChat-compatible template with inline CSS."""
    title = title_override or meta.get('title', 'Article')
    author = meta.get('author', '')
    date_val = meta.get('date', '') or meta.get('published', '')
    
    author_line = ''
    if author:
        parts = []
        if isinstance(author, str) and author.strip():
            parts.append(author.strip().lstrip('-').strip())
        elif isinstance(author, list):
            parts = [a.strip().lstrip('-').strip() for a in author if isinstance(a, str)]
        author_str = ' '.join(parts)
        if author_str:
            author_line = f'<p style="color:#999;font-size:13px;margin:0;">{author_str}{" · " + date_val if date_val else ""}</p>'
    
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
  {author_line}
</div>

<!-- Body -->
{body_html}

<!-- Footer -->
<p style="text-align:center;color:#ccc;font-size:12px;margin-top:32px;padding-top:16px;border-top:1px solid #eee;">
  {'© ' + author_str if author else ''}
</p>

</div>
</body>
</html>'''


def convert_markdown_to_wechat(md_text):
    """Convert markdown to WeChat-safe HTML."""
    extensions = ['fenced_code', 'tables', 'codehilite', 'nl2br']
    
    html = md_convert(md_text, extensions=extensions)
    
    # Remove any <style> tags
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # Style map: tag → CSS
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
        'img': 'max-width:100%;height:auto;display:block;margin:16px auto;border-radius:6px;',
        'table': 'width:100%;border-collapse:collapse;margin:12px 0;font-size:14px;',
        'th': 'background:#f0eee8;padding:8px 10px;text-align:left;font-weight:600;color:#1a1a2e;border-bottom:2px solid #e0ddd8;',
        'td': 'padding:8px 10px;border-bottom:1px solid #e0ddd8;color:#595959;',
        'hr': 'border:none;border-top:1px solid #e0ddd8;margin:24px 0;',
        'a': 'color:#e8633a;text-decoration:none;',
    }
    
    for tag, style in style_map.items():
        html = re.sub(
            f'<{tag}(\\s[^>]*?)?>',
            lambda m, s=style: f'<{tag}{m.group(1) or ""} style="{s}">',
            html
        )
    
    return html


def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to WeChat-compatible HTML')
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', required=True, help='Output HTML file')
    parser.add_argument('--title', help='Override title from frontmatter')
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(json.dumps({"status": "error", "message": f"File not found: {args.input}"}, ensure_ascii=False))
        sys.exit(1)
    
    with open(args.input) as f:
        text = f.read()
    
    meta, body = parse_frontmatter(text)
    body_html = convert_markdown_to_wechat(body)
    output_html = wechat_html(body_html, meta, args.title)
    
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(output_html)
    
    result = {
        'status': 'success',
        'output': os.path.abspath(args.output),
        'title': args.title or meta.get('title', ''),
        'char_count': len(body)
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()

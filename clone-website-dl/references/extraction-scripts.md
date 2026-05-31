# Extraction Scripts

Pre-built scripts in `scripts/`:

| Script | Phase | Usage |
|--------|-------|-------|
| `scripts/discover-assets.js` | Phase 2 | Copy-paste into browser MCP console to enumerate all page assets |
| `scripts/extract-component-css.js` | Phase 3 | Per-component CSS extraction via getComputedStyle |
| `scripts/verify-css.js` | Phase 5 | QA comparison: run on original AND clone, compare JSON output |
| `scripts/capture-reference.mjs` | Phase 5 | Deterministic screenshots and DOM geometry snapshots at desktop, tablet, and mobile widths |
| `scripts/visual-diff.mjs` | Phase 5 | Pixel mismatch score, heatmap, overlay, and JSON report via ImageMagick |
| `scripts/compare-geometry.mjs` | Phase 5 | DOM geometry drift report with configurable pixel tolerance |
| `scripts/audit-animations.mjs` | Phase 1 | Motion inventory and runtime style snapshots across scroll positions; run before deterministic capture |
| `scripts/audit-spacing.mjs` | Phase 1 | Structure-independent landmark rectangles and vertical heading gaps at desktop, tablet, and mobile widths |

## Measurable QA Commands

```bash
node scripts/audit-animations.mjs --url https://example.com/path --out docs/research/animations --label path
node scripts/audit-spacing.mjs --url https://example.com/path --out docs/research/spacing --label path
node scripts/capture-reference.mjs --url https://example.com/path --out docs/qa/path/source --label path
node scripts/capture-reference.mjs --url http://localhost:4173/path --out docs/qa/path/clone --label path
node scripts/visual-diff.mjs --reference docs/qa/path/source/path-desktop.png --candidate docs/qa/path/clone/path-desktop.png --out docs/qa/path/diff --label path-desktop --threshold 0.005
node scripts/compare-geometry.mjs --reference docs/qa/path/source/path-desktop.geometry.json --candidate docs/qa/path/clone/path-desktop.geometry.json --out docs/qa/path/diff --label path-desktop --tolerance 2
```

## Asset Discovery Script

Copy into browser MCP console:
```javascript
JSON.stringify({
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.currentSrc || img.src,
    lazySrc: img.dataset.src || img.dataset.lazy || null,
    srcset: img.currentSrc || img.dataset.srcset || img.srcset || null,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight,
    parentClasses: img.parentElement?.className,
    siblings: img.parentElement ? [...img.parentElement.querySelectorAll('img')].length : 0,
    position: getComputedStyle(img).position,
    zIndex: getComputedStyle(img).zIndex
  })),
  videos: [...document.querySelectorAll('video')].map(v => ({
    src: v.src || v.querySelector('source')?.src,
    poster: v.poster,
    autoplay: v.autoplay,
    loop: v.loop,
    muted: v.muted
  })),
  backgroundImages: [...document.querySelectorAll('*')].filter(el => {
    const bg = getComputedStyle(el).backgroundImage;
    return bg && bg !== 'none';
  }).map(el => ({
    url: getComputedStyle(el).backgroundImage,
    element: el.tagName + '.' + el.className?.split(' ')[0]
  })),
  svgCount: document.querySelectorAll('svg').length,
  fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 200).map(el => getComputedStyle(el).fontFamily))],
  favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({ href: l.href, sizes: l.sizes?.toString() }))
});
```

## Per-Component CSS Extraction

Copy into browser MCP console, replace SELECTOR:
```javascript
(function(selector) {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Element not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'textTransform','textDecoration','backgroundColor','background',
    'padding','paddingTop','paddingRight','paddingBottom','paddingLeft',
    'margin','marginTop','marginRight','marginBottom','marginLeft',
    'width','height','maxWidth','minWidth','maxHeight','minHeight',
    'display','flexDirection','justifyContent','alignItems','gap',
    'gridTemplateColumns','gridTemplateRows',
    'borderRadius','border','borderTop','borderBottom','borderLeft','borderRight',
    'boxShadow','overflow','overflowX','overflowY',
    'position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor',
    'objectFit','objectPosition','mixBlendMode','filter','backdropFilter',
    'whiteSpace','textOverflow','WebkitLineClamp'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => { const v = cs[p]; if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)') styles[p] = v; });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    const children = [...element.children];
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3 ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG' ? {
        src: element.currentSrc || element.src,
        lazySrc: element.dataset.src || element.dataset.lazy || null,
        srcset: element.dataset.srcset || element.srcset || null,
        alt: element.alt,
        naturalWidth: element.naturalWidth,
        naturalHeight: element.naturalHeight
      } : null,
      childCount: children.length,
      children: children.slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR');
```

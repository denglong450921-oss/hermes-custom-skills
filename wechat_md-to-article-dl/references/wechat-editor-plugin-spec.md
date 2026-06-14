# WeChat Editor Plugin Compatibility

Source: [微信公众平台编辑器插件开发规范](https://developers.weixin.qq.com/doc/service/guide/product/plugin_spec.html)

Reviewed on 2026-06-13. The official page response was last modified on
2026-06-12. This reference paraphrases the implementation-relevant requirements and
incorporates the user-provided 2026-06-13 clipping of the same page. Consult the
official page when the platform changes.

## Local audit rules

- Keep image opacity visible and do not hide editor controls with transparent
  `caret-color`.
- Do not use zero line height.
- Avoid fixed element width and height. Responsive values such as `width:100%`,
  `max-width`, and `height:auto` are acceptable.
- Use portable text alignment values rather than `start` or `end`.
- Avoid `<pre>`. Represent fenced code with a wrapping section and a styled
  block-level `<code>` element.
- Limit nesting of the same tag name to 15 levels.
- Keep `span[leaf]` content inline-only and `section[nodeleaf]` content limited to
  supported editor components or images.
- Do not override `font-family`; use the platform default typeface.

## Dark Mode rules

- Use moderate foreground/background contrast. The local audit flags explicit
  foreground/background pairs below a 3:1 ratio.
- Avoid text placed directly on gradients. A decorative gradient container without
  text can remain because the platform preserves that use case.
- Put one shared background on a container around multiple text nodes instead of
  repeating the background on each node.
- Use a container background instead of fragile absolute positioning or transforms.
- Avoid converting ordinary text into images.
- Manually review images containing text and transparent images against both light
  and `#191919` dark backgrounds. The algorithm does not inspect image content.
- Manually review text over CSS background images. The platform preserves the
  light-mode text color and may apply a complementing treatment to the image.
- Prefer SVG `currentColor` where black or text-like line art should follow text color.
- Use `data-no-dark` only for content that must retain its original rendering. It
  applies only to the marked node; inline styles on descendants are still converted.
- Do not rely on `!important`, which prevents platform adaptation.

## Interactive SVG

If an SVG animation uses `touchstart` in its `begin` trigger, provide a corresponding
`click` trigger so desktop and mobile editor behavior remain aligned.

## Official structure verification

The official checker accepts a JSON `POST` request:

```text
https://mp.weixin.qq.com/article-bin/verify_article_structure
```

Request body:

```json
{
  "content": "<complete article HTML>"
}
```

The bundled `scripts/official_verify.py` client normalizes the response into
`passed`, `blocked`, or `error`. `scripts/convert.py --official-check` and
`scripts/audit.py --official-check` call it only after local validation passes.
It also converts the rule-keyed `inValidInfo` object into a stable `violations` list
with `rule`, `message`, and `items[].outer_html`, while preserving the raw response.

The endpoint was tested on 2026-06-13 and accepted both JSON and form encoding. The
client uses JSON because that is the request format shown by the official specification.

The request sends the complete HTML to WeChat. Never enable it implicitly for private
or unpublished drafts.

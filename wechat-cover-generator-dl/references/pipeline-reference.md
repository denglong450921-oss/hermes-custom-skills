# Pipeline Reference

## Default self-contained pipeline

Use this path unless the user explicitly asks for live image search or another
specialized skill.

```text
Markdown/topic/title
  -> scripts/run_pipeline.py
  -> title metadata Markdown
  -> 900x383 PNG cover
  -> JSON validation report
```

The runner guarantees these output fields:

```json
{
  "cover_image_url": "/absolute/path/cover.png",
  "title_md_path": "/absolute/path/cover-title.md",
  "validation": "pass",
  "dimensions": [900, 383],
  "image_source": "deterministic_gradient",
  "image_validation_attempts": 1
}
```

## External skill composition

Use this path when the user wants live open-source images, richer title
ideation, or stricter visual validation.

```text
Input article
  -> wechat-title-generator-dl
  -> open-source-image-fetch-dl
  -> image-quality-validator-dl
  -> wechat_article_cover_image_gen or scripts/run_pipeline.py --image-url
  -> normalized JSON report
```

Keep the normalized report contract even when an external skill performs a
step. Downstream workflows should not need to know which path created the
cover.

## Retry policy

- Try up to 3 image candidates when using live image search.
- Broaden the query after each rejected image.
- If all image candidates fail, use the deterministic gradient and report that
  fallback honestly.
- Never mark `validation` as `pass` unless the final PNG exists and is exactly
  `900x383`.

## Quality checklist

- [ ] Title comes from `--title`, Markdown H1, or topic.
- [ ] Cover title is readable and no more than 2 lines.
- [ ] Final file is a PNG with dimensions `900x383`.
- [ ] Report includes source, validation status, dimensions, and attempt count.
- [ ] External image use records URL/license/source when available.
- [ ] Fallback mode is visible in `image_source`.

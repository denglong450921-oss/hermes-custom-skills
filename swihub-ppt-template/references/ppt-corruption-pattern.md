# PPTX Corruption: Slide Deletion Anti-Pattern

## The Problem

python-pptx has no native slide deletion API. The common workaround — direct XML manipulation of `prs.slides._sldIdLst` — produces files that python-pptx can open but Office (PowerPoint / Keynote) rejects.

## Why It Fails

When you delete sldId entries via XML:
1. `sldIdLst` entries are removed → presentation.xml says "32 slides"
2. Slide XML files remain in the .zip → `ppt/slides/slide1.xml` through `slide64.xml` still exist
3. Content_Types.xml still lists all 64 slide parts
4. Office sees: 32 sldId entries vs 64 Content_Types slide overrides vs 64 slide files → **corrupt**

Zip-level orphan cleanup (removing unreferenced slide files + cleaning Content_Types) produces files that python-pptx validates but Office still rejects — the `copy.deepcopy()` on slide XML trees appears to introduce namespace hygiene issues that only Office's stricter parser catches.

## The Only Safe Approach: In-Place Editing

Modify text on the existing template slides — zero structural changes:

```python
prs = Presentation("template.pptx")
for slide_idx, mapping in slides_map.items():
    slide = prs.slides[slide_idx]
    replace_text_on_slide(slide, mapping)  # modifies text only
prs.save("output.pptx")
```

This avoids ALL slide duplication, ALL deletion, ALL zip manipulation. The file structure is identical to the working template — only text content changes.

## When You MUST Add Slides

If the template has fewer slides than needed, `duplicate_slide()` is the only option. Accept the trade-off:
- Keep ALL slides (original + new) — do NOT attempt to delete originals
- Or, create a new blank presentation and copy shapes natively (no XML deep-copy)

## Detection

Corrupt files pass `python-pptx` validation but fail in Office with generic "can't open" errors.

Quick check: compare slide XML file count vs Content_Types slide overrides vs sldId entries:
```python
import zipfile
with zipfile.ZipFile('file.pptx') as z:
    slides = [n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml') and '_rels' not in n]
    ct = etree.fromstring(z.read('[Content_Types].xml'))
    ct_slides = len([ov for ov in ct.findall(f'{{{ns}}}Override') if 'slide' in ov.get('PartName','')])
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    sldIds = len(pres.findall('.//p:sldId', {'p': '...'}))
    # All three must be equal
```

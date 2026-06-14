# Cover Image Text Rendering (PIL + Chinese)

Captures learnings from generating WeChat cover images with Pillow on macOS.

## Font Selection

| Font | File path | Status |
|---|---|---|
| STHeiti Medium | `/System/Library/Fonts/STHeiti Medium.ttc` | ✅ Works for 14-125pt |
| PingFang SC | `/System/Library/Fonts/PingFang.ttc` | ❌ Pillow `cannot open resource` (TTC issue) |
| Songti | `/System/Library/Fonts/Supplemental/Songti.ttc` | ✅ Works (serif — less modern) |
| Arial Bold | `/System/Library/Fonts/Supplemental/Arial Bold.ttf` | ⚠️ Renders Chinese as tofu boxes |

**Rule:** Always use `STHeiti Medium.ttc` for mixed Chinese/English text on macOS.

## Centering Gotchas

1. **`ImageFont.getbbox()` overestimates width for large Chinese text.**  
   At 125px on 900px canvas, the overestimate is ~9px (843 vs 834 actual rendered).  
   This causes text to appear 4-5px off-center.

2. **Fix: mask-based centering.**  
   Render text at a known offset in a large enough temp image, find the actual
   first/last non-zero columns, then compute the draw-x that makes
   `L_margin == R_margin`:
   ```python
   draw_x = (canvas_w - 1 - l - r) / 2
   ```

3. **Even-width rendered text on an even-width canvas is off by 0.5px.**  
   This is a physical limit of pixel grids — 0.5px is imperceptible.

## Shadow & Outline

For large display text (80-125px), a heavy multi-pass shadow + 8-direction
outline gives a premium magazine look:

```python
# Heavy shadow: stepped alpha from outer to inner
for ox in range(6, 12):
    for oy in range(6, 12):
        dist = max(abs(ox-6), abs(oy-6))
        alpha = max(40, 130 - dist * 12)
        draw.text((x+ox, y+oy), text, fill=(0,0,0,alpha), font=font)

# Outline: 8-direction stroke
for ox in range(-2, 3):
    for oy in range(-2, 3):
        if ox == 0 and oy == 0: continue
        draw.text((x+ox, y+oy), text, fill=(0,0,0,180), font=font)

# Core
draw.text((x, y), text, fill=(255,255,255,255), font=font)
```

## Uniform Overlay

Cover the entire image with a single translucent rect to ensure all text is
readable regardless of the underlying photo's brightness:

```python
draw.rectangle([0, 0, w, h], fill=(5, 8, 15, 165))  # rgba
```

## Script

Use `scripts/draw_cover.py` for a reusable CLI tool that handles all of the
above — see its `--help` for arguments.

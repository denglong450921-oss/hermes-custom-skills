# Validation Criteria Reference

## Resolution thresholds

| Min width | Quality level | Use case |
|---|---|---|
| ≥ 2400px | Excellent | Large format, print-ready |
| ≥ 1920px | Very good | Full HD, covers well |
| ≥ 1200px | Acceptable | Minimum for WeChat 900×383 |
| < 1200px | Reject | Will look pixelated |

## Clarity (Laplacian variance)

| Variance | Rating | Readable at 900×383? |
|---|---|---|
| ≥ 200 | Sharp | Yes, perfect |
| 100-199 | Good | Yes, acceptable |
| 50-99 | Acceptable | Yes, minor softness |
| 20-49 | Soft | Noticeable blur |
| < 20 | Blurry | Reject |

## Aspect ratio for 900×383 crop

| Source ratio | Closeness to 2.35 | Crop quality |
|---|---|---|
| 1.8 - 2.8 | Excellent (< 20% diff) | Minor trimming |
| 1.6 - 3.0 | Good (< 40% diff) | Some trimming |
| 1.4 - 3.4 | Fair (< 60% diff) | Significant crop |
| < 1.4 or > 3.4 | Poor | Major crop, quality loss |

## Watermark detection heuristic

- Compares variance in bottom-right quadrant vs main image
- Low variance ratio (< 0.3) suggests watermark overlay
- Uniform bottom edge (< 5 std) suggests text bar
- Score < 0.7 → possible watermark

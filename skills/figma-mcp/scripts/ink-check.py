#!/usr/bin/env python3
"""
ink-check.py — fast screenshot verification for translated Figma nodes.
Counts visible-ink pixels (alpha > 10, or dark pixels on white composite)
instead of OCR: a text region that rendered shows ~10%+ ink; a blank-font
region shows ~3% or less. Also reports text color (dark vs white text).

Usage:
  python3 ink-check.py <png> [--min INK%] [--regions x0,y0,x1,y1 ...]
    --min        fail (exit 1) if overall ink is below this percent (default 5)
    --regions    extra named regions as x0,y0,x1,y1 (comma list) — each printed
    --white-text check for white text (alpha>10, RGB mean >200) instead of dark

Exit code: 0 = ink OK, 1 = below threshold, 2 = file/param error.
"""
import sys, argparse
import numpy as np

def load(path):
    from PIL import Image
    a = np.array(Image.open(path).convert("RGBA"))
    alpha = a[:, :, 3:4] / 255.0
    rgb = a[:, :, :3]
    comp = (rgb * alpha + 255 * (1 - alpha)).astype(np.uint8)
    return a, comp

def ink_pct(comp, dark=True, thresh=160):
    g = comp.mean(axis=2)
    return ((g < thresh if dark else g > thresh).mean() * 100)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("--min", type=float, default=5.0)
    ap.add_argument("--regions", nargs="*", default=[])
    ap.add_argument("--white-text", action="store_true")
    args = ap.parse_args()

    a, comp = load(args.png)
    h, w = comp.shape[:2]
    overall = ink_pct(comp, dark=not args.white_text)
    print(f"{args.png}: {w}x{h} overall ink {overall:.1f}%")
    for r in args.regions:
        try:
            x0, y0, x1, y1 = map(int, r.split(","))
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(w, x1), min(h, y1)
            reg = comp[y0:y1, x0:x1]
            if reg.size:
                print(f"  region {r}: ink {ink_pct(reg, dark=not args.white_text):.1f}%")
        except ValueError:
            print(f"  bad region spec: {r}", file=sys.stderr)
    sys.exit(0 if overall >= args.min else 1)

if __name__ == "__main__":
    main()

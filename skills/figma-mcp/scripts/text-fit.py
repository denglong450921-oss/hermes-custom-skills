#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
text-fit.py — compute per-node font sizes so translated text fits its ORIGINAL
text box (recorded before translation). Only shrinks; never enlarges.

Method per translated node, per language:
  1. rendered line widths  = PIL.getlength(line, size) + letterSpacing correction
  2. lines after wrap      = ceil(lineWidth / boxWidth) per line, sum x lineHeight
  3. if maxLineWidth > boxWidth OR totalHeight > boxHeight:
       newSize = size * min(boxWidth/maxLineWidth, boxHeight/totalHeight) * margin
     (iterate once; margin guards against metric drift between PIL and Figma)
  4. else: keep the original size

Usage:
  python3 scripts/text-fit.py <translations.json> <scan.json> <styles.json> <bounds.json> <out.json>
  env: TARGET_FONT (default 'Arial Unicode MS'), FIT_MARGIN (default 0.96),
       MIN_SIZE (default 8)
"""
import json, os, sys, math
from PIL import ImageFont

FONT_FILES = {
    "Arial Unicode MS": "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "Poppins": "/System/Library/Fonts/Supplemental/Poppins.ttf",  # fallback, may 404 -> use Arial Unicode
}

def font_file(family):
    f = FONT_FILES.get(family)
    if f and os.path.exists(f):
        return f
    # any installed fallback with wide script coverage
    for cand in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                 "/Library/Fonts/Arial Unicode.ttf"):
        if os.path.exists(cand):
            return cand
    return None

def line_width(font, text, size, ls_pct=0.0):
    w = font.getlength(text)
    if ls_pct:
        n = len(text)
        if n > 1:
            w += (size * ls_pct / 100.0) * (n - 1)
    return w

def fit_size(text, size, box_w, box_h, line_h, ls_pct, margin, src_text="", src_size=0.0):
    """Return the largest size <= size that fits (text, box). box_h<=0 => height unconstrained.
    Width-constrained (must not wrap) only when the SOURCE rendered as a single
    line (single-line source text that fit its box). Otherwise the node may
    wrap/reflow like the source did, so only HEIGHT constrains."""
    if not text:
        return size
    if box_w <= 0:
        return size
    ff = font_file("Arial Unicode MS")
    if not ff:
        return size
    # does the SOURCE render on one line? (single-line text that fits its box)
    source_single = False
    if src_text and "\n" not in src_text:
        src_size_v = src_size or size
        fsrc = ImageFont.truetype(ff, int(round(src_size_v)))
        if line_width(fsrc, src_text, src_size_v, ls_pct) <= box_w:
            source_single = True
    no_wrap = source_single
    low, high = 1.0, float(size)
    def fits(sz):
        f = ImageFont.truetype(ff, int(round(sz)))
        total_h = 0.0
        max_w = 0.0
        for line in text.split("\n"):
            w = line_width(f, line, sz, ls_pct)
            max_w = max(max_w, w)
            nlines = max(1, math.ceil((w + 0.5) / box_w))
            total_h += nlines * (line_h if line_h and line_h > 0 else sz * 1.4)
        if no_wrap and max_w > box_w:
            return False, max_w, total_h
        if box_h > 0 and total_h > box_h:
            return False, max_w, total_h
        return True, max_w, total_h
    ok, mw, th = fits(size)
    if ok:
        return size
    # binary search the largest fitting size
    for _ in range(24):
        mid = (low + high) / 2
        if fits(mid)[0]:
            low = mid
        else:
            high = mid
    return max(round(low * margin * 2) / 2.0, float(os.environ.get("MIN_SIZE", 8)))

def main():
    if len(sys.argv) < 6:
        print("usage: text-fit.py <translations.json> <scan.json> <styles.json> <bounds.json> <out.json>")
        sys.exit(1)
    trans_path, scan_path, styles_path, bounds_path, out_path = sys.argv[1:6]
    trans = json.load(open(trans_path, encoding="utf-8"))
    scan = json.load(open(scan_path, encoding="utf-8"))["textNodes"]
    styles = json.load(open(styles_path, encoding="utf-8"))
    bounds_raw = json.load(open(bounds_path, encoding="utf-8"))
    # bounds file may be nested {frameId: {nodeId: ...}} — flatten
    bounds = {}
    for v in bounds_raw.values():
        if isinstance(v, dict):
            bounds.update(v)
        else:
            raise SystemExit(f"unexpected bounds entry type: {type(v).__name__}")
    margin = float(os.environ.get("FIT_MARGIN", 0.96))

    result = {}
    for lang in trans["languages"]:
        code = lang["code"]
        arr = trans["translations"][code]
        lang_sizes = {}
        for i, node in enumerate(scan):
            src_text = node["characters"]
            new_text = arr[i]
            if new_text == src_text:
                continue  # passthrough: never touch
            st = styles.get(node["id"], {})
            b = bounds.get(node["id"])
            if not b:
                continue
            size = float(node.get("fontSize") or st.get("fontSize") or 14)
            line_h = (st.get("lineHeight") or {}).get("value") or 0
            ls = (st.get("letterSpacing") or {})
            ls_pct = ls.get("value", 0) if ls.get("unit") == "PERCENT" else 0.0
            new_size = fit_size(new_text, size, b["width"], b["height"], line_h, ls_pct, margin,
                                src_text, size)
            if abs(new_size - size) > 0.05:
                lang_sizes[str(i)] = round(new_size, 1)
        result[code] = lang_sizes
        shrunk = len(lang_sizes)
        print(f"{code}: {shrunk}/{len(scan)} translated nodes need smaller font")
    json.dump(result, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = sum(len(v) for v in result.values())
    print(f"\nwritten {out_path} | total size adjustments: {total}")

if __name__ == "__main__":
    main()

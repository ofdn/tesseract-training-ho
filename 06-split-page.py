#!/usr/bin/env python3
"""
06-split-page.py

Splits a scanned page + ground-truth text file into line images and
.gt.txt files in ground-truth/. Check the pairs, then run 02-make-lstmf.sh.

Usage:
  python3 06-split-page.py <image> <gt.txt> [--prefix p16]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# paths, relative to the repo root
GT_DIR        = Path("ground-truth")

# Line detection
ROW_THR      = 0.05   # fraction of row-max to count as text row
MIN_HEIGHT   = 6      # min px height to keep a region
SPARSE_FRAC  = 0.22   # regions with peak below this × median → skip (stray mark)
UPSCALE      = 2      # upscale factor for better pixel density
VPAD         = 4      # vertical padding in original pixels around each line

def detect_lines(gray_arr):
    binary = gray_arr < 180
    proj   = binary.sum(axis=1)
    thr    = proj.max() * ROW_THR
    lines, in_text, start = [], False, 0
    for i, v in enumerate(proj):
        if v > thr and not in_text:
            start, in_text = i, True
        elif v <= thr and in_text:
            if i - start >= MIN_HEIGHT:
                lines.append((start, i, int(proj[start:i].max())))
            in_text = False
    if in_text and (len(proj) - start) >= MIN_HEIGHT:
        lines.append((start, len(proj), int(proj[start:].max())))
    return lines

def filter_lines(lines):
    if not lines:
        return [], []
    peaks   = sorted(pk for _, _, pk in lines)
    med_pk  = peaks[len(peaks) // 2]
    sparse  = med_pk * SPARSE_FRAC
    heights = sorted(e - s for s, e, _ in lines)
    med_h   = heights[len(heights) // 2]
    kept, skipped = [], []
    last = len(lines) - 1
    dense = med_pk * 1.5
    for i, (s, e, pk) in enumerate(lines):
        if i == 0 and ((e - s) > med_h * 1.3 or pk > dense):
            skipped.append(i)
            continue
        if i == last and (e - s) > med_h * 1.25:
            skipped.append(i)
            continue
        if (e - s) > med_h * 1.7:               # any line much taller than median → non-body element
            skipped.append(i)
            continue
        if pk < sparse:                          # very sparse → stray mark
            skipped.append(i)
            continue
        kept.append((s, e, pk))
    return kept, skipped

# Warang Citi
def is_warang_citi(c):
    return 0x118A0 <= ord(c) <= 0x118FF

# Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    parser.add_argument('gt')
    parser.add_argument('--prefix', default=None)
    args = parser.parse_args()

    prefix = args.prefix or Path(args.image).stem

    img      = Image.open(args.image).convert('RGB')
    gray_arr = np.array(img.convert('L'))

    # Load GT: keep only non-blank lines with Warang Citi chars
    raw_gt   = Path(args.gt).read_text(encoding='utf-8').splitlines()
    gt_lines = [ln.strip() for ln in raw_gt
                if ln.strip() and any(is_warang_citi(c) for c in ln)]

    print(f"\n  Image:    {args.image}  ({img.size[0]}×{img.size[1]}px)")
    print(f"  GT lines: {len(gt_lines)}")

    all_lines          = detect_lines(gray_arr)
    kept, skipped_idx  = filter_lines(all_lines)

    print(f"  Detected: {len(all_lines)} regions  →  kept {len(kept)}, "
          f"skipped {len(skipped_idx)} (indices: {skipped_idx})")

    if len(kept) != len(gt_lines):
        print(f"\n  MISMATCH: {len(kept)} image lines vs {len(gt_lines)} GT lines")
        print("\n  All detected regions:")
        for i, (s, e, pk) in enumerate(all_lines):
            tag = 'SKIP' if i in skipped_idx else 'keep'
            print(f"    L{i+1:02d}  y={s}–{e}  h={e-s}px  peak={pk}  [{tag}]")
        print("\n  GT lines:")
        for i, ln in enumerate(gt_lines):
            print(f"    {i+1:2d}: {ln[:60]}")
        sys.exit(1)

    GT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    for idx, ((y0, y1, _), gt_text) in enumerate(zip(kept, gt_lines)):
        name     = f"{prefix}_line{idx+1:04d}"
        png_path = GT_DIR / f"{name}.png"

        # Crop line with padding, upscale 2×
        H_orig, W_orig = gray_arr.shape
        top    = max(0, y0 - VPAD)
        bottom = min(H_orig, y1 + VPAD)
        line_img = img.crop((0, top, W_orig, bottom))
        line_img = line_img.resize(
            (line_img.width * UPSCALE, line_img.height * UPSCALE),
            Image.LANCZOS
        )
        line_img.save(str(png_path))

        png_path.with_suffix('.gt.txt').write_text(gt_text + '\n', encoding='utf-8')
        preview = gt_text[:55] + ('…' if len(gt_text) > 55 else '')
        print(f"  {name}  {preview}")

    print(f"\n  Done: {len(kept)} lines in {GT_DIR}/")
    print()

if __name__ == '__main__':
    main()

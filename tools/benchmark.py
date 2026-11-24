#!/usr/bin/env python3
"""
benchmark.py — character and word error rates on images with .gt.txt files.

Usage:
  python3 tools/benchmark.py --test-dir ground-truth-heldout --psm 13 \
      --model output/hoc.traineddata

A model is a .traineddata path or a name in the system tessdata folder,
optionally followed by :0 for the legacy engine.
"""

import argparse
import subprocess
from pathlib import Path

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for ca in a:
        curr = [prev[0] + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


def ocr(image, model, psm):
    name, _, oem = model.partition(':')
    cmd = ['tesseract', str(image), 'stdout', '--psm', psm, '--oem', oem or '1']
    path = Path(name)
    if path.suffix == '.traineddata':
        cmd += ['--tessdata-dir', str(path.parent), '-l', path.stem]
    else:
        cmd += ['-l', name]
    out = subprocess.run(cmd, capture_output=True, text=True, errors='replace').stdout
    return ' '.join(out.split())


def pairs(test_dir):
    for img in sorted(Path(test_dir).iterdir()):
        gt = img.with_name(img.stem + '.gt.txt')
        if img.suffix.lower() in IMAGE_EXTS and gt.exists():
            yield img, ' '.join(gt.read_text(encoding='utf-8').split())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-dir', default='ground-truth-heldout')
    parser.add_argument('--psm', default='13')
    parser.add_argument('--model', action='append', required=True)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    totals = {m: [0] * 8 for m in args.model}
    for img, ref in pairs(args.test_dir):
        for m in args.model:
            hyp = ocr(img, m, args.psm)
            t = totals[m]
            t[0] += levenshtein(ref, hyp)
            t[1] += len(ref)
            t[2] += levenshtein(ref.split(), hyp.split())
            t[3] += len(ref.split())
            t[4] += min(hyp.count(' '), ref.count(' '))
            t[5] += ref.count(' ')
            t[6] += levenshtein(ref.replace(' ', ''), hyp.replace(' ', ''))
            t[7] += len(ref.replace(' ', ''))
            if args.verbose:
                print(f'{img.name}  {m}\n  GT:  {ref}\n  OCR: {hyp}')

    print(f'\n{args.test_dir}, --psm {args.psm}')
    # "CER no sp." leaves spaces out, for models that never output them
    print(f'{"model":<40} {"CER":>7} {"WER":>7} {"spaces":>7} {"CER no sp.":>10}')
    for m, (ce, cn, we, wn, sh, sn, ne, nn) in totals.items():
        print(f'{m:<40} {100 * ce / cn:6.1f}% {100 * we / wn:6.1f}% '
              f'{100 * sh / max(sn, 1):6.1f}% {100 * ne / nn:9.1f}%')


if __name__ == '__main__':
    main()

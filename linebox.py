#!/usr/bin/env python3
"""Line box files and .lstmf files for Tesseract LSTM training.

Usage: python3 linebox.py <dir with png + gt.txt> <output dir>
"""

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

TESSDATA = "tessdata_best"


def write_box(png, text):
    # one WordStr box for the whole line, as tesstrain does, so spaces are kept
    w, h = Image.open(png).size
    box = Path(png).with_suffix(".box")
    box.write_text(f"WordStr 0 0 {w} {h} 0 #{text}\n\t {w} 0 {w + 1} {h} 0\n",
                   encoding="utf-8")


def make_lstmf(png, text):
    png = Path(png)
    text = " ".join(text.split())
    if not text:
        return False
    write_box(png, text)
    subprocess.run(["tesseract", str(png), str(png.with_suffix("")),
                    "--tessdata-dir", TESSDATA, "-l", "Latin",
                    "--psm", "13", "lstm.train"],
                   capture_output=True)
    return png.with_suffix(".lstmf").exists()


def main(src, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for gt in sorted(Path(src).glob("*.gt.txt")):
        png = gt.with_name(gt.name[:-len(".gt.txt")] + ".png")
        if not png.exists():
            continue
        dst = out / png.name
        shutil.copy2(png, dst)
        shutil.copy2(gt, out / gt.name)
        if make_lstmf(dst, gt.read_text(encoding="utf-8")):
            ok += 1
        else:
            fail += 1
    print(f"  {src}: {ok} lstmf, {fail} failed")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

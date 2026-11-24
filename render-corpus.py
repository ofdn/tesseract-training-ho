#!/usr/bin/env python3
"""
render-corpus.py

Renders corpus/hoc_clean.txt in Noto Sans Warang Citi and Boyo Gagrai
Unicode into rendered/ as PNG + gt.txt pairs. Corpus lines that share a
run of four words with ground-truth-heldout/ are skipped, so the held-out
pages stay unseen.
"""

from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

BASE   = Path(__file__).parent
CORPUS = BASE / "corpus" / "hoc_clean.txt"
OUTDIR = BASE / "rendered"

FONTS = [
    ("noto_wc",    BASE / "fonts" / "NotoSansWarangCiti-Regular.ttf", 36),
    ("boyogagrai", BASE / "fonts" / "BoyoGagraiUnicode-4-4-17.ttf",   36),
]

PAD_X = 20
PAD_Y = 12
MIN_H = 60


def grams(text, n=4):
    w = text.split()
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


held = set()
for gt in (BASE / "ground-truth-heldout").glob("*.gt.txt"):
    held |= grams(gt.read_text(encoding="utf-8"))

lines = [l.strip() for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
kept = [l for l in lines if not grams(l) & held]
print(f"  {len(kept)} of {len(lines)} corpus lines kept, {len(lines) - len(kept)} overlap held-out pages")

OUTDIR.mkdir(exist_ok=True)
for tag, font_path, size in FONTS:
    font = ImageFont.truetype(str(font_path), size)
    for idx, text in enumerate(kept):
        bbox = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0] + PAD_X * 2
        h = max(bbox[3] - bbox[1] + PAD_Y * 2, MIN_H)
        img = Image.new("L", (w, h), 255)
        ImageDraw.Draw(img).text((PAD_X - bbox[0], PAD_Y - bbox[1]), text, font=font, fill=0)
        stem = OUTDIR / f"{tag}_line{idx:04d}"
        img.save(f"{stem}.png")
        Path(f"{stem}.gt.txt").write_text(text + "\n", encoding="utf-8")
    print(f"  {tag}: {len(kept)} images")

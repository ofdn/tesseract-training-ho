#!/usr/bin/env python3
"""Prints the training list: every scan line, 200 rendered lines per font
and every augmented line."""

import random
from pathlib import Path

PER_FONT = 200

random.seed(7)
lstmf = Path("lstmf").resolve()
files = sorted((lstmf / "scan").glob("*.lstmf"))

fonts = {}
for f in sorted((lstmf / "rendered").glob("*.lstmf")):
    fonts.setdefault(f.stem.rsplit("_line", 1)[0], []).append(f)
for lines in fonts.values():
    files += random.sample(lines, min(PER_FONT, len(lines)))

files += sorted((lstmf / "augmented").glob("*.lstmf"))
print("\n".join(str(f) for f in files))

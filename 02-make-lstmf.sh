#!/bin/bash
# Makes .lstmf files from the rendered lines and ground-truth/, adds noisy
# copies of some rendered lines and writes lstmf/list.txt. The held-out
# lines go to lstmf/eval.txt and are never trained on.
set -e
cd "$(dirname "$0")"

[ -f tessdata_best/hoc_base.traineddata ] || { echo "Run ./01-prep-base.sh first."; exit 1; }
[ -d rendered ] || { echo "Run python3 render-corpus.py first."; exit 1; }

rm -rf lstmf
python3 linebox.py rendered lstmf/rendered
python3 linebox.py ground-truth lstmf/scan
python3 tools/augment-synthetic.py
python3 make-list.py > lstmf/list.txt

python3 linebox.py ground-truth-heldout lstmf/heldout
ls "$PWD"/lstmf/heldout/*.lstmf > lstmf/eval.txt

echo "lstmf/list.txt: $(wc -l < lstmf/list.txt | tr -d ' ') lines"
echo "lstmf/eval.txt: $(wc -l < lstmf/eval.txt | tr -d ' ') lines"

# Ho (Warang Citi) Tesseract training

This repository holds the corpus, fonts, scripts and benchmark images used to train `hoc.traineddata`. The model is in [tessdata_contrib/hoc](https://github.com/tesseract-ocr/tessdata_contrib/tree/main/hoc).

## Requirements

- Tesseract 5 with the training tools (`lstmtraining`, `combine_lang_model`, `combine_tessdata`)
- Python 3 with Pillow and NumPy

## Steps

Run each step from the repository root:

```bash
mkdir -p tessdata_best output
curl -L -o tessdata_best/Latin.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/script/Latin.traineddata
combine_tessdata -e tessdata_best/Latin.traineddata output/latin.lstm
./01-prep-base.sh
python3 render-corpus.py
./02-make-lstmf.sh
python3 06-scan-to-lstmf.py <image.png> <gt.txt> --prefix <name>
./03-train-finetune.sh
./04-package.sh
./05-test.sh <image.png> <gt.txt>
```

`03-train-finetune.sh` fine-tunes from Latin. This is how the released model was trained. `03-train.sh` trains from scratch instead.

## Private Use Area mapping

Tesseract 5 cannot train on Warang Citi code points above U+FFFF. The scripts map U+118A0 to U+118FF onto U+E000 to U+E05F. The mapping is in `pua_mapping.json`.

Convert OCR output back to Warang Citi Unicode:

```bash
tesseract line.png stdout -l hoc --psm 13 --oem 1 | python3 tools/pua-to-warang.py
```

## Contents

| Path | Purpose |
|------|---------|
| `corpus/hoc_clean.txt` | Cleaned Ho corpus in Warang Citi Unicode |
| `corpus/hoc_clean_pua.txt` | The same corpus in Private Use Area code points |
| `fonts/` | Noto Sans Warang Citi and its Private Use Area copy |
| `test-images/benchmark/` | Scanned pages with ground truth |
| `tools/benchmark.py` | Measures accuracy on the benchmark pages |
| `tools/augment-synthetic.py` | Adds noise, blur and contrast changes to line images |
| `tools/check-plateau.sh` | Shows when training stops improving |
| `tools/pua-to-warang.py` | Converts output to Warang Citi Unicode |

## How to help

- Test the model on Ho documents and report the results.
- Add Ho text in Warang Citi Unicode to the corpus.
- Scan printed Ho documents and transcribe the ground truth.
- Check the GhanshyamBodra ASCII to Unicode mapping. A native reader needs to verify it.
- Send an improved `hoc.traineddata` to tessdata_contrib.

## Credits

Ganesh Birua contributed Ho text. Mangu Purty contributed Ho text and OER content. Subhashish Panigrahi contributed Ho text and OER content, and trained the model.

Text sources:

- [Ho Wikipedia Incubator](https://incubator.wikimedia.org/wiki/Wp/hoc), CC BY-SA
- [OFDN Ho OER](https://theofdn.org/oer/ho/) by Koshi Purty, CC BY-SA 4.0
- [Warang Chiti blog](https://warangchiti.blogspot.com/)

Fonts:

- Noto Sans Warang Citi (SIL Open Font License)
- Boyo Gagrai Unicode by Mangu Purty, a Unicode version of the Boyo Gagrai font by Boyo Gagrai
- GhanshyamBodra11, an ASCII-encoded font used in Ho publishing

## Licence

Code: Apache 2.0, the same as Tesseract. Corpus text keeps the licence of its source. The fonts in `fonts/` keep the SIL Open Font License.

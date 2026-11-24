#!/bin/bash
# Downloads Latin.traineddata, extracts output/latin.lstm and builds
# tessdata_best/hoc_base.traineddata. The unicharset holds the whole
# Warang Citi block plus every character in the corpus and ground truth.
# Safe to run again.
set -e
cd "$(dirname "$0")"

mkdir -p tessdata_best/configs output/langdata output/langmodel/hoc_base

if [ ! -f tessdata_best/Latin.traineddata ]; then
    curl -fL -o tessdata_best/Latin.traineddata \
        https://github.com/tesseract-ocr/tessdata_best/raw/main/script/Latin.traineddata
fi
combine_tessdata -e tessdata_best/Latin.traineddata output/latin.lstm > /dev/null

# all assigned Warang Citi code points, U+118A0 to U+118F2 and U+118FF
python3 -c "print(''.join(map(chr, [*range(0x118A0, 0x118F3), 0x118FF])))" > output/block.txt
cat corpus/hoc_clean.txt ground-truth/*.gt.txt ground-truth-heldout/*.gt.txt output/block.txt > output/all_text.txt
unicharset_extractor --output_unicharset output/hoc.unicharset --norm_mode 1 output/all_text.txt > /dev/null 2>&1

# combine_lang_model wants radical-stroke.txt even though only CJK uses it
printf "0\n" > output/langdata/radical-stroke.txt

# Warang Citi is above U+FFFF, which the compressed recoder can't take
combine_lang_model \
    --input_unicharset output/hoc.unicharset \
    --script_dir output/langdata \
    --output_dir output/langmodel \
    --lang hoc_base \
    --pass_through_recoder > output/langmodel/build.log 2>&1

BUILT=output/langmodel/hoc_base/hoc_base.traineddata
combine_tessdata -d "$BUILT" 2>&1 | grep -q lstm-recoder || {
    echo "ERROR: $BUILT has no recoder, see output/langmodel/build.log"; exit 1; }
cp "$BUILT" tessdata_best/hoc_base.traineddata

# config for making .lstmf files, the same as tesseract's own configs/lstm.train
cat > tessdata_best/configs/lstm.train << 'CFG'
file_type                   .bl
textord_fast_pitch_test	T
tessedit_zero_rejection T
tessedit_minimal_rejection F
tessedit_write_rep_codes F
edges_children_fix F
edges_childarea 0.65
edges_boxarea 0.9
tessedit_train_line_recognizer T
textord_no_rejects T
tessedit_init_config_only T
CFG

echo "tessdata_best/hoc_base.traineddata: $(head -1 output/hoc.unicharset) unicharset entries"

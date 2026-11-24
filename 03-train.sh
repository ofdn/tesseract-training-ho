#!/bin/bash
# Trains the Ho model on top of Latin. Latin's lower layers are kept and
# the top LSTM and output layer are replaced, since Warang Citi shares no
# letters with Latin. The error rate starts at 100%.
# Checkpoints go to output/. Stop with Ctrl+C and run again to resume from
# output/hoc_checkpoint.
#
# Usage: ./03-train.sh > logs/train.log 2>&1 &
set -e
cd "$(dirname "$0")"

MAX_ITERATIONS=${MAX_ITERATIONS:-30000}

[ -s lstmf/list.txt ] || { echo "Run ./02-make-lstmf.sh first."; exit 1; }
mkdir -p output logs

lstmtraining \
    --continue_from      output/latin.lstm \
    --old_traineddata    tessdata_best/Latin.traineddata \
    --traineddata        tessdata_best/hoc_base.traineddata \
    --append_index       5 \
    --net_spec           '[Lfx256 O1c1]' \
    --model_output       output/hoc \
    --train_listfile     lstmf/list.txt \
    --eval_listfile      lstmf/eval.txt \
    --learning_rate      0.001 \
    --max_iterations     "$MAX_ITERATIONS" \
    --target_error_rate  0.01

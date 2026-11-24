#!/bin/bash
# Packages a checkpoint as output/hoc.traineddata. By default it takes
# output/hoc_checkpoint, which holds the best model once training stops.
# Pick another with CHECKPOINT=output/hoc_1.234_5678_9000.checkpoint
set -e
cd "$(dirname "$0")"

CHECKPOINT=${CHECKPOINT:-output/hoc_checkpoint}
[ -f "$CHECKPOINT" ] || { echo "$CHECKPOINT not found. Run ./03-train.sh first."; exit 1; }

lstmtraining \
    --stop_training \
    --continue_from "$CHECKPOINT" \
    --traineddata   tessdata_best/hoc_base.traineddata \
    --model_output  output/hoc.traineddata

ls -lh output/hoc.traineddata

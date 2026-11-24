#!/bin/bash
# OCR one line image with output/hoc.traineddata and print the ground truth
# next to it if given.
#
# Usage: ./05-test.sh <line.png> [line.gt.txt]
set -e
cd "$(dirname "$0")"

[ -f "${1:-}" ] || { echo "Usage: $0 <line.png> [line.gt.txt]"; exit 1; }
echo "OCR: $(tesseract "$1" stdout --tessdata-dir output -l hoc --psm 13 2>/dev/null)"
[ -f "${2:-}" ] && echo "GT:  $(cat "$2")"
exit 0

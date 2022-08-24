#!/bin/bash
dpml analysis \
  --input-dir ../results_sibyl \
  --extraction-strategy top_n \
  --top-n-number 2 \
  --model bert-base-uncased-sst2 \
  --task text-classification

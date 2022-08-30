#!/bin/bash
dpml analysis \
  --input-dir ../results_sibyl \
  --extraction-strategy worst_n \
  --top-n-number 20 \
  --model bert-base-uncased-sst2 \
  --task text-classification

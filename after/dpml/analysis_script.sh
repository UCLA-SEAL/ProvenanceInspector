#!/bin/bash
dpml analysis \
  --input-dir ../results_a2t_mlm_word.8_sst2 \
  --extraction-strategy worst_n \
  --top-n-number 2 \
  --pred-same-constraint \
  --model bert-base-uncased-sst2 \
  --task sentiment-analysis

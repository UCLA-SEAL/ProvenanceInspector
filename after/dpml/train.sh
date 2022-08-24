#!/bin/bash
for input_dir in "../results_a2t_mlm_word.8_sst2" "../results_a2t_word.8_sst2" 
do
echo $input_dir
dpml train \
  --epochs 3 \
  --per-device-train-batch-size 16 \
  --random-seed 42 \
  --log-on-epoch \
  --model bert-base-uncased-sst2 \
  --dataset "${input_dir}/reverted_text.csv" \
  --adv-dataset ../adv_glue/dev.json 
done

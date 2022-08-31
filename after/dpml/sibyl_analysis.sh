#!/bin/bash
for input_dir in "../results_sibyl" 
do
echo $input_dir
dpml analysis \
  --input-dir $input_dir \
  --top-n-number 20 \
  --extraction-strategy worst_n \
  --model bert-base-uncased-sst2 \
  --task sentiment-analysis
dpml analysis \
  --input-dir $input_dir \
  --top-n-number 20 \
  --model bert-base-uncased-sst2 \
  --extraction-strategy top_n \
  --task sentiment-analysis
dpml analysis \
  --input-dir $input_dir \
  --extraction-strategy top_n \
  --top-n-number 20 \
  --pred-same-constraint \
  --model bert-base-uncased-sst2 \
  --task sentiment-analysis
dpml analysis \
  --input-dir $input_dir \
  --extraction-strategy worst_n \
  --top-n-number 20 \
  --pred-same-constraint \
  --model bert-base-uncased-sst2 \
  --task sentiment-analysis
done

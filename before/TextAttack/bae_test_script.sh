#!/bin/bash
time textattack attack --model distilbert-base-cased-sst2 --model-batch-size 1 --num-workers-per-device 1 --recipe bae --num-examples -1 --log-to-csv ../results/log.csv --csv-coloring-style plain --disable-stdout

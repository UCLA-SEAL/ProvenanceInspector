#!/bin/bash
time textattack attack --model bert-base-uncased-imdb --model-batch-size 32 --num-workers-per-device 1 --recipe bae --num-examples 1000 --log-to-csv ../results/log.csv --checkpoint-interval 100 --csv-coloring-style plain --disable-stdout

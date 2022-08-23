#!/bin/bash
time textattack attack --model bert-base-uncased-sst2 --recipe "a2t^mlm=True" --dataset-split train --num-examples 10000 --log-to-csv ../results/log.csv --checkpoint-interval 1000 --csv-coloring-style plain --disable-stdout

#!/bin/bash
time textattack attack --model bert-base-uncased-sst2 --recipe "a2t^mlm=True" --num-examples -1 --log-to-csv ../results/log.csv --checkpoint-interval 200 --csv-coloring-style plain --disable-stdout

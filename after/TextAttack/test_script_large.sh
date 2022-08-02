#!/bin/bash
time textattack attack --model bert-base-uncased-yelp --recipe a2t --num-examples 10000 --log-to-csv ../results/log.csv --checkpoint-interval 1000 --csv-coloring-style plain --disable-stdout

#!/bin/bash
time textattack attack --model bert-base-uncased-yelp --recipe a2t --num-examples 1000 --log-to-csv ../results/log.csv --checkpoint-interval 100 --csv-coloring-style plain --disable-stdout

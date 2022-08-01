#!/bin/bash
time textattack attack --model bert-base-uncased-imdb --recipe a2t --num-examples 1000 --log-to-csv ../results_a2t_imdb/log.csv --checkpoint-interval 100 --csv-coloring-style plain --disable-stdout

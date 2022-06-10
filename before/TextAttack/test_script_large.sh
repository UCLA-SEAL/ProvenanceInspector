#!/bin/bash
!> ../results/transformation.csv
!> ../results/to_original.csv
!> ../results/log.csv
textattack attack --model bert-base-uncased-yelp --recipe a2t --num-examples -1 --log-to-csv ../results/log.csv --checkpoint-interval 100 --csv-coloring-style plain --disable-stdout

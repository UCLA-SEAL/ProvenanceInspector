#!/bin/bash
!> ../results/transformation.csv
!> ../results/to_original.csv
textattack attack --model bert-base-uncased-sst2 --recipe a2t --num-examples 5

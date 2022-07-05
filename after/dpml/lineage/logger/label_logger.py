"""
Label Logs to CSV
========================
"""

import csv
from typing import Iterable
import numpy as np

import pandas as pd

#from textattack.shared import logger
import os.path as osp


class LabelLogger:
    """Logs transformation provenance to a CSV."""

    def __init__(self, dirname='../results/'):
        #logger.info(f"Logging transformation and text pairs to CSVs under directory {dirname}")
        self.path = osp.join(dirname, 'label.csv')
        open(self.path, "w").close()
        self._flushed = True
        self.init_df()

    def init_df(self):
        self.id_counter = 0
        self.label2id = {}
        self.new_rows = {}

    def log_label(self, label):
        if isinstance(label, Iterable):
            label=tuple(label)
        
        label=str(label)

        if label in self.label2id:
            label_id = self.label2id[label]
        else:
            label_id = self.id_counter
            if len(label) < 25:
                self.label2id[label] = label_id
            
            self.new_rows[label_id] = label
            self.id_counter+=1
        
        self._flushed = False

        return label_id


    def flush(self):
        if len(self.new_rows) > 0:
            pd.Series(self.new_rows, dtype=object).to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
            self.new_rows = {}
        self._flushed = True

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            print("ProvenanceLogger exiting without calling flush().")

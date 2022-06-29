"""
Label Logs to CSV
========================
"""

import csv
from typing import Iterable

import pandas as pd

#from textattack.shared import logger
import os.path as osp


class LabelLogger:
    """Logs transformation provenance to a CSV."""

    def __init__(self, dirname='../results/'):
        #logger.info(f"Logging transformation and text pairs to CSVs under directory {dirname}")
        self.path = osp.join(dirname, 'label.csv')
        self._flushed = True
        self.init_df()

    def init_df(self):
        if osp.exists(self.path):
            self.id2label = pd.read_csv(self.path, header=None, index_col=0, squeeze=True, dtype=object)
        else:
            self.id2label = pd.Series(dtype=object)

    def log_label(self, label):
        if isinstance(label, Iterable):
            label=tuple(label)

        try:
            label_id = pd.Index(self.id2label).get_loc(label)
        except:
            label_id = len(self.id2label)
            
            self.id2label =pd.concat([self.id2label, pd.Series({label_id: label}, dtype=object)], ignore_index=True)
            self._flushed = False

        return label_id


    def flush(self):
        if len(self.id2label) > 0:
            self.id2label.to_csv(self.path, mode='w', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
        self._flushed = True

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            print("ProvenanceLogger exiting without calling flush().")

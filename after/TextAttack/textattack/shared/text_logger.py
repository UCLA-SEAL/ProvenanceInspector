"""
Attack Logs to CSV
========================
"""

import csv
from numpy import indices

import pandas as pd

#from textattack.shared import logger
import os.path as osp


class TextLogger:
    """Logs transformation provenance to a CSV."""

    def __init__(self, dirname='../results/'):
        #logger.info(f"Logging transformation and text pairs to CSVs under directory {dirname}")
        self.path = osp.join(dirname, 'text.csv')
        open(self.path, "w").close()
        self._flushed = True
        self.init_df()

    def init_df(self):
        self.text_df = pd.DataFrame(columns = ["text_id", "text"])

    def log_text(self, text_id, text, le_attrs):
        row = {
            "text_id": text_id,
            "text": text
        }
        self.text_df = self.text_df.append(row, ignore_index=True)
        self._flushed = False
    

    def flush(self):
        self.text_df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
        self._flushed = True
        self.init_df()

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            print("ProvenanceLogger exiting without calling flush().")

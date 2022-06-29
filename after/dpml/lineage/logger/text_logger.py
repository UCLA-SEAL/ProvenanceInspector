"""
Text Logs to CSV
========================
"""

import csv

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
        self.init_store()

    def init_store(self):
        self.storage = []

    def log_text(self, text_id, text, le_attrs):
        row = {
            "text_id": text_id,
            "text": text
        }
        self.storage.append(row)
        self._flushed = False
    

    def flush(self):
        df = pd.DataFrame(self.storage)
        df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
        self._flushed = True
        self.init_store()

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            print("ProvenanceLogger exiting without calling flush().")

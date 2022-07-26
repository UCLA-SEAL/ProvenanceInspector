"""
Record Logs to DATA_STORE
========================
"""

import os
import csv
import pandas as pd

import hydra

class RecordLogger:
    """
    Store records as (text, target) tuples
    """

    hydra.core.global_hydra.GlobalHydra.instance().clear()
    with hydra.initialize(version_base=None, config_path="../../config"):
        cfg = hydra.compose(config_name="config", overrides=["storage=csv"])
        path = os.path.abspath(os.path.join(cfg.storage['path'], cfg.storage['filename']))

    def __init__(self, path=path, flush_after_count=100):
        self.path = path
        self.flush_after_count = flush_after_count
        self.init_storage()

    def init_storage(self):
        self.storage = []
        self._flushed = True

    def log(self, record):
        self.storage.append({
            "text": record[0],
            "target": record[1]
        })
        self._flushed = False
        if len(self.storage) > self.flush_after_count:
            self.flush()

    def flush(self):
        df = pd.DataFrame(self.storage)
        df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
        self.init_storage()

if __name__ == '__main__':
    
    logger = RecordLogger()
    logger.log(("mytest1", 0))
    logger.log(("mytest2", 1))
    logger.flush()
    
    df = pd.read_csv(logger.path, names=["text", "target"])
    print(df)

    # ~\dpml\after\dpml\lineage\storage\csv>python record_logger.py
    #       text  target
    # 0  mytest1       0
    # 1  mytest2       1
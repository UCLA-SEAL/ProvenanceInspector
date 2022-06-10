"""
Attack Logs to CSV
========================
"""

import csv
from numpy import indices

import pandas as pd
import itertools

#from textattack.shared import logger
import os.path as osp


class TransformationLogger:
    """Logs transformation provenance to a CSV."""
    id_iter = itertools.count()

    def __init__(self, dirname='../results/'):
        #logger.info(f"Logging transformation and text pairs to CSVs under directory {dirname}")
        self.path = osp.join(dirname, 'transformation.csv')
        open(self.path, "w").close()
        self._flushed = True
        self.init_df()
        

    def init_df(self):
        self.transformation_df = pd.DataFrame(columns=["transformation_id", "transformation_type",
            "prev_text", "after_text", "from_modified_indices",
            "to_modified_indices", "changes"])
        

    def log_transformation(self, current_text_id, transformed_text_id, transformation_type, modified_inds, changes):
        trans_id = next(TransformationLogger.id_iter)

        from_mod_inds, to_mod_inds = modified_inds
        # precarious color editing
        # current_text, transformed_text = color_text_pair(current_text, transformed_text, list(from_inds), list(to_inds))
        

        row = {
            "transformation_id": trans_id,
            "transformation_type": transformation_type,
            "prev_text": current_text_id,
            "after_text": transformed_text_id,
            "from_modified_indices": from_mod_inds,
            "to_modified_indices": to_mod_inds,
            "changes": changes
        }
        
        self.transformation_df = self.transformation_df.append(row, ignore_index=True)
        self._flushed = False
    

    def flush(self):
        self.transformation_df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
        self._flushed = True
        self.init_df()

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            print("ProvenanceLogger exiting without calling flush().")

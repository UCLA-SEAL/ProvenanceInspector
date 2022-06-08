"""
Attack Logs to CSV
========================
"""

import csv

import pandas as pd

from textattack.shared import AttackedText, logger
from textattack.shared.utils import text_word_diff, color_text_pair
import os.path as osp

from .logger import Logger


class ProvenanceLogger(Logger):
    """Logs transformation provenance to a CSV."""

    def __init__(self, dirname='./results/'):
        logger.info(f"Logging transformation and text pairs to CSVs under directory {dirname}")
        self.dirname = dirname
        self.transformation_df = pd.DataFrame(columns=["transformation_type",
            "transformation_meta", "prev_text", "after_text",
            "from_modified_indices",  "to_modified_indices", "operations"])
        self.to_original_df = self.to_original_df = pd.read_csv('results/to_original.csv', index_col="current_text_hash", 
                              names = ["current_text_hash", "original_text_hash", "original_text", "transformed_text"])
        self._flushed = True

    def log_transformations(self, current_text, transformed_texts, transformation, indices_to_modify):
        for text in transformed_texts:
            self.log_transformation(current_text, text, transformation, indices_to_modify)

    def log_transformation(self, current_text, transformed_text, transformation, indices_to_modify):
        from_inds, to_inds, op_codes = text_word_diff(current_text, transformed_text, indices_to_modify)
        before_text_hash = hash(current_text)
        after_text_hash = hash(transformed_text)

        if 'last_transformation' in current_text.attack_attrs or before_text_hash not in self.to_original_df.index:
            original_text_hash = before_text_hash
            original_text = current_text.printable_text()
        else:
            original_text_hash = self.to_original_df.loc[before_text_hash]['original_text_hash']
            original_text = self.to_original_df.loc[before_text_hash]['original_text']

        # precarious color editing
        # current_text, transformed_text = color_text_pair(current_text, transformed_text, list(from_inds), list(to_inds))
        row = {
            "original_text_hash": original_text_hash,
            "original_text": original_text,
            "transformed_text": transformed_text.printable_text()
        }
        self.to_original_df.loc[after_text_hash] = pd.Series(row)

        transformation_type = transformation.__class__.__name__
        transformation_meta = transformation.__dict__

        row = {
            "transformation_type": transformation_type,
            "transformation_meta": str(transformation_meta),
            "prev_text": before_text_hash,
            "after_text": after_text_hash,
            "from_modified_indices": list(from_inds),
            "to_modified_indices": list(to_inds),
            "operations": op_codes
        }
        transform_hash = str(hash(transformation)) + str(after_text_hash)
        
        self.transformation_df.loc[transform_hash] = pd.Series(row)
        
        self._flushed = False

    

    def flush(self):
        self.transformation_df.to_csv(osp.join(self.dirname, 'transformation.csv'), mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False)
        self.to_original_df.to_csv(osp.join(self.dirname, 'to_original.csv'), quoting=csv.QUOTE_NONNUMERIC, header=False)
        self._flushed = True

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            logger.warning("ProvenanceLogger exiting without calling flush().")

"""
Attack Logs to CSV
========================
"""

import csv

import pandas as pd

from textattack.shared import AttackedText, logger
from textattack.shared.utils import text_word_diff
import json

from .logger import Logger


class ProvenanceLogger(Logger):
    """Logs transformation provenance to a CSV."""

    def __init__(self, filename="provenance.csv"):
        logger.info(f"Logging transformation to CSV at path {filename}")
        self.filename = filename
        self.transformation_df = pd.DataFrame(columns=["transformation_type",
            "transformation_meta", "prev_text", "after_text",
            "from_modified_indices",  "to_modified_indices"])
        self.to_original_df = pd.DataFrame()
        self._flushed = True

    def log_transformations(self, current_text, transformed_texts, transformation, indices_to_modify):
        for text in transformed_texts:
            self.log_transformation(current_text, text, transformation, indices_to_modify)

    def log_transformation(self, current_text, transformed_text, transformation, indices_to_modify):
        modified_inds_tuple = text_word_diff(current_text, transformed_text, indices_to_modify)
        before_text_hash = hash(current_text)
        after_text_hash = hash(transformed_text)
        if 'last_transformation' not in current_text:
            original_text_hash = before_text_hash
        else:
            original_text_hash = self.transformation_df.loc[before_text_hash]
        row = {
            "original_text_hash": original_text_hash
        }
        self.to_original_df.loc[after_text_hash] = pd.Series(row)

        transformation_type = transformation.__class__.__name__
        transformation_meta = transformation.__dict__
        from_inds, to_inds = modified_inds_tuple
        row = {
            "transformation_type": transformation_type,
            "transformation_meta": str(transformation_meta),
            "prev_text": before_text_hash,
            "after_text": after_text_hash,
            "from_modified_indices": list(from_inds),
            "to_modified_indices": list(to_inds)
        }
        transform_hash = str(hash(transformation)) + str(hash(transformed_text))
        
        self.transformation_df.loc[transform_hash] = pd.Series(row)
        # text.printable_text()
        
        self._flushed = False

    def flush(self):
        self.transformation_df.to_csv(self.filename, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False)
        self.to_original_df.to_csv(self.filename, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False)
        self._flushed = True

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            logger.warning("ProvenanceLogger exiting without calling flush().")

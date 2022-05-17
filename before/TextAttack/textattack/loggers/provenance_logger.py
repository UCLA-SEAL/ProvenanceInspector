"""
Attack Logs to CSV
========================
"""

import csv

import pandas as pd

from textattack.shared import AttackedText, logger

from .logger import Logger


class ProvenanceLogger(Logger):
    """Logs transformation provenance to a CSV."""

    def __init__(self, filename="provenance.csv"):
        logger.info(f"Logging transformation to CSV at path {filename}")
        self.filename = filename
        self.df = pd.DataFrame()
        self._flushed = True

    def log_transformation(self, original_text, transformed_text, transformation, modified_inds_tuple):
        transformation_type = transformation.__class__.__name__
        transformation_meta = transformation.__dict__
        from_inds, to_inds = modified_inds_tuple
        row = {
            "transformation_type": transformation_type,
            "transformation_meta": transformation_meta,
            "original_text": original_text,
            "transformed_text": transformed_text,
            "from_modified_indices": from_inds,
            "to_modified_indices": to_inds
        }
        self.df = self.df.append(row, ignore_index=True)
        self._flushed = False

    def flush(self):
        self.df.to_csv(self.filename, mode='a', quoting=csv.QUOTE_NONNUMERIC, index=False, header=False)
        self._flushed = True

    def close(self):
        # self.fout.close()
        super().close()

    def __del__(self):
        if not self._flushed:
            logger.warning("ProvenanceLogger exiting without calling flush().")

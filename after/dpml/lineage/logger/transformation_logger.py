"""
Transformation Logs to CSV
========================
"""

import csv

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
        self.init_store()
        

    def init_store(self):
        self.storage = []
        # self.transformation_df = pd.DataFrame(columns=["transformation_id", "transformation_type",
        #     "prev_text", "after_text", "prev_target", "after_target"])
        # "from_modified_indices", "to_modified_indices"])
        

    def log_transformation(self, current_record, transformed_record):
        trans_id = next(TransformationLogger.id_iter)

        current_text_id = current_record.text_id
        transformed_text_id = transformed_record.text_id

        current_text_tgt_id = current_record.target_id
        transformed_text_tgt_id = transformed_record.target_id

        # from_mod_inds, to_mod_inds = modified_inds
        # precarious color editing
        # current_text, transformed_text = color_text_pair(current_text, transformed_text, list(from_inds), list(to_inds))

        edit_tags = (transformed_record.feature_provenance - current_record.feature_provenance).get_tags()

        history = (transformed_record.transformation_provenance - current_record.transformation_provenance).history
        trans = list(history)[0]
        transformation_info = trans[1]

        from_mod_inds = set()
        to_mod_inds = set()

        for tag in edit_tags:
            parts = tag.split(': ')
            op = parts[0]
            tag = parts[1]
            if op == 'replace' or op == 'insert':
                spans = tag[1:-1].split(']-[')
                from_span = tuple(map(int, spans[0].split(',')))
                to_span = tuple(map(int, spans[1].split(',')))
                for i in range(*to_span):
                    to_mod_inds.add(i)
            
            elif op == 'delete':
                from_span = tuple(map(int, tag[1:-1].split(',')))

            for i in range(*from_span):
                from_mod_inds.add(i)

        row = {
            "transformation_id": trans_id,
            "transformation": transformation_info,
            "prev_text": current_text_id,
            "after_text": transformed_text_id,
            "prev_target": current_text_tgt_id,
            "after_target": transformed_text_tgt_id,
            "from_modified_indices": from_mod_inds,
            "to_modified_indices": to_mod_inds,
            "changes": edit_tags
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

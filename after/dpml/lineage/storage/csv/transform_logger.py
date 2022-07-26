"""
Record Logs to DATA_STORE
========================
"""

import os
import csv
import json
import pandas as pd

import hydra

# def get_next_idx(path):
#     if os.path.exists(path):
#         with open(path) as f:
#             idx = sum(1 for line in f)
#         return idx
#     else:
#         return 0

class TransformLogger:
    """
    Store records and transform provenance info
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

    def log(self, input_record, output_record):
        # transformation provenance
        t_diff = (output_record.transformation_provenance - input_record.transformation_provenance)
        f_diff = (output_record.feature_provenance - input_record.feature_provenance)
        history = t_diff.history
        tp = json.loads(list(history)[0][1])

        self.storage.append({
            "input_text": input_record.text,
            "input_target": input_record.target,
            "output_text": output_record.text,
            "output_target": output_record.target,
            "module_name": tp["module_name"],
            "class_name": tp["class_name"],
            "trans_fn_name": tp["trans_fn_name"],
            "is_stochastic": tp["fn_is_stochastic"],
            "transformation_class_args": tp["class_args"],
            "transformation_class_kwargs": tp["class_kwargs"],
            "transformation_transform_args": tp["transform_args"],
            "transformation_transform_kwargs": tp["transform_kwargs"],
            "diff": f_diff.get_tags(),
            "diff_granularity": input_record.le_text.granularity
        })

        self._flushed = False
        if len(self.storage) > self.flush_after_count:
            self.flush()

    def flush(self):
        df = pd.DataFrame(self.storage)
        df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
        self.init_storage()

if __name__ == '__main__':

    from lineage.transformation import *
    from lineage.le_batch import LeBatch
    
    @mark_transformation_class 
    class MyTransformTester:
        def __init__(self, chars_to_append="!"):
            self.chars_to_append=chars_to_append

        @mark_transformation_method
        def transform_batch(self, batch, char_multiplier=0):
            new_text, new_labels = [], []
            for X, y in zip(*batch):
                X += self.chars_to_append * char_multiplier
                y += 1
                new_text.append(X)
                new_labels.append(y)  
            return (new_text, new_labels)
    
    text = ["mytest1", "mytest2"]
    target = [0, 1]
    batch = (text, target)

    transform = MyTransformTester(chars_to_append="?")
    for i in range(1,3):
        batch = LeBatch(batch).apply(transform.transform_batch, char_multiplier=i)

    logger = TransformLogger()
    df = pd.read_csv(logger.path, header=None)
    print(df)

    # ~\dpml\after\dpml\lineage>python storage\csv\transform_logger.py
    #          0   1           2   3   ...  10                      11                        12    13
    # 0   mytest1   0    mytest1?   1  ... NaN  {"char_multiplier": 1}  ['replace: [0,1]-[0,1]']  word
    # 1   mytest2   1    mytest2?   2  ... NaN  {"char_multiplier": 1}  ['replace: [0,1]-[0,1]']  word
    # 2  mytest1?   1  mytest1???   2  ... NaN  {"char_multiplier": 2}  ['replace: [0,1]-[0,1]']  word
    # 3  mytest2?   2  mytest2???   3  ... NaN  {"char_multiplier": 2}  ['replace: [0,1]-[0,1]']  word

    # [4 rows x 14 columns]
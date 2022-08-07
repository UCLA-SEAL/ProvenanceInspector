"""
Record Logs to DATA_STORE
========================
"""

import os
import csv
import json
from black import T, transform_line
import pandas as pd
import itertools


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
        transform_path = os.path.abspath(os.path.join(cfg.storage['path'], cfg.storage['transform_filename']))
        replay_only = cfg.replay_only

    id_iter = itertools.count()

    def __init__(self, path=path, transform_path=transform_path, replay_only=replay_only):
        self.path = path
        self.transform_path = transform_path
        self.replay_only = replay_only
        self._transform_id_counter = 0
        self._transform_id = {}
        self.init_storage()

    def init_storage(self):
        if self.replay_only:
            self._original = []
            self._transform_prov = []
            self._new_transforms = {}
        else:
            self._storage = []
        self._flushed = True


    def log(self, input_record, output_record):
        # transformation provenance
        t_diff = (output_record.transformation_provenance - input_record.transformation_provenance)
        f_diff = (output_record.feature_provenance - input_record.feature_provenance)
        history = t_diff.history
        tp = json.loads(list(history)[0][1])

        self._storage.append({
            "input_text": input_record.text,
            "input_target": input_record.target,
            "output_text": output_record.text,
            "output_target": output_record.target,
            "module_name": tp["module_name"],
            "class_name": tp["class_name"],
            "callable_class_args": tp["class_args"],
            "callable_class_kwargs": tp["class_kwargs"],
            "callable_name": tp["callable_name"],
            "callable_args": tp["callable_args"],
            "callable_kwargs": tp["callable_kwargs"],
            "callable_is_stochastic": tp["callable_is_stochastic"],
            "diff": f_diff.get_tags(),
            "diff_granularity": input_record.le_text.granularity
        })
        self._flushed = False

    def log_original(self, text, target):
        self._original.append((text, target))
        self._flushed = False

    def log_originals(self, texts, targets):
        self._original.extend(zip(texts, targets))
        self._flushed = False

    def log_transform_prov(self, transform_prov):
        self._transform_prov.append(transform_prov)
        self._flushed = False

    def log_transform_provs(self, transform_provs):
        self._transform_prov.extend(transform_provs)
        self._flushed = False

    def _flush_with_replay(self):
        out = []
        batch_id = next(TransformLogger.id_iter)
        for (text, target), t_prov in zip(self._original, self._transform_prov):
            t_id_prov = []
            for t in t_prov:
                if json.dumps(t) in self._transform_id:
                    transform_id = self._transform_id[json.dumps(t)]
                else:
                    transform_id = self._transform_id_counter
                    self._transform_id[json.dumps(t)] = transform_id
                    
                    self._new_transforms[transform_id] = t
                    self._transform_id_counter += 1
                t_id_prov.append(transform_id)

            out.append({
                'batch_id': batch_id, 
                'original_text': text,
                'original_target': target,
                'transformation_provenance': t_id_prov
            })
        df = pd.DataFrame(out)
        df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)

        if len(self._new_transforms) > 0:
            pd.Series(self._new_transforms, dtype=object).to_csv(self.transform_path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False)
            self.new_rows = {}

    # def _flush_with_replay(self):
    #     out = []
    #     for original, t_prov in zip(self._original, self._transform_prov):
    #         for tp in t_prov:
    #             tp = json.loads(tp)
    #             out.append(original | tp) 
    #     df = pd.DataFrame(out)
    #     df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)
                    
    def _flush_without_replay(self):
        df = pd.DataFrame(self._storage)
        df.to_csv(self.path, mode='a', quoting=csv.QUOTE_NONNUMERIC, header=False, index=False)

    def flush(self):
        if self.replay_only:
            self._flush_with_replay()
        else:
            self._flush_without_replay()
        self.init_storage()

if __name__ == '__main__':

    from lineage.transformation import *
    from lineage.le_batch import LeBatch
    
    class MyTransformTester:
        def __init__(self, chars_to_append="!"):
            self.chars_to_append=chars_to_append

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

    MyTransformTester = DPMLClassWrapper(MyTransformTester)
    transform = MyTransformTester(chars_to_append="?")
    with LeBatch(original_batch=batch) as le_batch:
        for i in range(1,5):
            batch = le_batch.apply(batch, transform.transform_batch, char_multiplier=i)

    logger = TransformLogger()
    df = pd.read_csv(logger.path, header=None)
    print(df)

    # ~\dpml\after\dpml\lineage>python storage\csv\transform_logger.py
    #               0   1                  2   3   ...                      10     11                        12    13
    # 0        mytest1   0           mytest1?   1  ...  {"char_multiplier": 1}  False  ['replace: [0,1]-[0,1]']  word
    # 1        mytest2   1           mytest2?   2  ...  {"char_multiplier": 1}  False  ['replace: [0,1]-[0,1]']  word
    # 2       mytest1?   1         mytest1???   2  ...  {"char_multiplier": 2}  False  ['replace: [0,1]-[0,1]']  word
    # 3       mytest2?   2         mytest2???   3  ...  {"char_multiplier": 2}  False  ['replace: [0,1]-[0,1]']  word
    # 4     mytest1???   2      mytest1??????   3  ...  {"char_multiplier": 3}  False  ['replace: [0,1]-[0,1]']  word
    # 5     mytest2???   3      mytest2??????   4  ...  {"char_multiplier": 3}  False  ['replace: [0,1]-[0,1]']  word
    # 6  mytest1??????   3  mytest1??????????   4  ...  {"char_multiplier": 4}  False  ['replace: [0,1]-[0,1]']  word
    # 7  mytest2??????   4  mytest2??????????   5  ...  {"char_multiplier": 4}  False  ['replace: [0,1]-[0,1]']  word

    # [8 rows x 14 columns]
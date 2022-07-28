"""
Record Logs to DATA_STORE
========================
"""

from multiprocessing import connection
import hydra

from .models import *
from .utils import *

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists

class TransformLogger:
    """
    Store records and transform provenance info
    """

    hydra.core.global_hydra.GlobalHydra.instance().clear()
    with hydra.initialize(version_base=None, config_path="../../config"):
        cfg = hydra.compose(config_name="config", overrides=["storage=sqlite"])
        connection_string = build_url_from_cfg(cfg)
        replay_only = cfg.replay_only

    def __init__(self, connection_string=connection_string, replay_only=replay_only):
        self.engine = create_engine(connection_string, future=True)
        if not database_exists(self.engine.url):
            print("creating database tables from models...")
            Base.metadata.create_all(self.engine)
        self.replay_only = replay_only
        self.init_storage()

    def init_storage(self):
        if self.replay_only:
            self._original = []
            self._transform_prov = []
        else:
            self._storage = []
        self._flushed = True

    def log(self, input_record, output_record):
        self._storage.append((input_record, output_record))
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
        with Session(self.engine) as session:
            for (text, target), t_prov in zip(self._original, self._transform_prov):

                # store records
                in_record = create_and_return(
                    session, Record,
                    text=text, 
                    target=target
                )

                # store transform provenance
                for tp in t_prov:

                    tp = json.loads(tp)
                    
                    transform, is_created = get_or_create(
                        session, Transform,
                        module_name = tp["module_name"],
                        class_name = tp["class_name"],
                        trans_fn_name = tp["trans_fn_name"],
                        is_stochastic = tp["fn_is_stochastic"],
                    )
                    transform_applied = create_and_return(
                        session, TransformApplied,
                        transformation_id = transform.id,
                        class_args = tp["class_args"],
                        class_kwargs = tp["class_kwargs"],
                        transform_args = tp["transform_args"],
                        transform_kwargs = tp["transform_kwargs"],
                        input_record_id = in_record.id,
                        # output_record_id = out_record.id,
                        # diff = f_diff.get_tags(),
                        # diff_granularity = in_rec.le_text.granularity,
                    )

    def _flush_without_replay(self):
        with Session(self.engine) as session:
            for in_rec, out_rec in self._storage:

                # store records
                in_record = create_and_return(
                    session, Record,
                    text=in_rec.text, 
                    target=in_rec.target
                )
                out_record = create_and_return(
                    session, Record,
                    text=out_rec.text, 
                    target=out_rec.target
                )

                # transformation provenance
                t_diff = (out_rec.transformation_provenance - in_rec.transformation_provenance)
                f_diff = (out_rec.feature_provenance - in_rec.feature_provenance)
                history = t_diff.history
                tp = json.loads(list(history)[0][1])

                transform, is_created = get_or_create(
                    session, Transform,
                    module_name = tp["module_name"],
                    class_name = tp["class_name"],
                    trans_fn_name = tp["trans_fn_name"],
                    is_stochastic = tp["fn_is_stochastic"],
                )
                transform_applied = create_and_return(
                    session, TransformApplied,
                    input_record_id = in_record.id,
                    output_record_id = out_record.id,
                    diff = f_diff.get_tags(),
                    diff_granularity = in_rec.le_text.granularity,
                    transformation_id = transform.id,
                    class_args = tp["class_args"],
                    class_kwargs = tp["class_kwargs"],
                    transform_args = tp["transform_args"],
                    transform_kwargs = tp["transform_kwargs"],
                )

    def flush(self):
        if self.replay_only:
            self._flush_with_replay()
        else:
            self._flush_without_replay()
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
    with LeBatch(original_batch=batch) as le_batch:
        for i in range(1,3):
            batch = le_batch.apply(batch, transform.transform_batch, char_multiplier=i)

    logger = TransformLogger()

    from sqlalchemy import select
    
    stmt = select(Record).where(Record.text.like('mytest%'))
    with logger.engine.connect() as conn:
        for row in conn.execute(stmt):
            print(row._mapping)

    stmt = select(Transform)
    with logger.engine.connect() as conn:
        for row in conn.execute(stmt):
            print(row._mapping)

    stmt = select(TransformApplied)
    with logger.engine.connect() as conn:
        for row in conn.execute(stmt):
            print(row._mapping)


    # ~\dpml\after\dpml\lineage>python storage\sqlalchemy\transformation_logger.py
    # creating database tables from models..
    # (1, 'mytest1', '0', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (2, 'mytest1?', '1', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (3, 'mytest2', '1', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (4, 'mytest2?', '2', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (5, 'mytest1?', '1', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (6, 'mytest1???', '2', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (7, 'mytest2?', '2', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (8, 'mytest2???', '3', datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (1, '__main__', 'MyTransformTester', 'transform_batch', False, datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (1, 1, None, {'chars_to_append': '?'}, None, {'char_multiplier': 1}, 1, 2, ['replace: [0,1]-[0,1]'], <RefGranularity.word: 2>, datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (2, 1, None, {'chars_to_append': '?'}, None, {'char_multiplier': 1}, 3, 4, ['replace: [0,1]-[0,1]'], <RefGranularity.word: 2>, datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (3, 1, None, {'chars_to_append': '?'}, None, {'char_multiplier': 2}, 5, 6, ['replace: [0,1]-[0,1]'], <RefGranularity.word: 2>, datetime.datetime(2022, 7, 20, 8, 59, 8))
    # (4, 1, None, {'chars_to_append': '?'}, None, {'char_multiplier': 2}, 7, 8, ['replace: [0,1]-[0,1]'], <RefGranularity.word: 2>, datetime.datetime(2022, 7, 20, 8, 59, 8))
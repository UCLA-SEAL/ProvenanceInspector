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
                        class_args = tp["class_args"],
                        class_kwargs = tp["class_kwargs"],
                        callable_name = tp["callable_name"],
                        callable_args = tp["callable_args"],
                        callable_kwargs = tp["callable_kwargs"],
                        callable_is_stochastic = tp["callable_is_stochastic"],
                    )
                    transform_applied = create_and_return(
                        session, TransformApplied,
                        transformation_id = transform.id,
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
                    class_args = tp["class_args"],
                    class_kwargs = tp["class_kwargs"],
                    callable_name = tp["callable_name"],
                    callable_args = tp["callable_args"],
                    callable_kwargs = tp["callable_kwargs"],
                    callable_is_stochastic = tp["callable_is_stochastic"],
                )

                transform_applied = create_and_return(
                    session, TransformApplied,
                    input_record_id = in_record.id,
                    output_record_id = out_record.id,
                    diff = f_diff.get_tags(),
                    diff_granularity = in_rec.le_text.granularity,
                    transformation_id = transform.id
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


    # ~\dpml\after\dpml\lineage>python storage\sqlalchemy\transform_logger.py
    # creating database tables from models...
    # {'id': 1, 'text': 'mytest1', 'target': '0', 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 2, 'text': 'mytest2', 'target': '1', 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 1, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 1}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 2, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 2}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 3, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 3}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 4, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 4}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 1, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 1, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 2, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 2, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 3, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 3, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 4, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 4, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 5, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 1, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 6, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 2, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 7, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 3, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
    # {'id': 8, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transformation_id': 4, 'created_at': datetime.datetime(2022, 8, 2, 1, 29, 24)}
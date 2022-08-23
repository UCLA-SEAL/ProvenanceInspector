"""
Record Logs to storage
========================
"""
from datetime import datetime
import hydra

from .models import *
from .utils import *

import json

from sqlalchemy import create_engine
from sqlalchemy import select
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
        flush_after_n_items = cfg.storage.flush_after_n_items

    def __init__(self, connection_string=connection_string, 
                       replay_only=replay_only,
                       flush_after_n_items = flush_after_n_items):
        self.engine = create_engine(connection_string, future=True)
        self.create_db_if_needed()
        self.replay_only = replay_only
        self.flush_after_n_items = flush_after_n_items
        self._batch_id = 0
        self._transforms = {}
        self.init_storage()
        self.set_new_run()

    def init_storage(self):
        if self.replay_only:
            self._storage = []
            self._transform_prov = []
            self._batch_ids = []
            self.set_next_ids()
        else:
            self._storage = []
        self._flushed = True

    def create_db_if_needed(self):
        if not database_exists(self.engine.url):
            print("creating database tables from models...")
            Base.metadata.create_all(self.engine)

    def set_new_run(self, run_name=None):
        if not run_name:
            run_name = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.run_name = run_name

    def set_next_ids(self):
        with self.engine.connect() as conn:
            self.next_R_id = len(list(conn.execute(select(Record)))) + 1
            self.next_T_id = len(list(conn.execute(select(Transform)))) + 1
            self.next_TA_id = len(list(conn.execute(select(TransformApplied)))) + 1

    def log(self, input_record, output_record):
        self._storage.append((input_record, output_record))
        self._batch_ids.append(self._batch_id)
        self._batch_id += 1
        self._flushed = False

    def log_original(self, text, target):
        self._storage.append((text, target))
        self._flushed = False

    def log_originals(self, texts, targets):
        self._storage.extend(zip(texts, targets))
        self._flushed = False

    def log_transform_prov(self, transform_prov):
        self._transform_prov.append(transform_prov)
        self._batch_ids.append(self._batch_id)
        self._batch_id += 1
        self._flushed = False

    def log_transform_provs(self, transform_provs):
        self._transform_prov.extend(transform_provs)
        self._batch_ids.extend([self._batch_id]*len(transform_provs))
        self._batch_id += 1
        self._flushed = False

    def _flush_with_replay(self):

        with Session(self.engine) as session:

            # store run
            run, is_created = get_or_commit(
                session, Run,
                name=self.run_name
            )

            Rs, Ts, TAs = [], [], []
            for i, (batch_id, (text, target), t_prov) in enumerate(zip(self._batch_ids, 
                                                                       self._storage, 
                                                                       self._transform_prov)):
                # print(self.next_R_id, self.next_T_id, self.next_TA_id)

                r = Record(
                    id = self.next_R_id,
                    text = text,
                    target = target
                )
                Rs.append(r)
                self.next_R_id += 1
                               
                # store transform provenance
                for tp in t_prov:
                    tp = json.loads(tp)
                    random_state_info = tp.pop('callable_rng_state')
                    tp_dump = json.dumps(tp)
                    if tp_dump in self._transforms:
                        # print(1, tp_dump)
                        T_id = self._transforms[tp_dump]
                    else:
                        # print(2, tp_dump)
                        T_id = self.next_T_id
                        t = Transform(
                            id = T_id,
                            module_name = tp["module_name"],
                            class_name = tp["class_name"],
                            class_args = tp["class_args"],
                            class_kwargs = tp["class_kwargs"],
                            class_rng = tp["class_rng"],
                            callable_name = tp["callable_name"],
                            callable_args = tp["callable_args"],
                            callable_kwargs = tp["callable_kwargs"],
                            callable_is_stochastic = tp["callable_is_stochastic"],
                        )
                        Ts.append(t)
                        self._transforms[tp_dump] = T_id
                        self.next_T_id += 1

                    ta = TransformApplied(
                        id = self.next_TA_id,
                        input_record_id = r.id,
                        transform_id = T_id,
                        transform_state = random_state_info,
                        run_id = run.id,
                        batch_id = batch_id
                        # output_record_id = out_record.id,
                        # diff = f_diff.get_tags(),
                        # diff_granularity = in_rec.le_text.granularity,
                    )
                    TAs.append(ta)
                    self.next_TA_id += 1


            session.bulk_save_objects(Rs)
            session.bulk_save_objects(Ts)
            session.bulk_save_objects(TAs)
            session.commit()
    
    # def _flush_with_replay(self):

    #     with Session(self.engine) as session:

    #         # store run
    #         run, is_created = get_or_commit(
    #             session, Run,
    #             name=self.run_name
    #         )

    #         for i, (batch_id, (text, target), t_prov) in enumerate(zip(self._batch_ids, 
    #                                                                    self._storage, 
    #                                                                    self._transform_prov)):

    #             r = Record(
    #                 text = text,
    #                 target = target
    #             )
    #             session.add(r)
                               
    #             # store transform provenance
    #             for j, tp in enumerate(t_prov):

    #                 tp = json.loads(tp)
                    
    #                 t, is_created = get_or_add(
    #                     session, Transform,
    #                     module_name = tp["module_name"],
    #                     class_name = tp["class_name"],
    #                     class_args = tp["class_args"],
    #                     class_kwargs = tp["class_kwargs"],
    #                     class_rng = tp["class_rng"],
    #                     callable_name = tp["callable_name"],
    #                     callable_args = tp["callable_args"],
    #                     callable_kwargs = tp["callable_kwargs"],
    #                     callable_is_stochastic = tp["callable_is_stochastic"],
    #                 )

    #                 ta = TransformApplied(
    #                     input_record_id = r.id,
    #                     transform_id = t.id,
    #                     transform_state = tp["callable_rng_state"],
    #                     run_id = run.id,
    #                     batch_id = batch_id
    #                     # output_record_id = out_record.id,
    #                     # diff = f_diff.get_tags(),
    #                     # diff_granularity = in_rec.le_text.granularity,
    #                 )
    #                 session.add(ta)

    #         session.commit()

    # def _flush_with_replay(self):

    #     with Session(self.engine) as session:

    #         # store run
    #         run, is_created = get_or_create(
    #             session, Run,
    #             name=self.run_name
    #         )
            
    #         for batch_id, (text, target), t_prov in zip(self._batch_ids, self._storage, self._transform_prov):
                
    #             # store records
    #             in_record = create_and_return(
    #                 session, Record,
    #                 text=text, 
    #                 target=target
    #             )

    #             # store transform provenance
    #             for tp in t_prov:

    #                 tp = json.loads(tp)
                    
    #                 transform, is_created = get_or_create(
    #                     session, Transform,
    #                     module_name = tp["module_name"],
    #                     class_name = tp["class_name"],
    #                     class_args = tp["class_args"],
    #                     class_kwargs = tp["class_kwargs"],
    #                     class_rng = tp["class_rng"],
    #                     callable_name = tp["callable_name"],
    #                     callable_args = tp["callable_args"],
    #                     callable_kwargs = tp["callable_kwargs"],
    #                     callable_is_stochastic = tp["callable_is_stochastic"],
    #                 )
    #                 transform_applied = create_and_return(
    #                     session, TransformApplied,
    #                     input_record_id = in_record.id,
    #                     transform_id = transform.id,
    #                     transform_state = tp["callable_rng_state"],
    #                     run_id = run.id,
    #                     batch_id = batch_id
    #                     # output_record_id = out_record.id,
    #                     # diff = f_diff.get_tags(),
    #                     # diff_granularity = in_rec.le_text.granularity,
    #                 )

    def _flush_without_replay(self):

        with Session(self.engine) as session:

            # store run
            run, is_created = get_or_commit(
                session, Run,
                name=self.run_name
            )

            for batch_id, (in_rec, out_rec) in zip(self._batch_ids, self._storage):
                
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

                transform, is_created = get_or_commit(
                    session, Transform,
                    module_name = tp["module_name"],
                    class_name = tp["class_name"],
                    class_args = tp["class_args"],
                    class_kwargs = tp["class_kwargs"],
                    class_rng = tp["class_rng"],
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
                    transform_id = transform.id,
                    transform_state = tp["callable_rng_state"],
                    run_id = run.id,
                    batch_id = batch_id
                )

    def flush(self, force=False):
        if force or len(self._storage) >= self.flush_after_n_items:
            if self.replay_only:
                self._flush_with_replay()
            else:
                self._flush_without_replay()
            self.init_storage()

    def clean_data_store(self):
        # Base.metadata.drop_all(self.engine)
        with Session(self.engine) as session:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        self.init_storage()
        self._transforms = {}

if __name__ == '__main__':

    from lineage.transformation import *
    from lineage.le_batch import LeBatch
    from sqlalchemy import select
    
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


    # ~\dpml\lineage>python storage\sqlalchemy\transform_logger.py
    # creating database tables from models...
    # {'id': 1, 'text': 'mytest1', 'target': '0', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 2, 'text': 'mytest2', 'target': '1', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 1, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'class_rng': None, 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 1}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 2, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'class_rng': None, 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 2}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 3, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'class_rng': None, 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 3}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 4, 'module_name': '__main__', 'class_name': 'MyTransformTester', 'class_args': 'null', 'class_kwargs': '{"chars_to_append": "?"}', 'class_rng': None, 'callable_name': 'transform_batch', 'callable_args': 'null', 'callable_kwargs': '{"char_multiplier": 4}', 'callable_is_stochastic': False, 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 1, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 1, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 2, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 2, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 3, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 3, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 4, 'input_record_id': 1, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 4, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 5, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 1, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 6, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 2, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 7, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 3, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
    # {'id': 8, 'input_record_id': 2, 'output_record_id': None, 'diff': None, 'diff_granularity': None, 'transform_id': 4, 'transform_state': 'null', 'created_at': datetime.datetime(2022, 8, 12, 20, 26, 30)}
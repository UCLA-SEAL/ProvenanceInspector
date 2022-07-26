"""
Record Logs to DATA_STORE
========================
"""

import hydra

from .models import *
from .utils import *

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists

class RecordLogger:
    """
    Store records as (text, target) tuples
    """
    
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    with hydra.initialize(version_base=None, config_path="../../config"):
        cfg = hydra.compose(config_name="config")
        connection_string = build_url_from_cfg(cfg)

    def __init__(self, connection_string=connection_string, flush_after_count=100):
        self.engine = create_engine(connection_string, future=True)
        if not database_exists(self.engine.url):
            print("creating database tables from models..")
            Base.metadata.create_all(self.engine)
        self.flush_after_count = flush_after_count
        self.init_storage()

    def init_storage(self):
        self.storage = []
        self._flushed = True

    def log(self, record):
        self.storage.append(record)
        self._flushed = False
        if len(self.storage) > self.flush_after_count:
            self.flush()

    def flush(self):
        with Session(self.engine) as session:
            records = [Record(text=text, target=target) for text, target in self.storage]
            session.add_all(records)
            session.commit()
        self.init_storage()

if __name__ == '__main__':
    
    logger = RecordLogger()
    logger.log(("mytest1", 0))
    logger.log(("mytest2", 1))
    logger.flush()

    from sqlalchemy import select
    
    stmt = select(Record).where(Record.text.like('mytest%'))
    with logger.engine.connect() as conn:
        for row in conn.execute(stmt):
            print(row)

    # ~\dpml\after\dpml\lineage>python storage\sqlalchemy\record_logger.py
    # creating database tables from models..
    # (1, 'mytest1', '0', datetime.datetime(2022, 7, 20, 6, 23, 35))
    # (2, 'mytest2', '1', datetime.datetime(2022, 7, 20, 6, 23, 35))
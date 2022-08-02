import os
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

def build_local_db_url(dialect, path, name):
    url = ""
    if dialect:
        url += dialect + ":///"
    if path and name:
        url += os.path.abspath(os.path.join(path, name))
    return url

def build_server_db_url(dialect, driver, username, password, host, port, database):
    url = ""
    if dialect:
        url += dialect
    if driver:
        url += "+" + driver
    url += "://"
    if username:
        url += username + ":"
    if password:
        url += password
    if host:
        url += "@" + host + ":"
    if port:
        url += port
    if database:
        url += "/" + database
    return url

def build_url_from_cfg(cfg):
    if cfg.storage.dialect in ["sqlite"]:
        return build_local_db_url(cfg.storage.dialect, cfg.storage.path, cfg.storage.name)
    elif cfg.stoage.dialect in ["mssql", "mysql", "postgresql"]:
        return build_server_db_url(cfg.storage.dialect, cfg.storage.driver, cfg.storage.username, 
                                   cfg.storage.password, cfg.storage.host, cfg.storage.port, cfg.storage.database)
    else: 
        return None

def infer_type(value):
	return type(eval(value))

def create_and_return(session, model, defaults=None, **kwargs):
    kwargs |= defaults or {}
    instance = model(**kwargs)
    try:
        session.add(instance)
        session.commit()
    except Exception:  
        session.rollback()
        return instance
    else:
        return instance

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance, False
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)
        try:
            session.add(instance)
            session.commit()
        except Exception:  
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance, False
        else:
            return instance, True

def get_records_and_provenance(session):
    records_stmt = text(
        """
        SELECT r.id, r.text, r.target
        FROM Record r
        """
    )

    provenance_stmt = text(
        """
        SELECT t.*, ta.* 
        FROM TransformApplied ta
        INNER JOIN Transform t ON ta.transformation_id = t.id
        WHERE ta.input_record_id == :id
        """
    )

    record_rows = session.execute(records_stmt)
    
    records_to_replay = []
    for row in record_rows:
        records_to_replay.append(row._mapping)
    
    provenance_to_replay = []
    for record in records_to_replay:
        provenance_rows = session.execute(provenance_stmt, dict(record))
        prov = []
        for row in provenance_rows:
            prov.append(row._mapping)
        provenance_to_replay.append(prov)
    
    return records_to_replay, provenance_to_replay
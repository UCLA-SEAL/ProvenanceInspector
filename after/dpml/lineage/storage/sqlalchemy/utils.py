import os

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
from hydra import compose, initialize

with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
    if 'dialect' in cfg.storage:
        from .sqlalchemy.transform_logger import TransformLogger
    else:
        from .csv.transform_logger import TransformLogger
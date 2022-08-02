import inspect
import json
from functools import partial
import pandas as pd
from sqlalchemy.orm import Session
from ..storage.sqlalchemy.utils import get_records_and_provenance

def full_module_name(o):
    """
    returns module_name (str), class_name (str)
    """
    if inspect.ismethod(o):
        return o.__self__.__module__, o.__self__.__class__.__name__
    elif inspect.isfunction(o):
        return o.__module__, None
    elif inspect.isclass(o):
        return o.__module__, o.__name__
    elif inspect.isclass(type(o)):
        return type(o).__module__, type(o).__name__    
    else:
        raise ValueError(f"Unable to parse {o} ({type(o)})")

def dynamic_import(module_name, obj_name):
    """
    Fetches both classes and functions without a class
    """
    
    module_path = module_name.split('.')
    
    #__import__ method used
    # to fetch module
    module = __import__(module_path[0])
    
    for cur_module in module_path[1:]:
        module = getattr(module, cur_module, None)
        
    my_class = None
    if module:
        # getting attribute by getattr() method
        obj = getattr(module, obj_name)

    return obj

def preprocess_params(param):
    if param in ['null', '"null"']:
        return {}
    else:
        while isinstance(param, str):
            param = json.loads(param)
        return param

def load_transform_from_replay_provenance(prov_dict):
    """
    Example: 
        t_prov = json.loads(t_raw)
        t_fn = load_transform_from_replay_provenance(t_prov)
        batch = t_fn(batch)
    """

    t = prov_dict

    # load transformation
    if t['class_name'] not in ['null', '"null"']:
        t_class = dynamic_import(t['module_name'],t['class_name'])
        class_args = preprocess_params(t['class_args'])
        class_kwargs = preprocess_params(t['class_kwargs'])
        t_instance = t_class(*class_args, **class_kwargs)
        t_fn = getattr(t_instance, t['callable_name'])
    else:
        t_fn = dynamic_import(t['module_name'],t['trans_fn_name'])
        
    # process transformation
    t_args = preprocess_params(t['callable_args'])
    t_kwargs = preprocess_params(t['callable_kwargs'])
    
    t_fn = partial(t_fn, *t_args, **t_kwargs)
    
    return t_fn

def replay_all_from_db():

    from lineage.storage.sqlalchemy.transform_logger import TransformLogger as SQLTransformLogger

    # fetch data
    logger = SQLTransformLogger()
    records_to_replay, provenance_to_replay = get_records_and_provenance(Session(logger.engine))

    # repay
    new_records = []
    for rec, prov in zip(records_to_replay, provenance_to_replay):
        batch = ([rec['text']], [eval(rec['target'])])
        for t_raw in prov:
            t_prov = dict(t_raw)
            t_fn = load_transform_from_replay_provenance(t_prov)
            batch = t_fn(batch)
        new_records.append(batch)
    return new_records

def replay_all_from_csv():
        
    from lineage.storage.csv.transform_logger import TransformLogger as CSVTransformLogger
    
    # fetch data
    logger = CSVTransformLogger()
    df = pd.read_csv(logger.path, header=None, names=['text', 'target', 'transform_prov'])
    
    # replay
    new_records = []
    for idx, row in df.iterrows():
        batch = ([row['text']], [row['target']])
        for t_raw in eval(row['transform_prov']):
            t_prov = json.loads(t_raw)
            t_fn = load_transform_from_replay_provenance(t_prov)
            batch = t_fn(batch)
        new_records.append(batch)
    return new_records
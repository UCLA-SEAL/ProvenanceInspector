import inspect
import json
from functools import partial
import pandas as pd
from sqlalchemy.orm import Session
from ..storage.sqlalchemy.utils import get_records_and_provenance
from collections import defaultdict
import numpy as np
import copy

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
    
    # for cur_module in module_path[1:]:
    #     module = getattr(module, cur_module, None)
    
    if module and hasattr(module, obj_name):
        # getting attribute by getattr() method
        obj = getattr(module, obj_name)
    else:
        obj = None

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
        if t['callable_is_stochastic'] and 'callable_rng_state' in t:
            rng_state = preprocess_params(t['callable_rng_state'])
            random_generator = getattr(t_instance, t['class_rng'])
            random_generator.__setstate__(rng_state)
            setattr(t_instance, t['class_rng'], random_generator)
        t_fn = getattr(t_instance, t['callable_name'])
    else:
        t_fn = dynamic_import(t['module_name'], t['trans_fn_name'])
        
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

    # replay
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
    df = pd.read_csv(logger.path, header=None, names=['batch_id', 'text', 'target', 'transform_prov'])
    transform_df = pd.read_csv(logger.transform_path, header=None, index_col=0, names=['transform_id', 'transform'])
    
    transform_idxs = set()
    batches = {}
    for idx, row in df.iterrows():
        bid = row['batch_id']
        if bid not in batches:
            batches[bid] = {'text':[], 'target':[], 'transform': []}

        batches[bid]['text'].append(row['text'])
        batches[bid]['target'].append(row['target'])

        if len(batches[bid]['transform']) == 0:
            batches[bid]['transform'] = eval(row['transform_prov'])
            transform_idxs = transform_idxs | set(batches[bid]['transform'])
                    
    transforms = []
    random_states = []
    hashes = []
    mapping = {}
    for idx in transform_idxs:
        t_prov = json.loads(transform_df.loc[idx]['transform'])
        random_state_attr = t_prov.pop('class_rng')
        random_state_info = t_prov.pop('callable_rng_state')
        random_states.append((random_state_attr, random_state_info))

        t_prov_hash = hash(repr(t_prov))
        if t_prov_hash not in hashes:
            transforms.append(load_transform_from_replay_provenance(t_prov))
            hashes.append(t_prov_hash)
            mapping[idx] = hashes.index(t_prov_hash)
        else:
            mapping[idx] = hashes.index(t_prov_hash)

    # replay
    new_records = []
    for batch_id in sorted(list(batches.keys())):
        batch = (batches[batch_id]['text'], batches[batch_id]['target'])
        for idx in batches[batch_id]['transform']:
            rs_attr, rs_info = random_states[idx]
            fn_id = mapping[idx]
            t_fn = set_rng_state(transforms[fn_id], rs_attr, rs_info)
            batch = t_fn(batch)
        texts, labels = batch
        new_records += [(x, y) for x,y in zip(texts, labels)]

    # del df, transform_df, batches, transforms, random_states, hashes, mapping
            
    return new_records

def set_rng_state(fn, attr, state):
    rng_state = preprocess_params(state)
    random_generator = getattr(fn.func.__self__, attr)
    random_generator.__setstate__(rng_state)
    setattr(fn.func.__self__, attr, random_generator)
    return fn
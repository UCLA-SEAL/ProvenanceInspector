from inspect import signature, ismethod, isfunction
import json

from .lazy_cloneable_provenance import LazyCloneableProvenance
from lineage.utils import add_branch_prefix, full_module_name
from lineage.transformation import DPMLCallableWrapper

def find_inner_self(obj):
    while not hasattr(obj, '__self__') and hasattr(obj, '__wrapped__'):
        obj = obj.__wrapped__
    return obj.__self__

def exclude_unserializable(arg_list):
    if isinstance(arg_list, tuple):
        args = []
        for arg in arg_list:
            try:
                json.dumps(arg)
                args.append(arg)
            except:
                args.append(repr(arg))
        return args
    elif isinstance(arg_list, dict):
        kwargs = {}
        for key, val in arg_list.items():
            try:
                json.dumps(val)
                kwargs[key] = val
            except:
                kwargs[key] = repr(val)
        return kwargs


class TransformationProvenance(LazyCloneableProvenance):
    def __init__(self, history=None, store_type='Set'):
        super().__init__()
        self.store_type = store_type
        if history:
            self.history = history
        else:
            if store_type=='Set':
                self.history = set()
            else:
                raise ValueError(f"{store_type} is not supported for TransformationProvenance creation")

    def _cloneProvenance(self):
        return TransformationProvenance(history=self.history.copy(), store_type=self.store_type)
        
    def add_provenance(self, transformation):
        """
        TODO: `callable_rng_state` changes often and it causes the transformations to be technically  
              unique from one another, which significantly expands storage (and slows down replay a bit).  
              We need to think of another option:
                - Enforce 1 random state
                    - pros: simplifies storage
                    - cons: decreases output diversity of transformations
                - Separate random states table
                    - pros: preserves diversity, reduces storage costs more than current design
                    - cons: increases data storage complexity
                - ???
        """
        transformation_order = len(self.history)

        if isinstance(transformation.__class__, DPMLCallableWrapper):
            module_name, class_name = full_module_name(transformation.parent_class)
        else:
            if  ismethod(transformation):
                transformation = transformation.__self__
            elif isfunction(transformation):
                transformation = find_inner_self(transformation)

        transformation_info={
            "module_name": transformation._module_name,
            "class_name":  transformation._class_name,
            "class_args": json.dumps(exclude_unserializable(transformation._class_args)),
            "class_kwargs": json.dumps(exclude_unserializable(transformation._class_kwargs)),
            "class_rng": transformation._class_rng,
            "callable_name": transformation._callable_name,
            "callable_args": json.dumps(exclude_unserializable(transformation._callable_args)),
            "callable_kwargs": json.dumps(exclude_unserializable(transformation._callable_kwargs)),
            "callable_is_stochastic": transformation._callable_is_stochastic,
            "callable_rng_state": json.dumps(transformation._callable_rng_state)
        }

        new_provenance = self._cloneProvenance()
        new_provenance.history.add((transformation_order, json.dumps(transformation_info)))
        return new_provenance

    def _merge(self, others):
        cur_hist = add_branch_prefix(self.history, 0)
        # append '#' to all provenance order numbers
        for i,other in enumerate(others):
            cur_hist.add(add_branch_prefix(other.history, i+1))
        
        self.history = cur_hist

        return self 

    def _sub(self, other):
        new_provenance = self._cloneProvenance()
        new_provenance.history = self.history - other.history
        return new_provenance


    def __eq__(self, other):
        if self.history != other.history:
            return False
            
        return True

    def __str__(self):
        return str(self.history)

    def __repr__(self):
        return f'<TransformationProvenance: {self.history}>'
    '''
    def containsAll(self, other):
        return other.history.issubset(self.history)
    '''
    

    

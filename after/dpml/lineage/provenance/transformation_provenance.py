from inspect import signature
import json

from.lazy_cloneable_provenance import LazyCloneableProvenance
from lineage.utils import add_branch_prefix, full_module_name


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
        transformation_order = len(self.history)
        #transformation_info = dir(transformation)

        #sig = signature(transformation.__init__)
        #for arg_name in sig.parameters.keys():
        #    if arg_name not in {'self', 'args', 'kwargs'}:
        #        transformation_info[arg_name] = getattr(transformation, arg_name)

        '''
        for name in vars(transformation):
            if name.startswith("__"):
                continue
            attr = getattr(transformation, name)
            if callable(attr):
                continue
            transformation_info[name] = attr
        '''

        module_name, class_name = full_module_name(transformation)
        transformation_info={
            "module_name": module_name,
            "class_name":  class_name,
            "trans_fn_name": transformation._transform_func,
            # serialization for callables, exclude them for now
            "init_args": exclude_unserializable(transformation._init_args),
            "init_kwargs": exclude_unserializable(transformation._init_kwargs),
            "transform_args": exclude_unserializable(transformation._transform_args),
            "transform_kwargs": exclude_unserializable(transformation._transform_kwargs)
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
    

    

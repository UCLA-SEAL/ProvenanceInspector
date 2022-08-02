import itertools
import functools
import inspect

'''
decorator to record initalization arguments of transformation class and transformation method
'''

def mark_transformation_class(transform_class=None, transform_method=None):
    def _decorate(original_transform_class):
        orig_init = original_transform_class.__init__
        def __init__(self, *args, **kwargs):
            if transform_method:
                setattr(self, transform_method, mark_transformation_method(getattr(self, transform_method)))
            orig_init(self, *args, **kwargs) # Call the original __init__
            self._module_name = transform_class.__module__
            self._class_name = transform_class.__name__
            self._class_args = args if args else []
            self._class_kwargs = kwargs if kwargs else []
        original_transform_class.__init__ = __init__ # Set the class' __init__ to the new one
        return original_transform_class
    if transform_class:
        return _decorate(transform_class)
    return _decorate


def mark_abstract_transformation_class(abstract_class=None, transform=None):
    def _decorate(origin_abstract_class):
        def __init_subclass__(subcls, **kwargs):
            subcls = mark_transformation_class(transform_class=subcls, transform_method=transform)
            super(origin_abstract_class, subcls).__init_subclass__(**kwargs)
        origin_abstract_class.__init_subclass__ = classmethod(__init_subclass__) # Set the class' __init__ to the new one
        return origin_abstract_class
    if abstract_class:
        return _decorate(abstract_class)
    return _decorate


def mark_transformation_method(transform_method=None, *, is_stochastic=False):
    def _decorate(trans_func):
        @functools.wraps(trans_func)
        def wrapped_function(*args, **kwargs):
            if len(args) > 0 and hasattr(args[0], trans_func.__name__):
                original_transform_obj = args[0]
                args, kwargs = clean_args_and_kwargs(original_transform_obj, args, kwargs)
            else:
                original_transform_obj = trans_func
                if hasattr(original_transform_obj, '__self__'):
                    original_transform_obj = original_transform_obj.__self__
                args, kwargs = clean_args_and_kwargs(original_transform_obj, args, kwargs)
            if getattr(original_transform_obj, trans_func.__name__, None):
                original_transform_obj._module_name = original_transform_obj.__module__
                original_transform_obj._callable_name = trans_func.__name__
                original_transform_obj._callable_args = args if args else []
                original_transform_obj._callable_kwargs = kwargs if kwargs else []
                original_transform_obj._callable_is_stochastic = is_stochastic  
            return trans_func(*args, **kwargs)
        return wrapped_function
    if transform_method:
        return _decorate(transform_method)
    return _decorate


"""
Class and Callable wrappers for objects already in memory (no need to modify source code)
"""

class DPMLClassWrapper(object):
    def __init__(self, wrapped_class):
        self.wrapped_class = wrapped_class
        self.init_class = None
        self.callable = None
        
        self._class_name = wrapped_class.__name__
        self._module_name = wrapped_class.__module__

    def __call__(self, *args, **kwargs):
        self._class_args = args if args else []
        self._class_kwargs = kwargs if kwargs else []
        self.init_class = self.wrapped_class(*args, **kwargs)
        return self

    def __getattr__(self, attr):
        orig_attr = self.init_class.__getattribute__(attr)
        if callable(orig_attr):
            self.init_hooked_callable(orig_attr)
            return self.hooked_callable
        else:
            return orig_attr

    def init_hooked_callable(self, _callable):
        self.callable = DPMLCallableWrapper(_callable, parent_class=self)

    def hooked_callable(self, *args, **kwargs):
                
        # run callable
        result = self.callable(*args, **kwargs)
        
        # track callable args + kwargs
        self._callable_name = self.callable._callable_name
        self._callable_args = self.callable._callable_args
        self._callable_kwargs = self.callable._callable_kwargs
        self._callable_is_stochastic = self.callable._callable_is_stochastic
        
        # prevent init_class from becoming unwrapped
        if isinstance(result, self.wrapped_class):
            return self
        
        return result

        
        
class DPMLCallableWrapper(object):
    def __init__(self, wrapped_callable, parent_class=None, is_stochastic=False):
        self.wrapped_callable = wrapped_callable
        self.parent_class = parent_class
        self._module_name = wrapped_callable.__module__
        if self.parent_class:
            self._class_name = self.parent_class._class_name
            self._class_args = self.parent_class._class_args
            self._class_kwargs = self.parent_class._class_kwargs
        else:
            self._class_name = ""
            self._class_args = []
            self._class_kwargs = []
        self._callable_name = self.wrapped_callable.__name__
        self._callable_is_stochastic = is_stochastic

    def __call__(self, *args, **kwargs):
        
        # run callable
        result = self.wrapped_callable(*args, **kwargs)
                
        # track callable args + kwargs
        args, kwargs = clean_args_and_kwargs(self.wrapped_callable, args, kwargs)
        self._callable_args = args
        self._callable_kwargs = kwargs
        
        return result


def clean_args_and_kwargs(_callable, args, kwargs):
    args = list(args)
    num_pops = 0
    for i, p in enumerate(inspect.signature(_callable).parameters):
        if p in ['batch', 'text', 'input', 'target', 'label', 'X', 'y']:
            args.pop(i-num_pops)
            kwargs.pop('batch', None)
            num_pops += 1

    return args if args else [], kwargs if kwargs else []
import itertools
import functools

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


def mark_transformation_method(transform_method=None, *, stochastic=False):
    def _decorate(trans_func):
        @functools.wraps(trans_func)
        def wrapped_function(*args, **kwargs):
            if len(args) > 0 and hasattr(args[0], trans_func.__name__):
                original_transform_obj = args[0]
                transform_args =  args[2:] if args[2:] else [] # 0 = self, 1 = batch inputs
            else:
                original_transform_obj = trans_func
                if hasattr(original_transform_obj, '__self__'):
                    original_transform_obj = original_transform_obj.__self__
                transform_args = args[2:] if args[2:] else [] # 0 = self, 1 = batch inputs
            if getattr(original_transform_obj, trans_func.__name__, None):
                original_transform_obj._transform_args = transform_args
                original_transform_obj._transform_fn_name = trans_func.__name__
                original_transform_obj._transform_kwargs = kwargs if kwargs else []
                original_transform_obj._transform_is_stochastic = stochastic  
            return trans_func(*args, **kwargs)
        return wrapped_function
    if transform_method:
        return _decorate(transform_method)
    return _decorate
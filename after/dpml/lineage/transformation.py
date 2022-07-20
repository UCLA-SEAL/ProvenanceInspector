import itertools
import functools

'''
decorator to record initalization arguments of transformation class and transformation method
'''

def mark_transformation_class(original_transform_class):

    orig_init = original_transform_class.__init__

    def __init__(self, *args, **kws):
        self._init_args = args
        self._init_kwargs = kws

        orig_init(self, *args, **kws) # Call the original __init__


    original_transform_class.__init__ = __init__ # Set the class' __init__ to the new one

    return original_transform_class

def mark_transformation_method(transform_method=None, *, stochastic=False):
    '''
    original_transform_obj = transform_method
    if hasattr(transform_method, '__self__'):
        original_transform_obj = original_transform_obj.__self__
    '''

    def _decorate(trans_func):

        @functools.wraps(trans_func)
        def wrapped_function(*args, **kwargs):

            if getattr(args[0], trans_func.__name__, None):
                original_transform_obj = args[0]

                original_transform_obj._transform_func = trans_func.__name__
                original_transform_obj._transform_args = args[1:]
                original_transform_obj._transform_kwargs = kwargs
                original_transform_obj._last_transform_stochastic = stochastic
                
            return trans_func(*args, **kwargs)

        return wrapped_function

    if transform_method:
        return _decorate(transform_method)

    return _decorate
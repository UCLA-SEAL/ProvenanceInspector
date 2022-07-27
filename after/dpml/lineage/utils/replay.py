import inspect

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

def dynamic_import(module_name, class_name):
    
    module_path = module_name.split('.')
    
    #__import__ method used
    # to fetch module
    module = __import__(module_path[0])
    
    for cur_module in module_path[1:]:
        module = getattr(module, cur_module, None)
        
    my_class = None
    if module:
        # getting attribute by
        # getattr() method
        my_class = getattr(module, class_name)

    return my_class

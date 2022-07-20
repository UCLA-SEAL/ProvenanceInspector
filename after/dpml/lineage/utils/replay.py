def full_module_name(o):
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__
    return module, o.__class__.__name__

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
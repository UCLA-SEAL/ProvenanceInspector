ARGS_SPLIT_TOKEN = "^"

def get_class_attributes(cls):
    attributes = set()
    for attribute in cls.__dict__.keys():
        if attribute[:2] != '__':
            value = getattr(cls, attribute)
            if not callable(value):
                #print(attribute, '=', value)
                attributes.add(attribute)
    return attributes
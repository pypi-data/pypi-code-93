def get_class_variables_values(class_obj):
    """Gets a list of values for every class variable"""
    class_variable_keys = [i for i in class_obj.__dict__.keys() if i[:1] != '_']
    return [class_obj.__dict__.get(key) for key in class_variable_keys]


def get_class_variables_dict(class_obj):
    """returns a dict containing class variables and values. __ methods and variables
    are excluded """
    return dict((key, value) for (key, value) in class_obj.__dict__.items() if key[:1] != '_')

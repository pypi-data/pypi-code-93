__version__ = '0.1.0'


# Get value from dotpath string
def getpath(obj: object, dotpath: str, default=None, **kwargs):
    raise_exception = kwargs.get('raise_exception', False)
    try:
        indexes = dotpath.split('.')
        index = indexes[0]
        
        # Cast list, set and tuple to dict, need to get the value from index
        if type(obj) in (list, set, tuple):
            obj = { str(i): v for i,v in tuple(enumerate(obj))}
        
        if isinstance(obj, dict):
            if len(indexes) > 1:
                return getpath(obj[index], '.'.join(indexes[1:]), default, **kwargs)
            return obj[index]
        
        # Get value when the obj is a dict, tuple, list or set
        if type(obj) in (dict, tuple):
            if len(indexes) > 1:
                return getpath(obj[index], '.'.join(indexes[1:]), default, **kwargs)
            return getattr(obj, index)
    
        # Get value when the obj is an other object
        if isinstance(obj, object):
            if len(indexes) > 1:
                return getpath(getattr(obj,index), '.'.join(indexes[1:]), default, **kwargs)
            return getattr(obj,index)
    except (AttributeError, KeyError, IndexError) as err:
        if raise_exception:
            raise err
        return default
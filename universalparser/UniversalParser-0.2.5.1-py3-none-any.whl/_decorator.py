from functools import wraps
from ._exception import *

def limit_one(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        result = func(*args, **kwargs)
        if True == kwargs.get('one_'):
            if 1 == len(result):
                return result[0]
            elif 0 == len(result):
                raise NotNodeFound('No match node.')
            else:
                raise MoreNodesFound('More nodes found.')
        else:
            return result
    return decorator

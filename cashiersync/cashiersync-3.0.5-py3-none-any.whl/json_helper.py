'''
'''
from typing import List

def obj_to_dict(obj):
    dic = {}
    dic.update(vars(obj))
    return dic

def object_list_to_dicts(objects: List) -> List[str]:
    ''' Convert a list of objects to a list of dictionaries '''
    result = []

    for obj in objects:
        dic = obj_to_dict(obj)
        result.append(dic)

    return result

ID_CLASS_MAP = {}


def bind_id(object_id, *args, **kwargs):
    def wrapper(class_ref, *args, **kwargs):
        if object_id not in ID_CLASS_MAP:
            ID_CLASS_MAP[object_id] = []
        ID_CLASS_MAP[object_id].append(class_ref)
    return wrapper

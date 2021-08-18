def chunkify(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_random_id():
    """Generate a random id

    :return: a unique UUID4 formatted string
    """
    import uuid
    return str(uuid.uuid4())


def generate_hash_id(data):
    import json
    import uuid
    import hashlib
    hash_id = uuid.UUID(
        hashlib.md5(
            str(json.dumps(data, sort_keys=True)).encode('utf-8')
        ).hexdigest()
    )
    return str(hash_id)


def get_subpackage_paths():
    import stratus_api
    import pkgutil
    import os
    for finder, modname, ispkg in pkgutil.iter_modules(stratus_api.__path__):
        subpackage_path = os.path.join(finder.path, modname)
        yield subpackage_path


def format_api_object(obj):
    if obj.get('created'):
        obj['created'] = int(obj['created'].timestamp())
    if obj.get('updated'):
        obj['updated'] = int(obj['updated'].timestamp())
    return obj


import os
from .logger import Logger
from .exceptions import DSOException

def clean_directory(path):
    for path in Path(path).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)




def is_binary_file(filename):
    """ 
    Return true if the given filename appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    with open(filename, 'rb') as f:
        for block in f:
            if b'\0' in block:
                return True
    return False


def exists_on_path(filename):
    return any([os.path.exists(os.path.join(p, filename)) for p in os.environ.get('PATH', '').split(os.pathsep)])


def render_stream(stream, values):
    if not values: return stream
    import jinja2
    template = jinja2.Environment(undefined=jinja2.StrictUndefined).from_string(stream)
    try:
        rendered = template.render(values)
    except Exception as e:
        Logger.error(f"Failed to render stream.")
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        raise DSOException(msg)

    return rendered


def __get_mode_from_file_name(file_name):
    from os.path import splitext
    ext = splitext(file_name)[1]
    if ext in ['.yml', '.yaml']:
        return 'yaml'
    elif ext in ['.json', '.csv']:
        return ext[1:]
    else:
        return 'raw'


def load_file(file_path, mode='auto', pre_render_values=None):
    if is_binary_file(file_path):
        raise DSOException(f"Cannot load binary file '{file_path}'.")
    
    if mode == 'auto':
        mode = __get_mode_from_file_name(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if mode == 'raw':
            return render_stream(f.read(), pre_render_values)
        elif mode == 'yaml':
            import yaml
            return yaml.safe_load(render_stream(f.read(), pre_render_values)) or {}
        elif mode == 'json':
            import json
            return json.load(render_stream(f.read(), pre_render_values)) or {}
        elif mode == 'csv':
            import csv
            return list(csv.reader(render_stream(f.read(), pre_render_values))) or []
        else:
            raise NotImplementedError



def save_data(data, file_path, mode='auto'):
    if mode == 'auto':
        mode = __get_mode_from_file_name(file_path)

    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        if mode == 'yaml':
            import yaml
            yaml.dump(data, f, sort_keys=False, indent=2)
        elif mode == 'json':
            import json
            json.dump(data, f, sort_keys=False, indent=2)
        else:
            raise NotImplementedError



import os
from os import path
from hyperc.settings import TEMPDIR
import hyperc.settings
import random, string
import time
import types
import hashlib, pickle
from typing import Any

_counter = None
_poodle_id = None
_id_map = dict()
_registry = dict()


def letter_index_next(letter=''):
    """
        Generate next alphabet index
    """
    if len(letter) == 0:
        return 'A'
    char_index = letter.upper()
    if char_index[-1] != 'Z':
        next_char = string.ascii_uppercase[string.ascii_uppercase.find(char_index[-1])+1]
        return char_index[:-1] + next_char
    else:
        return letter_index_next(letter[:-1]) + 'A'


#set flag in function to skip it while compilation
def side_effect_decorator(func):
    func.__side_effect__ = True
    return func
    
def get_registry():
    return _registry

def get_work_dir():
    if hyperc.settings.BROWSER_MODE: 
        return "/"
    curr_tmp_dir = path.join(TEMPDIR, str(int(time.time())) + hyperc.settings.APPENDIX + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)))
    if not os.path.exists(curr_tmp_dir):
        os.makedirs(curr_tmp_dir)
    _work_dir = curr_tmp_dir
    return curr_tmp_dir


def function_hash(f: types.FunctionType):
    h = hashlib.md5()
    h.update(pickle.dumps([f.__code__.co_code, sorted([str(c) for c in f.__code__.co_consts if type(c).__name__ != 'code']),
                            sorted(f.__code__.co_names), sorted(f.__code__.co_varnames),
                            f.__code__.co_kwonlyargcount, f.__code__.co_argcount,
                            f.__qualname__, f.__module__]))
                            
    # use h.digest() to perform serialisation
    return h.hexdigest()
    # return h.digest()

def custom_hash(obj):
    h = hashlib.md5()
    h.update(pickle.dumps(obj.__name__))
    if type(obj).__name__ == "module":
        pass
        # for i in sorted([item for item in dir(obj) if not item.startswith("__")]):
        #     h.update(pickle.dumps(i))
    else:
        h.update(pickle.dumps(obj.__qualname__))
    return h.digest()

def get_object_by_custom_hash(hash, all_classes=None):
    for c in all_classes:
        # print("from all_classes" ,c)
        try:
            if hasattr(c, "_self_wrapped"):
                c = c._self_wrapped
            if hash == custom_hash(c):
                return c
        except:
            continue
    return None


def get_class(kls, all_classes=None):
    if all_classes is None:
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    else:
        for c in all_classes:
            # print("from all_classes" ,c)
            if hasattr(c, '__qualname__') and hasattr(c, '__module__'):
                if kls == f'{c.__module__}.{c.__qualname__}':
                    return c
    return None

#get class by __qualname__ from shadow
def get_class_by_qualname(all_classes, qualname, module):
    # print("look for qualname", qualname)
    for c in all_classes:
        try:
            # print(str(c._self_class.__module__),".",str(c._self_class.__qualname__), " == ", module, ".", qualname)
            if (c._self_class.__qualname__ == qualname) and (c._self_class.__module__ == module):
                return c
        except:
            continue
    return None


def get_class_by_str(all_classes, name):
    # print("look for by name", name)
    for c in all_classes:
        try:
            # print(str(c), " == ", name)
            if str(c) == name:
                # print("ok")
                return c
        except:
            continue
    return None


def fullname(o):
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + o.__class__.__name__

def reset_state():
    global _poodle_id
    global _id_map
    global _registry
    global _counter
    _poodle_id = None
    _id_map = dict()
    _registry = dict()
    _counter = None


def poodle_id(python_id):
    global _poodle_id
    global _id_map

    if not _poodle_id:
        _poodle_id = 0
    if python_id in _id_map:
        return _id_map[python_id]
    _poodle_id += 1
    _id_map[python_id] = _poodle_id
    return _poodle_id


def register(ob):
    global _registry
    if ob._self_id in _registry:
        assert _registry[ob._self_id] == ob
        return
    _registry[ob._self_id] = ob

def mkcell(value):
    f = (lambda x: lambda: x)(value)
    return f.__closure__[0]


def stable_int_hash(s):
    return int(hashlib.sha1(s.encode("UTF-8")).hexdigest(), 16) % (10 ** 8)


def stable_int_hash15(s):
    return int(hashlib.sha1(s.encode("UTF-8")).hexdigest(), 16) % (10 ** 15)


def py_class_id(cls_):
    return stable_int_hash15(cls_.__qualname__)


def check_user_disable_execution(solver_lock):
    if solver_lock is not None:
        if not solver_lock.locked():
            time.sleep(1)
            import hyperc.exceptions
            raise hyperc.exceptions.UserInterrupt("user disable execution#")
    return

def h_id(obj):
    # if hasattr(obj, "__qualname__"):
    try:
        return stable_int_hash15(obj.__qualname__)
    except:
        return id(obj)


def class_id(class_):
    return f"{class_.__name__}-{py_class_id(class_)}"


def to_type(v, type_):
    if type_ == bool:
        if str(v).lower() == "true":
            attr_val = True
        elif str(v).lower() == "false":
            attr_val = False
        else:
            raise ValueError(f"Cant't convert `{repr(v)}` to `{type_}`")
    elif type_ == int:
        attr_val = int(v)
    elif type_ == str:
        attr_val = str(v)
    else:
        raise ValueError(f"Cant't convert `{repr(v)}` to `{type_}`")
    return attr_val


# https://stackoverflow.com/a/136368
def tail(f, lines=20):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


def hcp_append_if_not(arr, obj):
    "Append obj to arr if arr does not contain object with same _self_id()"
    found = False
    for ob in arr:
        if ob._self_id() == obj._self_id():
            return False
    arr.append(obj)
    return True

class ReadonlyLocals(types.ModuleType):
    __locals_dict: dict
    def __init__(self, locals_dict) -> None:
        locals_dict["__class__"] = types.ModuleType
        super(ReadonlyLocals, self).__setattr__('__locals_dict ', locals_dict) 
    def __setattr__(self, name: str, value: Any) -> None:
        raise NotImplementedError("Setattr is not supported on readonly local mock")
    def __getattribute__(self, name: str) -> Any:
        locals_dict = super(ReadonlyLocals, self).__getattribute__('__locals_dict ') 
        if not name in locals_dict:
            raise AttributeError(f"'locals proxy' has no attribute '{name}'")
        return locals_dict[name]
import importlib
import pkgutil
from typing import List


def submodules(entity: str) -> List[str]:
    submodules = [entity]
    discovered = []
    while submodules:
        entity = submodules.pop()
        try:
            imported = importlib.import_module(entity)
        except:
            # print(traceback.print_exc())
            # print('Cannot import module {}'.format(entity))
            continue
        discovered.append(entity)
        if hasattr(imported, "__path__"):
            try:
                for _, name, is_pkg in pkgutil.walk_packages(imported.__path__):
                    full_name = imported.__name__ + "." + name
                    submodules.append(full_name)
            except:
                pass
                # print('Error walking {}'.format(imported.__path__))
    return discovered


def get_classes(module_name, prefix="", human_submodule_func=lambda x: x):
    tasks = {}
    print(module_name)
    for submodule in submodules(module_name):
        imported = importlib.import_module(submodule)
        for obj in dir(imported):
            try:
                cls = getattr(imported, obj)
                tasks[prefix + cls.__name__] = {
                    "name": cls.__name__,
                    "prefix": prefix,
                    "cls": cls,
                    "submodule": submodule,
                    "human_submodule": human_submodule_func(submodule),
                }
            except Exception as e:
                print("not imported", obj, e)
    return tasks


def import_class(module, class_name):
    imported = importlib.import_module(module)
    return getattr(imported, class_name)

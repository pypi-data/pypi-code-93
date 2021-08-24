"""This module contains the function :func:`.load_funcs` to load a
mosaik environment.

This comprises to instantiate a world object und retrieve sensor and
actuator descriptions

"""
from importlib import import_module


def load_funcs(params):
    """Load the description functions.

    Expects a dictionary containing the keys *"module"*,
    *"description_func"*, and "instance_func". *"module"* can
    either be a python module or a python class. The path segments
    for modules are separated by a dot "." and a class is separated
    by a colon ":", e.g., if *descriptor* is a module::

        {
            "module": "midas.adapter.harlequin.descriptor",
            "description_func": "describe",
            "instance_func": "get_world",
        }

    or, if *Descriptor* is a class::

        {
            "module": "midas.adapter.harlequin:Descriptor",
            "description_func": "describe",
            "instance_func": "get_world",
        }


    Parameters
    ----------
    params : dict
        A *dict* containing the keys as described above.

    Returns
    -------
    tuple
        A *tuple* of the description function and the instance
        function.

    """

    if ":" in params["module"]:
        module, clazz = params["module"].split(":")
        module = import_module(module)
        obj = getattr(module, clazz)()
    else:
        obj = import_module(params["module"])

    dscr_func = getattr(obj, params["description_func"])
    inst_func = getattr(obj, params["instance_func"])

    return dscr_func, inst_func

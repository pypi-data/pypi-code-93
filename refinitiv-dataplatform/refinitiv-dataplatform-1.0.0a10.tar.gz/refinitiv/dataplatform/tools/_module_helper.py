# coding: utf-8

"""
Function to mask specific reference name from module name.
"""


def delete_reference_from_module(module_name, reference_name):
    """
    Remove reference_name from module_name to hide it for autocompletion
    :param module_name:
    :param reference_name:
    :return:
    """
    import sys

    try:
        current_module = sys.modules[module_name]
        del current_module.__dict__[reference_name]
    except Exception:
        pass

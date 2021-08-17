# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions used for code generation."""
from typing import Any, Dict, List, Tuple, Type

import ast
import sys
from contextlib import contextmanager

from azureml.automl.core.shared._diagnostics.contract import Contract


def check_code_syntax(code: str) -> None:
    Contract.assert_non_empty(
        code,
        "The provided code was empty.",
        log_safe=True
    )
    node = ast.parse(code, 'script.py', mode='exec')
    Contract.assert_non_empty(
        node,
        "The provided code was empty.",
        log_safe=True
    )


def indent_multiline_string(input_str: str, indent: int = 4) -> str:
    """
    Indent a multiline string to be used as a parameter value, except for the first line.

    :param input_str: The string to indent
    :return: The string with every line after the first being indented
    """
    lines = input_str.split("\n")
    if len(lines) == 1:
        return input_str

    new_lines = [lines[0]]
    for line in lines[1:]:
        new_lines.append(" " * indent + line)

    return "\n".join(new_lines)


def generate_repr_str(cls: "Type[Any]", params: Dict[str, Any], **kwargs: Any) -> str:
    """
    Generate an evaluatable string representation of this object.

    :param cls: The class of the object
    :param params: The parameters of the object (repr will be called on each value)
    :param kwargs: The parameters of the object (the value will be added as provided)
    :return: A string representation which can be executed to retrieve the same object
    """
    if len(params) == 0 and len(kwargs) == 0:
        return "{}()".format(cls.__name__)

    param_line = "    {}={}"

    assert set(kwargs.keys()).isdisjoint(set(params.keys()))

    init_params = [
        param_line.format(k, kwargs[k]) for k in kwargs
    ] + [
        param_line.format(k, _override_repr(params[k], k)) for k in params
    ]

    init_params = [indent_multiline_string(line) for line in init_params]

    lines = [
        "{}(\n".format(cls.__name__),
        ",\n".join(init_params),
        "\n)"
    ]
    return "".join(lines)


def get_import(obj: Any) -> Tuple[str, str, Any]:
    """
    Get the information needed to import the class.

    :param obj: The object to get import information for
    :return: the module name, the class name, and the class object
    """
    # The provided object is already a callable
    if callable(obj):
        return obj.__module__, obj.__name__, obj

    # azureml.automl.runtime.shared.model_wrappers
    # LightGBMClassifier
    # LightGBMClassifier obj
    return obj.__class__.__module__, obj.__class__.__name__, obj.__class__


def get_recursive_imports(obj: Any) -> List[Tuple[str, str, Any]]:
    """
    Get the information needed to import all classes required by this object.

    The object's params are traversed as a directed acyclic graph using depth-first search.
    Cycles will result in a stack overflow.

    This will not catch imports that are present in iterables which are not lists/sets/dicts.

    :param obj: The object to get import information for
    :return: a list containing module names, class names, and class objects
    """
    imports = set()
    if isinstance(obj, (list, set)):
        for item in obj:
            imports.update(get_recursive_imports(item))
    elif isinstance(obj, dict):
        for key in obj:
            imports.add(get_import(key))
            val = obj[key]
            imports.update(get_recursive_imports(val))
    else:
        if not is_builtin_type(obj):
            imports.add(get_import(obj))
    return list(imports)


def is_builtin_type(obj: Any) -> bool:
    """
    Determine whether the given object is a built-in type (ints, bools, lists, dicts, etc).

    :param obj: The object to check
    :return: True if the object is a built-in type, False otherwise
    """
    module_name = obj.__class__.__module__
    return module_name in {"builtins", "__builtins__"}


def generate_import_statements(imports: List[Tuple[str, str, Any]]) -> List[str]:
    deduplicate_set = set()
    output = []
    for x in imports:
        statement = "from {} import {}".format(x[0], x[1])
        if statement in deduplicate_set:
            continue
        output.append(statement)
        deduplicate_set.add(statement)
    return output


def _sklearn_repr(self: Any, N_CHAR_MAX: int = sys.maxsize) -> str:
    return generate_repr_str(self.__class__, self.get_params(deep=False))


def _override_repr(obj: Any, key_name: str) -> str:
    """
    Generate an evaluatable string representation of this object, overriding __repr__() for sklearn BaseEstimators.

    :param obj: The object to generate a string for
    :param key_name: The parameter name for which this object is for
    :return: A string representation of the object
    """
    with use_custom_repr():
        if obj.__class__.__name__ == "ndarray":
            # This object uses numpy ndarray, so just make sure indentation is correct.
            # Note that ndarrays are represented using numpy.array() in repr, so that must be imported instead.
            return indent_multiline_string(repr(obj), len(key_name) + 1)

        repr_str = repr(obj)

        # This is a bit of a temporary hack to handle numpy dtype objects.
        # We can't monkeypatch dtype objects because they use native code + __slots__, which makes them unpatchable
        # TODO: interface to handle custom code generation behavior for non-AutoML objects
        if key_name == 'dtype' and repr_str.startswith('<'):
            repr_str = "{}.{}".format(obj.__module__, obj.__name__)
        # Another hack to convert DataTransformer._wrap_in_lst to a lambda
        # One generic way to do this is to pickle the function and dump the string, but that's not acceptable here
        # Second way to handle this is to use inspect.getsource(), but then we would need to define another function
        # in the generated code and code gen doesn't currently have a signaling mechanism to allow for this.
        # Third way is to reference it directly, but this is a private function so we don't want to expose it.
        elif key_name == "tokenizer" and "._wrap_in_lst" in repr_str:
            repr_str = "lambda x: [x]"
        # Handle timeseries param dict.
        # Anything of type pd.DateOffset needs to call freqstr.
        elif isinstance(obj, dict):
            obj = obj.copy()
            for key in obj:
                if hasattr(obj[key], "freqstr"):
                    obj[key] = obj[key].freqstr
            repr_str = repr(obj)

        return repr_str


@contextmanager
def use_custom_repr():
    from sklearn.base import BaseEstimator
    old_repr = BaseEstimator.__repr__
    BaseEstimator.__repr__ = _sklearn_repr
    try:
        yield
    finally:
        BaseEstimator.__repr__ = old_repr

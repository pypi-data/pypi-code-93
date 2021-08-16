"""
Module with miscellaneous functions. For example myproperty, which is decarator for creating
simplified properties or json_to_py that can convert json string to correct python types or
str_to_infer_type that will convert string to correct type.
"""
import builtins

import mylogging


_JUPYTER = 1 if hasattr(builtins, "__IPYTHON__") else 0


def validate(value, types, options, name=None):
    """Validate type of variable and check if this variable is in defined options.

    Args:
        value (Any): Value that will be validated.
        types (type): For example int, str or list.
        options (list): List of possible options. If value is not in options, error will be raised.
        name (str, optional): If error raised, name will be printed. Defaults to None.

    Raises:
        TypeError: Type does not fit.
        KeyError: Value not in defined options.
    """
    if types:

        # To be able to use None in types instead of type(None)
        if isinstance(types, (list, tuple)) and None in types:
            types = list(types)

            for i, j in enumerate(types):
                if j is None:
                    types[i] = type(None)

        if isinstance(types, list):
            types = tuple(types)

        if not isinstance(value, types):
            raise TypeError(
                mylogging.return_str(
                    f"Allowed types for variable < {name} > are {types}, but you try to set an {type(value)}"
                )
            )

    if options and value not in options:
        raise KeyError(
            mylogging.return_str(
                f"New value < {value} > for variable < {name} > is not in allowed options {options}."
            )
        )


def str_to_infer_type(string_var):
    import ast

    evaluated = string_var
    try:
        evaluated = ast.literal_eval(evaluated)
    except Exception:
        pass
    return evaluated


def json_to_py(json, replace_comma_decimal=True, convert_decimal=False):
    """Take json and eval it from strings.
    If string to string, if float to float, if object then to dict.

    When to use? - If sending object as parameter in function.

    Args:
        json (dict): JSON with various formats as string.
        replace_comma_decimal (bool): Some countries use comma as decimal separator (e.g. 12,3).
            If True, comma replaced with dot (if not converted to number string remain untouched)
        convert_decimal (bool): Some countries has ',' decimal, then conversion would fail.
            If True, convert ',' to '.' in strings. Only if there are no brackets (list, dict...).
            For example '2,6' convert to 2.6.

    Returns:
        dict: Python dictionary with correct types.
    """

    import ast

    evaluated = json.copy()

    for i, j in json.items():

        if replace_comma_decimal and isinstance(j, str) and "(" not in j and "[" not in j and "{" not in j:
            j = j.replace(",", ".")

        try:
            evaluated[i] = ast.literal_eval(j)
        except Exception:
            pass

    return evaluated

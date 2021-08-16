import os
import re


def shellexpand(item, variables):
    item_type = type(item)
    if item_type == dict:
        return resolve(item, variables)
    else:
        return _shellexpand(item, variables)


def resolve(unknown, known):
    def inner_recursion(variable, dependency_chain=None):
        # shortcircuit if already resolved
        if variable in resolved:
            return

        if variable not in unknown:
            # shortcircuit if already defined in "known" object
            if variable in known:
                return
            else:
                raise Exception(
                    "Variable is not defined in either known or unknown stacks.",
                    variable,
                )

        dependency_chain.append(variable)
        value = unknown[variable]
        dependencies = shellexpand_dependencies(value)
        self_dependent = variable in dependencies
        if self_dependent:
            # ignore self-dependency until end
            dependencies.remove(variable)
        for dep in dependencies:
            if dep in dependency_chain:
                raise Exception(
                    "Circular reference detected: %s -> %s" % (dependency_chain, dep)
                )
            else:
                inner_recursion(dep, dependency_chain)

        resolved[variable] = _shellexpand(value, {**known, **resolved})
        dependency_chain.remove(variable)

    resolved = {}
    for k in unknown.keys():
        inner_recursion(k, [])
    return resolved


def shellexpand_dependencies(item):
    item_type = type(item)
    if item_type == str:
        return dep_string(item)
    elif item_type == dict:
        return dep_dict(item)
    elif item_type == list:
        return dep_list(item)
    else:
        return []


def dep_string(input_str: str):
    # short-circuit if is a single variable
    if input_str == "~":
        return {"HOME"}
    elif input_str.startswith("~/"):
        deps = {"HOME"}
        pos = 2
    else:
        deps = set()
        pos = 0

    matchobj = SHELL_VARIABLES_DEPENDENCY_PATTERN.search(input_str, pos)
    while matchobj:
        variable_name = matchobj[1] or matchobj[2]
        if variable_name:
            deps.add(variable_name)
        pos = matchobj.end()
        matchobj = SHELL_VARIABLES_DEPENDENCY_PATTERN.search(input_str, pos)
    return deps


def dep_dict(obj):
    return {dep for item in obj.values() for dep in shellexpand_dependencies(item)}


def dep_list(array):
    return {dep for item in array for dep in shellexpand_dependencies(item)}


def _shellexpand(item, variables):
    item_type = type(item)
    if item_type == str:
        return expand_string(item, variables)
    elif item_type == dict:
        return expand_dict(item, variables)
    elif item_type == list:
        return expand_list(item, variables)
    else:
        return item


class VariableNotSet(Exception):
    def __init__(self, not_set, variables):
        super().__init__(
            f'Variable "{not_set}" has not been set.',
            f"Here is dump of the variables that exist as of this point.",
            variables,
        )


SHELL_VARIABLES_DEPENDENCY_PATTERN = re.compile(
    r"\$\$?([a-zA-Z0-9_]+)|\$\$?\{([a-zA-Z0-9_]+)(?:\:([^}]*))?\}|\$\$"
)

SHELL_VARIABLES_PATTERN = re.compile(
    r"(\$\$)|\$([a-zA-Z0-9_]+)|\$\{([a-zA-Z0-9_]+)(?:\:([^}]*))?\}"
)


def expand_string(input_str: str, variables):
    # replace ~ with $HOME
    if input_str[0] == "~" and (len(input_str) == 1 or input_str[1] == "/"):
        input_str = input_str.replace("~", "${HOME}", 1)

    # if HOME not overwritten, then use system version of HOME
    if "HOME" not in variables:
        variables = {**variables, "HOME": os.path.expanduser("~")}

    # short-circuit if is a single variable
    result = SHELL_VARIABLES_PATTERN.match(input_str)
    if result and result.end() == len(input_str):
        variable_name = result[2] or result[3]
        if variable_name in variables:
            # notice lack of string-cohercion
            # this allows non-str variables with their native type
            return variables[variable_name]

    def replacements(matchobj):
        if matchobj[1]:
            return "$"
        variable_name = matchobj[2] or matchobj[3]
        default_value = matchobj[4]

        if variable_name in variables:
            # string cohercion of value, otherwise
            # re.sub throws error
            return str(variables[variable_name])
        elif default_value:
            return default_value
        else:
            raise VariableNotSet(variable_name, variables)

    return SHELL_VARIABLES_PATTERN.sub(replacements, input_str)


def expand_dict(obj, variables):
    return {k: _shellexpand(v, variables) for k, v in obj.items()}


def expand_list(array, variables):
    return [_shellexpand(v, variables) for v in array]

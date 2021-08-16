from collections import Counter


class ParameterStore:
    """
    Store parameters for a given query.
    Determine the parameter name depending on a parameter counter
    """

    def __init__(self):
        self._counter = Counter()
        self.params = {}

    def _get_params_name(self, key):
        """NB: the counter parameter is there in purpose, will be modified in the function
        to remember the count of each parameter

        :param p:
        :param counter:
        :return:
        """
        key = key.replace(".", "_")
        param_name = f"{key}_{self._counter[key]}"
        self._counter[key] += 1
        return param_name

    def add(self, key, value):
        param_name = self._get_params_name(key)
        self.params[param_name] = value
        return param_name


# WIP: cypher context to manage "WITH" clause
class CypherContext:
    def __init__(self, init_variables=None):
        self._variables = set(init_variables) if init_variables else set()

    def add(self, var):
        self._variables.add(var)

    def __contains__(self, item):
        return item in self._variables

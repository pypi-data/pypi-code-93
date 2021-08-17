class FunctionCalls(object):
    """Collection of function calls"""

    def __init__(self):
        self._name = ""
        self._function_calls = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def function_calls(self):
        return self._function_calls

    def add_function_call(self, function_call):
        """Adds a function call to the collection.

            Args:
                function_call (FunctionCall): object to append
        """
        self._function_calls.append(function_call)

    def remove_function_call(self, function_call):
        """Removes a function call from the collection.

            Args:
                function_call (FunctionCall): object to remove
        """
        self._function_calls = [f for f in self._function_calls if f != function_call]

    def _to_list(self):
        fcalls = []
        for item in self.function_calls:
            fcalls.append(item._to_dict())
        return fcalls

        # fcalls['name'] = self.name
        # fcalls['type'] = 'transform'
        # query_dict['outputs'] = [self.outputs]

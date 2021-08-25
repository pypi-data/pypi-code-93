# event binding
class __systemevent__:
    def initialize(self, Function: function):
        self.__js__.initialize = Function

    def update(self, Function: function):
        self.__js__.js_update = Function

    def shutdown(self, Function: function):
        self.__js__.shutdown = Function

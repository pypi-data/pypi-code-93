class slashcommand:
    def executeCommand(self, Command: str, Callback: function):
        self.__js__.executeCommand(Command, Callback)

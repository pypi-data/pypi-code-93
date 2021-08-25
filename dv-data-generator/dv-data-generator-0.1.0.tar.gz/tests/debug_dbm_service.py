class DebugDbmService:
    def __init__(self, response, exception=False):
        self._response = response
        self._exception = exception

    def queries(self):
        return self

    def getquery(self, *args, **kwargs):
        return self

    def execute(self):
        if self._exception:
            raise Exception("Something went wrong")
        return self._response
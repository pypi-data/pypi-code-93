class SqlReturnObj():
    def __init__(self,
                 data=None,
                 return_type=None,
                 callback=None,
                 error=None,
                 timer=None):
        self.data = data
        self.return_type = return_type
        self.callback = callback
        self.error = error
        self.timer = timer
        self.n_rows = len(self.data) if self.data is not None else 0


    def as_dict(self):
        return {"data": self.data,
                "return_type": self.return_type,
                "callback": self.callback,
                "error": self.error,
                "timer": self.timer,
                "n_rows": self.n_rows}

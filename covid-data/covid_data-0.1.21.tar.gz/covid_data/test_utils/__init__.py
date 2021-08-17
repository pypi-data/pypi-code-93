class MockDB(object):
    execute_return: list[dict] = []

    def cursor(self, *args, **kwargs):
        return self

    def execute(self, *args, **kwargs):
        return self

    def fetchone(self, *args, **kwargs):
        return self.execute_return[0] if len(self.execute_return) else None

    def fetchall(self, *args, **kwargs):
        return self.execute_return

    def commit(self, *args, **kwargs):
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

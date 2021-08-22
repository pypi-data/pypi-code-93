from ignite.engine import Engine


class LazyEngine(Engine):
    def __init__(self):
        super().__init__(self._dummy_process_function)

    def _dummy_process_function(self, engine, batch):
        pass

    def run(self, *args, **kwargs):
        super_run = super().run

        def decorator(func):
            self._process_function = func
            return super_run(*args, **kwargs)

        return decorator

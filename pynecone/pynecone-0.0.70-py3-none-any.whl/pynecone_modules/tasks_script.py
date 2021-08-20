from pynecone import TaskProvider


class Module(TaskProvider):

    def __init__(self, **kwargs):
        self.cfg = kwargs

    def run(self, *args, **kwargs):
        locals = {}
        globals = {}
        exec(self.cfg['script'], globals, locals)
        func = self.cfg['func']
        return locals[func](args, kwargs)
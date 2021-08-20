import importlib.util
from .cmd import Cmd


class TaskCmd(Cmd):

    def __init__(self):
        super().__init__("task")

    def get_help(self):
        return 'run a program'

    def add_arguments(self, parser):
        parser.add_argument('--path', help="path to the python script to be executed")
        parser.add_argument('--func', help="python expression to be evaluated")
        parser.add_argument('--method', help="name of the function in the script to be executed")
        parser.add_argument('--names', help="names of function arguments in order of apearance", nargs='+')
        parser.add_argument('--args', help="values of function arguments in order of apearance", nargs='+')

    def run(self, args):
        if args.func:
            if args.names and args.args and len(args.names) == len(args.args):
                eval(args.func)(**dict(zip(args.names, args.args)))
            else:
                eval(args.func)
        elif args.path:
            self.load_script(args.path, args.method)(**dict(zip(args.names, args.args)))
        else:
            import code
            d = dict()
            if args.names and args.args and len(args.names) == len(args.args):
                d = dict(zip(args.names, args.args))
            code.interact(banner='PyNeCoNe', local=d)

    def schedule(self):
        pass

    @classmethod
    def get_handler(cls, file, callback):
        spec = importlib.util.spec_from_file_location('testmod', file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def handler():
            getattr(module, callback)

        return handler

    @classmethod
    def load_script(cls, script_path, func_name):
        return cls.get_handler(script_path, func_name)

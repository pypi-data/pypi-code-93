from pynecone import Cmd


class Repl(Cmd):

        def __init__(self):
            super().__init__('repl')

        def add_arguments(self, parser):
            pass

        def run(self, args):
            self.repl()

        def get_help(self):
            return 'pynecone read-eval-print-loop'
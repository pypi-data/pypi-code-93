from .proto import ProtoCmd
import os


class Test(ProtoCmd):

        def __init__(self):
            super().__init__('test', 'run tests')

        def run(self, args):
            return os.system('python -m unittest')
            #TODO : cyclic dependency/wrong module load folder
            # loader = unittest.TestLoader()
            # tests = loader.discover('.')
            # test_runner = unittest.runner.TextTestRunner()
            # test_runner.run(tests)

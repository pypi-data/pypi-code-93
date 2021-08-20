from tst_fixtures.sample2 import SampleClass2


class SampleClass(object):
    def __init__(self):
        pass

    def sample_method(self):
        sample = SampleClass2()
        sample.sample_method_2()

    def exception_method(self):
        raise Exception("Some exception")

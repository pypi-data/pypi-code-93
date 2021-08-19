import os
import pytest

def run():
    tests_path = os.path.dirname(os.path.realpath(__file__))
    pytest.main()


run()



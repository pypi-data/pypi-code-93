import logging

import convo
from convo.nlu.train import training
from convo.nlu.test import run_eval as test
from convo.nlu.test import cross_validation

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = convo.__version__

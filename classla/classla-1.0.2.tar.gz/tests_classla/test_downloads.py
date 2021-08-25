import classla
from tests_classla import *

def test_all_downloads():
    classla.download('sl', dir=TEST_MODELS_DIR)
    classla.download('sl', type='standard_jos', dir=TEST_MODELS_DIR)
    classla.download('sl', type='nonstandard', dir=TEST_MODELS_DIR)
    classla.download('hr', dir=TEST_MODELS_DIR)
    classla.download('hr', type='nonstandard', dir=TEST_MODELS_DIR)
    classla.download('sr', dir=TEST_MODELS_DIR)
    classla.download('sr', type='nonstandard', dir=TEST_MODELS_DIR)
    classla.download('bg', dir=TEST_MODELS_DIR)
    classla.download('mk', dir=TEST_MODELS_DIR)

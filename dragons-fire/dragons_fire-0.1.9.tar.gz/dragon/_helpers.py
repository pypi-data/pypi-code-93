from .move_data import CramDeliveryRequest
from .sample_test import SampleTest

TEST_CLASSES = {
    "sample_test": SampleTest,
    "clinical": CramDeliveryRequest
}

TEST_CLASSES_LIST = list(TEST_CLASSES.keys())

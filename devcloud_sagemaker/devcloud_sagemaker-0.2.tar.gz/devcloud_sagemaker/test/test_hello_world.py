from unittest import TestCase

from devcloud_sagemaker.sm_client import HELLO_WORLD_MESSAGE
from devcloud_sagemaker.sm_client import get_message


class TestHelloWorld(TestCase):
    def test_get_message(self):
        assert HELLO_WORLD_MESSAGE == get_message()

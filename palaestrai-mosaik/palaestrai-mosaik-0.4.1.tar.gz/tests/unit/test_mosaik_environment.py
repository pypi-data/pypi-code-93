import unittest
from unittest.mock import MagicMock, patch

from palaestrai_mosaik import MosaikEnvironment


class TestMosaikEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = MosaikEnvironment("", "", 0, {"params": dict()})

    @patch(f"{MosaikEnvironment.__module__}.threading.Thread")
    @patch(f"{MosaikEnvironment.__module__}.MosaikWorld")
    def test_start(self, mock_world, mock_thread):
        mock_world.setup = MagicMock()

        self.env.start_environment()


if __name__ == "__main__":
    unittest.main()

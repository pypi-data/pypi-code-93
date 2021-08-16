import unittest
from typing import Tuple, Dict, Optional, Any, Union
from dataclasses import dataclass

from libbiomedit.lib import classify


class TestClassify(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(classify.classify(Dict[str, str]), Dict)
        self.assertEqual(classify.classify(Tuple[int, ...]), Tuple)
        self.assertEqual(classify.classify(Optional[str]), Optional)
        self.assertEqual(classify.classify(Union[str, bool]), Union)
        self.assertEqual(classify.classify(Any), Any)

        @dataclass
        class X:
            pass

        self.assertEqual(classify.classify(X), classify.IsDataclass)

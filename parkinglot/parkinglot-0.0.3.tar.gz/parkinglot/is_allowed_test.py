import unittest

from is_allowed import is_allowed
from utils import logger

logger.info(">>> START UNITTEST <<<")


class IsAllowedTest(unittest.TestCase):
    def test_not_allowed_inputs(self):
        self.assertEqual(is_allowed('123456'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('12345G'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('12345'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('12L3456'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('1234M56'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('100000000000000000'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('123MM456'), 'NOT_ALLOWED')
        self.assertEqual(is_allowed('1234LL56'), 'NOT_ALLOWED')

    def test_not_valid_inputs(self):
        # All ascii Non-Alphanumeric Printable Characters
        for i in '!\"#$%&\'()*+-./:;<=>?@[\\]^_{|}~':
            self.assertEqual(is_allowed(f'{i}'), 'NOT_VALID')
        self.assertEqual(is_allowed('asf78*'), 'NOT_VALID')
        self.assertEqual(is_allowed('asf%78'), 'NOT_VALID')
        self.assertEqual(is_allowed(''), 'NOT_VALID')

    def test_allowed_inputs(self):
        self.assertEqual(is_allowed('123HJK'), 'ALLOWED')
        self.assertEqual(is_allowed('123GHJK'), 'ALLOWED')
        self.assertEqual(is_allowed('123567O'), 'ALLOWED')


if __name__ == '__main__':
    unittest.main()

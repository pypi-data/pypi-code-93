import unittest
from weighting_platform.tests.test_objects import cam_operator_test
from weighting_platform.functions import pic_make_functions


class CamTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(CamTest, self).__init__(*args, **kwargs)
        self.cam_operator = cam_operator_test

    def test_make_pic(self):
        response = pic_make_functions.make_pic(self.cam_operator, '1337')
        print(response)


if __name__ == '__main__':
    unittest.main()

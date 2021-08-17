import unittest
from weighting_platform.functions import weigthing_functions as wf
from weighting_platform.tests.test_objects import weightsplitter_test
import time


class WeigtingTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(WeigtingTest, self).__init__(*args, **kwargs)
        self.weight_splitter = weightsplitter_test
        self.weight_splitter.start()

    def atest_get_value(self):
        """ Проверить получение веса """
        result = wf.get_weigth_single(self.weight_splitter)
        result_must = {'weight_data': '5', 'port_name': None,
                       'test_mode': True,
                       'manual_value_set': True}
        self.assertTrue(all(item in result.items() for item in result_must.items()))

    def test_get_stable_weight(self):
        value = 0
        self.weight_splitter.set_manual_value(manual_value=str(value))
        result = wf.get_stable_data(self.weight_splitter, 5, 500)
        self.assertEqual(value, result)

    def test_check_slice(self):
        slice_w = [101010, 101010, 101010, 101010]
        result = wf.check_weight_stable(slice_w)
        self.assertTrue(result)

    def test_set_value(self):
        self.weight_splitter.set_manual_value(manual_value='1488')
        time.sleep(3)
        result = self.weight_splitter.get_value()
        print('Result', result)

    def test_weight_changed(self):
        start = 0
        now = 500
        result = wf.if_weight_changed(start, now, 50)
        self.assertTrue(result)
        start = 0
        now = 40
        result = wf.if_weight_changed(start, now, 50)
        self.assertTrue(not result)


if __name__ == '__main__':
    unittest.main()

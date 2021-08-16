import unittest
from portdatasplitter import functions
import datetime


class FunctionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(FunctionsTest, self).__init__(*args, **kwargs)
        self.data_list = [
            {'name': 'e', 'creation_date': datetime.datetime(2021, 5, 15), 'port_name': '/dev/ttyS4'},
            {'name': 'c', 'creation_date': datetime.datetime(2021, 3, 15), 'port_name': '/dev/ttyS3'},
            {'name': 'b', 'creation_date': datetime.datetime(2021, 2, 15), 'port_name': '/dev/ttyS4'},
            {'name': 'a', 'creation_date': datetime.datetime(2021, 1, 15), 'port_name': '/dev/ttyS5'},
            {'name': 'd', 'creation_date': datetime.datetime(2021, 4, 15), 'port_name': '/dev/ttyS3'},

        ]

    def test_locals_return(self):
        result = functions.get_format_send_message(weight_data=110, some='123')
        self.assertTrue(result['weight_data'] == 110 and result['some'] == '123')

    def test_get_sorted_data_list(self):
        result = functions.sort_data_list_by_date(self.data_list)
        self.assertTrue(result[0]['name'] == 'a' and result[-1]['name'] == 'e')
        result = functions.sort_data_list_by_date(self.data_list, reverse=True)
        self.assertTrue(result[0]['name'] == 'e' and result[-1]['name'] == 'a')

    def test_get_data_time_by_port(self):
        response = functions.get_data_time_by_port(self.data_list, port_name='/dev/ttyS4')
        self.assertTrue(response['name'] == 'e')
        response = functions.get_data_time_by_port(self.data_list, port_name='/dev/ttyS3')
        self.assertTrue(response['name'] == 'd')

    def test_get_last_data_dict(self):
        response = functions.get_last_data_dict(self.data_list)
        self.assertTrue(response['name'] == 'e')
        response = functions.get_last_data_dict(self.data_list, port_name='/dev/ttyS3')
        self.assertTrue(response['name'] == 'd')

if __name__ == '__main__':
    unittest.main()

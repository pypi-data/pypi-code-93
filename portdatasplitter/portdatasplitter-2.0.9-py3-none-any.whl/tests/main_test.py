from portdatasplitter.main import PortDataSplitter
from portdatasplitter.tests import test_settings as s
import unittest
from qdk.main import QDK
from time import sleep


class MainClassTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pds_pi = PortDataSplitter(s.my_ip, s.my_port, test_mode=True, debug=True, port_names_list=['TEST1', 'TEST2'])
        #self.pds_dk = QDK(s.my_ip, s.my_port)

    def start_server(self):
        self.pds_pi.start()

    def test_set_value(self):
        self.start_server()
        #self.pds_dk.make_connection()
        self.pds_pi.set_manual_value(manual_value='1000')
        sleep(2)
        print("RESPONSE:", self.pds_pi.get_value())
        sleep(5)
        self.pds_pi.set_manual_value(manual_value='0')
        sleep(2)
        print("RESPONSE:", self.pds_pi.get_value())
        #response = self.pds_dk.execute_method('set_manual_value', manual_value='1337',  get_response=True)
        #sleep(3)
        #response = self.pds_dk.execute_method('set_manual_value', manual_value='5000', port_name='TEST1',
        #                                      get_response=True)
        #sleep(5)
        #self.pds_dk.subscribe(port_name='')
        #print("RESPONSE:", response)


if __name__ == '__main__':
    unittest.main()
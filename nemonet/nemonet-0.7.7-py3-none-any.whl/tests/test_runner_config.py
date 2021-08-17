# Created by Jan Rummens at 5/01/2021
import unittest
import json
from nemonet.runner.vision_runner import Runner

class RunnerConfigTestCase(unittest.TestCase):


    def setUp(self):
        json_config_dict = {}
        sub_config = {}
        sub_config["headless"] = False
        sub_config["browser"] = "chrome"
        sub_config["type"] = "selenium"
        sub_config["options"] = {"experimental_flags": ["same-site-by-default-cookies@2","cookies-without-same-site-must-be-secure@2"]}
        json_config_dict["driver"] = sub_config

        sub_config = {}
        sub_config["switch"] = False
        json_config_dict["recording"] = sub_config

        self.filename = 'runner_config.json'

        with open( self.filename, 'w') as fp:
            json.dump(json_config_dict, fp, indent=4)
            fp.close()


    def test_read_format(self):
        with open('runner_config.json', 'r') as fp:
            data = json.load(fp)

        self.assertTrue( list( data.keys() ) == ['driver', 'recording'] )
        self.assertTrue( list( data["driver"].keys() ) == ['headless', 'browser', 'type', 'options'] )
        self.assertTrue( list( data["recording"].keys()) == ['switch'] )


if __name__ == '__main__':
    unittest.main()

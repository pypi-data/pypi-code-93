import unittest
import pathlib
import yaml
from tests import BaseTemplateTest
from net_models.models.BaseModels import BaseNetModel


class BaseTemplateTestIos(BaseTemplateTest):

    VENDOR = 'ios'
    TEST_CLASS = None
    TEMPLATE_NAME = ''
    RESOURCE_DIR = pathlib.Path(__file__).resolve().parent.parent.joinpath("resources").joinpath(VENDOR)
    ENVIRONMENT = BaseTemplateTest.get_vendor_environment(vendor=VENDOR)

    def common_testbase(self, test_cases: list):

        template = self.ENVIRONMENT.get_template(name=f"{self.TEMPLATE_NAME}.j2")

        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                want = test_case["result"]

                dict_params = None
                if "dict_params" in test_case.keys():
                    dict_params = test_case["dict_params"]

                if isinstance(test_case["data"], BaseNetModel):
                    if dict_params:
                        test_case["data"] = test_case["data"].serial_dict(**dict_params)
                    else:
                        test_case["data"] = test_case["data"].serial_dict(**dict_params)
                elif isinstance(test_case["data"], dict):
                    for k in test_case["data"].keys():
                        print(k)
                        if isinstance(test_case["data"][k], BaseNetModel):
                            if dict_params:
                                test_case["data"][k] = test_case["data"][k].serial_dict(**dict_params)
                            else:
                                test_case["data"][k] = test_case["data"][k].serial_dict()
                print(test_case["data"])

                have = template.render(**test_case["data"])
                print(f"! Template: {self.TEMPLATE_NAME}\tTest: {test_case['test_name']}\n<< BEGIN >>\n{have}<< END >>\n")

                self.assertEqual(want, have)

    def get_test_cases_from_resources(self):
        test_cases = []
        data_files = [x for x in self.RESOURCE_DIR.joinpath("data").iterdir() if x.is_file and x.suffix == ".yml" and x.stem.split("-")[0] == self.TEMPLATE_NAME]
        results_files = [x for x in self.RESOURCE_DIR.joinpath("results").iterdir() if x.is_file and x.suffix == ".txt" and x.stem.split("-")[0] == self.TEMPLATE_NAME]
        data_file_names = [x.stem for x in data_files]
        results_file_names = [x.stem for x in results_files]
        assert set(data_file_names) == set(results_file_names)

        test_cases = [{"test_name": x, "data": None, "result": None} for x in data_file_names]

        for test_case in test_cases:
            if self.TEST_CLASS is not None:
                data = None
                raw_data = yaml.safe_load([x for x in data_files if x.stem == test_case["test_name"]][0].read_text())
                params_keys = [x for x in raw_data.keys() if "params" in x]
                if len(params_keys) == 1:
                    data = dict(raw_data)
                    if isinstance(data[params_keys[0]], dict):
                        data[params_keys[0]] = self.TEST_CLASS.parse_obj(data[params_keys[0]]).serial_dict()
                    elif isinstance(data[params_keys[0]], list):
                        data[params_keys[0]] = [self.TEST_CLASS.parse_obj(x).serial_dict() for x in data[params_keys[0]]]
                else:
                    data = dict(raw_data)
                test_case["data"] = data
                print(test_case["data"])
            else:
                test_case["data"] = yaml.safe_load([x for x in data_files if x.stem == test_case["test_name"]][0].read_text())
            test_case["result"] = [x for x in results_files if x.stem == test_case["test_name"]][0].read_text()
        return test_cases


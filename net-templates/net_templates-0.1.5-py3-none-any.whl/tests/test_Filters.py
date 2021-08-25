import unittest
from net_models.models.BaseModels import BaseNetModel
from net_templates.filters import CustomFilters, AnsibleFilters
from pydantic.error_wrappers import ValidationError


class TestTemplateFiltersBase(unittest.TestCase):

    pass

class TestToVlanRange(TestTemplateFiltersBase):

    TEST_CLASS = CustomFilters()

    def test_from_int_list(self):

        test_cases = [
            {
                "test_name": "Test-From-Int-01",
                "data": list(range(1,4)),
                "result": "1-3"
            },
            {
                "test_name": "Test-From-Int-02",
                "data": [1, 3, 5],
                "result": "1,3,5"
            },
            {
                "test_name": "Test-From-Int-03",
                "data": [1, 2, 3, 4, 5, 7, 8, 9, 11],
                "result": "1-5,7-9,11"
            },
            {
                "test_name": "Test-From-Text-01",
                "data": "all",
                "result": "all"
            },
            {
                "test_name": "Test-From-Text-02",
                "data": "none",
                "result": "none"
            }
        ]
        for test_case in test_cases:
            with self.subTest(msg=test_case["test_name"]):
                want = test_case["result"]
                have = self.TEST_CLASS.to_vlan_range(test_case["data"])
                self.assertEqual(want, have)


class TestToModel(TestTemplateFiltersBase):

    def test_valid_01(self):
        data = {
            "name": "Radius-1",
            "server": "192.0.2.1",
            "key": {
                "encryption_type": 0,
                "value": "SuperSecret"
            }
        }
        model = "RadiusServer"
        model_data = CustomFilters().to_model(data=data, model=model, many=False, serialize=False)
        self.assertIsInstance(model_data, BaseNetModel)

    def test_valid_list_01(self):
        data = [
            {
                "name": "Radius-1",
                "server": "192.0.2.1",
                "key": {
                    "encryption_type": 0,
                    "value": "SuperSecret"
                }
            },
            {
                "name": "Radius-2",
                "server": "192.0.2.2",
                "key": {
                    "encryption_type": 0,
                    "value": "SuperSecret"
                }
            }
        ]
        model = "RadiusServer"
        model_data = CustomFilters().to_model(data=data, model=model, many=True, serialize=False)
        if not isinstance(model_data, list):
            self.fail("Model data is not list.")
        elif not all([isinstance(x, BaseNetModel) for x in model_data]):
            self.fail("Some elements are not instance of BaseNetModel")

    def test_valid_02(self):
        data = {
            "name": "Radius-1",
            "server": "192.0.2.1",
            "key": {
                "encryption_type": 0,
                "value": "SuperSecret"
            }
        }
        model = "RadiusServer"
        model_data = CustomFilters().to_model(data=data, model=model, many=False, serialize=True, dict_params={"exclude_none": True})
        self.assertDictEqual(
            model_data,
            {
                'name': 'Radius-1',
                'server': '192.0.2.1',
                'address_version': 'ipv4',
                'key': {
                    'value': 'SuperSecret',
                    'encryption_type': 0
                }
            }
        )

    def test_invalid_01(self):
        data = {
            "name": "Radius-1",
            "server": "192.0.2.1"
        }
        model = "RadiusServer"
        with self.assertRaises(ValidationError):
            model_data = CustomFilters().to_model(data=data, model=model, many=False, serialize=False)

    def test_invalid_02(self):
        data = {
            "name": "Radius-1",
            "server": "192.0.2.1"
        }
        model = "NonExistentModel"
        with self.assertRaises(ValueError):
            model_data = CustomFilters().to_model(data=data, model=model, many=False, serialize=False)


class TestValidateData(TestTemplateFiltersBase):

    def test_valid_01(self):
        data = {
            "name": "Radius-1",
            "server": "192.0.2.1",
            "key": {
                "encryption_type": 0,
                "value": "SuperSecret"
            }
        }
        model = "RadiusServer"
        self.assertTrue(CustomFilters().validate_data(data=data, model=model))

    def test_invalid_02(self):
        data = {
            "name": "Radius-1",
            "server": "192.0.2.1"
        }
        model = "RadiusServer"
        self.assertFalse(CustomFilters().validate_data(data=data, model=model))

del TestTemplateFiltersBase

if __name__ == '__main__':
    unittest.main()
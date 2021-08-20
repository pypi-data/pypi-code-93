import copy
from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.Pharmacologic import Pharmacologic


class PharmacologicResourceTestCase(TestCase):
    def setUp(self):
        super(PharmacologicResourceTestCase, self).setUp()

        self.inst = Pharmacologic()

        self.pharmacologic1 = self.inst.create({
            "pharma_set_id": "ab7b3796-63bc-4891-91bd-232fbeefa4b1",
            'unii_code': "2A41N28TJQ",
            'unii_name': 'BROMUS CARINATUS POLLEN',
            "nui": "N0000185367",
            "code_system": "2.16.840.1.113883.6.345",
            "class_name": "Non-Standardized Pollen Allergenic Extract",
            "class_type": "EPC",
        })

        self.pharmacologic2 = self.inst.create({
            "pharma_set_id": "901fd38a-6b75-42b6-97e4-0b7d9cab8a27",
            'unii_code': "OG645J8RVW",
            'unii_name': 'PIRBUTEROL',
            "nui": "N0000009922",
            "code_system": "2.16.840.1.113883.3.26.1.5",
            "class_name": "Adrenergic beta2-Agonists",
            "class_type": "MoA",
        })

        self.valid_data = {
            "pharma_set_id": "7df933d0-1a3d-4280-82de-c10e9305fadd",
            'unii_code': "2GQ1IRY63P",
            'unii_name': 'ATRACURIUM',
            "nui": "N0000175732",
            "code_system": "2.16.840.1.113883.3.26.1.5",
            "class_name": "Neuromuscular Nondepolarizing Blockade",
            "class_type": "PE",
        }

    @parameterized.expand([
        ('pharma_set_id',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            base_data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        expected_data = {
            **self.valid_data,
        }
        second_equals_first(expected_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand([
        ('id', 'pharmacologic1', 'id', 1),
        ('pharma_set_id', 'pharmacologic1', 'pharma_set_id', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

        resp = self.inst.read({
            field_name: getattr(self, attr)[attr_field],
        })
        self.assertEqual(expected_length, len(resp))

    @parameterized.expand([
        ('id', 999, NoResultFound),
    ])
    def test_one_raises_exception(self, field_name, field_value, exception):
        self.assertRaises(
            exception,
            self.inst.one,
            {
                field_name: field_value,
            },
        )

    @parameterized.expand([
        ('id',),
        ('pharma_set_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.pharmacologic1[field_name],
        })
        second_equals_first(
            self.pharmacologic1,
            resp,
        )

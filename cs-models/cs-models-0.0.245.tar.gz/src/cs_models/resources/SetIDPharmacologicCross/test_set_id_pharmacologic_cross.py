from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.SetIDPharmacologicCross import SetIDPharmacologicCross


class SetIDPharmacologicCrossResourceTestCase(TestCase):
    def setUp(self):
        super(SetIDPharmacologicCrossResourceTestCase, self).setUp()
        self.inst = SetIDPharmacologicCross()

        self.setidpharmacross1 = self.inst.create({
            "spl_set_id": '000155a8-709c-44e5-a75f-cd890f3a7caf',
            "pharma_set_id": 'c29a4f1b-49e6-46a6-aefe-820474b74d5f',

        })

        self.setidpharmacross2 = self.inst.create({
            "spl_set_id": '001dcaf3-5838-4fb0-a4b8-d65ae2eb009e',
            "pharma_set_id": '60da9c53-1225-442f-bbe1-3e0b1175c6e5',

        })

        self.valid_data = {
            "spl_set_id": '0045ec13-789a-40a1-ac1f-8c29049cfd13',
            "pharma_set_id": '49165386-3fd3-40b9-b5b8-89eb6f691830',
        }

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
        ('spl_set_id', 'setidpharmacross1', 'spl_set_id', 1),
        ('pharma_set_id', 'setidpharmacross1', 'pharma_set_id', 1),
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
        ('spl_set_id', '999', NoResultFound),
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
        ('spl_set_id',),
        ('pharma_set_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.setidpharmacross1[field_name],
        })
        second_equals_first(
            self.setidpharmacross1,
            resp,
        )

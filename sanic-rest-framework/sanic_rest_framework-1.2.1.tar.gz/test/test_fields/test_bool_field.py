"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/2/3 10:07
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_bool_field.py
    布尔类型字段测试
@ChangeHistory:
    datetime action why
    example:
    2021/2/3 10:07 change 'Fix bug'
        
"""
import unittest

from tortoise.contrib.test import initializer

from srf.fields import BooleanField as TestField
from test.test_fields.test_base_field import TestBaseField

initializer(['test.models'])


class TestDecimalField(TestBaseField):

    async def test_external_to_internal(self):
        """
        外转内 str -> dict 是严格的，不符合类型的都应该报错,
        一切都要经过验证
        :return:
        """
        TRUE_VALUES = {
            't', 'T',
            'y', 'Y', 'yes', 'YES',
            'true', 'True', 'TRUE',
            'on', 'On', 'ON',
            '1', 1,
            True
        }
        FALSE_VALUES = {
            'f', 'F',
            'n', 'N', 'no', 'NO',
            'false', 'False', 'FALSE',
            'off', 'Off', 'OFF',
            '0', 0, 0.0,
            False
        }
        NULL_VALUES = {'null', 'Null', 'NULL', '', None}
        tf1 = TestField()
        for i in TRUE_VALUES:
            self.assertEqual(await tf1.external_to_internal(i), True)
        for i in FALSE_VALUES:
            self.assertEqual(await tf1.external_to_internal(i), False)
        for i in NULL_VALUES:
            self.assertEqual(await tf1.external_to_internal(i), None)

    async def test_internal_to_external(self):
        """
        内转外 str -> dict 是宽松的，
        只要类型正确都不报错
        :return:
        """
        TRUE_VALUES = {
            't', 'T',
            'y', 'Y', 'yes', 'YES',
            'true', 'True', 'TRUE',
            'on', 'On', 'ON',
            '1', 1,
            True
        }
        FALSE_VALUES = {
            'f', 'F',
            'n', 'N', 'no', 'NO',
            'false', 'False', 'FALSE',
            'off', 'Off', 'OFF',
            '0', 0, 0.0,
            False
        }
        tf1 = TestField()
        for i in TRUE_VALUES:
            self.assertEqual(await tf1.internal_to_external(i), True)
        for i in FALSE_VALUES:
            self.assertEqual(await tf1.internal_to_external(i), False)
        self.assertEqual(await tf1.internal_to_external(None), False)
        self.assertEqual(await tf1.internal_to_external(''), False)
        self.assertEqual(await tf1.internal_to_external('null'), True)
        self.assertEqual(await tf1.internal_to_external('any'), True)
        self.assertEqual(await tf1.internal_to_external('NULL'), True)
        self.assertEqual(await tf1.internal_to_external('yyyy'), True)
        self.assertEqual(await tf1.internal_to_external('曹凯'), True)


if __name__ == '__main__':
    unittest.main()

"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/1/28 16:16
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_char_field.py
    字符字段单元测试
@ChangeHistory:
    datetime action why
    example:
    2021/1/28 16:16 change 'Fix bug'
        
"""
import unittest

from tortoise.contrib.test import initializer

from srf.exceptions import ValidationException
from srf.fields import CharField
from test.test_fields.test_base_field import TestBaseField

initializer(['test.models'])


class TestCharField(TestBaseField):
    async def test_external_to_internal(self):
        data = ' Python'
        char1 = CharField()
        self.assertEqual(await char1.external_to_internal(data), 'Python')

    async def test_internal_to_external(self):
        data1 = {'char1': 'Python'}
        data2 = {'char1': 66666}
        char1 = CharField()
        char1.bind('char1', char1)

        value = await char1.get_internal_value(data1)
        self.assertEqual(await char1.internal_to_external(value), 'Python')

        value = await char1.get_internal_value(data2)
        self.assertEqual(await char1.internal_to_external(value), '66666')

    async def test_trim_whitespace(self):
        data = ' Python'
        char1 = CharField()
        char2 = CharField(trim_whitespace=True)
        char3 = CharField(trim_whitespace=False)
        c1_data = await char1.external_to_internal(data)
        c2_data = await char2.external_to_internal(data)
        c3_data = await char3.external_to_internal(data)
        self.assertEqual(c1_data, 'Python')
        self.assertEqual(c2_data, 'Python')
        self.assertEqual(c3_data, ' Python')

    async def test_max_length(self):
        data = 'Python'
        char1 = CharField()
        char2 = CharField(max_length=10)
        char3 = CharField(max_length=5)
        self.assertEqual(await char1.run_validation(data), 'Python')
        self.assertEqual(await char2.run_validation(data), 'Python')

        with self.assertRaises(ValidationException):
            await char3.run_validation(data)

    async def test_min_length(self):
        data = 'Python'
        char1 = CharField()
        char2 = CharField(min_length=5)
        char3 = CharField(min_length=10)
        self.assertEqual(await char1.run_validation(data), 'Python')
        self.assertEqual(await char2.run_validation(data), 'Python')

        with self.assertRaises(ValidationException):
            await char3.run_validation(data)


if __name__ == '__main__':
    unittest.main()

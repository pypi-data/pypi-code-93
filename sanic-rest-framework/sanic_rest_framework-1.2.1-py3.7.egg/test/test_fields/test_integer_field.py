"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/1/29 10:23
@DependencyLibrary：无
@MainFunction：无
@FileDoc：
    test_integer_field.py
    测试整数类型字段
@ChangeHistory:
    datetime action why
    example:
    2021/1/29 10:23 change 'Fix bug'

"""

import unittest

from srf.exceptions import ValidationException
from srf.fields import IntegerField as TestField
from test.test_fields.test_base_field import TestBaseField


class TestCharField(TestBaseField):

    async def test_external_to_internal(self):
        """
        外转内 str -> dict 是严格的，不符合类型的都应该报错,
        一切都要经过验证
        int => [1,'1','1.0',1.0',1.]
        :return:
        """

        tf = TestField()
        with self.assertRaises(ValidationException):
            await tf.external_to_internal(self.max_float)
        with self.assertRaises(ValidationException):
            await tf.external_to_internal(self.str_max_float)
        with self.assertRaises(ValidationException):
            await tf.external_to_internal(self.str_chinese)
        with self.assertRaises(ValidationException):
            await tf.external_to_internal(self.bool_True)

        self.assertEqual(await tf.external_to_internal(self.max_int), self.max_int)
        self.assertEqual(await tf.external_to_internal(self.str_max_int), self.max_int)

    async def test_internal_to_external(self):
        """
        内转外 str -> dict 是宽松的，
        只要是数值类型都不报错，int(xx)
        :return:
        """
        data1 = {'tf1': self.str_chinese}
        data2 = {'tf1': self.max_int}
        data3 = {'tf1': self.str_max_int}
        data4 = {'tf1': self.str_max_float}
        data5 = {'tf1': self.max_float}

        tf = TestField()
        tf.bind('tf1', tf)

        value = await tf.get_internal_value(data1)
        with self.assertRaises(ValueError):
            await tf.internal_to_external(value)

        value = await tf.get_internal_value(data2)
        self.assertEqual(await tf.internal_to_external(value), self.max_int)

        value = await tf.get_internal_value(data3)
        self.assertEqual(await tf.internal_to_external(value), self.max_int)
        value = await tf.get_internal_value(data4)

        with self.assertRaises(ValueError):
            # str_float 不可被转换
            await tf.internal_to_external(value)

        value = await tf.get_internal_value(data5)
        self.assertEqual(await tf.internal_to_external(value), self.max_int)

    def test_max_value(self):
        tf1 = TestField()
        tf2 = TestField(max_value=10)

        self.assertEqual(tf1.run_validators(data=self.str_max_int), None)

        # 超出限制
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.str_max_int), None)

        # 未设置 不存在超出限制
        self.assertEqual(tf1.run_validators(data=self.max_int), None)
        self.assertEqual(tf1.run_validators(data=self.min_int), None)

        # 超出限制
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.max_int), None)
        self.assertEqual(tf2.run_validators(data=self.min_int), None)

    def test_min_value(self):
        tf1 = TestField()
        tf2 = TestField(min_value=10)

        # 无限制，则无验证器所以不报错
        self.assertEqual(tf1.run_validators(data=self.str_max_int), None)

        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.str_max_int), None)
            # 超出限制

        # 未设置 不存在超出限制
        self.assertEqual(tf1.run_validators(data=self.max_int), None)
        self.assertEqual(tf1.run_validators(data=self.min_int), None)

        # 低于最小值
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.min_int), None)
        self.assertEqual(tf2.run_validators(data=self.max_int), None)

    async def test_max_string_length(self):
        tf1 = TestField()
        with self.assertRaises(ValidationException):
            #  超出约定长度
            await tf1.external_to_internal(self.long_str)
        self.assertEqual(await tf1.external_to_internal(self.str_max_int), self.max_int)


if __name__ == '__main__':
    unittest.main()

"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/1/29 10:23
@DependencyLibrary：无
@MainFunction：无
@FileDoc：
    test_decimal_field.py
    测试十进制类型字段
@ChangeHistory:
    datetime action why
    example:
    2021/1/29 10:23 change 'Fix bug'

"""

import unittest
from decimal import Decimal, ROUND_DOWN, getcontext, InvalidOperation
from srf.exceptions import ValidationException
from srf.fields import DecimalField as TestField
from test.test_fields.test_base_field import TestBaseField


class TestDecimalField(TestBaseField):

    def test_validate_precision(self):
        """
        测试 max_digits, decimal_places
        :return:
        """

        tf = TestField(max_digits=6, decimal_places=2)
        with self.assertRaises(ValidationException):
            tf.validate_precision(Decimal('99.999'))
        with self.assertRaises(ValidationException):
            tf.validate_precision(Decimal('99999.99'))
        self.assertEqual(tf.validate_precision(Decimal('99.99')), Decimal('99.99'))
        self.assertEqual(tf.validate_precision(Decimal('9999.99')), Decimal('9999.99'))
        with self.assertRaises(ValidationException):
            tf.validate_precision(Decimal('999.999'))

    def test_quantize(self):
        tf = TestField(max_digits=6, decimal_places=2)
        context = getcontext()  # 获取decimal现在的上下文
        context.rounding = ROUND_DOWN
        self.assertEqual(tf.quantize(Decimal('99.99999999')), Decimal('99.99'))

    async def test_external_to_internal(self):
        """
        外转内 str -> dict 是严格的，不符合类型的都应该报错,
        一切都要经过验证
        :return:
        """
        tf1 = TestField(max_digits=6, decimal_places=2)

        # 布尔类型 不行
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.bool_True)
        # 字符类型 中文 不行
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_chinese)
        # 字符类型 小数π 超长不行
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_pi)
        # 浮点类型 小数π 超长不行
        with self.assertRaises(ValidationException):
            self.assertEqual(await tf1.external_to_internal(self.pi), self.pi)

        self.assertEqual(await tf1.external_to_internal(self.str_max_float), Decimal(self.str_max_float))

        self.assertEqual(await tf1.external_to_internal(self.max_int), Decimal(self.max_int))

        self.assertEqual(await tf1.external_to_internal(self.str_max_int), Decimal(self.max_int))

    async def test_internal_to_external(self):
        """
        内转外 str -> dict 是宽松的，
        只要类型正确都不报错
        :return:
        """
        data1 = {'tf': self.str_chinese}
        data2 = {'tf': self.max_int}
        data3 = {'tf': self.str_max_int}
        data4 = {'tf': self.str_max_float}
        data5 = {'tf': self.max_float}

        tf = TestField(max_digits=6, decimal_places=2, coerce_to_string=False)
        tf.bind('tf', tf)

        value = await tf.get_internal_value(data1)
        with self.assertRaises(InvalidOperation):
            await tf.internal_to_external(value)

        value = await tf.get_internal_value(data2)
        self.assertEqual(await tf.internal_to_external(value), 9999.00)

        # Decimal(int) == int
        # Decimal(str_int) == int
        value = await tf.get_internal_value(data3)
        self.assertEqual(await tf.internal_to_external(value), self.max_int)

        # Decimal(float) == float
        # Decimal(str_float) != float
        value = await tf.get_internal_value(data4)
        self.assertNotEqual(await tf.internal_to_external(value), self.max_float)
        self.assertEqual(await tf.internal_to_external(value), Decimal(self.str_max_float))

        value = await tf.get_internal_value(data5)
        self.assertEqual(await tf.internal_to_external(value), Decimal(self.str_max_float))

    def test_max_value(self):
        tf1 = TestField(max_digits=6, decimal_places=2)
        tf2 = TestField(max_digits=6, decimal_places=2, max_value=10.69)

        # 未设置 不存在超出限制
        self.assertEqual(tf1.run_validators(data=self.str_max_int), None)
        self.assertEqual(tf1.run_validators(data=self.min_float), None)
        self.assertEqual(tf1.run_validators(data=self.str_max_float), None)
        self.assertEqual(tf1.run_validators(data=self.max_float), None)

        # 超出限制
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.max_int), None)
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.max_float), None)
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.str_max_int), None)
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.str_max_float), None)

        self.assertEqual(tf2.run_validators(data=self.min_int), None)
        self.assertEqual(tf2.run_validators(data=self.min_float), None)

    def test_min_value(self):
        tf1 = TestField(max_digits=6, decimal_places=2)
        tf2 = TestField(max_digits=6, decimal_places=2, min_value=10.69)

        # 未设置 不存在超出限制
        self.assertEqual(tf1.run_validators(data=self.str_max_int), None)
        self.assertEqual(tf1.run_validators(data=self.min_float), None)
        self.assertEqual(tf1.run_validators(data=self.str_max_float), None)
        self.assertEqual(tf1.run_validators(data=self.max_float), None)

        # 超出限制
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.min_float), None)
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.min_int), None)

        # 不支持其除 int float 以外的格式
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.str_min_float), None)
        with self.assertRaises(ValidationException):
            self.assertEqual(tf2.run_validators(data=self.str_min_int), None)

        self.assertEqual(tf2.run_validators(data=self.max_int), None)
        self.assertEqual(tf2.run_validators(data=self.max_float), None)

    async def test_max_string_length(self):
        tf1 = TestField(max_digits=6, decimal_places=2)
        with self.assertRaises(ValidationException):
            #  超出约定长度
            await tf1.external_to_internal(self.long_str)
        self.assertEqual(await tf1.external_to_internal(self.str_max_int), self.max_int)


if __name__ == '__main__':
    unittest.main()

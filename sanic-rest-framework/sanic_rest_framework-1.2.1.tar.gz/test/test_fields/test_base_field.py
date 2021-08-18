"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/2/2 15:58
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_base_field.py
    字段
@ChangeHistory:
    datetime action why
    example:
    2021/2/2 15:58 change 'Fix bug'
        
"""
import asyncio
from tortoise.contrib import test
from tortoise.contrib.test import initializer, finalizer

from srf.exceptions import ValidationException
from srf.fields import Field as TestField, empty, SkipField
from srf.validators import MaxValueValidator
from test.utils import TestDataMixin

initializer(['test.models'])


class TestBaseField(TestDataMixin, test.TestCase):
    """测试基类的基本功能"""

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()

    def test_bing(self):
        tf1 = TestField()
        tf2 = TestField()
        tf1.bind('test1', tf2)
        self.assertEqual(tf1.field_name, 'test1')
        self.assertEqual(tf1.source, 'test1')
        self.assertEqual(tf1.source_attrs, ['test1'])
        self.assertEqual(tf1.parent, tf2)

    def test_get_external_value(self):
        data1 = {'test': self.str_max_int}
        data2 = {'test': self.max_int}
        data3 = {'test': self.str_chinese}
        data4 = {'test1': self.str_chinese}
        base_tf = TestField()
        tf1 = TestField()
        tf2 = TestField(default=1)
        tf1.bind('test', base_tf)
        tf2.bind('test1', base_tf)

        self.assertEqual(tf1.get_external_value(data1), self.str_max_int)
        self.assertEqual(tf1.get_external_value(data2), self.max_int)
        self.assertEqual(tf1.get_external_value(data3), self.str_chinese)
        self.assertEqual(tf1.get_external_value(data4), empty)
        self.assertEqual(tf1.get_external_value({}), empty)

        self.assertEqual(tf2.get_external_value(data1), 1)
        self.assertEqual(tf2.get_external_value(data2), 1)
        self.assertEqual(tf2.get_external_value(data3), 1)
        self.assertEqual(tf2.get_external_value(data4), self.str_chinese)

    async def test_get_internal_value(self):
        # 未进行 Model 类型测试
        test_data = [
            [self.str_chinese, {'tf': self.str_chinese}],
            [self.str_england, {'tf': self.str_england}],
            [self.max_float, {'tf': self.max_float}],
            [self.str_max_float, {'tf': self.str_max_float}],
            [self.max_int, {'tf': self.max_int}],
            [self.str_max_int, {'tf': self.str_max_int}],
            [self.pi, {'tf': self.pi}],
            [self.str_pi, {'tf': self.str_pi}],
            [self.bool_True, {'tf': self.bool_True}],
            [self.bool_False, {'tf': self.bool_False}],
            [self.str_bool_True, {'tf': self.str_bool_True}],
            [self.str_bool_False, {'tf': self.str_bool_False}],
        ]

        tf = TestField()
        tf.bind('tf', tf)
        for value, data in test_data:
            self.assertEqual(await tf.get_internal_value(data), value)

    def test_run_validators(self):
        tf = TestField(validators=[MaxValueValidator(1000)])
        tf.bind('tf', tf)
        tf.run_validators(10)
        tf.run_validators(1000)
        with self.assertRaises(ValidationException):
            tf.run_validators(1001)

    def test_get_default(self):
        def test():
            return '5'

        tf1 = TestField()
        tf2 = TestField(default=0)
        tf3 = TestField(default=test)
        with self.assertRaises(SkipField):
            tf1.get_default()
        self.assertEqual(tf2.get_default(), 0)
        self.assertEqual(tf3.get_default(), '5')

    def test_validate_empty_values(self):
        base_tf = TestField()

        tf1 = TestField()
        tf1.bind('t1', base_tf)
        self.assertEqual(tf1.validate_empty_values(10), (False, 10))
        with self.assertRaises(SkipField):
            tf1.validate_empty_values(empty)
        with self.assertRaises(ValidationException):
            tf1.validate_empty_values(None)

        tf2 = TestField(default=0)
        tf2.bind('t2', base_tf)
        self.assertEqual(tf2.validate_empty_values(10), (False, 10))
        self.assertEqual(tf2.validate_empty_values(empty), (True, 0))
        with self.assertRaises(ValidationException):
            tf2.validate_empty_values(None)

        tf3 = TestField(default=0, read_only=True)
        tf3.bind('t3', base_tf)
        self.assertEqual(tf3.validate_empty_values(10), (True, 0))
        self.assertEqual(tf3.validate_empty_values(empty), (True, 0))
        self.assertEqual(tf3.validate_empty_values(None), (True, 0))

        tf4 = TestField(default=0, required=True)
        tf4.bind('t4', base_tf)
        self.assertEqual(tf4.validate_empty_values(10), (False, 10))
        with self.assertRaises(ValidationException):
            tf4.validate_empty_values(empty)
        with self.assertRaises(ValidationException):
            tf4.validate_empty_values(None)

        tf5 = TestField(default=0, allow_null=True)
        tf5.bind('t5', base_tf)
        self.assertEqual(tf5.validate_empty_values(10), (False, 10))
        self.assertEqual(tf5.validate_empty_values(empty), (True, 0))
        self.assertEqual(tf5.validate_empty_values(empty), (True, 0))

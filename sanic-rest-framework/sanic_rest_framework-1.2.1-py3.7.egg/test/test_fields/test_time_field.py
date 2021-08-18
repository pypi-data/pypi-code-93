"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/2/4 14:35
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_time_field.py
    测试时间格式字段
@ChangeHistory:
    datetime action why
    example:
    2021/2/4 14:35 change 'Fix bug'
        
"""

import unittest

from srf.exceptions import ValidationException
from srf.fields import TimeField as TestField
from test.test_fields.test_base_field import TestBaseField


class TestDateTimeField(TestBaseField):

    async def test_external_to_internal(self):
        """
        外转内 str -> dict 是严格的，不符合类型的都应该报错,
        一切都要经过验证
        :return:
        """

        # 正常测试
        tf1 = TestField()

        self.assertEqual(await tf1.external_to_internal(self.str_time), self.obj_time)
        self.assertEqual(await tf1.external_to_internal(self.obj_time), self.obj_time)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime_bad_y)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime_bad_ym)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime_bad_d)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime_bad_h)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime_bad_hm)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime_bad_s)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_date)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_datetime)

    async def test_internal_to_external(self):
        """
        内转外 str -> dict 是宽松的，
        只要类型正确都不报错
        :return:
        """
        tf1 = TestField()
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(None)
        # 可以转换对象类型的 datetime
        self.assertEqual(await tf1.internal_to_external(self.obj_datetime), self.str_time)
        self.assertEqual(await tf1.internal_to_external(self.obj_time), self.str_time)
        self.assertEqual(await tf1.internal_to_external(self.str_time), self.str_time)

        # 不可转换字符类型的 datetime
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(self.str_datetime)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(self.obj_date)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(self.str_date)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(1)


if __name__ == '__main__':
    unittest.main()

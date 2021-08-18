"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/2/3 10:34
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_datetime_field.py
    测试日期时间类型字段
@ChangeHistory:
    datetime action why
    example:
    2021/2/3 10:34 change 'Fix bug'
        
"""

import unittest
from datetime import timezone, timedelta, datetime
from srf.exceptions import ValidationException
from srf.fields import DateTimeField as TestField
from test.test_fields.test_base_field import TestBaseField


class TestDateTimeField(TestBaseField):

    def test_get_default_timezone(self):
        tf = TestField()
        tf.get_default_timezone()
        self.assertEqual(tf.get_default_timezone(), timezone(timedelta(hours=8)))

    def test_enforce_timezone(self):
        time1 = datetime.now()
        tf1 = TestField()
        tf2 = TestField(set_timezone=timezone(timedelta(hours=6)))
        self.assertEqual(tf1.enforce_timezone(time1).tzinfo, tf1.get_default_timezone())
        self.assertEqual(tf2.enforce_timezone(time1).tzinfo, timezone(timedelta(hours=6)))
        self.assertNotEqual(tf2.enforce_timezone(time1).tzinfo, tf1.get_default_timezone())

    async def test_external_to_internal(self):
        """
        外转内 str -> dict 是严格的，不符合类型的都应该报错,
        一切都要经过验证
        :return:
        """

        # 正常测试
        tf1 = TestField()
        tf2 = TestField(set_timezone=timezone(timedelta(hours=5)))
        self.assertEqual(await tf1.external_to_internal(self.str_datetime), datetime(
            2019, 12, 18, 8, 21, 25, 0, tf1.get_default_timezone()))
        self.assertNotEqual((await tf2.external_to_internal(self.str_datetime)).tzinfo, tf2.get_default_timezone())
        self.assertEqual((await tf2.external_to_internal(self.str_datetime)).tzinfo, timezone(timedelta(hours=5)))
        self.assertEqual(await tf2.external_to_internal(self.str_datetime), datetime(
            2019, 12, 18, 5, 21, 25, 0, timezone(timedelta(hours=5))))
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
            await tf1.external_to_internal(self.str_time)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(self.str_date)

    async def test_internal_to_external(self):
        """
        内转外 str -> dict 是宽松的，
        只要类型正确都不报错
        :return:
        """
        tf1 = TestField()
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(None)
        self.assertEqual(await tf1.internal_to_external(self.obj_datetime), self.str_datetime)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(self.obj_date)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(self.obj_time)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(1)


if __name__ == '__main__':
    unittest.main()

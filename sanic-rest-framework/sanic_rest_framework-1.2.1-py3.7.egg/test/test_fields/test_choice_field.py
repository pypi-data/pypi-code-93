"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/3/4 11:20
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_choice_field.py
    文件说明
@ChangeHistory:
    datetime action why
    example:
    2021/3/4 11:20 change 'Fix bug'
        
"""

import unittest

from srf.exceptions import ValidationException
from srf.fields import ChoiceField as TestField
from test.test_fields.test_base_field import TestBaseField


class TestDateTimeField(TestBaseField):
    def setUp(self) -> None:
        self.choice = (
            ('刘文静', '开发人员'),
            ('光明', '播音员'),
            ('李焕英', '纺织厂女工')
        )

    async def test_external_to_internal(self):
        """
        外转内 str -> dict 是严格的，不符合类型的都应该报错,
        一切都要经过验证
        :return:
        """

        # 正常测试
        tf1 = TestField(choices=self.choice)
        self.assertEqual(await tf1.external_to_internal('刘文静'), '开发人员')
        self.assertEqual(await tf1.external_to_internal('光明'), '播音员')
        self.assertEqual(await tf1.external_to_internal('李焕英'), '纺织厂女工')

        with self.assertRaises(ValidationException):
            await tf1.external_to_internal(None)
        with self.assertRaises(ValidationException):
            await tf1.external_to_internal('曹凯')

    async def test_internal_to_external(self):
        """
        内转外 str -> dict 是宽松的，
        只要类型正确都不报错
        :return:
        """
        # 正常测试
        tf1 = TestField(choices=self.choice)
        self.assertEqual(await tf1.internal_to_external('刘文静'), '开发人员')
        self.assertEqual(await tf1.internal_to_external('光明'), '播音员')
        self.assertEqual(await tf1.internal_to_external('李焕英'), '纺织厂女工')

        with self.assertRaises(ValidationException):
            await tf1.internal_to_external(None)
        with self.assertRaises(ValidationException):
            await tf1.internal_to_external('曹凯')


if __name__ == '__main__':
    unittest.main()

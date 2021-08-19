# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from argparse import Namespace
import six
import unittest

from anna.configuration import parametrize
from anna.parameters import ActionParameter, AwareParameter, BoolParameter


class TestCaseWithParameters(unittest.TestCase):
    def test_name_clashes(self):
        with self.assertRaises(ValueError):
            parametrize(BoolParameter('Test'), BoolParameter('Test'))
        with self.assertRaises(ValueError):
            parametrize(BoolParameter('Test'), _test=BoolParameter('SomeName'))

    def test_self_dependent_parameter(self):
        with self.assertRaises(ValueError):
            parametrize(
                ActionParameter(BoolParameter('Test'), six.text_type, depends_on=('Test',))
            )

    def test_non_resolving_dependency(self):
        with self.assertRaises(ValueError):
            parametrize(
                ActionParameter(BoolParameter('Test'), six.text_type,
                                depends_on=('DoesNotResolve',))
            )

    def test_invalid_dependency_types(self):
        with self.assertRaises(TypeError):
            parametrize(ActionParameter(BoolParameter('Test'), six.text_type,
                                        depends_on=(BoolParameter('NonAwareParameter'),)))
        with self.assertRaises(TypeError):
            parametrize(ActionParameter(BoolParameter('Test'), six.text_type,
                                        depends_on=(1,)))

    def test_string_dependency_replacement(self):
        cls_cover = Namespace(CONFIG_PATH='')
        action_parameter = ActionParameter(BoolParameter('Test'), six.text_type,
                                           depends_on=('Other',))
        decorator = parametrize(action_parameter,
                                BoolParameter('Other'))
        decorator(cls_cover)
        self.assertIsInstance(action_parameter.depends_on[0], AwareParameter)

    def test_conversion_to_aware_parameters_upon_decorating(self):
        cls_cover = Namespace(CONFIG_PATH='')
        decorator = parametrize(ActionParameter(BoolParameter('Test'), six.text_type),
                                BoolParameter('Other'))
        cls_cover = decorator(cls_cover)
        self.assertIsInstance(cls_cover._test, AwareParameter)
        self.assertIsInstance(cls_cover._other, AwareParameter)


if __name__ == '__main__':
    unittest.main()

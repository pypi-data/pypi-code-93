# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import unittest

import numpy
import scipy.constants as constants
from scipy.constants import physical_constants

from anna.adaptors import JSONAdaptor
from anna.exceptions import IncompleteConfigurationError, RepresentationError, InvalidUnitError
from anna.input import Unit, Value
from anna.parameters import Parameter, BoolParameter, IntegerParameter, \
    NumberParameter, PhysicalQuantityParameter, StringParameter, VectorParameter, \
    DupletParameter, TripletParameter, ComplementaryParameterGroup, SubstitutionParameterGroup


class TestCaseParameter(unittest.TestCase):
    def test_validate_representation(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            BoolParameter.validate_representation(True, {})
        with self.assertRaises(TypeError):
            BoolParameter.validate_representation('', '')

    def test_field_names(self):
        self.assertEqual(Parameter('CamelCaseName').field_name, '_camel_case_name')
        self.assertEqual(Parameter('snake_case_name').field_name, '_snake_case_name')
        self.assertEqual(
            Parameter('Those spaces should be replaced with underscores').field_name,
            '_those_spaces_should_be_replaced_with_underscores'
        )
        self.assertEqual(
            Parameter('Spaces before Uppercase Letters should also be replaced').field_name,
            '_spaces_before_uppercase_letters_should_also_be_replaced'
        )
        self.assertEqual(
            Parameter('dashes-should-be-replaced-by-underscores').field_name,
            '_dashes_should_be_replaced_by_underscores'
        )


class TestCaseBoolParameter(unittest.TestCase):
    def test_convert_representation(self):
        # From doc string.
        self.assertEqual(BoolParameter.convert_representation('true'), True)
        self.assertEqual(BoolParameter.convert_representation('false'), False)

    def test_validate_representation(self):
        with self.assertRaises(RepresentationError):
            BoolParameter.validate_representation('invalid representation', {})
        # From doc string.
        self.assertEqual(BoolParameter.validate_representation('true'), None)
        self.assertEqual(BoolParameter.validate_representation('false'), None)
        with self.assertRaises(RepresentationError):
            BoolParameter.validate_representation('whatever')

    def test_load_from_representation(self):
        self.assertEqual(BoolParameter('Test').load_from_representation('true', {}), True)
        self.assertEqual(BoolParameter('Test').load_from_representation('false', {}), False)


class TestCaseIntegerParameter(unittest.TestCase):
    def test_convert_representation(self):
        self.assertEqual(IntegerParameter.convert_representation('1', {}), 1)
        self.assertEqual(IntegerParameter.convert_representation('1*2', {}), 2)
        self.assertEqual(IntegerParameter.convert_representation('1 * 2', {}), 2)
        self.assertEqual(IntegerParameter.convert_representation('2**3', {}), 8)
        self.assertEqual(IntegerParameter.convert_representation('2+3', {}), 5)
        self.assertEqual(IntegerParameter.convert_representation('2-3', {}), -1)
        self.assertEqual(IntegerParameter.convert_representation('10 - 2**3', {}), 2)
        self.assertEqual(IntegerParameter.convert_representation('25 - 3**3 + 5', {}), 3)
        self.assertEqual(IntegerParameter.convert_representation('25 - 3**3 + 5*4', {}), 18)
        # From doc string.
        self.assertEqual(IntegerParameter.convert_representation('2'), 2)
        self.assertEqual(IntegerParameter.convert_representation('2 + 5'), 7)
        self.assertEqual(IntegerParameter.convert_representation('2 + 5*3'), 17)
        self.assertEqual(IntegerParameter.convert_representation('2**3 + 5*3'), 23)
        self.assertEqual(IntegerParameter.convert_representation('2 ** (3 + 5) *3'), 768)

    def test_validate_representation(self):
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('invalid representation', {})
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('1/2', {})
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('1.2', {})
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('1e2', {})
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('%e', {})
        # From doc string.
        self.assertEqual(IntegerParameter.validate_representation('1**2 + 3*4 - (5 + 3)'), None)
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('1/2')
        with self.assertRaises(RepresentationError):
            IntegerParameter.validate_representation('1.1 * 5')

    def test_load_from_representation(self):
        parameter = IntegerParameter('Test')
        self.assertEqual(parameter.load_from_representation('1', {}), 1)
        self.assertEqual(parameter.load_from_representation('1*2', {}), 2)
        self.assertEqual(parameter.load_from_representation('1 * 2', {}), 2)
        self.assertEqual(parameter.load_from_representation('2**3', {}), 8)
        self.assertEqual(parameter.load_from_representation('2+3', {}), 5)
        self.assertEqual(parameter.load_from_representation('2-3', {}), -1)
        self.assertEqual(parameter.load_from_representation('10 - 2**3', {}), 2)
        self.assertEqual(parameter.load_from_representation('25 - 3**3 + 5', {}), 3)
        self.assertEqual(parameter.load_from_representation('25 - 3**3 + 5*4', {}), 18)


class TestCaseStringParameter(unittest.TestCase):
    def test_convert_representation(self):
        test_string = ('This string contains numbers (1, 2, 3, ..., 9) '
                       'as well as other characters such as %[]#-+=/*^@!?\\<>')
        self.assertEqual(StringParameter.convert_representation(test_string, {}), test_string)


class TestCaseNumberParameter(unittest.TestCase):
    def convert_representation(self):
        # From doc string.
        self.assertEqual(NumberParameter.convert_representation('1 * 2 + 3'), 5.0)
        self.assertEqual(NumberParameter.convert_representation('2 * np.pi'), 2 * numpy.pi)
        self.assertEqual(
            NumberParameter.convert_representation('np.sin(np.pi / 2)'),
            numpy.sin(numpy.pi / 2)
        )


# noinspection PyPep8Naming
class TestCaseVectorParameter(unittest.TestCase):
    def test_validate_representation(self):
        BoolVector = VectorParameter[BoolParameter]
        with self.assertRaises(RepresentationError):
            BoolVector.validate_representation('true', None)
        with self.assertRaises(RepresentationError):
            BoolVector.validate_representation('true, false', None)
        with self.assertRaises(RepresentationError):
            BoolVector.validate_representation('[true; false]', None)
        with self.assertRaises(RepresentationError):
            BoolVector.validate_representation('[1, 2]', None)
        self.assertIsNone(BoolVector.validate_representation('[true]', None))
        self.assertIsNone(BoolVector.validate_representation('[true, true]', None))
        self.assertIsNone(BoolVector.validate_representation('[true  false]', None))
        self.assertIsNone(BoolVector.validate_representation('[true     false, true]', None))
        bool_vector = BoolVector('BoolVector')
        self.assertListEqual(
            bool_vector.load_from_representation('[true]', None),
            [True]
        )
        self.assertListEqual(
            bool_vector.load_from_representation('[true, true]', None),
            [True, True]
        )
        self.assertListEqual(
            bool_vector.load_from_representation('[true  false]', None),
            [True, False]
        )
        self.assertListEqual(
            bool_vector.load_from_representation('[true     false, true]', None),
            [True, False, True]
        )

        IntegerVector = VectorParameter[IntegerParameter]
        with self.assertRaises(RepresentationError):
            IntegerVector.validate_representation('1', None)
        with self.assertRaises(RepresentationError):
            IntegerVector.validate_representation('1, 2', None)
        with self.assertRaises(RepresentationError):
            IntegerVector.validate_representation('[1, hello]', None)
        with self.assertRaises(RepresentationError):
            IntegerVector.validate_representation('[1.0]', None)
        self.assertIsNone(IntegerVector.validate_representation('[1]', None))
        self.assertIsNone(IntegerVector.validate_representation('[1, 2]', None))
        self.assertIsNone(IntegerVector.validate_representation('[1, 3  4]', None))
        self.assertIsNone(IntegerVector.validate_representation('[2*2, 2**3, 2*2 + 2*2]', None))
        integer_vector = IntegerVector('IntegerVector')
        self.assertListEqual(
            integer_vector.load_from_representation('[1]', None),
            [1]
        )
        self.assertListEqual(
            integer_vector.load_from_representation('[1, 2]', None),
            [1, 2]
        )
        self.assertListEqual(
            integer_vector.load_from_representation('[1, 3  4]', None),
            [1, 3, 4]
        )
        self.assertListEqual(
            integer_vector.load_from_representation('[2*2, 2**3, 2*2 + 2*2]', None),
            [4, 8, 8]
        )

        NumberVector = VectorParameter[NumberParameter]
        with self.assertRaises(RepresentationError):
            NumberVector.validate_representation('1.0', None)
        with self.assertRaises(RepresentationError):
            NumberVector.validate_representation('1.0, 2.0', None)
        self.assertIsNone(NumberVector.validate_representation('[1.0, 2.0]', None))
        self.assertIsNone(NumberVector.validate_representation('[np.pi  np.sin(np.pi/2.)]', None))
        number_vector = NumberVector('NumberVector')
        self.assertListEqual(
            number_vector.load_from_representation('[1.0, 2.0]', None),
            [1.0, 2.0]
        )
        self.assertListEqual(
            number_vector.load_from_representation('[np.pi  np.sin(np.pi/2.)]', None),
            [numpy.pi, numpy.sin(numpy.pi / 2.)]
        )

        PhysicalQuantityVector = VectorParameter[PhysicalQuantityParameter]
        physical_quantity_vector = PhysicalQuantityVector('PhysicalQuantityVector', unit='1')
        self.assertListEqual(
            physical_quantity_vector.load_from_representation(
                '[%(pi), %(elementary charge)]',
                {'unit': '1'}
            ),
            [constants.pi, physical_constants['elementary charge'][0]]
        )

        StringVector = VectorParameter[StringParameter]
        string_vector = StringVector('StringVector')
        self.assertListEqual(
            string_vector.load_from_representation('[This, is, a, string.]', None),
            ['This', 'is', 'a', 'string.']
        )

    def test_use_container(self):
        integer_vector = VectorParameter[IntegerParameter]('Integer')
        self.assertIs(integer_vector._container_type, list)
        self.assertListEqual(
            integer_vector.load_from_representation('[1, 2, 3]', None),
            [1, 2, 3]
        )
        return_value = integer_vector.use_container(tuple)
        self.assertIs(integer_vector, return_value)
        self.assertIs(integer_vector._container_type, tuple)
        self.assertTupleEqual(
            integer_vector.load_from_representation('[1, 2, 3]', None),
            (1, 2, 3)
        )
        integer_vector.use_container(numpy.array)
        self.assertIs(integer_vector._container_type, numpy.array)
        vector = integer_vector.load_from_representation('[1, 2, 3]', None)
        self.assertIsInstance(vector, numpy.ndarray)
        self.assertListEqual(vector.tolist(), [1, 2, 3])


# noinspection PyPep8Naming
class TestCaseDupletParameter(unittest.TestCase):
    def test_validate_representation(self):
        IntegerDuplet = DupletParameter[IntegerParameter]
        with self.assertRaises(RepresentationError):
            IntegerDuplet.validate_representation('[1]', None)
        with self.assertRaises(RepresentationError):
            IntegerDuplet.validate_representation('[1, 2, 3]', None)
        with self.assertRaises(RepresentationError):
            IntegerDuplet.validate_representation('[ 1  2  3 ]', None)
        integer_duplet = IntegerDuplet('IntegerDuplet')
        self.assertTupleEqual(
            integer_duplet.load_from_representation('[ 123, 456 ]', None),
            (123, 456)
        )


# noinspection PyPep8Naming
class TestCaseTripletParameter(unittest.TestCase):
    def test_validate_representation(self):
        IntegerTriplet = TripletParameter[IntegerParameter]
        with self.assertRaises(RepresentationError):
            IntegerTriplet.validate_representation('[1]', None)
        with self.assertRaises(RepresentationError):
            IntegerTriplet.validate_representation('[1, 2]', None)
        with self.assertRaises(RepresentationError):
            IntegerTriplet.validate_representation('[ 1  2 ]', None)
        with self.assertRaises(RepresentationError):
            IntegerTriplet.validate_representation('[ 1, 2, 3, 4 ]', None)
        integer_triplet = IntegerTriplet('IntegerTriplet')
        self.assertTupleEqual(
            integer_triplet.load_from_representation('[ 123, 456, 789 ]', None),
            (123, 456, 789)
        )


class TestCasePhysicalQuantityParameter(unittest.TestCase):
    conversion_cases = [
        {
            'text': '1',
            'meta': {'unit': 'm'},
            'converted': Value(1.0, 'm'),
            'loaded': 1.0
        },
        {
            'text': '1e2',
            'meta': {'unit': 'm'},
            'converted': Value(1e2, 'm'),
            'loaded': 1e2
        },
        {
            'text': '2*3e5',
            'meta': {'unit': 'm'},
            'converted': Value(2*3e5, 'm'),
            'loaded': 2*3e5
        },
        {
            'text': '3.0 / 2',
            'meta': {'unit': 'm'},
            'converted': Value(3.0/2, 'm'),
            'loaded': 3.0/2
        },
        {
            'text': '2 * np.pi',
            'meta': {'unit': 'm'},
            'converted': Value(2*numpy.pi, 'm'),
            'loaded': 2*numpy.pi
        },
    ]

    def test_convert_representation(self):
        for case in self.conversion_cases:
            self.assertEqual(PhysicalQuantityParameter.convert_representation(
                case['text'], case['meta']), case['converted'])

        for obj_str in dir(constants):
            obj = getattr(constants, obj_str)
            if not isinstance(obj, float):
                continue
            self.assertEqual(
                PhysicalQuantityParameter.convert_representation(
                    '%({0})'.format(obj_str),
                    {'unit': 'm'}
                ),
                Value(obj, 'm')
            )

        for key in physical_constants:
            self.assertEqual(
                PhysicalQuantityParameter.convert_representation(
                    '%({0})'.format(key),
                    {'unit': 'm'}
                ),
                Value(physical_constants[key][0], 'm')
            )

        # From doc string.
        self.assertEqual(
            PhysicalQuantityParameter.convert_representation('1 * 2 + 3', {'unit': 'm'}).magnitude,
            5.0
        )
        self.assertEqual(
            PhysicalQuantityParameter.convert_representation('np.pi', {'unit': 'm'}).magnitude,
            numpy.pi
        )
        self.assertEqual(
            PhysicalQuantityParameter.convert_representation('%(pi)', {'unit': 'm'}).magnitude,
            constants.pi
        )
        self.assertAlmostEqual(
            PhysicalQuantityParameter.convert_representation(
                '%(electron mass energy equivalent in MeV)*1.0e6 '
                '* %(elementary charge) / %(speed of light in vacuum)**2',
                {'unit': 'kg'}
            ).magnitude,
            physical_constants['electron mass'][0]
        )
        self.assertEqual(PhysicalQuantityParameter.convert_representation(
            '%(electron mass)', {'unit': 'kg'}).magnitude,
            physical_constants['electron mass'][0]
        )

    def test_validate_representation(self):
        with self.assertRaises(RepresentationError):
            PhysicalQuantityParameter.validate_representation(
                'invalid representation', {'unit': 'm'}
            )
        with self.assertRaises(RepresentationError):
            PhysicalQuantityParameter.validate_representation('%e', {'unit': 'm'})
        with self.assertRaises(RepresentationError):
            PhysicalQuantityParameter.validate_representation('1.0', {})
        with self.assertRaises(RepresentationError):
            PhysicalQuantityParameter.validate_representation('1.0', {'unit': ''})

        for obj_str in dir(constants):
            obj = getattr(constants, obj_str)
            if not isinstance(obj, float):
                continue
            self.assertEqual(
                PhysicalQuantityParameter.validate_representation(
                    '%({0})'.format(obj_str),
                    {'unit': 'm'}
                ),
                None
            )

        for key in physical_constants:
            self.assertEqual(
                PhysicalQuantityParameter.validate_representation(
                    '%({0})'.format(key),
                    {'unit': 'm'}
                ),
                None
            )

    def test_load_from_representation_same_unit(self):
        parameter = PhysicalQuantityParameter('', unit='m')
        for case in self.conversion_cases:
            self.assertEqual(
                parameter.load_from_representation(case['text'], case['meta']),
                case['loaded']
            )

    def test_load_from_representation_other_unit(self):
        parameter = PhysicalQuantityParameter('', unit='mm')
        for case in self.conversion_cases:
            conversion_factor = Unit(case['meta']['unit']).conversion_factor('mm')
            self.assertEqual(
                parameter.load_from_representation(case['text'], case['meta']),
                case['loaded'] * conversion_factor
            )

    def test_load_from_representation_no_conversion_rule(self):
        parameters = [
            PhysicalQuantityParameter('', unit='kg'),
            PhysicalQuantityParameter('', unit='s'),
            PhysicalQuantityParameter('', unit='eV'),
            PhysicalQuantityParameter('', unit='C'),
        ]
        for parameter in parameters:
            with self.assertRaises(InvalidUnitError):
                parameter.load_from_representation('1.0', {'unit': 'm'})

    def test_load_from_representation_string_interpolation(self):
        parameter = PhysicalQuantityParameter('', unit='m')

        for obj_str in dir(constants):
            obj = getattr(constants, obj_str)
            if not isinstance(obj, float):
                continue
            self.assertEqual(
                parameter.load_from_representation(
                    '%({0})'.format(obj_str),
                    {'unit': 'm'}
                ),
                obj
            )

        for key in physical_constants:
            self.assertEqual(
                parameter.load_from_representation(
                    '%({0})'.format(key),
                    {'unit': 'm'}
                ),
                physical_constants[key][0]
            )


class TestCaseComplementaryParameterGroup(unittest.TestCase):
    def test_number_of_specification(self):
        def sum_all(*args):
            return sum(args)

        group = ComplementaryParameterGroup(
            'TestGroup',
            (
                IntegerParameter('Integer1'),
                sum_all
            ),
            (
                IntegerParameter('Integer2'),
                sum_all
            ),
            (
                IntegerParameter('Integer3'),
                sum_all
            )
        )

        config = JSONAdaptor(root={})
        with self.assertRaises(IncompleteConfigurationError):
            group.load_from_configuration(config, '')

        config = JSONAdaptor(root={
            'TestGroup': '1',
        })
        with self.assertRaises(IncompleteConfigurationError):
            group.load_from_configuration(config, '')

        config = JSONAdaptor(root={
            'TestGroup/WrongParameter': '1',
        })
        with self.assertRaises(IncompleteConfigurationError):
            group.load_from_configuration(config, '')

        config = JSONAdaptor(root={
            'TestGroup/Integer1': '1',
        })
        with self.assertRaises(RepresentationError):
            group.load_from_configuration(config, '')

        config = JSONAdaptor(root={
            'TestGroup/Integer1': '1',
            'TestGroup/Integer2': '2',
            'TestGroup/Integer3': '3',
        })
        with self.assertRaises(RepresentationError):
            group.load_from_configuration(config, '')

        config = JSONAdaptor(root={
            'TestGroup/Integer1': '1',
            'TestGroup/Integer2': '2',
        })
        self.assertSequenceEqual(
            group.load_from_configuration(config, ''),
            (1, 2, 3)
        )

        config = JSONAdaptor(root={
            'TestGroup/Integer1': '1',
            'TestGroup/Integer3': '3',
        })
        self.assertSequenceEqual(
            group.load_from_configuration(config, ''),
            (1, 4, 3)
        )

        config = JSONAdaptor(root={
            'TestGroup/Integer2': '2',
            'TestGroup/Integer3': '3',
        })
        self.assertSequenceEqual(
            group.load_from_configuration(config, ''),
            (5, 2, 3)
        )

    def test_load_from_representation(self):
        def sum_all(*args):
            return sum(args)

        group = ComplementaryParameterGroup(
            'TestGroup',
            (
                IntegerParameter('Integer1'),
                sum_all
            ),
            (
                IntegerParameter('Integer2'),
                sum_all
            ),
            (
                IntegerParameter('Integer3'),
                sum_all
            )
        )

        with self.assertRaises(RepresentationError):
            group.load_from_representation({
                'Integer1': '1',
            }, {
                'Integer1': None,
            })

        with self.assertRaises(RepresentationError):
            group.load_from_representation({
                'Integer1': '1',
                'Integer2': '2',
                'Integer3': '3',
            }, {
                'Integer1': None,
                'Integer2': None,
                'Integer3': None,
            })

        self.assertSequenceEqual(
            group.load_from_representation({
                'Integer1': '1',
                'Integer2': '2',
            }, {
                'Integer1': None,
                'Integer2': None,
            }),
            (1, 2, 3)
        )

        self.assertSequenceEqual(
            group.load_from_representation({
                'Integer1': '1',
                'Integer3': '3',
            }, {
                'Integer1': None,
                'Integer3': None,
            }),
            (1, 4, 3)
        )

        self.assertSequenceEqual(
            group.load_from_representation({
                'Integer2': '2',
                'Integer3': '3',
            }, {
                'Integer2': None,
                'Integer3': None,
            }),
            (5, 2, 3)
        )


class TestCaseSubstituteParameterGroup(unittest.TestCase):
    def test_load_from_configuration(self):
        def convert_from_string(string):
            return int(re.match(r'integer: (\d)', string).groups()[0])

        def convert_from_number(number):
            return int(number)

        group = SubstitutionParameterGroup(
            IntegerParameter('Integer')
        ).add_option(
            StringParameter('String'), convert_from_string
        ).add_option(
            NumberParameter('Number'), convert_from_number
        )

        config = JSONAdaptor(root={
            'Integer': '1',
        })
        self.assertEqual(
            group.load_from_configuration(config, ''),
            1
        )

        config = JSONAdaptor(root={
            'String': 'integer: 2',
        })
        self.assertEqual(
            group.load_from_configuration(config, ''),
            2
        )

        config = JSONAdaptor(root={
            'Number': '3.14',
        })
        self.assertEqual(
            group.load_from_configuration(config, ''),
            3
        )

        config = JSONAdaptor(root={
            'Integer': '1',
            'String': 'integer: 2',
            'Number': '3.14',
        })
        self.assertEqual(
            group.load_from_configuration(config, ''),
            1
        )


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import six
import unittest
import xml.etree.ElementTree as XMLElementTree

from anna.adaptors import ConfigurationAdaptor as Adaptor
from anna.adaptors import JSONAdaptor, XMLAdaptor
from anna.exceptions import InvalidPathError


class TestCaseAdaptorAuxiliaryMethods(unittest.TestCase):
    def test_element_name_from_indexed_path(self):
        # Examples from docs.
        self.assertEqual(Adaptor.element_name_from_indexed_path('path/to/element'), 'element')
        self.assertEqual(Adaptor.element_name_from_indexed_path('path/to/element[2]'), 'element')
        # Additional cases.
        self.assertEqual(Adaptor.element_name_from_indexed_path('path/to/element[123]'), 'element')

    def test_join_paths(self):
        # Examples from docs.
        self.assertEqual(Adaptor.join_paths('path/to', 'element'), 'path/to/element')
        self.assertEqual(Adaptor.join_paths('path/', 'to/', 'element/'), 'path/to/element')
        self.assertEqual(Adaptor.join_paths('/path/', '/to/', '/element/'), 'path/to/element')

    def test_split_path(self):
        # Examples from docs.
        self.assertListEqual(Adaptor.split_path('path/to/element'), ['path', 'to', 'element'])
        self.assertListEqual(
            Adaptor.split_path('path/to/element', max_number_of_splits=1),
            ['path', 'to/element']
        )

    def test_parse_index_from_element_identifier(self):
        # Examples from docs.
        self.assertEqual(Adaptor._parse_index_from_element_identifier('SomeElement'), None)
        self.assertEqual(Adaptor._parse_index_from_element_identifier('SomeElement[0]'), 0)
        self.assertEqual(Adaptor._parse_index_from_element_identifier('SomeElement[1]'), 1)

    def test_parse_name_from_element_identifier(self):
        # Examples from docs.
        self.assertEqual(
            Adaptor._parse_name_from_element_identifier('SomeElement'),
            'SomeElement'
        )
        self.assertEqual(
            Adaptor._parse_name_from_element_identifier('SomeElement[0]'),
            'SomeElement'
        )
        self.assertEqual(
            Adaptor._parse_name_from_element_identifier('SomeElement[1]'),
            'SomeElement'
        )


class TestCase(unittest.TestCase):
    def create_empty_configuration(self):
        raise NotImplementedError

    def setup_test_element_access(self):
        raise NotImplementedError

    def test_element_access(self):
        config = self.setup_test_element_access()
        self.assertIsInstance(config.get_text('A'), six.text_type)
        self.assertEqual(config.get_text('A'), 'A')
        self.assertEqual(config.get_text('A/B'), 'B')
        self.assertEqual(config.get_text('A/B/C'), 'C')
        self.assertEqual(config.get_text('A[0]'), 'A')
        self.assertEqual(config.get_text('A[0]/B[0]'), 'B')
        self.assertEqual(config.get_text('A[0]/B[0]/C[0]'), 'C')
        self.assertEqual(config.get_meta('A'), {})
        self.assertEqual(config.get_meta('A/B'), {})
        self.assertEqual(config.get_meta('A/B/C'), {})

        # Examples from docs for get_text.
        config = self.create_empty_configuration()
        config.insert_element('A', Adaptor.Element('A', 'a'))
        config.insert_element('A/B', Adaptor.Element('B', 'b'))
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B'), 'b')

        # Examples from docs for get_meta.
        config = self.create_empty_configuration()
        config.insert_element('A', Adaptor.Element('A', meta={'a': 1}))
        config.insert_element('A/B', Adaptor.Element('B', meta={'b': 2}))
        self.assertEqual(config.get_meta('A'), {'a': 1})
        self.assertEqual(config.get_meta('A/B'), {'b': 2})

        # Examples from docs for get_element.
        config = self.create_empty_configuration()
        config.insert_element('A/B', Adaptor.Element('B', text='b', meta={'b': 2}))
        element = config.get_element('A/B')
        self.assertEqual(element.name, 'B')
        self.assertEqual(element.text, 'b')
        self.assertEqual(element.meta['b'], 2)

    def test_get_direct_elements(self):
        # Examples from docs for get_direct_elements.
        config = self.create_empty_configuration()
        config.insert_element('A', Adaptor.Element('A', 'a'))
        config.insert_element('A/B', Adaptor.Element('AB', 'ab'))
        config.insert_element('A/B/C', Adaptor.Element('ABC', 'abc'))
        config.insert_element('B', Adaptor.Element('B', 'b'))
        config.insert_element('A', Adaptor.Element('A', 'a2'))
        elements = config.get_direct_elements()
        self.assertEqual(len(elements), 3)
        # Order of of elements is not necessarily preserved for JSONAdaptor!
        if isinstance(config, XMLAdaptor):
            self.assertEqual(elements[0].name, 'A')
            self.assertEqual(elements[0].text, 'a')
            self.assertEqual(elements[1].name, 'B')
            self.assertEqual(elements[1].text, 'b')
            self.assertEqual(elements[2].name, 'A')
            self.assertEqual(elements[2].text, 'a2')
        elif isinstance(config, JSONAdaptor):
            names = tuple(map(lambda e: e.name, elements))
            texts = tuple(map(lambda e: e.text, elements))
            self.assertIn('A', names)
            self.assertIn('B', names)
            self.assertIn('a', texts)
            self.assertIn('b', texts)
            self.assertIn('a2', texts)

    def setup_test_get_configuration(self):
        raise NotImplementedError

    def test_get_configuration(self):
        config = self.setup_test_get_configuration()

        sub_config = config.get_configuration('A')
        self.assertEqual(sub_config.get_text('B'), 'B')
        self.assertEqual(sub_config.get_text('B/C'), 'C')

        sub_config = config.get_configuration('A[0]')
        self.assertEqual(sub_config.get_text('B'), 'B')
        self.assertEqual(sub_config.get_text('B/C'), 'C')

        # Examples from docs.
        config = self.create_empty_configuration()
        config.insert_element('A/B', Adaptor.Element('B', 'B'))
        config.insert_element('A/B/C', Adaptor.Element('C', 'C'))
        config.insert_element('A/B/C/D', Adaptor.Element('D', 'D'))
        self.assertEqual(config.get_configuration('A/B').get_text('C'), 'C')
        self.assertEqual(config.get_configuration('A/B').get_text('C/D'), 'D')
        config.insert_element('A/B[1]/C/D', Adaptor.Element('D2', 'D2'))
        self.assertEqual(config.get_configuration('A/B').get_text('C'), 'C')
        self.assertEqual(config.get_configuration('A/B').get_text('C/D'), 'D')
        self.assertEqual(config.get_configuration('A/B[1]').get_text('C/D'), 'D2')

    def setup_test_get_sibling_configurations(self):
        raise NotImplementedError

    def test_get_sibling_configurations(self):
        config = self.setup_test_get_sibling_configurations()

        sibling_configs = config.get_sibling_configurations('A/B')
        self.assertEqual(sibling_configs[0].get_text('C'), '0')
        self.assertEqual(sibling_configs[1].get_text('C'), '1')
        self.assertEqual(sibling_configs[2].get_text('C'), '2')

        sibling_configs = config.get_sibling_configurations('A/B[0]')
        self.assertEqual(sibling_configs[0].get_text('C'), '0')
        self.assertEqual(sibling_configs[1].get_text('C'), '1')
        self.assertEqual(sibling_configs[2].get_text('C'), '2')

        # Examples from docs.
        config = self.create_empty_configuration()
        config.insert_element('A/B', Adaptor.Element('B', 'B'))
        config.insert_element('A/B/C', Adaptor.Element('C', 'C'))
        config.insert_element('A/B/C/D', Adaptor.Element('D', 'D'))
        sibling_configurations = config.get_sibling_configurations('A/B')
        self.assertEqual(len(sibling_configurations), 1)
        self.assertEqual(sibling_configurations[0].get_text('C'), 'C')
        self.assertEqual(sibling_configurations[0].get_text('C/D'), 'D')
        config.insert_element('A/B[1]/C/D', Adaptor.Element('D2', 'D2'))
        sibling_configurations = config.get_sibling_configurations('A/B')
        self.assertEqual(len(sibling_configurations), 2)
        self.assertEqual(sibling_configurations[0].get_text('C'), 'C')
        self.assertEqual(sibling_configurations[0].get_text('C/D'), 'D')
        self.assertEqual(sibling_configurations[1].get_text('C/D'), 'D2')

    def setup_test_get_sub_configurations(self):
        raise NotImplementedError

    def test_get_sub_configurations(self):
        config = self.setup_test_get_sub_configurations()

        sub_configs = config.get_sub_configurations('A')
        self.assertEqual(sub_configs[0].get_text('C'), '0')
        self.assertEqual(sub_configs[1].get_text('C'), '1')
        self.assertEqual(sub_configs[2].get_text('C'), '2')

        sub_configs = config.get_sub_configurations('A[0]')
        self.assertEqual(sub_configs[0].get_text('C'), '0')
        self.assertEqual(sub_configs[1].get_text('C'), '1')
        self.assertEqual(sub_configs[2].get_text('C'), '2')

        # Examples from docs.
        config = self.create_empty_configuration()
        config.insert_element('A/B', Adaptor.Element('B', 'B'))
        config.insert_element('A/B/C', Adaptor.Element('C', 'C'))
        config.insert_element('A/B/C/D', Adaptor.Element('D', 'D'))
        sub_configurations = config.get_sub_configurations('A')
        self.assertEqual(len(sub_configurations), 1)
        self.assertEqual(sub_configurations[0].get_text('C'), 'C')
        self.assertEqual(sub_configurations[0].get_text('C/D'), 'D')
        config.insert_element('A/B[1]/C/D', Adaptor.Element('D2', 'D2'))
        sub_configurations = config.get_sub_configurations('A')
        self.assertEqual(len(sub_configurations), 2)
        self.assertEqual(sub_configurations[0].get_text('C'), 'C')
        self.assertEqual(sub_configurations[0].get_text('C/D'), 'D')
        self.assertEqual(sub_configurations[1].get_text('C/D'), 'D2')

    def test_insert_element(self):
        # Examples from docs for insert_element.
        config = self.create_empty_configuration()
        config.insert_element('A', 'a')
        self.assertEqual(config.get_text('A'), 'a')
        config.insert_element('A/B/C', 'c', some_attribute='Some helpful information')
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B/C'), 'c')
        self.assertEqual(config.get_meta('A/B/C'), {'some_attribute': 'Some helpful information'})
        config.insert_element('A/B/C', 'c2')
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B/C'), 'c')
        self.assertEqual(config.get_text('A/B/C[0]'), 'c')
        self.assertEqual(config.get_text('A/B/C[1]'), 'c2')
        config.insert_element('A/B/C[1]', 'replaced', replace=True)
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B/C'), 'c')
        self.assertEqual(config.get_text('A/B/C[0]'), 'c')
        self.assertEqual(config.get_text('A/B/C[1]'), 'replaced')
        config.insert_element('A/B/C[2]', 'c2')
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B/C'), 'c')
        self.assertEqual(config.get_text('A/B/C[0]'), 'c')
        self.assertEqual(config.get_text('A/B/C[1]'), 'replaced')
        self.assertEqual(config.get_text('A/B/C[2]'), 'c2')
        config.insert_element('A/B/C[100]', 'c3')
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B/C'), 'c')
        self.assertEqual(config.get_text('A/B/C[0]'), 'c')
        self.assertEqual(config.get_text('A/B/C[1]'), 'replaced')
        self.assertEqual(config.get_text('A/B/C[2]'), 'c2')
        self.assertEqual(config.get_text('A/B/C[3]'), 'c3')
        config.insert_element('A[1]/B[1]/C[1]', 'many indices')
        self.assertEqual(config.get_text('A'), 'a')
        self.assertEqual(config.get_text('A/B/C'), 'c')
        self.assertEqual(config.get_text('A/B/C[0]'), 'c')
        self.assertEqual(config.get_text('A/B/C[1]'), 'replaced')
        self.assertEqual(config.get_text('A/B/C[2]'), 'c2')
        self.assertEqual(config.get_text('A/B/C[3]'), 'c3')
        self.assertEqual(config.get_text('A[1]/B/C'), 'many indices')
        self.assertEqual(config.get_text('A[1]/B[0]/C[0]'), 'many indices')

    def test_insert_element_no_index(self):
        config = self.create_empty_configuration()

        config.insert_element('A', Adaptor.Element('A', 'A'))
        self.assertEqual(config.get_text('A'), 'A')

        config.insert_element('A/B', Adaptor.Element('B', 'B'))
        self.assertEqual(config.get_text('A/B'), 'B')

        config.insert_element('A/B/C', Adaptor.Element('C', 'C'))
        self.assertEqual(config.get_text('A/B/C'), 'C')

        config.insert_element('A/B/C', Adaptor.Element('C2', 'C2'))
        self.assertEqual(config.get_text('A/B/C'), 'C')

    def test_insert_element_indexed(self):
        config = self.create_empty_configuration()

        config.insert_element('A', Adaptor.Element('A', 'A'))
        self.assertEqual(config.get_text('A[0]'), 'A')

        config.insert_element('A/B', Adaptor.Element('B', 'B'))
        self.assertEqual(config.get_text('A[0]/B'), 'B')
        self.assertEqual(config.get_text('A/B[0]'), 'B')
        self.assertEqual(config.get_text('A[0]/B[0]'), 'B')

        config.insert_element('A/B/C', Adaptor.Element('C', 'C'))
        config.insert_element('A/B/C', Adaptor.Element('C2', 'C2'))
        self.assertEqual(config.get_text('A/B/C[0]'), 'C')
        self.assertEqual(config.get_text('A/B/C[1]'), 'C2')
        with self.assertRaises(InvalidPathError):
            config.get_text('A/B/C[2]')
        with self.assertRaises(InvalidPathError):
            config.get_text('A[1]/B/C')
        config.insert_element('A[0]/B/C/D', Adaptor.Element('A0D0', 'A0D0'))
        config.insert_element('A[1]/B/C/D', Adaptor.Element('A1D0', 'A1D0'))
        config.insert_element('A[2]/B/C/D', Adaptor.Element('A2D0', 'A2D0'))
        config.insert_element('A/B/C/D', Adaptor.Element('A0D1', 'A0D1'))
        self.assertEqual(config.get_text('A[0]/B/C/D'), 'A0D0')
        self.assertEqual(config.get_text('A[0]/B/C/D[0]'), 'A0D0')
        self.assertEqual(config.get_text('A[0]/B/C/D[1]'), 'A0D1')
        self.assertEqual(config.get_text('A[1]/B/C/D'), 'A1D0')
        self.assertEqual(config.get_text('A[2]/B/C/D'), 'A2D0')
        with self.assertRaises(InvalidPathError):
            config.get_text('A[3]/B/C/D')
        with self.assertRaises(InvalidPathError):
            config.get_text('A[4]/B/C')

        config.insert_element('A/B[2]/C/D/E', Adaptor.Element('E1', 'E1'))
        with self.assertRaises(InvalidPathError):
            config.get_text('A/B[2]/C/D/E')
        self.assertEqual(config.get_text('A/B[1]/C/D/E'), 'E1')
        config.insert_element('A/B[0]/C/D/E', Adaptor.Element('E0', 'E0'))
        with self.assertRaises(InvalidPathError):
            config.get_text('A/B[2]/C/D/E')
        self.assertEqual(config.get_text('A/B[0]/C/D/E'), 'E0')

        config.insert_element('A/B/C/D/E/F[0]', Adaptor.Element('F0', 'F0'))
        config.insert_element('A/B/C/D/E/F[2]', Adaptor.Element('F1', 'F1'))
        config.insert_element('A/B/C/D/E/F[2]', Adaptor.Element('F2', 'F2'))
        self.assertEqual(config.get_text('A/B/C/D/E/F[0]'), 'F0')
        self.assertEqual(config.get_text('A/B/C/D/E/F[1]'), 'F1')
        self.assertEqual(config.get_text('A/B/C/D/E/F[2]'), 'F2')

        config.insert_element('A/B/C/D[1]/E/F[0]', Adaptor.Element('D1F0', 'D1F0'))
        config.insert_element('A/B/C/D[1]/E/F[1]', Adaptor.Element('D1F1', 'D1F1'))
        self.assertEqual(config.get_text('A/B/C/D[1]/E/F[0]'), 'D1F0')
        self.assertEqual(config.get_text('A/B/C/D[1]/E/F[1]'), 'D1F1')

        config = self.create_empty_configuration()
        config.insert_element('Path', 'path')
        config.insert_element('Path/To', 'path_to')
        config.insert_element('Path/To/Element', 'path_to_element')
        config.insert_element('Path/To', 'replaced', replace=False)
        self.assertEqual(config.get_text('Path'), 'path')
        self.assertEqual(config.get_text('Path/To'), 'path_to')
        self.assertEqual(config.get_text('Path/To[0]'), 'path_to')
        self.assertEqual(config.get_text('Path/To[1]'), 'replaced')
        self.assertEqual(config.get_text('Path/To/Element'), 'path_to_element')

    def test_insert_element_replace(self):
        config = self.create_empty_configuration()
        config.insert_element('A/B/C', Adaptor.Element('C0', 'C0'))
        self.assertEqual(config.get_text('A/B/C'), 'C0')
        config.insert_element('A/B/C', Adaptor.Element('CR', 'CR'), replace=True)
        self.assertEqual(config.get_text('A/B/C'), 'CR')
        config.insert_element('A/B/C', Adaptor.Element('C1', 'C1'))
        self.assertEqual(config.get_text('A/B/C'), 'CR')
        self.assertEqual(config.get_text('A[0]/B/C'), 'CR')
        self.assertEqual(config.get_text('A/B/C[1]'), 'C1')
        config.insert_element('A/B/C[1]', Adaptor.Element('C1R', 'C1R'), replace=True)
        self.assertEqual(config.get_text('A/B/C[1]'), 'C1R')

        config = self.create_empty_configuration()
        config.insert_element('Path', 'path')
        config.insert_element('Path/To', 'path_to')
        config.insert_element('Path/To/Element', 'path_to_element')
        config.insert_element('Path/To', 'replaced', replace=True)
        self.assertEqual(config.get_text('Path'), 'path')
        self.assertEqual(config.get_text('Path/To'), 'replaced')
        self.assertEqual(config.get_text('Path/To/Element'), 'path_to_element')

    def test_insert_config(self):
        config = self.create_empty_configuration()
        other = self.create_empty_configuration()

        other.insert_element('A', Adaptor.Element('A', 'A'))
        other.insert_element('A/B', Adaptor.Element('B', 'B'))
        other.insert_element('A/B/C', Adaptor.Element('C', 'C'))

        config.insert_config('a', other)
        self.assertEqual(config.get_text('a/A'), 'A')
        self.assertEqual(config.get_text('a/A/B'), 'B')
        self.assertEqual(config.get_text('a/A/B/C'), 'C')

        config.insert_config('a/b', other)
        self.assertEqual(config.get_text('a/b/A'), 'A')
        self.assertEqual(config.get_text('a/b/A/B'), 'B')
        self.assertEqual(config.get_text('a/b/A/B/C'), 'C')

        # Examples from docs for extend_at.
        config = self.create_empty_configuration()
        config.insert_element('A', Adaptor.Element('A', 'a'))
        config.insert_element('A/B/C', Adaptor.Element('C', 'c'))
        extended_config = self.create_empty_configuration().insert_config('X/Y/Z', config)
        self.assertEqual(extended_config.get_text('X/Y/Z/A'), 'a')
        self.assertEqual(extended_config.get_text('X/Y/Z/A/B/C'), 'c')

        other_config = self.create_empty_configuration()
        other_config.insert_element('A/D/E', 'e')
        extended_config = config.insert_config('', other_config)
        self.assertEqual(extended_config.get_text('A/D/E'), 'e')
        other_config.insert_element('A/D/E', 'e replaced', replace=True)
        extended_config = extended_config.insert_config('', other_config, replace=True)
        self.assertEqual(extended_config.get_text('A/D/E'), 'e replaced')
        with self.assertRaises(InvalidPathError):
            extended_config.get_text('A/D/E[1]')
        extended_config = extended_config.insert_config('', other_config)
        self.assertEqual(extended_config.get_text('A/D/E[1]'), 'e replaced')

    def test_insert_config_replacements(self):
        config = self.create_empty_configuration()
        other = self.create_empty_configuration()
        config.insert_element('Path', 'path')
        config.insert_element('Path/To', 'path_to')
        config.insert_element('Path/To/Element', 'path_to_element')
        other.insert_element('Path/To', 'path_to_replaced')
        config.insert_config('', other, replace=True)
        self.assertEqual(config.get_text('Path'), 'path')
        self.assertEqual(config.get_text('Path/To'), 'path_to_replaced')
        self.assertEqual(config.get_text('Path/To/Element'), 'path_to_element')

    def test_insert_config_no_replacements(self):
        config = self.create_empty_configuration()
        other = self.create_empty_configuration()
        config.insert_element('Path', 'path')
        config.insert_element('Path/To', 'path_to')
        config.insert_element('Path/To/Element', 'path_to_element')
        other.insert_element('Path/To', 'path_to_replaced')
        config.insert_config('', other)
        self.assertEqual(config.get_text('Path'), 'path')
        self.assertEqual(config.get_text('Path/To[0]'), 'path_to')
        self.assertEqual(config.get_text('Path/To[1]'), 'path_to_replaced')
        self.assertEqual(config.get_text('Path/To/Element'), 'path_to_element')


class TestCaseJSONAdaptor(TestCase):
    ADAPTOR = JSONAdaptor

    def create_empty_configuration(self):
        return self.ADAPTOR()

    def setup_test_element_access(self):
        return self.ADAPTOR(root={
            'A': {'text': 'A', 'meta': {}},
            'A/B': {'text': 'B', 'meta': {}},
            'A/B/C': {'text': 'C', 'meta': {}},
        })

    def setup_test_get_configuration(self):
        return self.ADAPTOR(root={
            'A': {'text': 'A', 'meta': {}},
            'A/B': {'text': 'B', 'meta': {}},
            'A/B/C': {'text': 'C', 'meta': {}},
        })

    def setup_test_get_sibling_configurations(self):
        return self.ADAPTOR(root={
            'A/B/C': {'text': '0', 'meta': {}},
            'A/B__1/C': {'text': '1', 'meta': {}},
            'A/B__2/C': {'text': '2', 'meta': {}},
        })

    def setup_test_get_sub_configurations(self):
        return self.ADAPTOR(root={
            'A/B/C': {'text': '0', 'meta': {}},
            'A/B__1/C': {'text': '1', 'meta': {}},
            'A/B__2/C': {'text': '2', 'meta': {}},
        })


class TestCaseJSONAdaptorAuxiliaryMethods(unittest.TestCase):
    def test_gradually_check_and_adjust_path_indices(self):
        config = JSONAdaptor(root={
            'A': {'text': 'A', 'meta': {}},
            'A/B': {'text': 'B', 'meta': {}},
            'A/B/C': {'text': 'C', 'meta': {}},
        })
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A[0]/B/C'), 'A/B/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A[1]/B/C'), 'A[1]/B/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A[2]/B/C'), 'A[1]/B/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A/B[0]/C'), 'A/B/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A/B[1]/C'), 'A/B[1]/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A/B[2]/C'), 'A/B[1]/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A/B/C[0]'), 'A/B/C')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A/B/C[1]'), 'A/B/C[1]')
        self.assertEqual(config._gradually_check_and_adjust_path_indices('A/B/C[2]'), 'A/B/C[1]')
        self.assertEqual(
            config._gradually_check_and_adjust_path_indices('A[0]/B[1]/C[2]'),
            'A/B[1]/C'
        )
        self.assertEqual(
            config._gradually_check_and_adjust_path_indices('A[1]/B[1]/C[1]'),
            'A[1]/B/C'
        )
        self.assertEqual(
            config._gradually_check_and_adjust_path_indices('A[2]/B[2]/C[2]'),
            'A[1]/B/C'
        )


class TestCaseXMLAdaptor(TestCase):
    ADAPTOR = XMLAdaptor

    def create_empty_configuration(self):
        return self.ADAPTOR()

    def setup_test_element_access(self):
        return self.ADAPTOR(root=XMLElementTree.fromstring(
            """<Root><A>A<B>B<C>C</C></B></A></Root>"""
        ))

    def setup_test_get_configuration(self):
        return self.ADAPTOR(root=XMLElementTree.fromstring(
            """<Root><A>A<B>B<C>C</C></B></A></Root>"""
        ))

    def setup_test_get_sibling_configurations(self):
        return self.ADAPTOR(root=XMLElementTree.fromstring(
            """<Root><A><B><C>0</C></B><B><C>1</C></B><B><C>2</C></B></A></Root>"""
        ))

    def setup_test_get_sub_configurations(self):
        return self.ADAPTOR(root=XMLElementTree.fromstring(
            """<Root><A><B><C>0</C></B><B><C>1</C></B><B><C>2</C></B></A></Root>"""
        ))


class TestCaseXMLAdaptorAuxiliaryMethods(unittest.TestCase):
    def test_find_all_leaf_elements(self):
        root = XMLElementTree.Element('Root')
        a = XMLElementTree.Element('A')
        a_b = XMLElementTree.Element('AB')
        a.append(a_b)
        root.append(a)
        b = XMLElementTree.Element('B')
        root.append(b)
        leafs = XMLAdaptor._find_all_leaf_elements(root)
        self.assertEqual(len(leafs), 2)
        self.assertSequenceEqual(tuple(zip(*leafs))[0], ('A/AB', 'B'))
        self.assertSequenceEqual(tuple(map(lambda x: x.tag, tuple(zip(*leafs))[1])), ('AB', 'B'))
        self.assertIs(leafs[0][1], a_b)
        self.assertIs(leafs[1][1], b)
        leafs = XMLAdaptor._find_all_leaf_elements(a)
        self.assertEqual(len(leafs), 1)
        self.assertSequenceEqual(leafs[0], ('AB', a_b))
        leafs = XMLAdaptor._find_all_leaf_elements(b)
        self.assertEqual(len(leafs), 1)
        self.assertSequenceEqual(leafs[0], ('', b))

    def test_find_all_relevant_elements(self):
        root = XMLElementTree.Element('Root')
        a = XMLElementTree.Element('A')
        a.text = 'a'
        a_b = XMLElementTree.Element('AB')
        a_b_c = XMLElementTree.Element('ABC')
        a_b_c.text = 'abc'
        a_b.append(a_b_c)
        a.append(a_b)
        root.append(a)
        b = XMLElementTree.Element('B')
        b.text = 'b'
        root.append(b)
        relevant_elements = XMLAdaptor._find_all_relevant_elements(root)
        self.assertEqual(len(relevant_elements), 3)
        self.assertSequenceEqual(
            tuple(zip(*relevant_elements))[0],
            ('A[0]', 'A[0]/AB[0]/ABC[0]', 'B[0]')
        )
        self.assertSequenceEqual(
            tuple(map(lambda x: x.tag, tuple(zip(*relevant_elements))[1])),
            ('A', 'ABC', 'B')
        )
        self.assertIs(relevant_elements[0][1], a)
        self.assertIs(relevant_elements[1][1], a_b_c)
        self.assertIs(relevant_elements[2][1], b)
        relevant_elements = XMLAdaptor._find_all_relevant_elements(a)
        self.assertEqual(len(relevant_elements), 2)
        self.assertSequenceEqual(tuple(zip(*relevant_elements))[0], ('', 'AB[0]/ABC[0]'))
        self.assertSequenceEqual(
            tuple(map(lambda x: x.tag, tuple(zip(*relevant_elements))[1])),
            ('A', 'ABC')
        )
        self.assertIs(relevant_elements[0][1], a)
        self.assertIs(relevant_elements[1][1], a_b_c)


if __name__ == '__main__':
    unittest.main()

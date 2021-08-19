#*****************************************************************#
# (C) Copyright IBM Corporation 2020.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
'''Test the methods of the AttributeAccessDict class.
'''

import unittest

import aconfig

from . import fixtures


# Unit tests #######################################################################################


class TestAttributeAccessDict(unittest.TestCase):
    '''Test methods of AttributeAccessDict class.
    '''
    def test__init__pass(self):
        '''Test that initialization will pass with valid dict's.
        '''
        flat_dict = aconfig.AttributeAccessDict(fixtures.GOOD_FLAT_DICT)
        self.assertIsInstance(flat_dict, aconfig.AttributeAccessDict)

        nested_dict = aconfig.AttributeAccessDict(fixtures.GOOD_NESTED_DICT)
        self.assertIsInstance(nested_dict, aconfig.AttributeAccessDict)

    def test__init__fail(self):
        '''Test that initialization will fail with invalid dict's.
        '''
        with self.assertRaises(AssertionError) as ex:
            bad_dict = aconfig.AttributeAccessDict(['a', 'list', 'of', 'strings'])

        raised_exception = ex.exception
        self.assertIsInstance(raised_exception, AssertionError)

        # make sure bad_dict was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_dict', None), None)

    def test__getattr__pass(self):
        '''Test that __getattr__ passes.
        '''
        flat_dict = aconfig.AttributeAccessDict(fixtures.GOOD_FLAT_DICT)

        # get all known keys; implicitly tests type too
        self.assertEqual(flat_dict.__getattr__('none_key'), None)
        self.assertEqual(flat_dict.__getattr__('int_key'), 1)
        self.assertEqual(flat_dict.__getattr__('str_key'), 'string')
        self.assertEqual(flat_dict.__getattr__('float_key'), 3.14)
        self.assertEqual(flat_dict.__getattr__('list_key'), [0, 1, 2, 3])

        # get some unknown keys
        self.assertEqual(flat_dict.__getattr__('bad_key1'), None)
        self.assertEqual(flat_dict.__getattr__('bad_key2', None), None)
        self.assertEqual(flat_dict.__getattr__('bad_key3', 'default'), 'default')
        self.assertEqual(flat_dict.__getattr__('bad_key4', 1234), 1234)

        nested_dict = aconfig.AttributeAccessDict(fixtures.GOOD_NESTED_DICT)
        # get all known keys; implicitly tests type too
        self.assertEqual(nested_dict.__getattr__('key1'), fixtures.GOOD_NESTED_DICT['key1'])
        self.assertEqual(nested_dict.__getattr__('key2'), fixtures.GOOD_NESTED_DICT['key2'])
        self.assertEqual(nested_dict.__getattr__('list_key'), [0, 1, 2, 3])
        self.assertEqual(
            nested_dict.__getattr__('key1').__getattr__('key3'),
            fixtures.GOOD_NESTED_DICT['key1']['key3'])
        self.assertEqual(
            nested_dict.__getattr__('key2').__getattr__('key4'),
            fixtures.GOOD_NESTED_DICT['key2']['key4'])
        self.assertEqual(
            nested_dict.__getattr__('key1').__getattr__('key3').__getattr__('none_key'), None)
        self.assertEqual(
            nested_dict.__getattr__('key1').__getattr__('key3').__getattr__('int_key'), 1)
        self.assertEqual(
            nested_dict.__getattr__('key2').__getattr__('key4').__getattr__('key5'),
            fixtures.GOOD_NESTED_DICT['key2']['key4']['key5'])
        self.assertEqual(
            nested_dict.__getattr__('key2').__getattr__('key4').__getattr__('float_key'), 3.14)
        self.assertEqual(
            nested_dict.__getattr__(
                'key2').__getattr__('key4').__getattr__('key5').__getattr__('str_key'), 'string')

        # get some unknown keys
        self.assertEqual(nested_dict.__getattr__('bad_key1'), None)
        self.assertEqual(nested_dict.__getattr__('bad_key2', None), None)
        self.assertEqual(nested_dict.__getattr__('bad_key3', 'default'), 'default')
        self.assertEqual(nested_dict.__getattr__('bad_key4', 1234), 1234)
        self.assertEqual(nested_dict.__getattr__('key1').__getattr__('bad_key1'), None)
        self.assertEqual(nested_dict.__getattr__('key2').__getattr__('bad_key2', None), None)
        self.assertEqual(
            nested_dict.__getattr__('key1').__getattr__('bad_key3', 'default'), 'default')
        self.assertEqual(
            nested_dict.__getattr__('key2').__getattr__('bad_key4', 1234), 1234)

    def test__setattr__pass(self):
        '''Test that __setattr__ passes.
        '''
        new_access_dict = aconfig.AttributeAccessDict({})

        # assign 2 new attributes; one is nested
        new_access_dict.__setattr__('int_key', 1)
        new_access_dict.__setattr__('key1', {'key2': {'float_key': 3.14}})

        # test it assigned correctly!
        self.assertEqual(new_access_dict.int_key, 1)
        self.assertEqual(new_access_dict['int_key'], 1)
        self.assertEqual(new_access_dict.key1, {'key2': {'float_key': 3.14}})
        self.assertEqual(new_access_dict['key1'], {'key2': {'float_key': 3.14}})
        self.assertEqual(new_access_dict.key1['key2'], {'float_key': 3.14})
        self.assertEqual(new_access_dict['key1'].key2, {'float_key': 3.14})
        self.assertEqual(new_access_dict.key1['key2'].float_key, 3.14)
        self.assertEqual(new_access_dict['key1'].key2['float_key'], 3.14)

    def test__delattr__pass(self):
        '''Test that __delattr__ passes.
        '''
        # copies internally; won't mess up other tests
        new_access_dict = aconfig.AttributeAccessDict(fixtures.GOOD_NESTED_DICT)

        # get rid of some attributes; one is nested
        new_access_dict.__delattr__('key1')
        new_access_dict.key2.key4.__delattr__('key5')

        # see if values are gone, but the rest are the existent
        self.assertNotIn('key1', new_access_dict)
        self.assertNotIn('key5', new_access_dict.key2.key4)
        self.assertEqual(new_access_dict.get('key1'), None)
        self.assertEqual(new_access_dict.key2.key4.key5, None)
        self.assertEqual(new_access_dict.list_key, [0, 1, 2, 3])
        self.assertEqual(new_access_dict.key2.key4.float_key, 3.14)

    def test_get_pass(self):
        '''Test that get passes.
        '''
        # copies internally; won't mess up other tests
        nested_dict = aconfig.AttributeAccessDict(fixtures.GOOD_NESTED_DICT)

        # get all known keys; implicitly tests type too
        self.assertEqual(nested_dict.get('key1'), fixtures.GOOD_NESTED_DICT['key1'])
        self.assertEqual(nested_dict.get('key2'), fixtures.GOOD_NESTED_DICT['key2'])
        self.assertEqual(nested_dict.get('list_key'), [0, 1, 2, 3])
        self.assertEqual(
            nested_dict.get('key1').get('key3'), fixtures.GOOD_NESTED_DICT['key1']['key3'])
        self.assertEqual(
            nested_dict.get('key2').get('key4'), fixtures.GOOD_NESTED_DICT['key2']['key4'])
        self.assertEqual(nested_dict.get('key1').get('key3').get('none_key'), None)
        self.assertEqual(nested_dict.get('key1').get('key3').get('int_key'), 1)
        self.assertEqual(
            nested_dict.get('key2').get('key4').get('key5'),
            fixtures.GOOD_NESTED_DICT['key2']['key4']['key5'])
        self.assertEqual(nested_dict.get('key2').get('key4').get('float_key'), 3.14)
        self.assertEqual(nested_dict.get('key2').get('key4').get('key5').get('str_key'), 'string')

        # get some unknown keys
        self.assertEqual(nested_dict.get('bad_key1'), None)
        self.assertEqual(nested_dict.get('bad_key2', None), None)
        self.assertEqual(nested_dict.get('bad_key3', 'default'), 'default')
        self.assertEqual(nested_dict.get('bad_key4', 1234), 1234)
        self.assertEqual(nested_dict.get('key1').get('bad_key1'), None)
        self.assertEqual(nested_dict.get('key2').get('bad_key2', None), None)
        self.assertEqual(nested_dict.get('key1').get('bad_key3', 'default'), 'default')
        self.assertEqual(nested_dict.get('key2').get('bad_key4', 1234), 1234)

    def test__setitem__pass(self):
        '''Test that __setitem__ passes.
        '''
        new_access_dict = aconfig.AttributeAccessDict({})

        # assign 2 new attributes; one is nested
        new_access_dict.__setitem__('int_key', 1)
        new_access_dict.__setitem__('key1', {'key2': {'float_key': 3.14}})

        # test it assigned correctly!
        self.assertEqual(new_access_dict.int_key, 1)
        self.assertEqual(new_access_dict['int_key'], 1)
        self.assertEqual(new_access_dict.key1, {'key2': {'float_key': 3.14}})
        self.assertEqual(new_access_dict['key1'], {'key2': {'float_key': 3.14}})
        self.assertEqual(new_access_dict.key1['key2'], {'float_key': 3.14})
        self.assertEqual(new_access_dict['key1'].key2, {'float_key': 3.14})
        self.assertEqual(new_access_dict.key1['key2'].float_key, 3.14)
        self.assertEqual(new_access_dict['key1'].key2['float_key'], 3.14)

    def test__delitem__pass(self):
        '''Test that __delitem__ passes.
        '''
        # copies internally; won't mess up other tests
        new_access_dict = aconfig.AttributeAccessDict(fixtures.GOOD_NESTED_DICT)

        # get rid of some attributes; one is nested
        new_access_dict.__delitem__('key1')
        new_access_dict.key2.key4.__delitem__('key5')

        # see if values are gone, but the rest are the existent
        self.assertNotIn('key1', new_access_dict)
        self.assertNotIn('key5', new_access_dict.key2.key4)
        self.assertEqual(new_access_dict.get('key1'), None)
        self.assertEqual(new_access_dict.key2.key4.key5, None)
        self.assertEqual(new_access_dict.list_key, [0, 1, 2, 3])
        self.assertEqual(new_access_dict.key2.key4.float_key, 3.14)

    def test_builtin_method(self):
        d = {'update': True}
        aad = aconfig.AttributeAccessDict(d)

        self.assertNotEqual(aad.update, None)
        self.assertEqual(aad['update'], True)

        del aad['update']

        self.assertNotEqual(aad.update, None)
        self.assertNotIn('update', aad)

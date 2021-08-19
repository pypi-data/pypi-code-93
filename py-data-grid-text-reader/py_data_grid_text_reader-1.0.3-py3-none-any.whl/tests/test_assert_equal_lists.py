# Copyright 2021 The Data Text Grid Reader Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime

from pytest import raises

from data_grid_text_reader.assert_equal_lists import assert_equal


def test_assert_equal_when_lists_are_equal():
    input_list = [
        {
            'a': '1a',  # str
            'b': 2,  # int
            'c': 3.3,  # float
            'd': datetime(2021, 1, 1),  # datetime
            'd': True,  # bool
            'e': None,  # NoneType
        },
        {
            'a': '2a',
        },
        {},
    ]
    # No error or assertion failure should be thrown:
    assert_equal(input_list, input_list)


def test_assert_equal_when_actual_list_has_different_value():
    list_1 = [
        {
            'a': '1a',
            'b': '1b',
        },
    ]
    list_2 = [
        {
            'a': '1a',
            'b': '1b mismatch',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert str(exception_info.value).startswith('Expected list element 1')


def test_assert_equal_when_element_order_is_different():
    list_1 = [
        {
            'a': '1a',
            'b': '1b',
        },
    ]
    list_2 = [
        {
            'b': '1b',
            'a': '1a',
        },
    ]
    # No error or assertion failure should be thrown:
    assert_equal(list_1, list_2)


def test_assert_equal_when_lists_are_empty():
    # No error or assertion failure should be thrown:
    assert_equal({}, {})


def test_assert_equal_when_lists_are_none():
    # No error or assertion failure should be thrown:
    assert_equal(None, None)


def test_assert_equal_when_actual_list_has_too_few_rows():
    list_1 = [
        {
            'a': '1a',
        },
        {
            'a': '2a',
        },
    ]
    list_2 = [
        {
            'a': '1a',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert ('Expected list contains 2 elements, but actual list contains 1 element.'
            == str(exception_info.value))


def test_assert_equal_when_actual_list_has_too_many_rows():
    list_1 = [
        {
            'a': '1a',
        },
    ]
    list_2 = [
        {
            'a': '1a',
        },
        {
            'a': '2a',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert ('Expected list contains 1 element, but actual list contains 2 elements.'
            == str(exception_info.value))


def test_assert_equal_when_actual_list_has_duplicate_element():
    list_1 = [
        {
            'a': '1a',
        },
    ]
    list_2 = [
        {
            'a': '1a',
            'a': '1a',
        },
    ]
    # No error or assertion failure should be thrown:
    assert_equal(list_1, list_2)


def test_assert_equal_when_actual_list_has_too_few_elements():
    list_1 = [
        {
            'a': '1a',
            'b': '1b',
        },
    ]
    list_2 = [
        {
            'a': '1a',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert str(exception_info.value).startswith('Expected list element 1')


def test_assert_equal_when_actual_list_has_too_many_elements():
    list_1 = [
        {
            'a': '1a',
        },
    ]
    list_2 = [
        {
            'a': '1a',
            'b': '1b',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert str(exception_info.value).startswith('Expected list element 1')


def test_assert_equal_when_elements_names_do_not_match():
    list_1 = [
        {
            'a': '1a',
        },
    ]
    list_2 = [
        {
            'b': '1a',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert str(exception_info.value).startswith('Expected list element 1')


def test_assert_equal_when_data_types_do_not_match():
    list_1 = [
        {
            'a': 1,
        },
    ]
    list_2 = [
        {
            'b': '1',
        },
    ]
    with raises(AssertionError) as exception_info:
        assert_equal(list_1, list_2)
    assert str(exception_info.value).startswith('Expected list element 1')


def test_assert_equal_when_actual_list_is_none():
    with raises(AssertionError) as exception_info:
        assert_equal([], None)
    assert 'Expected list is not None and actual list is None.' \
           == str(exception_info.value)


def test_assert_equal_when_expected_list_is_none():
    with raises(AssertionError) as exception_info:
        assert_equal(None, [])
    assert 'Expected list is None and actual list is not None.' \
           == str(exception_info.value)


def test_assert_equal_when_both_lists_are_none():
    # No error or assertion failure should be thrown:
    assert_equal(None, None)

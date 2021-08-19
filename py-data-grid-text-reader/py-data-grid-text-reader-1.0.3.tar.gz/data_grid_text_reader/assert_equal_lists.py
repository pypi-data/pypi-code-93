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
from typing import Optional

# Dummy datetime instance to use when a test just needs a non-null datetime.
# This doesn't save many characters, but hopefully helps communicate the
# intention of the value:
DUMMY_DATETIME = datetime.min


def assert_equal(
        expected_list: list,
        actual_list: list,
        keys_to_check_for_none_only: Optional[list] = []
):
    if expected_list is None and actual_list is None:
        return
    if expected_list is None and actual_list is not None:
        raise AssertionError('Expected list is None and actual list is not None.')
    if expected_list is not None and actual_list is None:
        raise AssertionError('Expected list is not None and actual list is None.')
    expected_list_count = len(expected_list)
    actual_list_count = len(actual_list)
    if expected_list_count != actual_list_count:
        raise AssertionError(f'Expected list contains {expected_list_count}'
                             f' {_get_element_text(expected_list_count)},'
                             f' but actual list contains {actual_list_count}'
                             f' {_get_element_text(actual_list_count)}.')

    non_null_value = '[non-null value]'
    for i, expected_dict in enumerate(expected_list):
        actual_dict = actual_list[i]
        if keys_to_check_for_none_only:
            for field in keys_to_check_for_none_only:
                if expected_dict[field] is not None:
                    expected_dict[field] = non_null_value
                    actual_dict[field] = non_null_value
        if expected_dict != actual_dict:
            raise AssertionError(
                f'Expected list element {i + 1}:\n{expected_dict}\n'
                + f'Differs from actual list element {i + 1}:\n{actual_dict}'
            )


def _get_element_text(count: int) -> str:
    return 'element' if count == 1 else 'elements'

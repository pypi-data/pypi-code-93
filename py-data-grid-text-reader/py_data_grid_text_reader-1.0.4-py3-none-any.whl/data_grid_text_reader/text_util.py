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

def strip_lines(multi_line_string: str, strip_first_and_list_lines: bool = True) -> str:
    """
    Strip leading and trailing whitespace from every line in the input string.
    :param multi_line_string: A string where some lines may or may not have
    leading or trailing whitespace
    :param strip_first_and_list_lines: If the first and/or last lines are
    empty, remove them.
    :return: A string where no lines have leading or trailing whitespace
    """
    stripped = '\n'.join([line.strip() for line in multi_line_string.strip().splitlines()])
    return stripped.strip() if strip_first_and_list_lines else stripped

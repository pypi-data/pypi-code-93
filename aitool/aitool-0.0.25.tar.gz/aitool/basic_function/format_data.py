# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
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
"""

"""
from typing import Dict, Union, List, Any, NoReturn, Iterable, Tuple, Generator


def flatten(data: Union[List[Any], Tuple[Any]], ignore_types: tuple = (str, bytes)) -> Generator:
    """
    flatten list or tuple
    :param data: a list or a tuple
    :param ignore_types: types will not be flatten
    :return: a generator of a flatten list

    >>> [x for x in flatten([[1,2,('abc',4)],'hello'])]
    [1, 2, 'abc', 4, 'hello']
    >>> [x for x in flatten('abc')]
    ['abc']
    """

    if isinstance(data, Iterable) and not isinstance(data, ignore_types):
        for item in data:
            if isinstance(item, Iterable) and not isinstance(item, ignore_types):
                yield from flatten(item)
            else:
                yield item
    else:
        yield data


if __name__ == '__main__':
    # print([x for x in flatten('abc')])
    import doctest
    doctest.testmod()

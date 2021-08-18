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
from typing import Dict, Union, List, Any, NoReturn


def concat_all(*args, **kwargs):
    return '{}{}'.format(args, kwargs)


def cache(
        cache_size=100000,
        get_key=concat_all,
):
    def decorate(func):
        _cache = {}

        def implement(*args, **kwargs):
            key = get_key(*args, **kwargs)
            if key in _cache:
                return _cache[key]
            result = func(*args, **kwargs)
            if len(_cache) < cache_size:
                _cache[key] = result
            return result
        return implement
    return decorate


if __name__ == '__main__':
    @cache()
    def repeat(x):
        return x


    repeat(10)
    repeat(10)

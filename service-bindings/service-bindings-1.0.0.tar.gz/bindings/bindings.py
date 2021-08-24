# Copyright 2021 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from functools import reduce
from os import path
from typing import List, Optional

from bindings.binding import Binding, CacheBinding, ConfigTreeBinding

SERVICE_BINDING_ROOT: str = "SERVICE_BINDING_ROOT"
"""The name of the environment variable read to determine the bindings filesystem root.  Specified by the Kubernetes
Service Binding Specification: https://github.com/k8s-service-bindings/spec#workload-projection """


def cached(bindings: List[Binding]) -> List[Binding]:
    """
    Wraps each Binding in a CacheBinding.

    :param bindings: the bindings to wrap
    :return: the wrapped bindings
    """

    return [CacheBinding(v) for v in bindings]


def from_path(root: str) -> List[Binding]:
    """
    Creates a new collection of Bindings using the specified root.  If the directory does not exist,
    an empty collection is returned.

    :param root: the root to populate the Bindings from
    :return: the bindings found in the root
    """

    if not path.exists(root) or not path.isdir(root):
        return []

    def r(b: List[Binding], c: str) -> List[Binding]:
        p = path.join(root, c)

        if path.isdir(p):
            b.append(ConfigTreeBinding(p))

        return b

    return reduce(r, os.listdir(root), [])


def from_service_binding_root() -> List[Binding]:
    """
    Creates a new collection of Bindings using the $SERVICE_BINDING_ROOT environment variable to determine the file
    system root.  If the $SERVICE_BINDING_ROOT environment variable is not set, an empty collection is returned.  If
    the directory does not exist, an empty collection is returned.

    :return: the bindings found in $SERVICE_BINDING_ROOT
    """
    path = os.getenv(SERVICE_BINDING_ROOT)
    return [] if path is None else from_path(path)


def find(bindings: List[Binding], name: str) -> Optional[Binding]:
    """
    Returns a Binding with a given name.  Comparison is case-insensitive.

    :param bindings: the Bindings to find in
    :param name: the name of the Binding to find
    :return: the Binding with a given name if it exists, None otherwise
    """

    for b in bindings:
        if b.get_name().lower() == name.lower():
            return b

    return None


def filter(bindings: List[Binding], type: Optional[str] = None, provider: Optional[str] = None) -> List[Binding]:
    """
    Returns zero or more Bindings with a given type and provider.  If type or provider are None, the result is not
    filter on that argument.  Comparisons are case-insensitive.

    :param bindings: the Bindings to filter
    :param type: the type of the binding to find
    :param provider: the provider of the Binding to find
    :return: the collection Bindings with a given type and provider
    """

    match = []

    for b in bindings:
        if type is not None:
            t = b.get_type()
            if t.lower() != type.lower():
                continue

        if provider is not None:
            p = b.get_provider()
            if p is None or p.lower() != provider.lower():
                continue

        match.append(b)

    return match

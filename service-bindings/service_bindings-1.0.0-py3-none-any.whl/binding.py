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

from os import path
from typing import Dict, Optional

from bindings.secret import is_valid_secret_key

PROVIDER: str = "provider"
"""The key for the provider of a binding"""

TYPE: str = "type"
"""The key for the type of a binding"""


class Binding:
    """A representation of a binding as defined by the Kubernetes Service Binding Specification:
    https://github.com/k8s-service-bindings/spec#workload-projection"""

    def get_as_bytes(self, key: str) -> Optional[bytes]:
        """
        Returns the contents of a binding entry in its raw bytes form.

        :param key: the key of the entry to retrieve
        :return: the contents of a binding entry if it exists, otherwise None
        """
        pass

    def get_name(self) -> str:
        """
        Returns the name of the binding

        :return: the name of the binding
        """
        pass

    def get(self, key: str) -> Optional[str]:
        """
        Returns the contents of a binding entry as a UTF-8 decoded str.  Any whitespace is trimmed.

        :param key: the key of the entry to retrieve
        :return: the contents of a binding entry as a UTF-8 decoded str if it exists, otherwise None
        """

        b = self.get_as_bytes(key)

        if b is None:
            return None

        return b.decode("utf-8").strip()

    def get_provider(self) -> Optional[str]:
        """
        Returns the value of the PROVIDER key.

        :return: the value of the PROVIDER key if it exists, otherwise None
        """

        return self.get(PROVIDER)

    def get_type(self) -> str:
        """
        Returns the value of the TYPE key.

        :param binding: the binding to read from
        :return: the value of the TYPE key
        """

        t = self.get(TYPE)
        if t is None:
            raise ValueError("binding does not contain a type")
        return t


class CacheBinding(Binding):
    """An implementation of Binding that caches values once they've been retrieved"""

    _delegate: Binding

    _cache: Dict[str, bytes]

    def __init__(self, delegate: Binding):
        """
        Creates a new instance.

        :param delegate: the Binding used to retrieve original values
        """

        self._delegate = delegate
        self._cache = {}

    def get_as_bytes(self, key: str) -> Optional[bytes]:
        if key in self._cache:
            return self._cache[key]

        v = self._delegate.get_as_bytes(key)
        if v is not None:
            self._cache[key] = v
        return v

    def get_name(self) -> str:
        return self._delegate.get_name()


class ConfigTreeBinding(Binding):
    """An implementation of Binding that reads files from a volume mounted Kubnernetes Secret:
    https://kubernetes.io/docs/concepts/configuration/secret/#using-secrets"""

    _root: str

    def __init__(self, root: str):
        """
        Creates a new instance.

        :param root: the root of the volume mounted Kubernetes secret
        """

        self._root = root

    def get_as_bytes(self, key: str) -> Optional[bytes]:
        if not is_valid_secret_key(key):
            return None

        p = path.join(self._root, key)

        if not path.exists(p):
            return None

        if not path.isfile(p):
            return None

        print(path.abspath(p))

        with open(p, "rb") as file:
            return file.read()

    def get_name(self) -> str:
        return path.basename(self._root)


class DictBinding(Binding):
    """An implementation of Binding that returns values from a dict"""

    _name: str

    _content: Dict[str, bytes]

    def __init__(self, name: str, content: Dict[str, bytes]):
        """
        Creates a new instance.

        :param name: the name of the binding
        :param content: the content of the binding
        """

        self._name = name
        self._content = content

    def get_as_bytes(self, key: str) -> Optional[bytes]:
        if not is_valid_secret_key(key):
            return None

        if key not in self._content:
            return None

        return self._content[key]

    def get_name(self) -> str:
        return self._name

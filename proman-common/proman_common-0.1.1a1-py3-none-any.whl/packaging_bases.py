# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Provide base objects for proman.'''

from abc import ABC, abstractmethod
from typing import Any, Dict


class PackageManagerBase(ABC):
    '''Define required methods for package manager.'''

    @abstractmethod
    def install(self, *packages: Any, **options: Any) -> None:
        '''Perform package install.'''
        pass

    @abstractmethod
    def uninstall(self, *packages: Any, **options: Any) -> None:
        '''Perform package uninstall.'''
        pass

    @abstractmethod
    def update(self, *packages: Any, **options: Any) -> None:
        '''Update the package.'''
        pass

    @abstractmethod
    def search(self, query: str, **options: Any) -> Any:
        '''Perform package search.'''
        pass

    @abstractmethod
    def info(self, name: str, output: str) -> Dict[str, Any]:
        '''Retrieve package information.'''
        pass

    @abstractmethod
    def download(self, package: Any, dest: str, **options: Any) -> None:
        '''Download package.'''
        pass

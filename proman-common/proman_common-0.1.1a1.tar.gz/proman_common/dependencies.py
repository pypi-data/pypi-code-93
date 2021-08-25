# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Resolve package dependencies.'''

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple


class DependencyBase(ABC):
    '''Provide common base functions for dependencies.'''

    # def __getattr__(self, attr: str) -> Any:
    #     '''Provide proxy for distribution.'''
    #     return getattr(self._artifact, attr)

    @property
    @abstractmethod
    def name(self) -> str:
        '''Retrieve dependency name.'''
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        '''Retrieve dependency version.'''
        pass

    @property
    @abstractmethod
    def digests(self) -> Tuple[Dict[str, str]]:
        '''Retrieve dependency digests.'''
        pass

    @property
    @abstractmethod
    def url(self) -> str:
        '''Retrieve dependency URL.'''
        pass

    @property
    def is_dev(self) -> bool:
        '''Check if dependency for development.'''
        return self.__dev if hasattr(self, '__dev') else False

    @is_dev.setter
    def is_dev(self, dev: bool) -> None:
        '''Set dependency for development or release.'''
        self.__dev = dev

    @property
    def platform(self) -> Optional[str]:
        '''Check the compatible platform requirement.'''
        return self.__platform

    @platform.setter
    def platform(self, platform: str) -> None:
        '''Set the compatible platform requirement.'''
        self.__platform = platform

    @property
    def is_optional(self) -> bool:
        '''Check if the dependency is optional.'''
        return self.__optional if hasattr(self, '__optional') else False

    @is_optional.setter
    def is_optional(self, optional: bool) -> None:
        '''Set dependency to optional or required.'''
        self.__optional = optional

    @property
    def allow_prerelease(self) -> bool:
        '''Check if the prerelease dependency is allowed.'''
        return self.__prerelease if hasattr(self, '__prerelease') else False

    @allow_prerelease.setter
    def allow_prerelease(self, prerelease: bool) -> None:
        '''Set if a dependency prerelease is allowed.'''
        self.__prerelease = prerelease

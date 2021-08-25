# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Manage package dependencies.'''

import os
from typing import Any, Dict, List, TYPE_CHECKING

from .dependencies import DependencyBase

# from . import exception
if TYPE_CHECKING:
    # from packaging.specifiers import SpecifierSet
    from .config import Config

url_base = os.getenv('PROMAN_GITHUB_URL', 'https://api.github.com')


class ProjectSettingsMixin:
    '''Provide common methods for project settings.'''

    @staticmethod
    def dependency_type(dev: bool = False) -> str:
        '''Check if development dependency.'''
        return 'dev-dependencies' if dev else 'dependencies'


class SourceTreeFile(ProjectSettingsMixin):
    '''Manage source tree configuration file for project.

    see PEP-0517

    '''

    def __init__(
        self,
        config_file: 'Config',
        basepath: str = '.tool.proman'
    ) -> None:
        '''Initialize source tree defaults.'''
        self.__settings = config_file
        self.__basepath = basepath

    def is_dependency(self, dependency: 'DependencyBase') -> bool:
        '''Check if dependency exists.'''
        result = dependency.name in (
            self.__settings.retrieve(
                f"{self.__basepath}.{self.dependency_type(dependency.is_dev)}"
            ) or {}
        )
        return result

    def get_dependencies(self, dev: bool = False) -> List[Dict[str, Any]]:
        '''Retrieve depencency configuration.'''
        return self.__settings.retrieve(
            f"{self.__basepath}.{self.dependency_type(dev)}"
        ) or []

    def get_dependency(
        self,
        name: str,
        dev: bool = False,
    ) -> Dict[str, Any]:
        '''Retrieve depencency configuration.'''
        return {
            k: v
            for k, v in (
                self.__settings.retrieve(
                    f"{self.__basepath}.{self.dependency_type(dev)}"
                ) or {}
            ).items()
            if k == name
        }

    def add_dependency(self, dependency: 'DependencyBase') -> None:
        '''Add dependency to configuration.'''
        if not self.is_dependency(dependency):
            self.__settings.create(
                "{b}.{d}.{n}".format(
                    b=self.__basepath,
                    d=self.dependency_type(dependency.is_dev),
                    n=dependency.name,
                ),
                dependency.version,
            )

    def remove_dependency(self, dependency: 'DependencyBase') -> None:
        '''Remove dependency from configuration.'''
        if self.is_dependency(dependency):
            self.__settings.delete(
                f"{self.__basepath}\
                .{self.dependency_type(dependency.is_dev)}\
                .{dependency.name}".replace(' ', '')
            )

    def update_dependency(self, dependency: 'DependencyBase') -> None:
        '''Update existing dependency.'''
        # TODO: handle distlib key
        self.remove_dependency(dependency)
        self.add_dependency(dependency)

    def save(self) -> None:
        '''Update the source tree config.'''
        self.__settings.dump()


class LockFile(ProjectSettingsMixin):
    '''Manage project lock configuration file.'''

    def __init__(self, lock_config: 'Config', basepath: str = '') -> None:
        '''Initialize lock configuration settings.'''
        self.__settings = lock_config
        self.__basepath = basepath

    def is_locked(self, dependency: 'DependencyBase') -> bool:
        '''Check if package lock is in configuration.'''
        print(self.__settings.data)
        result = any(
            dependency.name in p['name']
            for p in (
                self.__settings.retrieve(
                    f"{self.__basepath}\
                    .{self.dependency_type(dependency.is_dev)}"
                ) or {}
            )
        )
        print('result', result)
        return result

    def get_locks(self, dev: bool = False) -> List[Dict[str, Any]]:
        '''Get all dependencies.'''
        return self.__settings.retrieve(
            f"{self.__basepath}.{self.dependency_type(dev)}"
        ) or []

    def get_lock(self, name: str, dev: bool = False) -> Dict[str, Any]:
        '''Retrieve package lock from configuration.'''
        result = [
            x
            for x in self.__settings.retrieve(
                f"{self.__basepath}.{self.dependency_type(dev)}"
                .replace(' ', '')
            ) or []
            if x['name'] == name
        ]
        return result[0] if result else {}

    def update_lock(
        self,
        dependency: 'DependencyBase',
        digests: Dict[str, Any] = {},
    ) -> None:
        '''Update existing package lock in configuration.'''
        self.remove_lock(dependency)
        self.add_lock(dependency)

    def add_lock(self, dependency: 'DependencyBase', **kwargs: Any) -> None:
        '''Add package lock to configuration.'''
        if not self.is_locked(dependency):
            # package_hashes = self.lookup_hashes(
            #     package.name, package.version
            # )
            print('digests', dependency.digests)
            lock = {
                'name': dependency.name,
                'version': dependency.version,
                'digests': [x for x in dependency.digests],
                **kwargs
            }
            self.__settings.append(
                f"{self.__basepath}.{self.dependency_type(dependency.is_dev)}",
                lock
            )
        else:
            print('package lock already exists')

    def remove_lock(self, dependency: 'DependencyBase') -> None:
        '''Remove package lock from configuration.'''
        self.__settings.set(
            f"{self.__basepath}.{self.dependency_type(dependency.is_dev)}",
            [
                x
                for x in self.get_locks(dependency.is_dev)
                if not x['name'] == dependency.name
            ],
        )

    def save(self) -> None:
        '''Update the source tree config.'''
        self.__settings.dump()


class Manifest:
    '''Provide package manifest.'''

    def __init__(
        self,
        source_tree: 'SourceTreeFile',
        lockfile: 'LockFile',
        dependency_class: Dict[str, str]
    ) -> None:
        '''Initialize project manifest.'''
        self.source_tree = source_tree
        self.lockfile = lockfile
        self.dependency_class = dependency_class

    def __get_dependency(
        self,
        settings: Dict[str, str],
    ) -> 'DependencyBase':
        '''Create dependency instance.'''
        print(settings)
        module = __import__(self.dependency_class['module'])
        cls = getattr(module, self.dependency_class['class'])
        dependency = cls(package=settings)
        return dependency

    def save(self) -> None:
        '''Save each configuration.'''
        self.source_tree.save()
        self.lockfile.save()

    def get_dependencies(self, dev: bool = False) -> List['DependencyBase']:
        '''Get all dependencies.'''
        dependencies: List['DependencyBase'] = []
        for dependency in self.lockfile.get_locks(dev=dev):
            print(dependency)
            dependencies.append(
                self.get_dependency(name=dependency['name'], dev=dev)
            )
        return dependencies

    def get_dependency(self, name: str, dev: bool = False) -> 'DependencyBase':
        '''Get dependency.'''
        source = self.source_tree.get_dependency(name=name, dev=dev)
        lock = self.lockfile.get_lock(name=name, dev=dev)
        settings = {'specifier': source[name], **lock} if source else lock
        return self.__get_dependency(settings=settings)

    def add_dependency(
         self, dependency: 'DependencyBase', **kwargs: Any
    ) -> None:
        '''Add dependency to configuration.'''
        if self.source_tree.is_dependency(dependency):
            print('dependency exists:', dependency)
        else:
            self.source_tree.add_dependency(dependency)

        if self.lockfile.is_locked(dependency):
            lock = self.lockfile.get_lock(dependency.name, dependency.is_dev)
            print('package locked:', lock)
        else:
            self.lockfile.add_lock(dependency, **kwargs)
        self.save()

    def remove_dependency(self, dependency: 'DependencyBase') -> None:
        '''Remove dependency from configuration.'''
        if self.source_tree.is_dependency(dependency):
            self.source_tree.remove_dependency(dependency)
        else:
            print('package is not tracked:', dependency.name)

        if self.lockfile.is_locked(dependency):
            self.lockfile.remove_lock(dependency)
        else:
            print('lock is not locked:', dependency.name)
        self.save()

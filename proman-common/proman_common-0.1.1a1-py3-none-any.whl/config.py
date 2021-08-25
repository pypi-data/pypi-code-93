# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Provide configuration for proman.'''

import os
from dataclasses import dataclass
from typing import Optional

from compendium.loader import ConfigFile

from . import exception

index_url = 'https://pypi.org'
url_base = 'https://api.github.com'


@dataclass
class PyPIRC(ConfigFile):
    '''Manage settings from configuration file.'''

    filepath: str = os.path.join(os.path.expanduser('~'), '.pypirc')
    filetype: str = 'ini'
    writable: bool = True

    def __post_init__(self) -> None:
        '''Initialize settings from configuration.'''
        super().__init__(self.filepath, filetype=self.filetype)
        try:
            self.load()
        except Exception:
            print('no ".pypirc" found')

    def add_repository(
        self,
        name: str,
        repository: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        '''Add repository to .pypirc config.'''
        data = {}
        if repository:
            data['repository'] = repository
        if username:
            data['username'] = username
            if password:
                data['password'] = password
        self.create(name, data)

    def remove_repository(self, name: str) -> None:
        '''Remove repository from .pypirc config.'''
        self.delete(name)


@dataclass
class Config(ConfigFile):
    '''Provide configuration.'''

    filepath: str
    index_url: str = url_base
    include_prereleases: bool = False
    digest_algorithm: str = 'sha256'
    lookup_memory: Optional[str] = None
    writable: bool = True

    def __post_init__(self) -> None:
        '''Initialize settings from configuration.'''
        super().__init__(
            self.filepath,
            writable=self.writable,
            separator='.',
        )
        if os.path.isfile(self.filepath):
            try:
                self.load()
            except Exception:
                raise exception.PromanException('could not load configuration')

# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Filesystem paths for common modules.'''

import os
from dataclasses import InitVar, dataclass, field
from typing import Optional

from .system import System


@dataclass
class SystemDirs:
    '''Provide system directory paths.'''

    system: 'System' = System()

    def __post_init__(self) -> None:
        '''Initialize system paths.'''
        if self.system.kind == 'darwin':
            pass
        elif self.system.kind == 'linux':
            pass
        elif self.system.kind == 'windows':
            pass


@dataclass
class GlobalDirs:
    '''Provide global directory paths.'''

    home_dir: str = os.path.expanduser('~')
    system: 'System' = System()
    cache_dir: str = field(init=False)
    config_dir: str = field(init=False)
    data_dir: str = field(init=False)
    data_local_dir: str = field(init=False)
    executable_dir: Optional[str] = field(init=False)
    preference_dir: str = field(init=False)
    runtime_dir: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        '''Perform post-intialization for base directories.'''
        if self.system.kind == 'darwin':
            self.cache_dir = os.path.join(self.home_dir, 'Library', 'Caches')
            self.config_dir = os.path.join(
                self.home_dir, 'Library', 'Application', 'Support'
            )
            self.data_dir = os.path.join(
                self.home_dir, 'Library', 'Application', 'Support'
            )
            self.data_local_dir = os.path.join(
                self.home_dir, 'Library', 'Application', 'Support'
            )
            self.executable_dir = None
            self.preference_dir = os.path.join(
                self.home_dir, 'Library', 'Preferences'
            )
            self.runtime_dir = None
        elif self.system.kind == 'linux':
            self.cache_dir = os.getenv(
                'XDG_CACHE_HOME', os.path.join(self.home_dir, '.cache')
            )
            self.config_dir = os.getenv(
                'XDG_CONFIG_HOME', os.path.join(self.home_dir, '.config')
            )
            self.data_dir = os.getenv(
                'XDG_DATA_HOME', os.path.join(self.home_dir, '.local', 'share')
            )
            self.data_local_dir = os.getenv(
                'XDG_DATA_HOME', os.path.join(self.home_dir, '.local', 'share')
            )
            self.executable_dir = os.getenv(
                'XDG_BIN_HOME', os.path.join(self.home_dir, '.local', 'bin')
            )
            self.preference_dir = os.getenv(
                'XDG_CONFIG_HOME', os.path.join(self.home_dir, '.config')
            )
            self.runtime_dir = os.getenv('XDG_RUNTIME_DIR')
        elif self.system.kind == 'windows':
            self.cache_dir = os.getenv(
                'LOCALAPPDATA', os.path.join(self.home_dir, 'AppData', 'Local')
            )
            self.config_dir = os.getenv(
                'APPDATA', os.path.join(self.home_dir, 'AppData', 'Roaming')
            )
            self.data_dir = os.getenv(
                'APPDATA', os.path.join(self.home_dir, 'AppData', 'Roaming')
            )
            self.data_local_dir = os.getenv(
                'LOCALAPPDATA', os.path.join(self.home_dir, 'AppData', 'Local')
            )
            self.executable_dir = None
            self.preference_dir = os.getenv(
                'APPDATA', os.path.join(self.home_dir, 'AppData', 'Roaming')
            )
            self.runtime_dir = None


@dataclass
class AppDirs(GlobalDirs):
    '''Provide project directory paths.'''

    project_name: InitVar[str] = None
    system: 'System' = System()

    def __post_init__(self, project_name: str) -> None:  # type: ignore
        '''Perform post-intialization for project directories.'''
        super().__post_init__()
        self.project_name = project_name
        if self.system.kind == 'darwin':
            self.cache_dir = os.path.join(self.cache_dir, self.project_name)
            self.config_dir = os.path.join(self.config_dir, self.project_name)
            self.data_dir = os.path.join(self.data_dir, self.project_name)
            self.data_local_dir = os.path.join(
                self.data_local_dir, self.project_name
            )
            self.preference_dir = os.path.join(
                self.preference_dir, self.project_name
            )
        elif self.system.kind == 'linux':
            self.cache_dir = os.path.join(
                self.cache_dir, self.project_name
            )
            self.config_dir = os.path.join(
                self.config_dir, self.project_name
            )
            self.data_dir = os.path.join(self.data_dir, self.project_name)
            self.data_local_dir = os.path.join(
                self.data_local_dir, self.project_name
            )
            self.preference_dir = os.path.join(
                self.preference_dir, self.project_name
            )
            if self.runtime_dir:
                self.runtime_dir = os.path.join(
                    self.runtime_dir, self.project_name
                )
        elif self.system.kind == 'windows':
            if self.cache_dir:
                self.cache_dir = os.path.join(
                    self.cache_dir, self.project_name, 'cache'
                )
            if self.config_dir:
                self.config_dir = os.path.join(
                    self.config_dir, self.project_name, 'config'
                )
            if self.data_dir:
                self.data_dir = os.path.join(
                    self.data_dir, self.project_name, 'data'
                )
            if self.data_local_dir:
                self.data_local_dir = os.path.join(
                    self.data_local_dir, self.project_name, 'data'
                )
            if self.preference_dir:
                self.preference_dir = os.path.join(
                    self.preference_dir, self.project_name, 'config'
                )


@dataclass
class UserDirs(GlobalDirs):
    '''Provide user directory paths.'''

    system: 'System' = System()
    audio_dir: Optional[str] = field(init=False)
    desktop_dir: Optional[str] = field(init=False)
    documents_dir: Optional[str] = field(init=False)
    download_dir: Optional[str] = field(init=False)
    fonts_dir: Optional[str] = field(init=False)
    pictures_dir: Optional[str] = field(init=False)
    public_dir: Optional[str] = field(init=False)
    templates_dir: Optional[str] = field(init=False)
    videos_dir: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        '''Perform post-intialization for user directories.'''
        super().__post_init__()
        if self.system.kind == 'darwin':
            self.audio_dir = os.path.join(self.home_dir, 'Music')
            self.desktop_dir = os.path.join(self.home_dir, 'Desktop')
            self.documents_dir = os.path.join(self.home_dir, 'Documents')
            self.download_dir = os.path.join(self.home_dir, 'Downloads')
            self.fonts_dir = os.path.join(self.home_dir, 'Library', 'fonts')
            self.pictures_dir = os.path.join(self.home_dir, 'Pictures')
            self.public_dir = os.path.join(self.home_dir, 'Public')
            self.templates_dir = None
            self.videos_dir = os.path.join(self.home_dir, 'Movies')
        elif self.system.kind == 'linux':
            self.audio_dir = os.getenv(
                'XDG_MUSIC_DIR', os.path.join(self.home_dir, 'Music')
            )
            self.desktop_dir = os.getenv(
                'XDG_DESKTOP_DIR', os.path.join(self.home_dir, 'Desktop')
            )
            self.documents_dir = os.getenv(
                'XDG_DOCUMENTS_DIR', os.path.join(self.home_dir, 'Documents')
            )
            self.download_dir = os.getenv(
                'XDG_DOWNLOAD_DIR', os.path.join(self.home_dir, 'Downloads')
            )
            self.fonts_dir = os.getenv(
                'XDG_DATA_HOME',
                os.path.join(self.home_dir, '.local', 'share', 'fonts'),
            )
            self.pictures_dir = os.getenv(
                'XDG_PICTURES_DIR', os.path.join(self.home_dir, 'Pictures')
            )
            self.public_dir = os.getenv(
                'XDG_PUBICSHARE_DIR', os.path.join(self.home_dir, 'Public')
            )
            self.templates_dir = os.getenv(
                'XDG_TEMPLATES_DIR', os.path.join(self.home_dir, 'Templates')
            )
            self.videos_dir = os.getenv(
                'XDG_VIDEOS_DIR', os.path.join(self.home_dir, 'Videos')
            )
        elif self.system.kind == 'windows':
            self.audio_dir = os.path.join(self.home_dir, 'Music')
            self.desktop_dir = os.path.join(self.home_dir, 'Desktop')
            self.documents_dir = os.path.join(self.home_dir, 'Documents')
            self.download_dir = os.path.join(self.home_dir, 'Downloads')
            self.fonts_dir = os.path.join(
                self.home_dir, 'Local', 'Microsoft', 'Windows', 'Fonts'
            )
            self.pictures_dir = os.path.join(self.home_dir, 'Pictures')
            self.public_dir = os.path.join(self.home_dir, 'Public')
            self.videos_dir = os.path.join(self.home_dir, 'Videos')

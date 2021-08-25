# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Control Package Archives.'''

import mimetypes
import tarfile


class Archive:
    '''Provide archive capabilities.'''

    def __init__(self) -> None:
        '''Initialize archive.'''
        pass

    def _unpack_tarball(self, path: str, dest: str, mode: str) -> None:
        '''Unpack tarball.'''
        with tarfile.open(path, mode) as archive:
            archive.extractall(dest, members=None, numeric_owner=False)

    def pack(self, path: str) -> None:
        '''Pack archive.'''
        pass

    def unpack(self, path: str, dest: str = '.') -> None:
        '''Unpack archive.'''
        mt = mimetypes.guess_type(path)
        if mt[0] == 'application/gzip':
            mode = 'r:gz'
        if mt[0] == 'application/x-tar':
            mode = 'r:gz'
        if mt[0] == 'application/x-bzip2':
            mode = 'r:bz2'
        if mt[0] == 'application/x-lzma':
            mode = 'r:xz'
        # if mt[0] == 'application/zip':
        #     mode = 'zip'

        self._unpack_tarball(path, dest, mode)

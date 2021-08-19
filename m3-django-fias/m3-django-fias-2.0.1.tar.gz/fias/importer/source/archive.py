# coding: utf-8
from __future__ import unicode_literals, absolute_import

import os
from uuid import uuid4

from django.conf import settings

import rarfile
import zipfile
import tempfile
from progress.bar import Bar

from fias.compat import urlretrieve, HTTPError
from fias.importer.signals import (
    pre_download, post_download,
    pre_unpack, post_unpack,
)
from fias.importer.table import table_dbf_re, table_dbt_re

from .tablelist import TableList, TableListLoadingError
from .directory import DirectoryTableList
from .wrapper import RarArchiveWrapper

# Задаем UNRAR_TOOL глобально
rarfile.UNRAR_TOOL = getattr(settings, 'FIAS_UNRAR_TOOL', 'unrar')


class BadArchiveError(TableListLoadingError):

    def __init__(self, source, *args):
        super(BadArchiveError, self).__init__(
            'Archive: `{0}` corrupted or is not archive'.format(
                source
            ),
            *args
        )


class EmptyArchiveError(TableListLoadingError):
    def __init__(self, source, *args):
        super(EmptyArchiveError, self).__init__(
            'Archive: `{0}` is empty'.format(source),
            *args
        )


class RetrieveError(TableListLoadingError):
    pass


class RarFile(rarfile.RarFile):

    @classmethod
    def open_file(cls, source):
        try:
            return cls(source)
        except (rarfile.NotRarFile, rarfile.BadRarFile):
            raise BadArchiveError(source)


class ZipFile(zipfile.ZipFile):

    @classmethod
    def open_file(cls, source):
        try:
            return cls(source)
        except zipfile.BadZipfile:
            raise BadArchiveError(source)


class LocalArchiveTableList(TableList):
    wrapper_class = RarArchiveWrapper

    @staticmethod
    def unpack(archive, tempdir=None):
        path = tempfile.mkdtemp(dir=tempdir)
        archive.extractall(path)
        return path

    def get_archive(self, source):
        if rarfile.is_rarfile(source):
            archive_class = RarFile
        elif zipfile.is_zipfile(source):
            archive_class = ZipFile
        else:
            raise BadArchiveError(source)

        return archive_class.open_file(source)

    def load_data(self, source):
        archive = self.get_archive(source)

        if not archive.namelist():
            raise EmptyArchiveError(source)

        first_name = archive.namelist()[0]
        if table_dbf_re.match(first_name) or table_dbt_re.match(first_name):
            pre_unpack.send(sender=self.__class__, archive=archive)

            path = LocalArchiveTableList.unpack(archive=archive, tempdir=self.tempdir)

            post_unpack.send(sender=self.__class__, archive=archive, dst=path)

            return DirectoryTableList.wrapper_class(source=path, is_temporary=True)

        return self.wrapper_class(source=archive)


class DlProgressBar(Bar):
    message = 'Downloading: '
    suffix = '%(index)d/%(max)d. ETA: %(elapsed)s'
    hide_cursor = False


class RemoteArchiveTableList(LocalArchiveTableList):
    download_progress_class = DlProgressBar

    def load_data(self, source):
        progress = self.download_progress_class()

        def update_progress(count, block_size, total_size):
            progress.goto(int(count * block_size * 100 / total_size))

        if self.tempdir:
            tmp_file = os.path.join(self.tempdir, str(uuid4()))
        else:
            tmp_file = None

        pre_download.send(sender=self.__class__, url=source)
        try:
            path = urlretrieve(source, reporthook=update_progress, filename=tmp_file)[0]
        except HTTPError as e:
            raise RetrieveError('Can not download data archive at url `{0}`. Error occurred: "{1}"'.format(
                source, str(e)
            ))
        progress.finish()
        post_download.send(sender=self.__class__, url=source, path=path)

        return super(RemoteArchiveTableList, self).load_data(source=path)

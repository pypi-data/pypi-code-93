#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/4/8 2:08
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : storage_utils.py
@Desc    : 
"""
import os
from pprint import pformat
import logging
from waveletai.envs import WARN_SIZE
from abc import ABCMeta, abstractmethod
import six
import time
from waveletai.utils.datastream import FileStream, compress_to_tar_gz_in_memory, FileChunkStream

_logger = logging.getLogger(__name__)


class UploadEntry(object):
    def __init__(self, source_path, target_path=None):
        self.source_path = source_path
        if target_path is None:
            """不存在时，赋值为filename"""
            self.target_path = os.path.split(source_path)[1]
        else:
            self.target_path = target_path
        self.filename = os.path.split(self.target_path)[1]
        self.prefix = os.path.split(self.target_path)[0]

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

    def __hash__(self):
        """
        Returns the hash of source and target path
        """
        return hash((self.source_path, self.target_path))

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.__dict__)

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def is_stream(self):
        return hasattr(self.source_path, 'read')


class UploadPackage(object):
    def __init__(self):
        self.items = []
        self.size = 0
        self.len = 0

    def reset(self):
        self.items = []
        self.size = 0
        self.len = 0

    def update(self, entry, size):
        self.items.append(entry)
        self.size += size
        self.len += 1

    def is_empty(self):
        return self.len == 0

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.__dict__)

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()


def scan_upload_entries(upload_entries):
    """
    Returns upload entries for all files that could be found for given upload entries.
    In case of directory as upload entry, files we be taken from all subdirectories recursively.
    Any duplicated entries are removed.
    """
    walked_entries = set()
    for entry in upload_entries:
        if entry.is_stream() or not os.path.isdir(entry.source_path):
            entry.target_path = os.path.split(entry.source_path)[1]
            walked_entries.add(entry)
        else:
            for root, _, files in os.walk(entry.source_path):
                path_relative_to_entry_source = os.path.relpath(root, entry.source_path)
                target_root = os.path.normpath(os.path.join(entry.target_path, path_relative_to_entry_source))
                for filename in files:
                    walked_entries.add(UploadEntry(os.path.join(root, filename), os.path.join(target_root, filename)))

    return walked_entries


# class ProgressBar(object):
#
#     def __init__(self, title,
#                  count=0.0,
#                  run_status=None,
#                  fin_status=None,
#                  total=100.0,
#                  unit='', sep='/',
#                  chunk_size=1.0):
#         super(ProgressBar, self).__init__()
#         self.info = "(%s)%s %.2f %s %s %.2f %s"
#         self.title = title
#         self.total = total
#         self.count = count
#         self.chunk_size = chunk_size
#         self.status = run_status or ""
#         self.fin_status = fin_status or " " * len(self.status)
#         self.unit = unit
#         self.seq = sep
#
#     def __get_info(self):
#         # 【名称】状态 进度 单位 分割线 总数 单位
#         _info = self.info % (self.title, self.status,
#                              self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
#         return _info
#
#     def refresh(self, count=1, status=None):
#         self.count += count
#         # if status is not None:
#         self.status = status or self.status
#         end_str = "\r"
#         if self.count >= self.total:
#             end_str = '\n'
#             self.status = status or self.fin_status
#         print(self.__get_info(), end=end_str)


@six.add_metaclass(ABCMeta)
class ProgressIndicator(object):

    @abstractmethod
    def progress(self, steps):
        pass

    @abstractmethod
    def complete(self):
        pass


class SilentProgressIndicator(ProgressIndicator):
    def __init__(self, total, filename=None):
        self.filename = filename
        self.total = total

    def progress(self, steps):
        pass

    def complete(self):
        if self.filename:
            _logger.warning('[%s] 资源文件 任务进度 %.2f KB (100%%)', self.filename, self.total / 1024)
        else:
            _logger.warning('所有任务均已完成 %.2f KB (100%%)', self.total / 1024)


class LoggingProgressIndicator(ProgressIndicator):
    def __init__(self, total, filename=None, frequency=10):
        self.current = 0
        self.filename = filename
        self.total = total
        self.last_warning = time.time()
        self.frequency = frequency
        _logger.warning('[%s] 资源文件 大小为 %.2fMB 任务耗时较长，请耐心等待。', self.filename, self.total / (1024 * 1024))

    def progress(self, steps):
        self.current += steps
        if time.time() - self.last_warning > self.frequency:
            _logger.warning('[%s] 资源文件 任务进度 %.2f MB / %.2f MB (%.2f%%)', self.filename, self.current / (1024 * 1024),
                            self.total / (1024 * 1024), 100 * self.current / self.total)
            self.last_warning = time.time()

    def complete(self):
        _logger.warning('所有任务均已完成 %.2f MB (100%%)', self.total / (1024 * 1024))


# class LoggingUploadProgressIndicator(ProgressIndicator):
#     def __init__(self, total, filename=None, frequency=10):
#         self.current = 0
#         self.filename = filename
#         self.total = total
#         self.last_warning = time.time()
#         self.frequency = frequency
#         _logger.warning('You are sending %dMB of source code to WaveletAI. '
#                         'It is pretty uncommon - please make sure it\'s what you wanted.',
#                         self.total / (1024 * 1024))
#
#     def progress(self, steps):
#         self.current += steps
#         if time.time() - self.last_warning > self.frequency:
#             _logger.warning('%d MB / %d MB (%d%%) of source code was sent to WaveletAI.',
#                             self.current / (1024 * 1024),
#                             self.total / (1024 * 1024),
#                             100 * self.current / self.total)
#             self.last_warning = time.time()
#
#     def complete(self):
#         _logger.warning('%d MB (100%%) of source code was sent to WaveletAI.',
#                         self.total / (1024 * 1024))


def split_upload_files(upload_entries, max_package_size=1 * 1024 * 1024, max_files=500):
    current_package = UploadPackage()

    for entry in upload_entries:
        if entry.is_stream():
            if current_package.len > 0:
                yield current_package
                current_package.reset()
            current_package.update(entry, 0)
            yield current_package
            current_package.reset()
        else:
            size = os.path.getsize(entry.source_path)
            if (size + current_package.size > max_package_size or current_package.len > max_files) \
                    and not current_package.is_empty():
                yield current_package
                current_package.reset()
            current_package.update(entry, size)

    yield current_package


def normalize_file_name(name):
    return name.replace(os.sep, '/')


def upload_to_storage(upload_entries, upload_api_fun, upload_chunk_api_fun, model_repo_id, warn_limit=None):
    unique_upload_entries = scan_upload_entries(upload_entries)
    total_size = 0
    for entry in unique_upload_entries:
        if not entry.is_stream():
            total_size += os.path.getsize(entry.source_path)
    progress_indicator = SilentProgressIndicator(total_size)
    if warn_limit is not None and total_size >= warn_limit:
            progress_indicator = LoggingProgressIndicator(total_size)
    s_count = f_count = 0
    for entry in unique_upload_entries:
        curr_size = os.path.getsize(entry.source_path)
        if os.path.getsize(entry.source_path) > WARN_SIZE:
            res = upload_chunk_api_fun(
                **dict(entry=entry, model_repo_id=model_repo_id))
        else:
            res = upload_api_fun(
                **dict(entry=entry, model_repo_id=model_repo_id))
        if res:
            s_count = s_count + 1
        else:
            f_count = f_count + 1
        progress_indicator.progress(curr_size)
    progress_indicator.complete()

def dataset_upload_to_storage(upload_entries, upload_api_fun, upload_chunk_api_fun, dataset_id, warn_limit=None):
    unique_upload_entries = scan_upload_entries(upload_entries)
    total_size = 0
    for entry in unique_upload_entries:
        if not entry.is_stream():
            total_size += os.path.getsize(entry.source_path)
    progress_indicator = SilentProgressIndicator(total_size)
    if warn_limit is not None and total_size >= warn_limit:
            progress_indicator = LoggingProgressIndicator(total_size)
    s_count = f_count = 0
    for entry in unique_upload_entries:
        curr_size = os.path.getsize(entry.source_path)
        if os.path.getsize(entry.source_path) > WARN_SIZE:
            res = upload_chunk_api_fun(
                **dict(entry=entry, dataset_id=dataset_id))
        else:
            res = upload_api_fun(
                **dict(entry=entry, dataset_id=dataset_id))
        if res:
            s_count = s_count + 1
        else:
            f_count = f_count + 1
        progress_indicator.progress(curr_size)
    progress_indicator.complete()

# def upload_to_storage(upload_entries, upload_api_fun, upload_tar_api_fun, warn_limit=None, **kwargs):
#     unique_upload_entries = scan_upload_entries(upload_entries)
#     progress_indicator = SilentProgressIndicator()
#
#     if warn_limit is not None:
#         total_size = 0
#         for entry in unique_upload_entries:
#             if not entry.is_stream():
#                 total_size += os.path.getsize(entry.source_path)
#         if total_size >= warn_limit:
#             progress_indicator = LoggingUploadProgressIndicator(total_size)
#
#     for package in split_upload_files(unique_upload_entries):
#         if package.is_empty():
#             continue
#
#         uploading_multiple_entries = package.len > 1
#         creating_a_single_empty_dir = package.len == 1 and not package.items[0].is_stream() \
#                                       and os.path.isdir(package.items[0].source_path)
#
#         if uploading_multiple_entries or creating_a_single_empty_dir:
#             data = compress_to_tar_gz_in_memory(upload_entries=package.items)
#             upload_api_fun(**dict(kwargs, data=data))
#             progress_indicator.progress(package.size)
#         else:
#             file_chunk_stream = FileChunkStream(package.items[0])
#             upload_api_fun(**dict(kwargs, data=file_chunk_stream, progress_indicator=progress_indicator))
#
#     progress_indicator.complete()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/4/6 10:41
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : dataset.py
@Desc    : 
"""

import logging

_logger = logging.getLogger(__name__)


class Dataset(object):

    def __init__(self, backend, id, name, desc, zone, dimension, json_data, create_time, data_type, create_user_id,
                 update_time,
                 update_user_id):
        self._backend = backend
        self.id = id
        self.name = name
        self.desc = desc
        self.zone = zone
        self.dimension = dimension
        self.json_data = json_data
        self.create_time = create_time
        self.data_type = data_type
        self.create_user_id = create_user_id
        self.update_time = update_time
        self.update_user_id = update_user_id

    def update(self, name, zone, desc):
        """
        更新当前数据集信息
        :param: name 数据集名称
        :param: zone 数据集区域
        :param: desc 数据集参数
        :return: Class of `Dataset` Object
        """
        return self._backend.update_dataset(self.id, name, zone, desc)

    def delete(self):
        """
        删除当前数据集
        :return:
        """
        return self._backend.delete_dataset(self.id)

    def download_artifact(self, path, destination_dir=None):
        """Download an artifact (file) from the dataset.
        Download a file indicated by ``path`` from the experiment artifacts and save it in ``destination_dir``.
        Args:
            path (:obj:`str`): Path to the file to be downloaded.
            destination_dir (:obj:`str`):
                The directory where the file will be downloaded.
                If ``None`` is passed, the file will be downloaded to the current working directory.

        Raises:
            `NotADirectory`: When ``destination_dir`` is not a directory.
            `FileNotFound`: If a path in dataset artifacts does not exist.

        Examples:
            Assuming that `dataset` is an instance of :class:`~waveletai.dataset.Dataset`.

            .. code:: python3

                dataset.download_asset('raw_data.csv', '/home/dataset/files/')

        """
        return self._backend.download_dataset_artifact_(self.id, self.data_type, self.name, path, destination_dir)

    def download_artifacts(self, destination_dir=None):
        """Download all artifacts from the dataset.
        Download all artifacts and save it in ``destination_dir``

        Args:
            destination_dir (:obj:`str`): The directory where the archive will be downloaded.
                If ``None`` is passed, the archive will be downloaded to the current working directory.

        Raises:
            `NotADirectory`: When ``destination_dir`` is not a directory.
            `FileNotFound`: If a path in dataset artifacts does not exist.

        Examples:
            Assuming that that `dataset` is an instance of :class:`~waveletai.dataset.Dataset`.

            .. code:: python3

                # Download all experiment artifacts to current working directory
                experiment.download_artifacts()

                # Download to user-defined directory
                experiment.download_artifacts('/home/dataset/')

        """
        return self._backend.download_dataset_artifacts_(self.id, self.data_type, self.name, destination_dir)

    def upload_dataset_artifacts(self, path):
        """upload data_asset files"""
        return self._backend.upload_dataset_artifacts(self.id, path)


class Asset(object):
    def __init__(self, id, name, path, content_type, size, asset_type, dataset_id):
        self.id = id
        self.name = name
        self.path = path
        self.content_type = content_type
        self.size = size
        self.asset_type = asset_type
        self.dataset_id = dataset_id

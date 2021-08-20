############################################################################
# Copyright 2020, Anteris Technologies LLC d/b/a Insipher.
# All rights reserved.
# info@insipher.com
# 
# NOTICE:  All information contained herein is, and remains
# the property of Anteris Technologies LLC d/b/a Insipher (“Insipher”).
# The intellectual and technical concepts contained herein are proprietary
# to Insipher and may be covered by U.S. and foreign patents or
# patent applications, trade secret, or copyright. Dissemination of
# this information or reproduction of this material is strictly
# forbidden unless prior written permission is obtained from Insipher.
#

import os
import random
import shutil
import string
import time
from abc import abstractmethod
from typing import Union

import yaml
from minio import Minio
from minio.error import S3Error

from .error import InsipherError


class InsipherAlgorithm(object):
    __artifacts = []
    __algorithm_id = ''
    __minio_config = ''
    __minio_config_file = '/insipher/config/minio-external-configmap.yaml'
    __minio_secret_file = '/vault/secrets/minio.txt'
    model = ''
    __tmpdir = ''
    __standalone = True

    def __init__(self):
        # check to see if this algorithm is running standalone or integrated in the Insipher platform
        if "STANDALONE" in os.environ:
            standalone_env = os.environ.get('STANDALONE').lower()
            if standalone_env == 'false':
                # default is always true
                self.__standalone = False

        self.__algorithm_id = os.environ.get('ALGORITHM_ID')

        if not self.__standalone:
            # wait for configmap to exist
            while not os.path.exists(self.__minio_config_file):
                time.sleep(1)
            with open(self.__minio_config_file, 'r') as f:
                self.__minio_config = yaml.load(f, Loader=yaml.FullLoader)

        # set temp workspace for this process to prevent overwrites
        self.__tmpdir = "/tmp/" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7))
        os.mkdir(self.__tmpdir)
        os.chdir(self.__tmpdir)

    def run_handler(self, data: Union[dict, list], query_params: dict):
        response = self.run(data, query_params)
        self.__cleanup()
        return response

    def train_handler(self, data: Union[dict, list], query_params: dict):
        response = self.train(data, query_params)
        self.__cleanup()
        return response
    
    # abstract function to be implemented by algorithm developer
    @abstractmethod
    def run(self, data: Union[dict, list], query_params: dict):
        pass

    # abstract function to be implemented by algorithm developer
    @abstractmethod
    def train(self, data: Union[dict, list], query_params: dict):
        pass

    def persist_artifact(self, name):
        self.__artifacts.append(name)

        # running in cluster - persist model artifact to object store
        if not self.__standalone:
            minioClient = self.__get_minio_client()
            metadata = {"X-Amz-Meta-Insipher-Mlflow-Run-Id": self.__run_id}
            try:
                with open(name, 'rb') as file_data:
                    file_stat = os.stat(name)
                    minioClient.put_object(self.__minio_config['algorithmBucket'], self.__algorithm_id+'/models/'+self.model+'/'+name,
                                file_data, file_stat.st_size, metadata=metadata)
            except S3Error as err:
                raise InsipherError("Unable to persist artifact: " + name + " from object storage.")
        return name

    def get_artifact(self, name):
        # running in cluster - download model artifact locally
        if not self.__standalone:
            minioClient = self.__get_minio_client()
            try:
                data = minioClient.get_object(self.__minio_config['algorithmBucket'], self.__algorithm_id+'/models/'+self.model+'/'+name)
                with open(name, 'wb') as file_data:
                    for d in data.stream(32*1024):
                        file_data.write(d)
            except S3Error as err:
                raise InsipherError("Unable to get artifact: " + name + " from object storage.")
        return name

    def __get_minio_client(self):
        # get secret
        with open(self.__minio_secret_file, 'r') as f:
            secret = f.read()

        minio_access_key, minio_secret_key = secret.split(':')
        endpointSplit = self.__minio_config['endpoint'].split("//")
        return Minio(endpointSplit[1],
                  access_key=minio_access_key,
                  secret_key=minio_secret_key,
                  secure=self.__minio_config['useSSL'])

    def __cleanup(self):
        shutil.rmtree(self.__tmpdir)

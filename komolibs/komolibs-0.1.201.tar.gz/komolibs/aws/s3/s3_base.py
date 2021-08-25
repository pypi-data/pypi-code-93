import logging
from enum import Enum
from typing import Optional

import boto3

from komolibs.logger import KomoLogger


class S3Result(Enum):
    SUCCESS = 0
    FAILURE = 1


class S3Base:
    s3_base_logger: Optional[KomoLogger] = None

    @classmethod
    def logger(cls) -> KomoLogger:
        if cls.s3_base_logger is None:
            cls.s3_base_logger = logging.getLogger(__name__)
        return cls.s3_base_logger

    def __init__(self):
        self._resource = boto3.Session()

    @property
    def resource(self):
        return self._resource.resource('s3')

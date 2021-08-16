from __future__ import annotations

from media_platform.job.job import Job
from media_platform.job.job_type import JobType
from media_platform.job.specification import Specification


class IndexImageSpecification(Specification):
    def __init__(self, collection_id):
        self.collection_id = collection_id

    @classmethod
    def deserialize(cls, data):
        return IndexImageSpecification(data.get('collectionId'))

    def serialize(self) -> dict:
        return {
            'collectionId': self.collection_id
        }


class IndexImageJob(Job):
    type = JobType.index_image
    specification_type = IndexImageSpecification

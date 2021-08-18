from typing import Optional

from data_engineering_pulumi_components.aws import (
    BucketPutPermissionsArgs,
    CopyObjectFunction,
    CuratedBucket,
    RawHistoryBucket,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions
from pulumi_aws import Provider

# Should be depricated in near future due to Glue Component,
# but left in currently to ensure compatibility


class RawHistoryToCuratedPipeline(ComponentResource):
    def __init__(
        self,
        name: str,
        raw_history_bucket: RawHistoryBucket,
        tagger: Tagger,
        curated_bucket_provider: Optional[Provider] = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            t=(
                "data-engineering-pulumi-components:pipelines:"
                "RawHistoryToCuratedPipeline"
            ),
            name=name,
            props=None,
            opts=opts,
        )

        self._curatedBucket = CuratedBucket(
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self, provider=curated_bucket_provider),
        )

        self._copyObjectFunction = CopyObjectFunction(
            destination_bucket=self._curatedBucket,
            name=name,
            source_bucket=raw_history_bucket,
            tagger=tagger,
            opts=ResourceOptions(parent=self),
        )

        self._curatedBucket.add_put_permissions(
            put_permissions=[
                BucketPutPermissionsArgs(principal=self._copyObjectFunction._role.arn)
            ],
        )

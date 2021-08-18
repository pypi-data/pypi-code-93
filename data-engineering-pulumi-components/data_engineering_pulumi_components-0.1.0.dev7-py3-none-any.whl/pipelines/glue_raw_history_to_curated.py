from data_engineering_pulumi_components.aws.glue_move_job import GlueComponent
from typing import Optional

from data_engineering_pulumi_components.aws import (
    BucketPutPermissionsArgs,
    CuratedBucket,
    RawHistoryBucket,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions
from pulumi_aws import Provider


class GlueRawHistoryToCuratedPipeline(ComponentResource):
    def __init__(
        self,
        name: str,
        raw_history_bucket: RawHistoryBucket,
        tagger: Tagger,
        glue_script: str = None,
        curated_bucket_provider: Optional[Provider] = None,
        test_trigger: bool = False,
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

        if glue_script is not None:
            self._glueMoveJob = GlueComponent(
                destination_bucket=self._curatedBucket,
                name=name,
                source_bucket=raw_history_bucket,
                tagger=tagger,
                glue_script=glue_script,
                test_trigger=test_trigger,
                opts=ResourceOptions(parent=self, depends_on=[self._curatedBucket]),
            )
        else:
            self._glueMoveJob = GlueComponent(
                destination_bucket=self._curatedBucket,
                name=name,
                source_bucket=raw_history_bucket,
                tagger=tagger,
                test_trigger=test_trigger,
                opts=ResourceOptions(parent=self, depends_on=[self._curatedBucket]),
            )

        self._curatedBucket.add_put_permissions(
            put_permissions=[
                BucketPutPermissionsArgs(principal=self._glueMoveJob._role.arn)
            ],
            glue_permissions=True,
        )

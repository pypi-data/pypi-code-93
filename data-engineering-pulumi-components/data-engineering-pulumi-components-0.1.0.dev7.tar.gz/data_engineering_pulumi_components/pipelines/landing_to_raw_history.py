from typing import Optional

from data_engineering_pulumi_components.aws import (
    LandingBucket,
    RawHistoryBucket,
    FailBucket,
    ValidateMoveObjectFunction,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions


class LandingToRawHistoryPipeline(ComponentResource):
    def __init__(
        self,
        name: str,
        aws_arn_for_put_permission: str,
        tagger: Tagger,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            t=(
                "data-engineering-pulumi-components:pipelines:"
                "LandingToRawHistoryPipeline"
            ),
            name=name,
            props=None,
            opts=opts,
        )

        self._landing_bucket = LandingBucket(
            name=name,
            aws_arn_for_put_permission=aws_arn_for_put_permission,
            tagger=tagger,
            opts=ResourceOptions(parent=self),
        )

        self._raw_history_bucket = RawHistoryBucket(
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self),
        )

        self._fail_bucket = FailBucket(
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self),
        )

        self._validate_move_object_function = ValidateMoveObjectFunction(
            pass_bucket=self._raw_history_bucket,
            fail_bucket=self._fail_bucket,
            name=name,
            source_bucket=self._landing_bucket,
            opts=ResourceOptions(
                parent=self,
                depends_on=[
                    self._raw_history_bucket,
                    self._fail_bucket,
                    self._landing_bucket,
                ],
            ),
            tagger=tagger,
        )

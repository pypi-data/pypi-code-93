from typing import Optional

from data_engineering_pulumi_components.aws.bucket import (
    Bucket,
    BucketPutPermissionsArgs,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ResourceOptions


class LandingBucket(Bucket):
    def __init__(
        self,
        name: str,
        aws_arn_for_put_permission: str,
        tagger: Tagger,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            name=name + "-landing",
            t="data-engineering-pulumi-components:aws:LandingBucket",
            put_permissions=[
                BucketPutPermissionsArgs(
                    aws_arn_for_put_permission, allow_anonymous_users=False
                )
            ],
            tagger=tagger,
            opts=opts,
        )

import json
from pathlib import Path
from typing import Optional

from data_engineering_pulumi_components.aws import Bucket
from data_engineering_pulumi_components.aws.lambda_.copy_ import copy_
from data_engineering_pulumi_components.utils import Tagger
from pulumi import AssetArchive, ComponentResource, FileArchive, Output, ResourceOptions
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, Permission
from pulumi_aws.s3 import BucketNotification, BucketNotificationLambdaFunctionArgs


class CopyObjectFunction(ComponentResource):
    def __init__(
        self,
        destination_bucket: Bucket,
        name: str,
        source_bucket: Bucket,
        tagger: Tagger,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provides a Lambda function that copies objects from a source bucket to a
        destination bucket.

        Parameters
        ----------
        destination_bucket : Bucket
            The bucket to copy data to.
        name : str
            The name of the resource.
        source_bucket : Bucket
            The bucket to copy data from.
        tagger : Tagger
            A tagger resource.
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:CopyObjectFunction",
            name=name,
            props=None,
            opts=opts,
        )

        self._role = Role(
            resource_name=f"{name}-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
            name=f"{name}-copy",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-copy"),
            opts=ResourceOptions(parent=self),
        )
        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-role-policy",
            name="s3-access",
            policy=Output.all(source_bucket.arn, destination_bucket.arn).apply(
                lambda args: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "GetSourceBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[0]}/*"],
                                "Action": ["s3:GetObject*"],
                            },
                            {
                                "Sid": "PutDestinationBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[1]}/*"],
                                "Action": ["s3:PutObject*"],
                            },
                        ],
                    }
                )
            ),
            role=self._role.id,
            opts=ResourceOptions(parent=self._role),
        )
        self._rolePolicyAttachment = RolePolicyAttachment(
            resource_name=f"{name}-role-policy-attachment",
            policy_arn=(
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            ),
            role=self._role.name,
            opts=ResourceOptions(parent=self._role),
        )
        self._function = Function(
            resource_name=f"{name}-function",
            code=AssetArchive(
                assets={
                    ".": FileArchive(path=str(Path(copy_.__file__).absolute().parent))
                }
            ),
            description=Output.all(source_bucket.name, destination_bucket.name).apply(
                lambda args: f"Copies data from {args[0]} to {args[1]}"
            ),
            environment=destination_bucket.name.apply(
                lambda name: FunctionEnvironmentArgs(
                    variables={"DESTINATION_BUCKET": name}
                )
            ),
            handler="copy_.handler",
            name=f"{name}-copy",
            role=self._role.arn,
            runtime="python3.8",
            tags=tagger.create_tags(f"{name}-copy"),
            timeout=300,
            opts=ResourceOptions(parent=self),
        )
        self._permission = Permission(
            resource_name=f"{name}-permission",
            action="lambda:InvokeFunction",
            function=self._function.arn,
            principal="s3.amazonaws.com",
            source_arn=source_bucket.arn,
            opts=ResourceOptions(parent=self._function),
        )
        self._bucketNotification = BucketNotification(
            resource_name=f"{name}-bucket-notification",
            bucket=source_bucket.id,
            lambda_functions=[
                BucketNotificationLambdaFunctionArgs(
                    events=["s3:ObjectCreated:*"],
                    lambda_function_arn=self._function.arn,
                )
            ],
            opts=ResourceOptions(parent=self._permission),
        )

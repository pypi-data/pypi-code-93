import json
from typing import Optional
import os

from data_engineering_pulumi_components.aws import Bucket
from data_engineering_pulumi_components.utils import Tagger
from pulumi import (
    ComponentResource,
    Output,
    ResourceOptions,
    FileAsset,
)
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment
from pulumi_aws.glue import (
    Job,
    JobArgs,
    JobCommandArgs,
    JobExecutionPropertyArgs,
    SecurityConfiguration,
    Trigger,
    TriggerActionArgs,
)
from pulumi_aws.s3 import BucketObject


class GlueComponent(ComponentResource):
    def __init__(
        self,
        destination_bucket: Bucket,
        name: str,
        source_bucket: Bucket,
        tagger: Tagger,
        glue_script: str = os.path.join(
            os.path.dirname(__file__), "glue_move_script.py"
        ),
        test_trigger: bool = False,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provides a Glue Component that copies objects from a source bucket to a
        destination bucket as a parquet file. This currently only supports .json files,
        but will support other file types in future.

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
        glue_script: str
            File path leading to a valid glue script for the job to run. By default,
            uses the Glue Move Script.
        test_trigger : bool
            In the test environment, the trigger has to go off immediately for tests
            to pass. This, when set to true, will cause an immediate trigger rather
            than a scheduled one. Defaults to False (and thus a 3am schedule).
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:GlueMoveJob",
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
                            "Principal": {"Service": "glue.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
            name=f"{name}-glue-role",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-glue-role"),
            opts=ResourceOptions(parent=self),
        )
        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-role-policy",
            name="AWSGlueServiceRole-Glue-s3-access",
            policy=Output.all(source_bucket.arn, destination_bucket.arn).apply(
                lambda args: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "GetSourceBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[0]}/*"],
                                "Action": [
                                    "s3:GetObject*",
                                    "s3:PutObject*",
                                    "s3:ListBucket*",
                                    "s3:DeleteObject*",
                                ],
                            },
                            {
                                "Sid": "PutDestinationBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[1]}"] + [f"{args[1]}/*"],
                                "Action": [
                                    "s3:GetObject*",
                                    "s3:PutObject*",
                                    "s3:ListBucket*",
                                    "s3:DeleteObject*",
                                ],
                            },
                        ],
                    }
                ),
            ),
            role=self._role.id,
            opts=ResourceOptions(parent=self._role),
        )
        self._rolePolicyAttachment = RolePolicyAttachment(
            resource_name=f"{name}-role-policy-attachment",
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
            role=self._role.name,
            opts=ResourceOptions(parent=self._role),
        )
        self._glueJobScript = BucketObject(
            resource_name=f"{name}-glue-job-script",
            opts=ResourceOptions(depends_on=[self._rolePolicy]),
            bucket=source_bucket.name,
            key="glue_jobs/glue_move_script.py",
            server_side_encryption="AES256",
            source=FileAsset(glue_script),
            tags=tagger.create_tags(f"{name}-glue-script"),
        )
        self._securityConfiguration = SecurityConfiguration(
            resource_name=f"{name}-security-config",
            opts=ResourceOptions(parent=self),
            encryption_configuration={
                "cloudwatch_encryption": {"cloudwatch_encryption_mode": "DISABLED"},
                "job_bookmarks_encryption": {
                    "job_bookmarks_encryption_mode": "DISABLED"
                },
                "s3_encryption": {"s3_encryption_mode": "SSE-S3"},
            },
            name=f"{name}-security-config",
        )
        self._job = Job(
            resource_name=f"{name}-glue-job",
            args=JobArgs(
                command=JobCommandArgs(
                    script_location=Output.all(
                        self._glueJobScript.bucket, self._glueJobScript.key
                    ).apply(lambda o: f"s3://{o[0]}/{o[1]}"),
                ),
                role_arn=self._role.arn,
                default_arguments={
                    "--source_bucket": source_bucket._name,
                    "--destination_bucket": destination_bucket._name,
                },
                description=f"Populates the {name} curated bucket with parquets",
                execution_property=JobExecutionPropertyArgs(max_concurrent_runs=1),
                glue_version="2.0",
                name=f"{name}-glue-job",
                number_of_workers=2,
                security_configuration=self._securityConfiguration.name,
                tags=tagger.create_tags(f"{name}-glue-job"),
                worker_type="G.1X",
            ),
            opts=ResourceOptions(
                parent=self,
                depends_on=[
                    self._glueJobScript,
                    self._role,
                    self._securityConfiguration,
                ],
            ),
        )
        if test_trigger:
            self._trigger = Trigger(
                resource_name=f"{name}-glue-trigger",
                type="ON_DEMAND",
                actions=[TriggerActionArgs(job_name=self._job.name)],
                opts=ResourceOptions(parent=self, depends_on=[self._job]),
            )
        else:
            self._trigger = Trigger(
                resource_name=f"{name}-glue-trigger",
                schedule="cron(0 3 * * ? *)",
                type="SCHEDULED",
                actions=[TriggerActionArgs(job_name=self._job.name)],
                opts=ResourceOptions(parent=self, depends_on=[self._job]),
            )

import json
from typing import Optional

from data_engineering_pulumi_components.aws import Bucket
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_aws.glue import Crawler, CrawlerS3TargetArgs
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment
from pulumi_aws.athena import Database


class GlueDataCrawler(ComponentResource):
    def __init__(
        self,
        source_bucket: Bucket,
        name: str,
        tagger: Tagger,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provides a component that will create a database from the 'Data' folder
        of a bucket.

        Parameters
        ----------
        source_bucket : Bucket
            The bucket to construct an athena database from.
        name : str
            The name of the resource.
        tagger : Tagger
            A tagger resource.
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:GlueDataCrawler",
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
            name=f"{name}-crawler-role",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-crawler-role"),
            opts=ResourceOptions(parent=self),
        )
        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-role-policy",
            name="AWSGlueServiceRole-Glue-s3-access",
            policy=Output.all(source_bucket.arn).apply(
                lambda args: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "CreateDatabase",
                                "Effect": "Allow",
                                "Resource": [f"{args[0]}/*"],
                                "Action": ["s3:GetObject*", "s3:PutObject*"],
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
            policy_arn=("arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"),
            role=self._role.name,
            opts=ResourceOptions(parent=self._role),
        )
        # Athena Databases only allow underscores for special chars
        db_name = name.replace("-", "_")
        self._database = Database(
            resource_name=f"{name}-database",
            opts=opts,
            bucket=f"{name}-athena-query-bucket",
            name=f"{db_name}",
        )
        self._crawler = Crawler(
            resource_name=f"{name}-crawler",
            opts=ResourceOptions(parent=self, depends_on=[self._database, self._role]),
            database_name=self._database.name,
            role=self._role.arn,
            s3_targets=[CrawlerS3TargetArgs(path=f"s3://{source_bucket._name}/data")],
            schedule="cron(0 3 * * ? *)",
            name=f"{name}-crawler",
        )

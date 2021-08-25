'''
# replace this
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_lambda
import aws_cdk.core


class FlywayConstruct(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="flywaymigrationconstruct.FlywayConstruct",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        vpc: aws_cdk.aws_ec2.Vpc,
        subnet: aws_cdk.aws_ec2.SubnetSelection,
        security_group: aws_cdk.aws_ec2.SecurityGroup,
        bucket_name: builtins.str,
        url: builtins.str,
        user: builtins.str,
        password: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: -
        :param subnet: -
        :param security_group: -
        :param bucket_name: -
        :param url: -
        :param user: -
        :param password: -
        '''
        jsii.create(FlywayConstruct, self, [scope, id, vpc, subnet, security_group, bucket_name, url, user, password])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="flywayLambdaMigration")
    def flyway_lambda_migration(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "flywayLambdaMigration"))

    @flyway_lambda_migration.setter
    def flyway_lambda_migration(self, value: aws_cdk.aws_lambda.Function) -> None:
        jsii.set(self, "flywayLambdaMigration", value)


__all__ = [
    "FlywayConstruct",
]

publication.publish()

'''
# AWS Secrets Manager Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
from aws_cdk import aws_secretsmanager as secretsmanager
```

## Create a new Secret in a Stack

In order to have SecretsManager generate a new secret value automatically,
you can get started with the following:

[example of creating a secret](test/integ.secret.lit.ts)

The `Secret` construct does not allow specifying the `SecretString` property
of the `AWS::SecretsManager::Secret` resource (as this will almost always
lead to the secret being surfaced in plain text and possibly committed to
your source control).

If you need to use a pre-existing secret, the recommended way is to manually
provision the secret in *AWS SecretsManager* and use the `Secret.fromSecretArn`
or `Secret.fromSecretAttributes` method to make it available in your CDK Application:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
secret = secretsmanager.Secret.from_secret_attributes(scope, "ImportedSecret",
    secret_arn="arn:aws:secretsmanager:<region>:<account-id-number>:secret:<secret-name>-<random-6-characters>",
    # If the secret is encrypted using a KMS-hosted CMK, either import or reference that key:
    encryption_key=encryption_key
)
```

SecretsManager secret values can only be used in select set of properties. For the
list of properties, see [the CloudFormation Dynamic References documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html).

A secret can set `RemovalPolicy`. If it set to `RETAIN`, that removing a secret will fail.

## Grant permission to use the secret to a role

You must grant permission to a resource for that resource to be allowed to
use a secret. This can be achieved with the `Secret.grantRead` and/or `Secret.grantUpdate`
method, depending on your need:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
role = iam.Role(stack, "SomeRole", assumed_by=iam.AccountRootPrincipal())
secret = secretsmanager.Secret(stack, "Secret")
secret.grant_read(role)
secret.grant_write(role)
```

If, as in the following example, your secret was created with a KMS key:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
key = kms.Key(stack, "KMS")
secret = secretsmanager.Secret(stack, "Secret", encryption_key=key)
secret.grant_read(role)
secret.grant_write(role)
```

then `Secret.grantRead` and `Secret.grantWrite` will also grant the role the
relevant encrypt and decrypt permissions to the KMS key through the
SecretsManager service principal.

The principal is automatically added to Secret resource policy and KMS Key policy for cross account access:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
other_account = iam.AccountPrincipal("1234")
key = kms.Key(stack, "KMS")
secret = secretsmanager.Secret(stack, "Secret", encryption_key=key)
secret.grant_read(other_account)
```

## Rotating a Secret

### Using a Custom Lambda Function

A rotation schedule can be added to a Secret using a custom Lambda function:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
fn = lambda_.Function(...)
secret = secretsmanager.Secret(self, "Secret")

secret.add_rotation_schedule("RotationSchedule",
    rotation_lambda=fn,
    automatically_after=Duration.days(15)
)
```

Note: The required permissions for Lambda to call SecretsManager and the other way round are automatically granted based on [AWS Documentation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets-required-permissions.html) as long as the Lambda is not imported.

See [Overview of the Lambda Rotation Function](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets-lambda-function-overview.html) on how to implement a Lambda Rotation Function.

### Using a Hosted Lambda Function

Use the `hostedRotation` prop to rotate a secret with a hosted Lambda function:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
secret = secretsmanager.Secret(self, "Secret")

secret.add_rotation_schedule("RotationSchedule",
    hosted_rotation=secretsmanager.HostedRotation.mysql_single_user()
)
```

Hosted rotation is available for secrets representing credentials for MySQL, PostgreSQL, Oracle,
MariaDB, SQLServer, Redshift and MongoDB (both for the single and multi user schemes).

When deployed in a VPC, the hosted rotation implements `ec2.IConnectable`:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
my_hosted_rotation = secretsmanager.HostedRotation.mysql_single_user(vpc=my_vpc)
secret.add_rotation_schedule("RotationSchedule", hosted_rotation=my_hosted_rotation)
db_connections.allow_default_port_from(hosted_rotation)
```

See also [Automating secret creation in AWS CloudFormation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_cloudformation.html).

## Rotating database credentials

Define a `SecretRotation` to rotate database credentials:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
secretsmanager.SecretRotation(self, "SecretRotation",
    application=secretsmanager.SecretRotationApplication.MYSQL_ROTATION_SINGLE_USER, # MySQL single user scheme
    secret=my_secret,
    target=my_database, # a Connectable
    vpc=my_vpc, # The VPC where the secret rotation application will be deployed
    exclude_characters=" %+:;{}"
)
```

The secret must be a JSON string with the following format:

```json
{
  "engine": "<required: database engine>",
  "host": "<required: instance host name>",
  "username": "<required: username>",
  "password": "<required: password>",
  "dbname": "<optional: database name>",
  "port": "<optional: if not specified, default port will be used>",
  "masterarn": "<required for multi user rotation: the arn of the master secret which will be used to create users/change passwords>"
}
```

For the multi user scheme, a `masterSecret` must be specified:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
secretsmanager.SecretRotation(stack, "SecretRotation",
    application=secretsmanager.SecretRotationApplication.MYSQL_ROTATION_MULTI_USER,
    secret=my_user_secret, # The secret that will be rotated
    master_secret=my_master_secret, # The secret used for the rotation
    target=my_database,
    vpc=my_vpc
)
```

See also [aws-rds](https://github.com/aws/aws-cdk/blob/master/packages/%40aws-cdk/aws-rds/README.md) where
credentials generation and rotation is integrated.

## Importing Secrets

Existing secrets can be imported by ARN, name, and other attributes (including the KMS key used to encrypt the secret).
Secrets imported by name should use the short-form of the name (without the SecretsManager-provided suffx);
the secret name must exist in the same account and region as the stack.
Importing by name makes it easier to reference secrets created in different regions, each with their own suffix and ARN.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk import aws_kms as kms


secret_complete_arn = "arn:aws:secretsmanager:eu-west-1:111111111111:secret:MySecret-f3gDy9"
secret_partial_arn = "arn:aws:secretsmanager:eu-west-1:111111111111:secret:MySecret"# No Secrets Manager suffix
encryption_key = kms.Key.from_key_arn(stack, "MyEncKey", "arn:aws:kms:eu-west-1:111111111111:key/21c4b39b-fde2-4273-9ac0-d9bb5c0d0030")
my_secret_from_complete_arn = secretsmanager.Secret.from_secret_complete_arn(stack, "SecretFromCompleteArn", secret_complete_arn)
my_secret_from_partial_arn = secretsmanager.Secret.from_secret_partial_arn(stack, "SecretFromPartialArn", secret_partial_arn)
my_secret_from_name = secretsmanager.Secret.from_secret_name_v2(stack, "SecretFromName", "MySecret")
my_secret_from_attrs = secretsmanager.Secret.from_secret_attributes(stack, "SecretFromAttributes",
    secret_complete_arn=secret_complete_arn,
    encryption_key=encryption_key
)
```

## Replicating secrets

Secrets can be replicated to multiple regions by specifying `replicaRegions`:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
secretsmanager.Secret(self, "Secret",
    replica_regions=[{
        "region": "eu-west-1"
    }, {
        "region": "eu-central-1",
        "encryption_key": my_key
    }
    ]
)
```

Alternatively, use `addReplicaRegion()`:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
secret = secretsmanager.Secret(self, "Secret")
secret.add_replica_region("eu-west-1")
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_e0a482dc,
    CfnTag as _CfnTag_95fbdc29,
    Construct as _Construct_e78e779f,
    Duration as _Duration_070aa057,
    IInspectable as _IInspectable_82c04a63,
    IResolvable as _IResolvable_a771d0ef,
    IResource as _IResource_8c1dbbbd,
    RemovalPolicy as _RemovalPolicy_c97e7a20,
    Resource as _Resource_abff4495,
    SecretValue as _SecretValue_c18506ef,
    TagManager as _TagManager_0b7ab120,
    TreeInspector as _TreeInspector_1cd1894e,
)
from ..aws_ec2 import (
    Connections as _Connections_57ccbda9,
    IConnectable as _IConnectable_c1c0e72c,
    ISecurityGroup as _ISecurityGroup_cdbba9d3,
    IVpc as _IVpc_6d1f76c4,
    SubnetSelection as _SubnetSelection_1284e62c,
)
from ..aws_iam import (
    AddToResourcePolicyResult as _AddToResourcePolicyResult_0fd9d2a9,
    Grant as _Grant_bcb5eae7,
    IGrantable as _IGrantable_4c5a91d1,
    PolicyDocument as _PolicyDocument_b5de5177,
    PolicyStatement as _PolicyStatement_296fe8a3,
)
from ..aws_kms import IKey as _IKey_36930160
from ..aws_lambda import IFunction as _IFunction_6e14f09e


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.AttachedSecretOptions",
    jsii_struct_bases=[],
    name_mapping={"target": "target"},
)
class AttachedSecretOptions:
    def __init__(self, *, target: "ISecretAttachmentTarget") -> None:
        '''(deprecated) Options to add a secret attachment to a secret.

        :param target: (deprecated) The target to attach the secret to.

        :deprecated: use ``secret.attach()`` instead

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
        }

    @builtins.property
    def target(self) -> "ISecretAttachmentTarget":
        '''(deprecated) The target to attach the secret to.

        :stability: deprecated
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast("ISecretAttachmentTarget", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttachedSecretOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_secretsmanager.AttachmentTargetType")
class AttachmentTargetType(enum.Enum):
    '''(experimental) The type of service or database that's being associated with the secret.

    :stability: experimental
    '''

    INSTANCE = "INSTANCE"
    '''(deprecated) A database instance.

    :deprecated: use RDS_DB_INSTANCE instead

    :stability: deprecated
    '''
    CLUSTER = "CLUSTER"
    '''(deprecated) A database cluster.

    :deprecated: use RDS_DB_CLUSTER instead

    :stability: deprecated
    '''
    RDS_DB_PROXY = "RDS_DB_PROXY"
    '''(experimental) AWS::RDS::DBProxy.

    :stability: experimental
    '''
    REDSHIFT_CLUSTER = "REDSHIFT_CLUSTER"
    '''(experimental) AWS::Redshift::Cluster.

    :stability: experimental
    '''
    DOCDB_DB_INSTANCE = "DOCDB_DB_INSTANCE"
    '''(experimental) AWS::DocDB::DBInstance.

    :stability: experimental
    '''
    DOCDB_DB_CLUSTER = "DOCDB_DB_CLUSTER"
    '''(experimental) AWS::DocDB::DBCluster.

    :stability: experimental
    '''


@jsii.implements(_IInspectable_82c04a63)
class CfnResourcePolicy(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.CfnResourcePolicy",
):
    '''A CloudFormation ``AWS::SecretsManager::ResourcePolicy``.

    :cloudformationResource: AWS::SecretsManager::ResourcePolicy
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        resource_policy: typing.Any,
        secret_id: builtins.str,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
    ) -> None:
        '''Create a new ``AWS::SecretsManager::ResourcePolicy``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param resource_policy: ``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.
        :param secret_id: ``AWS::SecretsManager::ResourcePolicy.SecretId``.
        :param block_public_policy: ``AWS::SecretsManager::ResourcePolicy.BlockPublicPolicy``.
        '''
        props = CfnResourcePolicyProps(
            resource_policy=resource_policy,
            secret_id=secret_id,
            block_public_policy=block_public_policy,
        )

        jsii.create(CfnResourcePolicy, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcePolicy")
    def resource_policy(self) -> typing.Any:
        '''``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-resourcepolicy
        '''
        return typing.cast(typing.Any, jsii.get(self, "resourcePolicy"))

    @resource_policy.setter
    def resource_policy(self, value: typing.Any) -> None:
        jsii.set(self, "resourcePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> builtins.str:
        '''``AWS::SecretsManager::ResourcePolicy.SecretId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-secretid
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretId"))

    @secret_id.setter
    def secret_id(self, value: builtins.str) -> None:
        jsii.set(self, "secretId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicy")
    def block_public_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::ResourcePolicy.BlockPublicPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-blockpublicpolicy
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "blockPublicPolicy"))

    @block_public_policy.setter
    def block_public_policy(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "blockPublicPolicy", value)


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.CfnResourcePolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "resource_policy": "resourcePolicy",
        "secret_id": "secretId",
        "block_public_policy": "blockPublicPolicy",
    },
)
class CfnResourcePolicyProps:
    def __init__(
        self,
        *,
        resource_policy: typing.Any,
        secret_id: builtins.str,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::SecretsManager::ResourcePolicy``.

        :param resource_policy: ``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.
        :param secret_id: ``AWS::SecretsManager::ResourcePolicy.SecretId``.
        :param block_public_policy: ``AWS::SecretsManager::ResourcePolicy.BlockPublicPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource_policy": resource_policy,
            "secret_id": secret_id,
        }
        if block_public_policy is not None:
            self._values["block_public_policy"] = block_public_policy

    @builtins.property
    def resource_policy(self) -> typing.Any:
        '''``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-resourcepolicy
        '''
        result = self._values.get("resource_policy")
        assert result is not None, "Required property 'resource_policy' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def secret_id(self) -> builtins.str:
        '''``AWS::SecretsManager::ResourcePolicy.SecretId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-secretid
        '''
        result = self._values.get("secret_id")
        assert result is not None, "Required property 'secret_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_public_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::ResourcePolicy.BlockPublicPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-blockpublicpolicy
        '''
        result = self._values.get("block_public_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResourcePolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnRotationSchedule(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.CfnRotationSchedule",
):
    '''A CloudFormation ``AWS::SecretsManager::RotationSchedule``.

    :cloudformationResource: AWS::SecretsManager::RotationSchedule
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        secret_id: builtins.str,
        hosted_rotation_lambda: typing.Optional[typing.Union["CfnRotationSchedule.HostedRotationLambdaProperty", _IResolvable_a771d0ef]] = None,
        rotation_lambda_arn: typing.Optional[builtins.str] = None,
        rotation_rules: typing.Optional[typing.Union["CfnRotationSchedule.RotationRulesProperty", _IResolvable_a771d0ef]] = None,
    ) -> None:
        '''Create a new ``AWS::SecretsManager::RotationSchedule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param secret_id: ``AWS::SecretsManager::RotationSchedule.SecretId``.
        :param hosted_rotation_lambda: ``AWS::SecretsManager::RotationSchedule.HostedRotationLambda``.
        :param rotation_lambda_arn: ``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.
        :param rotation_rules: ``AWS::SecretsManager::RotationSchedule.RotationRules``.
        '''
        props = CfnRotationScheduleProps(
            secret_id=secret_id,
            hosted_rotation_lambda=hosted_rotation_lambda,
            rotation_lambda_arn=rotation_lambda_arn,
            rotation_rules=rotation_rules,
        )

        jsii.create(CfnRotationSchedule, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> builtins.str:
        '''``AWS::SecretsManager::RotationSchedule.SecretId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-secretid
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretId"))

    @secret_id.setter
    def secret_id(self, value: builtins.str) -> None:
        jsii.set(self, "secretId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedRotationLambda")
    def hosted_rotation_lambda(
        self,
    ) -> typing.Optional[typing.Union["CfnRotationSchedule.HostedRotationLambdaProperty", _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::RotationSchedule.HostedRotationLambda``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda
        '''
        return typing.cast(typing.Optional[typing.Union["CfnRotationSchedule.HostedRotationLambdaProperty", _IResolvable_a771d0ef]], jsii.get(self, "hostedRotationLambda"))

    @hosted_rotation_lambda.setter
    def hosted_rotation_lambda(
        self,
        value: typing.Optional[typing.Union["CfnRotationSchedule.HostedRotationLambdaProperty", _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "hostedRotationLambda", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationLambdaArn")
    def rotation_lambda_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationlambdaarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationLambdaArn"))

    @rotation_lambda_arn.setter
    def rotation_lambda_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "rotationLambdaArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationRules")
    def rotation_rules(
        self,
    ) -> typing.Optional[typing.Union["CfnRotationSchedule.RotationRulesProperty", _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::RotationSchedule.RotationRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationrules
        '''
        return typing.cast(typing.Optional[typing.Union["CfnRotationSchedule.RotationRulesProperty", _IResolvable_a771d0ef]], jsii.get(self, "rotationRules"))

    @rotation_rules.setter
    def rotation_rules(
        self,
        value: typing.Optional[typing.Union["CfnRotationSchedule.RotationRulesProperty", _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "rotationRules", value)

    @jsii.data_type(
        jsii_type="monocdk.aws_secretsmanager.CfnRotationSchedule.HostedRotationLambdaProperty",
        jsii_struct_bases=[],
        name_mapping={
            "rotation_type": "rotationType",
            "kms_key_arn": "kmsKeyArn",
            "master_secret_arn": "masterSecretArn",
            "master_secret_kms_key_arn": "masterSecretKmsKeyArn",
            "rotation_lambda_name": "rotationLambdaName",
            "vpc_security_group_ids": "vpcSecurityGroupIds",
            "vpc_subnet_ids": "vpcSubnetIds",
        },
    )
    class HostedRotationLambdaProperty:
        def __init__(
            self,
            *,
            rotation_type: builtins.str,
            kms_key_arn: typing.Optional[builtins.str] = None,
            master_secret_arn: typing.Optional[builtins.str] = None,
            master_secret_kms_key_arn: typing.Optional[builtins.str] = None,
            rotation_lambda_name: typing.Optional[builtins.str] = None,
            vpc_security_group_ids: typing.Optional[builtins.str] = None,
            vpc_subnet_ids: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param rotation_type: ``CfnRotationSchedule.HostedRotationLambdaProperty.RotationType``.
            :param kms_key_arn: ``CfnRotationSchedule.HostedRotationLambdaProperty.KmsKeyArn``.
            :param master_secret_arn: ``CfnRotationSchedule.HostedRotationLambdaProperty.MasterSecretArn``.
            :param master_secret_kms_key_arn: ``CfnRotationSchedule.HostedRotationLambdaProperty.MasterSecretKmsKeyArn``.
            :param rotation_lambda_name: ``CfnRotationSchedule.HostedRotationLambdaProperty.RotationLambdaName``.
            :param vpc_security_group_ids: ``CfnRotationSchedule.HostedRotationLambdaProperty.VpcSecurityGroupIds``.
            :param vpc_subnet_ids: ``CfnRotationSchedule.HostedRotationLambdaProperty.VpcSubnetIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "rotation_type": rotation_type,
            }
            if kms_key_arn is not None:
                self._values["kms_key_arn"] = kms_key_arn
            if master_secret_arn is not None:
                self._values["master_secret_arn"] = master_secret_arn
            if master_secret_kms_key_arn is not None:
                self._values["master_secret_kms_key_arn"] = master_secret_kms_key_arn
            if rotation_lambda_name is not None:
                self._values["rotation_lambda_name"] = rotation_lambda_name
            if vpc_security_group_ids is not None:
                self._values["vpc_security_group_ids"] = vpc_security_group_ids
            if vpc_subnet_ids is not None:
                self._values["vpc_subnet_ids"] = vpc_subnet_ids

        @builtins.property
        def rotation_type(self) -> builtins.str:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.RotationType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-rotationtype
            '''
            result = self._values.get("rotation_type")
            assert result is not None, "Required property 'rotation_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def kms_key_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-kmskeyarn
            '''
            result = self._values.get("kms_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def master_secret_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.MasterSecretArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-mastersecretarn
            '''
            result = self._values.get("master_secret_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def master_secret_kms_key_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.MasterSecretKmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-mastersecretkmskeyarn
            '''
            result = self._values.get("master_secret_kms_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def rotation_lambda_name(self) -> typing.Optional[builtins.str]:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.RotationLambdaName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-rotationlambdaname
            '''
            result = self._values.get("rotation_lambda_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def vpc_security_group_ids(self) -> typing.Optional[builtins.str]:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.VpcSecurityGroupIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-vpcsecuritygroupids
            '''
            result = self._values.get("vpc_security_group_ids")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def vpc_subnet_ids(self) -> typing.Optional[builtins.str]:
            '''``CfnRotationSchedule.HostedRotationLambdaProperty.VpcSubnetIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-hostedrotationlambda.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda-vpcsubnetids
            '''
            result = self._values.get("vpc_subnet_ids")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HostedRotationLambdaProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="monocdk.aws_secretsmanager.CfnRotationSchedule.RotationRulesProperty",
        jsii_struct_bases=[],
        name_mapping={"automatically_after_days": "automaticallyAfterDays"},
    )
    class RotationRulesProperty:
        def __init__(
            self,
            *,
            automatically_after_days: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param automatically_after_days: ``CfnRotationSchedule.RotationRulesProperty.AutomaticallyAfterDays``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-rotationrules.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if automatically_after_days is not None:
                self._values["automatically_after_days"] = automatically_after_days

        @builtins.property
        def automatically_after_days(self) -> typing.Optional[jsii.Number]:
            '''``CfnRotationSchedule.RotationRulesProperty.AutomaticallyAfterDays``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-rotationrules.html#cfn-secretsmanager-rotationschedule-rotationrules-automaticallyafterdays
            '''
            result = self._values.get("automatically_after_days")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RotationRulesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.CfnRotationScheduleProps",
    jsii_struct_bases=[],
    name_mapping={
        "secret_id": "secretId",
        "hosted_rotation_lambda": "hostedRotationLambda",
        "rotation_lambda_arn": "rotationLambdaArn",
        "rotation_rules": "rotationRules",
    },
)
class CfnRotationScheduleProps:
    def __init__(
        self,
        *,
        secret_id: builtins.str,
        hosted_rotation_lambda: typing.Optional[typing.Union[CfnRotationSchedule.HostedRotationLambdaProperty, _IResolvable_a771d0ef]] = None,
        rotation_lambda_arn: typing.Optional[builtins.str] = None,
        rotation_rules: typing.Optional[typing.Union[CfnRotationSchedule.RotationRulesProperty, _IResolvable_a771d0ef]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::SecretsManager::RotationSchedule``.

        :param secret_id: ``AWS::SecretsManager::RotationSchedule.SecretId``.
        :param hosted_rotation_lambda: ``AWS::SecretsManager::RotationSchedule.HostedRotationLambda``.
        :param rotation_lambda_arn: ``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.
        :param rotation_rules: ``AWS::SecretsManager::RotationSchedule.RotationRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret_id": secret_id,
        }
        if hosted_rotation_lambda is not None:
            self._values["hosted_rotation_lambda"] = hosted_rotation_lambda
        if rotation_lambda_arn is not None:
            self._values["rotation_lambda_arn"] = rotation_lambda_arn
        if rotation_rules is not None:
            self._values["rotation_rules"] = rotation_rules

    @builtins.property
    def secret_id(self) -> builtins.str:
        '''``AWS::SecretsManager::RotationSchedule.SecretId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-secretid
        '''
        result = self._values.get("secret_id")
        assert result is not None, "Required property 'secret_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_rotation_lambda(
        self,
    ) -> typing.Optional[typing.Union[CfnRotationSchedule.HostedRotationLambdaProperty, _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::RotationSchedule.HostedRotationLambda``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-hostedrotationlambda
        '''
        result = self._values.get("hosted_rotation_lambda")
        return typing.cast(typing.Optional[typing.Union[CfnRotationSchedule.HostedRotationLambdaProperty, _IResolvable_a771d0ef]], result)

    @builtins.property
    def rotation_lambda_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationlambdaarn
        '''
        result = self._values.get("rotation_lambda_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_rules(
        self,
    ) -> typing.Optional[typing.Union[CfnRotationSchedule.RotationRulesProperty, _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::RotationSchedule.RotationRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationrules
        '''
        result = self._values.get("rotation_rules")
        return typing.cast(typing.Optional[typing.Union[CfnRotationSchedule.RotationRulesProperty, _IResolvable_a771d0ef]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRotationScheduleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnSecret(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.CfnSecret",
):
    '''A CloudFormation ``AWS::SecretsManager::Secret``.

    :cloudformationResource: AWS::SecretsManager::Secret
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        generate_secret_string: typing.Optional[typing.Union["CfnSecret.GenerateSecretStringProperty", _IResolvable_a771d0ef]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        replica_regions: typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.Sequence[typing.Union["CfnSecret.ReplicaRegionProperty", _IResolvable_a771d0ef]]]] = None,
        secret_string: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::SecretsManager::Secret``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::SecretsManager::Secret.Description``.
        :param generate_secret_string: ``AWS::SecretsManager::Secret.GenerateSecretString``.
        :param kms_key_id: ``AWS::SecretsManager::Secret.KmsKeyId``.
        :param name: ``AWS::SecretsManager::Secret.Name``.
        :param replica_regions: ``AWS::SecretsManager::Secret.ReplicaRegions``.
        :param secret_string: ``AWS::SecretsManager::Secret.SecretString``.
        :param tags: ``AWS::SecretsManager::Secret.Tags``.
        '''
        props = CfnSecretProps(
            description=description,
            generate_secret_string=generate_secret_string,
            kms_key_id=kms_key_id,
            name=name,
            replica_regions=replica_regions,
            secret_string=secret_string,
            tags=tags,
        )

        jsii.create(CfnSecret, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::SecretsManager::Secret.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecretString")
    def generate_secret_string(
        self,
    ) -> typing.Optional[typing.Union["CfnSecret.GenerateSecretStringProperty", _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::Secret.GenerateSecretString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-generatesecretstring
        '''
        return typing.cast(typing.Optional[typing.Union["CfnSecret.GenerateSecretStringProperty", _IResolvable_a771d0ef]], jsii.get(self, "generateSecretString"))

    @generate_secret_string.setter
    def generate_secret_string(
        self,
        value: typing.Optional[typing.Union["CfnSecret.GenerateSecretStringProperty", _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "generateSecretString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaRegions")
    def replica_regions(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnSecret.ReplicaRegionProperty", _IResolvable_a771d0ef]]]]:
        '''``AWS::SecretsManager::Secret.ReplicaRegions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-replicaregions
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnSecret.ReplicaRegionProperty", _IResolvable_a771d0ef]]]], jsii.get(self, "replicaRegions"))

    @replica_regions.setter
    def replica_regions(
        self,
        value: typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnSecret.ReplicaRegionProperty", _IResolvable_a771d0ef]]]],
    ) -> None:
        jsii.set(self, "replicaRegions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretString")
    def secret_string(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.SecretString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-secretstring
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretString"))

    @secret_string.setter
    def secret_string(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "secretString", value)

    @jsii.data_type(
        jsii_type="monocdk.aws_secretsmanager.CfnSecret.GenerateSecretStringProperty",
        jsii_struct_bases=[],
        name_mapping={
            "exclude_characters": "excludeCharacters",
            "exclude_lowercase": "excludeLowercase",
            "exclude_numbers": "excludeNumbers",
            "exclude_punctuation": "excludePunctuation",
            "exclude_uppercase": "excludeUppercase",
            "generate_string_key": "generateStringKey",
            "include_space": "includeSpace",
            "password_length": "passwordLength",
            "require_each_included_type": "requireEachIncludedType",
            "secret_string_template": "secretStringTemplate",
        },
    )
    class GenerateSecretStringProperty:
        def __init__(
            self,
            *,
            exclude_characters: typing.Optional[builtins.str] = None,
            exclude_lowercase: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            exclude_numbers: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            exclude_punctuation: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            exclude_uppercase: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            generate_string_key: typing.Optional[builtins.str] = None,
            include_space: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            password_length: typing.Optional[jsii.Number] = None,
            require_each_included_type: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
            secret_string_template: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param exclude_characters: ``CfnSecret.GenerateSecretStringProperty.ExcludeCharacters``.
            :param exclude_lowercase: ``CfnSecret.GenerateSecretStringProperty.ExcludeLowercase``.
            :param exclude_numbers: ``CfnSecret.GenerateSecretStringProperty.ExcludeNumbers``.
            :param exclude_punctuation: ``CfnSecret.GenerateSecretStringProperty.ExcludePunctuation``.
            :param exclude_uppercase: ``CfnSecret.GenerateSecretStringProperty.ExcludeUppercase``.
            :param generate_string_key: ``CfnSecret.GenerateSecretStringProperty.GenerateStringKey``.
            :param include_space: ``CfnSecret.GenerateSecretStringProperty.IncludeSpace``.
            :param password_length: ``CfnSecret.GenerateSecretStringProperty.PasswordLength``.
            :param require_each_included_type: ``CfnSecret.GenerateSecretStringProperty.RequireEachIncludedType``.
            :param secret_string_template: ``CfnSecret.GenerateSecretStringProperty.SecretStringTemplate``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if exclude_characters is not None:
                self._values["exclude_characters"] = exclude_characters
            if exclude_lowercase is not None:
                self._values["exclude_lowercase"] = exclude_lowercase
            if exclude_numbers is not None:
                self._values["exclude_numbers"] = exclude_numbers
            if exclude_punctuation is not None:
                self._values["exclude_punctuation"] = exclude_punctuation
            if exclude_uppercase is not None:
                self._values["exclude_uppercase"] = exclude_uppercase
            if generate_string_key is not None:
                self._values["generate_string_key"] = generate_string_key
            if include_space is not None:
                self._values["include_space"] = include_space
            if password_length is not None:
                self._values["password_length"] = password_length
            if require_each_included_type is not None:
                self._values["require_each_included_type"] = require_each_included_type
            if secret_string_template is not None:
                self._values["secret_string_template"] = secret_string_template

        @builtins.property
        def exclude_characters(self) -> typing.Optional[builtins.str]:
            '''``CfnSecret.GenerateSecretStringProperty.ExcludeCharacters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludecharacters
            '''
            result = self._values.get("exclude_characters")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def exclude_lowercase(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnSecret.GenerateSecretStringProperty.ExcludeLowercase``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludelowercase
            '''
            result = self._values.get("exclude_lowercase")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def exclude_numbers(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnSecret.GenerateSecretStringProperty.ExcludeNumbers``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludenumbers
            '''
            result = self._values.get("exclude_numbers")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def exclude_punctuation(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnSecret.GenerateSecretStringProperty.ExcludePunctuation``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludepunctuation
            '''
            result = self._values.get("exclude_punctuation")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def exclude_uppercase(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnSecret.GenerateSecretStringProperty.ExcludeUppercase``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludeuppercase
            '''
            result = self._values.get("exclude_uppercase")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def generate_string_key(self) -> typing.Optional[builtins.str]:
            '''``CfnSecret.GenerateSecretStringProperty.GenerateStringKey``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-generatestringkey
            '''
            result = self._values.get("generate_string_key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def include_space(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnSecret.GenerateSecretStringProperty.IncludeSpace``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-includespace
            '''
            result = self._values.get("include_space")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def password_length(self) -> typing.Optional[jsii.Number]:
            '''``CfnSecret.GenerateSecretStringProperty.PasswordLength``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-passwordlength
            '''
            result = self._values.get("password_length")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def require_each_included_type(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''``CfnSecret.GenerateSecretStringProperty.RequireEachIncludedType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-requireeachincludedtype
            '''
            result = self._values.get("require_each_included_type")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        @builtins.property
        def secret_string_template(self) -> typing.Optional[builtins.str]:
            '''``CfnSecret.GenerateSecretStringProperty.SecretStringTemplate``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-secretstringtemplate
            '''
            result = self._values.get("secret_string_template")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GenerateSecretStringProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="monocdk.aws_secretsmanager.CfnSecret.ReplicaRegionProperty",
        jsii_struct_bases=[],
        name_mapping={"region": "region", "kms_key_id": "kmsKeyId"},
    )
    class ReplicaRegionProperty:
        def __init__(
            self,
            *,
            region: builtins.str,
            kms_key_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param region: ``CfnSecret.ReplicaRegionProperty.Region``.
            :param kms_key_id: ``CfnSecret.ReplicaRegionProperty.KmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-replicaregion.html
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "region": region,
            }
            if kms_key_id is not None:
                self._values["kms_key_id"] = kms_key_id

        @builtins.property
        def region(self) -> builtins.str:
            '''``CfnSecret.ReplicaRegionProperty.Region``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-replicaregion.html#cfn-secretsmanager-secret-replicaregion-region
            '''
            result = self._values.get("region")
            assert result is not None, "Required property 'region' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def kms_key_id(self) -> typing.Optional[builtins.str]:
            '''``CfnSecret.ReplicaRegionProperty.KmsKeyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-replicaregion.html#cfn-secretsmanager-secret-replicaregion-kmskeyid
            '''
            result = self._values.get("kms_key_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ReplicaRegionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.CfnSecretProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "generate_secret_string": "generateSecretString",
        "kms_key_id": "kmsKeyId",
        "name": "name",
        "replica_regions": "replicaRegions",
        "secret_string": "secretString",
        "tags": "tags",
    },
)
class CfnSecretProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        generate_secret_string: typing.Optional[typing.Union[CfnSecret.GenerateSecretStringProperty, _IResolvable_a771d0ef]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        replica_regions: typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.Sequence[typing.Union[CfnSecret.ReplicaRegionProperty, _IResolvable_a771d0ef]]]] = None,
        secret_string: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::SecretsManager::Secret``.

        :param description: ``AWS::SecretsManager::Secret.Description``.
        :param generate_secret_string: ``AWS::SecretsManager::Secret.GenerateSecretString``.
        :param kms_key_id: ``AWS::SecretsManager::Secret.KmsKeyId``.
        :param name: ``AWS::SecretsManager::Secret.Name``.
        :param replica_regions: ``AWS::SecretsManager::Secret.ReplicaRegions``.
        :param secret_string: ``AWS::SecretsManager::Secret.SecretString``.
        :param tags: ``AWS::SecretsManager::Secret.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if generate_secret_string is not None:
            self._values["generate_secret_string"] = generate_secret_string
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if name is not None:
            self._values["name"] = name
        if replica_regions is not None:
            self._values["replica_regions"] = replica_regions
        if secret_string is not None:
            self._values["secret_string"] = secret_string
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def generate_secret_string(
        self,
    ) -> typing.Optional[typing.Union[CfnSecret.GenerateSecretStringProperty, _IResolvable_a771d0ef]]:
        '''``AWS::SecretsManager::Secret.GenerateSecretString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-generatesecretstring
        '''
        result = self._values.get("generate_secret_string")
        return typing.cast(typing.Optional[typing.Union[CfnSecret.GenerateSecretStringProperty, _IResolvable_a771d0ef]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replica_regions(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union[CfnSecret.ReplicaRegionProperty, _IResolvable_a771d0ef]]]]:
        '''``AWS::SecretsManager::Secret.ReplicaRegions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-replicaregions
        '''
        result = self._values.get("replica_regions")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union[CfnSecret.ReplicaRegionProperty, _IResolvable_a771d0ef]]]], result)

    @builtins.property
    def secret_string(self) -> typing.Optional[builtins.str]:
        '''``AWS::SecretsManager::Secret.SecretString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-secretstring
        '''
        result = self._values.get("secret_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::SecretsManager::Secret.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnSecretTargetAttachment(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.CfnSecretTargetAttachment",
):
    '''A CloudFormation ``AWS::SecretsManager::SecretTargetAttachment``.

    :cloudformationResource: AWS::SecretsManager::SecretTargetAttachment
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        secret_id: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
    ) -> None:
        '''Create a new ``AWS::SecretsManager::SecretTargetAttachment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param secret_id: ``AWS::SecretsManager::SecretTargetAttachment.SecretId``.
        :param target_id: ``AWS::SecretsManager::SecretTargetAttachment.TargetId``.
        :param target_type: ``AWS::SecretsManager::SecretTargetAttachment.TargetType``.
        '''
        props = CfnSecretTargetAttachmentProps(
            secret_id=secret_id, target_id=target_id, target_type=target_type
        )

        jsii.create(CfnSecretTargetAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> builtins.str:
        '''``AWS::SecretsManager::SecretTargetAttachment.SecretId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-secretid
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretId"))

    @secret_id.setter
    def secret_id(self, value: builtins.str) -> None:
        jsii.set(self, "secretId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> builtins.str:
        '''``AWS::SecretsManager::SecretTargetAttachment.TargetId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targetid
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetId"))

    @target_id.setter
    def target_id(self, value: builtins.str) -> None:
        jsii.set(self, "targetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetType")
    def target_type(self) -> builtins.str:
        '''``AWS::SecretsManager::SecretTargetAttachment.TargetType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targettype
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetType"))

    @target_type.setter
    def target_type(self, value: builtins.str) -> None:
        jsii.set(self, "targetType", value)


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.CfnSecretTargetAttachmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "secret_id": "secretId",
        "target_id": "targetId",
        "target_type": "targetType",
    },
)
class CfnSecretTargetAttachmentProps:
    def __init__(
        self,
        *,
        secret_id: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::SecretsManager::SecretTargetAttachment``.

        :param secret_id: ``AWS::SecretsManager::SecretTargetAttachment.SecretId``.
        :param target_id: ``AWS::SecretsManager::SecretTargetAttachment.TargetId``.
        :param target_type: ``AWS::SecretsManager::SecretTargetAttachment.TargetType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret_id": secret_id,
            "target_id": target_id,
            "target_type": target_type,
        }

    @builtins.property
    def secret_id(self) -> builtins.str:
        '''``AWS::SecretsManager::SecretTargetAttachment.SecretId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-secretid
        '''
        result = self._values.get("secret_id")
        assert result is not None, "Required property 'secret_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''``AWS::SecretsManager::SecretTargetAttachment.TargetId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targetid
        '''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> builtins.str:
        '''``AWS::SecretsManager::SecretTargetAttachment.TargetType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targettype
        '''
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSecretTargetAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IConnectable_c1c0e72c)
class HostedRotation(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.HostedRotation",
):
    '''(experimental) A hosted rotation.

    :stability: experimental
    '''

    @jsii.member(jsii_name="mariaDbMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def maria_db_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) MariaDB Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "mariaDbMultiUser", [options]))

    @jsii.member(jsii_name="mariaDbSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def maria_db_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) MariaDB Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "mariaDbSingleUser", [options]))

    @jsii.member(jsii_name="mongoDbMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def mongo_db_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) MongoDB Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "mongoDbMultiUser", [options]))

    @jsii.member(jsii_name="mongoDbSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def mongo_db_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) MongoDB Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "mongoDbSingleUser", [options]))

    @jsii.member(jsii_name="mysqlMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def mysql_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) MySQL Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "mysqlMultiUser", [options]))

    @jsii.member(jsii_name="mysqlSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def mysql_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) MySQL Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "mysqlSingleUser", [options]))

    @jsii.member(jsii_name="oracleMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def oracle_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) Oracle Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "oracleMultiUser", [options]))

    @jsii.member(jsii_name="oracleSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def oracle_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) Oracle Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "oracleSingleUser", [options]))

    @jsii.member(jsii_name="postgreSqlMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def postgre_sql_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) PostgreSQL Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "postgreSqlMultiUser", [options]))

    @jsii.member(jsii_name="postgreSqlSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def postgre_sql_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) PostgreSQL Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "postgreSqlSingleUser", [options]))

    @jsii.member(jsii_name="redshiftMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def redshift_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) Redshift Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "redshiftMultiUser", [options]))

    @jsii.member(jsii_name="redshiftSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def redshift_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) Redshift Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "redshiftSingleUser", [options]))

    @jsii.member(jsii_name="sqlServerMultiUser") # type: ignore[misc]
    @builtins.classmethod
    def sql_server_multi_user(
        cls,
        *,
        master_secret: "ISecret",
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) SQL Server Multi User.

        :param master_secret: (experimental) The master secret for a multi user rotation scheme.
        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = MultiUserHostedRotationOptions(
            master_secret=master_secret,
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "sqlServerMultiUser", [options]))

    @jsii.member(jsii_name="sqlServerSingleUser") # type: ignore[misc]
    @builtins.classmethod
    def sql_server_single_user(
        cls,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> "HostedRotation":
        '''(experimental) SQL Server Single User.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        options = SingleUserHostedRotationOptions(
            function_name=function_name,
            security_groups=security_groups,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("HostedRotation", jsii.sinvoke(cls, "sqlServerSingleUser", [options]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        secret: "ISecret",
        scope: constructs.Construct,
    ) -> CfnRotationSchedule.HostedRotationLambdaProperty:
        '''(experimental) Binds this hosted rotation to a secret.

        :param secret: -
        :param scope: -

        :stability: experimental
        '''
        return typing.cast(CfnRotationSchedule.HostedRotationLambdaProperty, jsii.invoke(self, "bind", [secret, scope]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> _Connections_57ccbda9:
        '''(experimental) Security group connections for this hosted rotation.

        :stability: experimental
        '''
        return typing.cast(_Connections_57ccbda9, jsii.get(self, "connections"))


class HostedRotationType(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.HostedRotationType",
):
    '''(experimental) Hosted rotation type.

    :stability: experimental
    '''

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MARIADB_MULTI_USER")
    def MARIADB_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) MariaDB Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "MARIADB_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MARIADB_SINGLE_USER")
    def MARIADB_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) MariaDB Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "MARIADB_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MONGODB_MULTI_USER")
    def MONGODB_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) MongoDB Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "MONGODB_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MONGODB_SINGLE_USER")
    def MONGODB_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) MongoDB Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "MONGODB_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MYSQL_MULTI_USER")
    def MYSQL_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) MySQL Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "MYSQL_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MYSQL_SINGLE_USER")
    def MYSQL_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) MySQL Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "MYSQL_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ORACLE_MULTI_USER")
    def ORACLE_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) Oracle Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "ORACLE_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ORACLE_SINGLE_USER")
    def ORACLE_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) Oracle Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "ORACLE_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POSTGRESQL_MULTI_USER")
    def POSTGRESQL_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) PostgreSQL Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "POSTGRESQL_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POSTGRESQL_SINGLE_USER")
    def POSTGRESQL_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) PostgreSQL Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "POSTGRESQL_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="REDSHIFT_MULTI_USER")
    def REDSHIFT_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) Redshift Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "REDSHIFT_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="REDSHIFT_SINGLE_USER")
    def REDSHIFT_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) Redshift Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "REDSHIFT_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SQLSERVER_MULTI_USER")
    def SQLSERVER_MULTI_USER(cls) -> "HostedRotationType":
        '''(experimental) SQL Server Multi User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "SQLSERVER_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SQLSERVER_SINGLE_USER")
    def SQLSERVER_SINGLE_USER(cls) -> "HostedRotationType":
        '''(experimental) SQL Server Single User.

        :stability: experimental
        '''
        return typing.cast("HostedRotationType", jsii.sget(cls, "SQLSERVER_SINGLE_USER"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The type of rotation.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isMultiUser")
    def is_multi_user(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the rotation uses the mutli user scheme.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "isMultiUser"))


@jsii.interface(jsii_type="monocdk.aws_secretsmanager.ISecret")
class ISecret(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) A secret in AWS Secrets Manager.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) The ARN of the secret in AWS Secrets Manager.

        Will return the full ARN if available, otherwise a partial arn.
        For secrets imported by the deprecated ``fromSecretName``, it will return the ``secretName``.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        '''(experimental) The name of the secret.

        For "owned" secrets, this will be the full resource name (secret name + suffix), unless the
        '@aws-cdk/aws-secretsmanager:parseOwnedSecretName' feature flag is set.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> _SecretValue_c18506ef:
        '''(experimental) Retrieve the value of the stored secret as a ``SecretValue``.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretFullArn")
    def secret_full_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The full ARN of the secret in AWS Secrets Manager, which is the ARN including the Secrets Manager-supplied 6-character suffix.

        This is equal to ``secretArn`` in most cases, but is undefined when a full ARN is not available (e.g., secrets imported by name).

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(
        self,
        id: builtins.str,
        *,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
    ) -> "RotationSchedule":
        '''(experimental) Adds a rotation schedule to the secret.

        :param id: -
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the IAM resource policy associated with this secret.

        If this secret was created in this stack, a resource policy will be
        automatically created upon the first call to ``addToResourcePolicy``. If
        the secret is imported, then this is a no-op.

        :param statement: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="attach")
    def attach(self, target: "ISecretAttachmentTarget") -> "ISecret":
        '''(experimental) Attach a target to this secret.

        :param target: The target to attach.

        :return: An attached secret

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="denyAccountRootDelete")
    def deny_account_root_delete(self) -> None:
        '''(experimental) Denies the ``DeleteSecret`` action to all principals within the current account.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _IGrantable_4c5a91d1,
        version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grants reading the secret value to some role.

        :param grantee: the principal being granted permission.
        :param version_stages: the version stages the grant is limited to. If not specified, no restriction on the version stages is applied.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grants writing and updating the secret value to some role.

        :param grantee: the principal being granted permission.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, key: builtins.str) -> _SecretValue_c18506ef:
        '''(experimental) Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        :param key: -

        :stability: experimental
        '''
        ...


class _ISecretProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) A secret in AWS Secrets Manager.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_secretsmanager.ISecret"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) The ARN of the secret in AWS Secrets Manager.

        Will return the full ARN if available, otherwise a partial arn.
        For secrets imported by the deprecated ``fromSecretName``, it will return the ``secretName``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        '''(experimental) The name of the secret.

        For "owned" secrets, this will be the full resource name (secret name + suffix), unless the
        '@aws-cdk/aws-secretsmanager:parseOwnedSecretName' feature flag is set.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> _SecretValue_c18506ef:
        '''(experimental) Retrieve the value of the stored secret as a ``SecretValue``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(_SecretValue_c18506ef, jsii.get(self, "secretValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_IKey_36930160], jsii.get(self, "encryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretFullArn")
    def secret_full_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The full ARN of the secret in AWS Secrets Manager, which is the ARN including the Secrets Manager-supplied 6-character suffix.

        This is equal to ``secretArn`` in most cases, but is undefined when a full ARN is not available (e.g., secrets imported by name).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretFullArn"))

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(
        self,
        id: builtins.str,
        *,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
    ) -> "RotationSchedule":
        '''(experimental) Adds a rotation schedule to the secret.

        :param id: -
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        options = RotationScheduleOptions(
            automatically_after=automatically_after,
            hosted_rotation=hosted_rotation,
            rotation_lambda=rotation_lambda,
        )

        return typing.cast("RotationSchedule", jsii.invoke(self, "addRotationSchedule", [id, options]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the IAM resource policy associated with this secret.

        If this secret was created in this stack, a resource policy will be
        automatically created upon the first call to ``addToResourcePolicy``. If
        the secret is imported, then this is a no-op.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(_AddToResourcePolicyResult_0fd9d2a9, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="attach")
    def attach(self, target: "ISecretAttachmentTarget") -> ISecret:
        '''(experimental) Attach a target to this secret.

        :param target: The target to attach.

        :return: An attached secret

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.invoke(self, "attach", [target]))

    @jsii.member(jsii_name="denyAccountRootDelete")
    def deny_account_root_delete(self) -> None:
        '''(experimental) Denies the ``DeleteSecret`` action to all principals within the current account.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "denyAccountRootDelete", []))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _IGrantable_4c5a91d1,
        version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grants reading the secret value to some role.

        :param grantee: the principal being granted permission.
        :param version_stages: the version stages the grant is limited to. If not specified, no restriction on the version stages is applied.

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantRead", [grantee, version_stages]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grants writing and updating the secret value to some role.

        :param grantee: the principal being granted permission.

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantWrite", [grantee]))

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, key: builtins.str) -> _SecretValue_c18506ef:
        '''(experimental) Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        :param key: -

        :stability: experimental
        '''
        return typing.cast(_SecretValue_c18506ef, jsii.invoke(self, "secretValueFromJson", [key]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecret).__jsii_proxy_class__ = lambda : _ISecretProxy


@jsii.interface(jsii_type="monocdk.aws_secretsmanager.ISecretAttachmentTarget")
class ISecretAttachmentTarget(typing_extensions.Protocol):
    '''(experimental) A secret attachment target.

    :stability: experimental
    '''

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> "SecretAttachmentTargetProps":
        '''(experimental) Renders the target specifications.

        :stability: experimental
        '''
        ...


class _ISecretAttachmentTargetProxy:
    '''(experimental) A secret attachment target.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_secretsmanager.ISecretAttachmentTarget"

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> "SecretAttachmentTargetProps":
        '''(experimental) Renders the target specifications.

        :stability: experimental
        '''
        return typing.cast("SecretAttachmentTargetProps", jsii.invoke(self, "asSecretAttachmentTarget", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecretAttachmentTarget).__jsii_proxy_class__ = lambda : _ISecretAttachmentTargetProxy


@jsii.interface(jsii_type="monocdk.aws_secretsmanager.ISecretTargetAttachment")
class ISecretTargetAttachment(ISecret, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretTargetAttachmentSecretArn")
    def secret_target_attachment_secret_arn(self) -> builtins.str:
        '''(experimental) Same as ``secretArn``.

        :stability: experimental
        :attribute: true
        '''
        ...


class _ISecretTargetAttachmentProxy(
    jsii.proxy_for(ISecret) # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_secretsmanager.ISecretTargetAttachment"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretTargetAttachmentSecretArn")
    def secret_target_attachment_secret_arn(self) -> builtins.str:
        '''(experimental) Same as ``secretArn``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretTargetAttachmentSecretArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecretTargetAttachment).__jsii_proxy_class__ = lambda : _ISecretTargetAttachmentProxy


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.ReplicaRegion",
    jsii_struct_bases=[],
    name_mapping={"region": "region", "encryption_key": "encryptionKey"},
)
class ReplicaRegion:
    def __init__(
        self,
        *,
        region: builtins.str,
        encryption_key: typing.Optional[_IKey_36930160] = None,
    ) -> None:
        '''(experimental) Secret replica region.

        :param region: (experimental) The name of the region.
        :param encryption_key: (experimental) The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "region": region,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) The name of the region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The customer-managed encryption key to use for encrypting the secret value.

        :default: - A default KMS key for the account and region is used.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReplicaRegion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResourcePolicy(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.ResourcePolicy",
):
    '''(experimental) Secret Resource Policy.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret: ISecret,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: (experimental) The secret to attach a resource-based permissions policy.

        :stability: experimental
        '''
        props = ResourcePolicyProps(secret=secret)

        jsii.create(ResourcePolicy, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="document")
    def document(self) -> _PolicyDocument_b5de5177:
        '''(experimental) The IAM policy document for this policy.

        :stability: experimental
        '''
        return typing.cast(_PolicyDocument_b5de5177, jsii.get(self, "document"))


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.ResourcePolicyProps",
    jsii_struct_bases=[],
    name_mapping={"secret": "secret"},
)
class ResourcePolicyProps:
    def __init__(self, *, secret: ISecret) -> None:
        '''(experimental) Construction properties for a ResourcePolicy.

        :param secret: (experimental) The secret to attach a resource-based permissions policy.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret": secret,
        }

    @builtins.property
    def secret(self) -> ISecret:
        '''(experimental) The secret to attach a resource-based permissions policy.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourcePolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RotationSchedule(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.RotationSchedule",
):
    '''(experimental) A rotation schedule.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret: ISecret,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: (experimental) The secret to rotate. If hosted rotation is used, this must be a JSON string with the following format:: { "engine": <required: database engine>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port will be used>, "masterarn": <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords> } This is typically the case for a secret referenced from an ``AWS::SecretsManager::SecretTargetAttachment`` or an ``ISecret`` returned by the ``attach()`` method of ``Secret``.
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        props = RotationScheduleProps(
            secret=secret,
            automatically_after=automatically_after,
            hosted_rotation=hosted_rotation,
            rotation_lambda=rotation_lambda,
        )

        jsii.create(RotationSchedule, self, [scope, id, props])


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.RotationScheduleOptions",
    jsii_struct_bases=[],
    name_mapping={
        "automatically_after": "automaticallyAfter",
        "hosted_rotation": "hostedRotation",
        "rotation_lambda": "rotationLambda",
    },
)
class RotationScheduleOptions:
    def __init__(
        self,
        *,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
    ) -> None:
        '''(experimental) Options to add a rotation schedule to a secret.

        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if automatically_after is not None:
            self._values["automatically_after"] = automatically_after
        if hosted_rotation is not None:
            self._values["hosted_rotation"] = hosted_rotation
        if rotation_lambda is not None:
            self._values["rotation_lambda"] = rotation_lambda

    @builtins.property
    def automatically_after(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

        :default: Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("automatically_after")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def hosted_rotation(self) -> typing.Optional[HostedRotation]:
        '''(experimental) Hosted rotation.

        :default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        result = self._values.get("hosted_rotation")
        return typing.cast(typing.Optional[HostedRotation], result)

    @builtins.property
    def rotation_lambda(self) -> typing.Optional[_IFunction_6e14f09e]:
        '''(experimental) A Lambda function that can rotate the secret.

        :default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        result = self._values.get("rotation_lambda")
        return typing.cast(typing.Optional[_IFunction_6e14f09e], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotationScheduleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.RotationScheduleProps",
    jsii_struct_bases=[RotationScheduleOptions],
    name_mapping={
        "automatically_after": "automaticallyAfter",
        "hosted_rotation": "hostedRotation",
        "rotation_lambda": "rotationLambda",
        "secret": "secret",
    },
)
class RotationScheduleProps(RotationScheduleOptions):
    def __init__(
        self,
        *,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
        secret: ISecret,
    ) -> None:
        '''(experimental) Construction properties for a RotationSchedule.

        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param secret: (experimental) The secret to rotate. If hosted rotation is used, this must be a JSON string with the following format:: { "engine": <required: database engine>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port will be used>, "masterarn": <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords> } This is typically the case for a secret referenced from an ``AWS::SecretsManager::SecretTargetAttachment`` or an ``ISecret`` returned by the ``attach()`` method of ``Secret``.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret": secret,
        }
        if automatically_after is not None:
            self._values["automatically_after"] = automatically_after
        if hosted_rotation is not None:
            self._values["hosted_rotation"] = hosted_rotation
        if rotation_lambda is not None:
            self._values["rotation_lambda"] = rotation_lambda

    @builtins.property
    def automatically_after(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

        :default: Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("automatically_after")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def hosted_rotation(self) -> typing.Optional[HostedRotation]:
        '''(experimental) Hosted rotation.

        :default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        result = self._values.get("hosted_rotation")
        return typing.cast(typing.Optional[HostedRotation], result)

    @builtins.property
    def rotation_lambda(self) -> typing.Optional[_IFunction_6e14f09e]:
        '''(experimental) A Lambda function that can rotate the secret.

        :default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        result = self._values.get("rotation_lambda")
        return typing.cast(typing.Optional[_IFunction_6e14f09e], result)

    @builtins.property
    def secret(self) -> ISecret:
        '''(experimental) The secret to rotate.

        If hosted rotation is used, this must be a JSON string with the following format::

           {
              "engine": <required: database engine>,
              "host": <required: instance host name>,
              "username": <required: username>,
              "password": <required: password>,
              "dbname": <optional: database name>,
              "port": <optional: if not specified, default port will be used>,
              "masterarn": <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords>
           }

        This is typically the case for a secret referenced from an ``AWS::SecretsManager::SecretTargetAttachment``
        or an ``ISecret`` returned by the ``attach()`` method of ``Secret``.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotationScheduleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ISecret)
class Secret(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.Secret",
):
    '''(experimental) Creates a new secret in AWS SecretsManager.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        generate_secret_string: typing.Optional["SecretStringGenerator"] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        replica_regions: typing.Optional[typing.Sequence[ReplicaRegion]] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: (experimental) An optional, human-friendly description of the secret. Default: - No description.
        :param encryption_key: (experimental) The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.
        :param generate_secret_string: (experimental) Configuration for how to generate a secret value. Default: - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each category), per the default values of ``SecretStringGenerator``.
        :param removal_policy: (experimental) Policy to apply when the secret is removed from this stack. Default: - Not set.
        :param replica_regions: (experimental) A list of regions where to replicate this secret. Default: - Secret is not replicated
        :param secret_name: (experimental) A name for the secret. Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to 30 days blackout period. During that period, it is not possible to create another secret that shares the same name. Default: - A name is generated by CloudFormation.

        :stability: experimental
        '''
        props = SecretProps(
            description=description,
            encryption_key=encryption_key,
            generate_secret_string=generate_secret_string,
            removal_policy=removal_policy,
            replica_regions=replica_regions,
            secret_name=secret_name,
        )

        jsii.create(Secret, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecretArn") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        secret_arn: builtins.str,
    ) -> ISecret:
        '''
        :param scope: -
        :param id: -
        :param secret_arn: -

        :deprecated: use ``fromSecretCompleteArn`` or ``fromSecretPartialArn``

        :stability: deprecated
        '''
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretArn", [scope, id, secret_arn]))

    @jsii.member(jsii_name="fromSecretAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        secret_arn: typing.Optional[builtins.str] = None,
        secret_complete_arn: typing.Optional[builtins.str] = None,
        secret_partial_arn: typing.Optional[builtins.str] = None,
    ) -> ISecret:
        '''(experimental) Import an existing secret into the Stack.

        :param scope: the scope of the import.
        :param id: the ID of the imported Secret in the construct tree.
        :param encryption_key: (experimental) The encryption key that is used to encrypt the secret, unless the default SecretsManager key is used.
        :param secret_arn: (deprecated) The ARN of the secret in SecretsManager. Cannot be used with ``secretCompleteArn`` or ``secretPartialArn``.
        :param secret_complete_arn: (experimental) The complete ARN of the secret in SecretsManager. This is the ARN including the Secrets Manager 6-character suffix. Cannot be used with ``secretArn`` or ``secretPartialArn``.
        :param secret_partial_arn: (experimental) The partial ARN of the secret in SecretsManager. This is the ARN without the Secrets Manager 6-character suffix. Cannot be used with ``secretArn`` or ``secretCompleteArn``.

        :stability: experimental
        '''
        attrs = SecretAttributes(
            encryption_key=encryption_key,
            secret_arn=secret_arn,
            secret_complete_arn=secret_complete_arn,
            secret_partial_arn=secret_partial_arn,
        )

        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromSecretCompleteArn") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_complete_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        secret_complete_arn: builtins.str,
    ) -> ISecret:
        '''(experimental) Imports a secret by complete ARN.

        The complete ARN is the ARN with the Secrets Manager-supplied suffix.

        :param scope: -
        :param id: -
        :param secret_complete_arn: -

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretCompleteArn", [scope, id, secret_complete_arn]))

    @jsii.member(jsii_name="fromSecretName") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        secret_name: builtins.str,
    ) -> ISecret:
        '''(deprecated) Imports a secret by secret name;

        the ARN of the Secret will be set to the secret name.
        A secret with this name must exist in the same account & region.

        :param scope: -
        :param id: -
        :param secret_name: -

        :deprecated: use ``fromSecretNameV2``

        :stability: deprecated
        '''
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretName", [scope, id, secret_name]))

    @jsii.member(jsii_name="fromSecretNameV2") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_name_v2(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        secret_name: builtins.str,
    ) -> ISecret:
        '''(experimental) Imports a secret by secret name.

        A secret with this name must exist in the same account & region.
        Replaces the deprecated ``fromSecretName``.

        :param scope: -
        :param id: -
        :param secret_name: -

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretNameV2", [scope, id, secret_name]))

    @jsii.member(jsii_name="fromSecretPartialArn") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_partial_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        secret_partial_arn: builtins.str,
    ) -> ISecret:
        '''(experimental) Imports a secret by partial ARN.

        The partial ARN is the ARN without the Secrets Manager-supplied suffix.

        :param scope: -
        :param id: -
        :param secret_partial_arn: -

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretPartialArn", [scope, id, secret_partial_arn]))

    @jsii.member(jsii_name="addReplicaRegion")
    def add_replica_region(
        self,
        region: builtins.str,
        encryption_key: typing.Optional[_IKey_36930160] = None,
    ) -> None:
        '''(experimental) Adds a replica region for the secret.

        :param region: The name of the region.
        :param encryption_key: The customer-managed encryption key to use for encrypting the secret value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addReplicaRegion", [region, encryption_key]))

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(
        self,
        id: builtins.str,
        *,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
    ) -> RotationSchedule:
        '''(experimental) Adds a rotation schedule to the secret.

        :param id: -
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        options = RotationScheduleOptions(
            automatically_after=automatically_after,
            hosted_rotation=hosted_rotation,
            rotation_lambda=rotation_lambda,
        )

        return typing.cast(RotationSchedule, jsii.invoke(self, "addRotationSchedule", [id, options]))

    @jsii.member(jsii_name="addTargetAttachment")
    def add_target_attachment(
        self,
        id: builtins.str,
        *,
        target: ISecretAttachmentTarget,
    ) -> "SecretTargetAttachment":
        '''(deprecated) Adds a target attachment to the secret.

        :param id: -
        :param target: (deprecated) The target to attach the secret to.

        :return: an AttachedSecret

        :deprecated: use ``attach()`` instead

        :stability: deprecated
        '''
        options = AttachedSecretOptions(target=target)

        return typing.cast("SecretTargetAttachment", jsii.invoke(self, "addTargetAttachment", [id, options]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the IAM resource policy associated with this secret.

        If this secret was created in this stack, a resource policy will be
        automatically created upon the first call to ``addToResourcePolicy``. If
        the secret is imported, then this is a no-op.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(_AddToResourcePolicyResult_0fd9d2a9, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="attach")
    def attach(self, target: ISecretAttachmentTarget) -> ISecret:
        '''(experimental) Attach a target to this secret.

        :param target: The target to attach.

        :return: An attached secret

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.invoke(self, "attach", [target]))

    @jsii.member(jsii_name="denyAccountRootDelete")
    def deny_account_root_delete(self) -> None:
        '''(experimental) Denies the ``DeleteSecret`` action to all principals within the current account.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "denyAccountRootDelete", []))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _IGrantable_4c5a91d1,
        version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grants reading the secret value to some role.

        :param grantee: -
        :param version_stages: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantRead", [grantee, version_stages]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grants writing and updating the secret value to some role.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantWrite", [grantee]))

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, json_field: builtins.str) -> _SecretValue_c18506ef:
        '''(experimental) Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        :param json_field: -

        :stability: experimental
        '''
        return typing.cast(_SecretValue_c18506ef, jsii.invoke(self, "secretValueFromJson", [json_field]))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''(experimental) Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnForPolicies")
    def _arn_for_policies(self) -> builtins.str:
        '''(experimental) Provides an identifier for this secret for use in IAM policies.

        If there is a full ARN, this is just the ARN;
        if we have a partial ARN -- due to either importing by secret name or partial ARN --
        then we need to add a suffix to capture the full ARN's format.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arnForPolicies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoCreatePolicy")
    def _auto_create_policy(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "autoCreatePolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) The ARN of the secret in AWS Secrets Manager.

        Will return the full ARN if available, otherwise a partial arn.
        For secrets imported by the deprecated ``fromSecretName``, it will return the ``secretName``.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        '''(experimental) The name of the secret.

        For "owned" secrets, this will be the full resource name (secret name + suffix), unless the
        '@aws-cdk/aws-secretsmanager:parseOwnedSecretName' feature flag is set.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> _SecretValue_c18506ef:
        '''(experimental) Retrieve the value of the stored secret as a ``SecretValue``.

        :stability: experimental
        '''
        return typing.cast(_SecretValue_c18506ef, jsii.get(self, "secretValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_IKey_36930160], jsii.get(self, "encryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretFullArn")
    def secret_full_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The full ARN of the secret in AWS Secrets Manager, which is the ARN including the Secrets Manager-supplied 6-character suffix.

        This is equal to ``secretArn`` in most cases, but is undefined when a full ARN is not available (e.g., secrets imported by name).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretFullArn"))


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretAttachmentTargetProps",
    jsii_struct_bases=[],
    name_mapping={"target_id": "targetId", "target_type": "targetType"},
)
class SecretAttachmentTargetProps:
    def __init__(
        self,
        *,
        target_id: builtins.str,
        target_type: AttachmentTargetType,
    ) -> None:
        '''(experimental) Attachment target specifications.

        :param target_id: (experimental) The id of the target to attach the secret to.
        :param target_type: (experimental) The type of the target to attach the secret to.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_id": target_id,
            "target_type": target_type,
        }

    @builtins.property
    def target_id(self) -> builtins.str:
        '''(experimental) The id of the target to attach the secret to.

        :stability: experimental
        '''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> AttachmentTargetType:
        '''(experimental) The type of the target to attach the secret to.

        :stability: experimental
        '''
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast(AttachmentTargetType, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretAttachmentTargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_key": "encryptionKey",
        "secret_arn": "secretArn",
        "secret_complete_arn": "secretCompleteArn",
        "secret_partial_arn": "secretPartialArn",
    },
)
class SecretAttributes:
    def __init__(
        self,
        *,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        secret_arn: typing.Optional[builtins.str] = None,
        secret_complete_arn: typing.Optional[builtins.str] = None,
        secret_partial_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes required to import an existing secret into the Stack.

        One ARN format (``secretArn``, ``secretCompleteArn``, ``secretPartialArn``) must be provided.

        :param encryption_key: (experimental) The encryption key that is used to encrypt the secret, unless the default SecretsManager key is used.
        :param secret_arn: (deprecated) The ARN of the secret in SecretsManager. Cannot be used with ``secretCompleteArn`` or ``secretPartialArn``.
        :param secret_complete_arn: (experimental) The complete ARN of the secret in SecretsManager. This is the ARN including the Secrets Manager 6-character suffix. Cannot be used with ``secretArn`` or ``secretPartialArn``.
        :param secret_partial_arn: (experimental) The partial ARN of the secret in SecretsManager. This is the ARN without the Secrets Manager 6-character suffix. Cannot be used with ``secretArn`` or ``secretCompleteArn``.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if secret_arn is not None:
            self._values["secret_arn"] = secret_arn
        if secret_complete_arn is not None:
            self._values["secret_complete_arn"] = secret_complete_arn
        if secret_partial_arn is not None:
            self._values["secret_partial_arn"] = secret_partial_arn

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The encryption key that is used to encrypt the secret, unless the default SecretsManager key is used.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def secret_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The ARN of the secret in SecretsManager.

        Cannot be used with ``secretCompleteArn`` or ``secretPartialArn``.

        :deprecated: use ``secretCompleteArn`` or ``secretPartialArn`` instead.

        :stability: deprecated
        '''
        result = self._values.get("secret_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_complete_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The complete ARN of the secret in SecretsManager.

        This is the ARN including the Secrets Manager 6-character suffix.
        Cannot be used with ``secretArn`` or ``secretPartialArn``.

        :stability: experimental
        '''
        result = self._values.get("secret_complete_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_partial_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The partial ARN of the secret in SecretsManager.

        This is the ARN without the Secrets Manager 6-character suffix.
        Cannot be used with ``secretArn`` or ``secretCompleteArn``.

        :stability: experimental
        '''
        result = self._values.get("secret_partial_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "encryption_key": "encryptionKey",
        "generate_secret_string": "generateSecretString",
        "removal_policy": "removalPolicy",
        "replica_regions": "replicaRegions",
        "secret_name": "secretName",
    },
)
class SecretProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        generate_secret_string: typing.Optional["SecretStringGenerator"] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        replica_regions: typing.Optional[typing.Sequence[ReplicaRegion]] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The properties required to create a new secret in AWS Secrets Manager.

        :param description: (experimental) An optional, human-friendly description of the secret. Default: - No description.
        :param encryption_key: (experimental) The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.
        :param generate_secret_string: (experimental) Configuration for how to generate a secret value. Default: - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each category), per the default values of ``SecretStringGenerator``.
        :param removal_policy: (experimental) Policy to apply when the secret is removed from this stack. Default: - Not set.
        :param replica_regions: (experimental) A list of regions where to replicate this secret. Default: - Secret is not replicated
        :param secret_name: (experimental) A name for the secret. Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to 30 days blackout period. During that period, it is not possible to create another secret that shares the same name. Default: - A name is generated by CloudFormation.

        :stability: experimental
        '''
        if isinstance(generate_secret_string, dict):
            generate_secret_string = SecretStringGenerator(**generate_secret_string)
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if generate_secret_string is not None:
            self._values["generate_secret_string"] = generate_secret_string
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replica_regions is not None:
            self._values["replica_regions"] = replica_regions
        if secret_name is not None:
            self._values["secret_name"] = secret_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional, human-friendly description of the secret.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The customer-managed encryption key to use for encrypting the secret value.

        :default: - A default KMS key for the account and region is used.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def generate_secret_string(self) -> typing.Optional["SecretStringGenerator"]:
        '''(experimental) Configuration for how to generate a secret value.

        :default:

        - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each
        category), per the default values of ``SecretStringGenerator``.

        :stability: experimental
        '''
        result = self._values.get("generate_secret_string")
        return typing.cast(typing.Optional["SecretStringGenerator"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) Policy to apply when the secret is removed from this stack.

        :default: - Not set.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    @builtins.property
    def replica_regions(self) -> typing.Optional[typing.List[ReplicaRegion]]:
        '''(experimental) A list of regions where to replicate this secret.

        :default: - Secret is not replicated

        :stability: experimental
        '''
        result = self._values.get("replica_regions")
        return typing.cast(typing.Optional[typing.List[ReplicaRegion]], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the secret.

        Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to
        30 days blackout period. During that period, it is not possible to create another secret that shares the same name.

        :default: - A name is generated by CloudFormation.

        :stability: experimental
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecretRotation(
    _Construct_e78e779f,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.SecretRotation",
):
    '''(experimental) Secret rotation for a service or database.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        application: "SecretRotationApplication",
        secret: ISecret,
        target: _IConnectable_c1c0e72c,
        vpc: _IVpc_6d1f76c4,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        exclude_characters: typing.Optional[builtins.str] = None,
        master_secret: typing.Optional[ISecret] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application: (experimental) The serverless application for the rotation.
        :param secret: (experimental) The secret to rotate. It must be a JSON string with the following format:. Example:: { "engine": <required: database engine>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port will be used>, "masterarn": <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords> } This is typically the case for a secret referenced from an ``AWS::SecretsManager::SecretTargetAttachment`` or an ``ISecret`` returned by the ``attach()`` method of ``Secret``.
        :param target: (experimental) The target service or database.
        :param vpc: (experimental) The VPC where the Lambda rotation function will run.
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param exclude_characters: (experimental) Characters which should not appear in the generated password. Default: - no additional characters are explicitly excluded
        :param master_secret: (experimental) The master secret for a multi user rotation scheme. Default: - single user rotation scheme
        :param security_group: (experimental) The security group for the Lambda rotation function. Default: - a new security group is created
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        props = SecretRotationProps(
            application=application,
            secret=secret,
            target=target,
            vpc=vpc,
            automatically_after=automatically_after,
            exclude_characters=exclude_characters,
            master_secret=master_secret,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(SecretRotation, self, [scope, id, props])


class SecretRotationApplication(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.SecretRotationApplication",
):
    '''(experimental) A secret rotation serverless application.

    :stability: experimental
    '''

    def __init__(
        self,
        application_id: builtins.str,
        semantic_version: builtins.str,
        *,
        is_multi_user: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param application_id: -
        :param semantic_version: -
        :param is_multi_user: (experimental) Whether the rotation application uses the mutli user scheme. Default: false

        :stability: experimental
        '''
        options = SecretRotationApplicationOptions(is_multi_user=is_multi_user)

        jsii.create(SecretRotationApplication, self, [application_id, semantic_version, options])

    @jsii.member(jsii_name="applicationArnForPartition")
    def application_arn_for_partition(self, partition: builtins.str) -> builtins.str:
        '''(experimental) Returns the application ARN for the current partition.

        Can be used in combination with a ``CfnMapping`` to automatically select the correct ARN based on the current partition.

        :param partition: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "applicationArnForPartition", [partition]))

    @jsii.member(jsii_name="semanticVersionForPartition")
    def semantic_version_for_partition(self, partition: builtins.str) -> builtins.str:
        '''(experimental) The semantic version of the app for the current partition.

        Can be used in combination with a ``CfnMapping`` to automatically select the correct version based on the current partition.

        :param partition: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "semanticVersionForPartition", [partition]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MARIADB_ROTATION_MULTI_USER")
    def MARIADB_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS MariaDB using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "MARIADB_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MARIADB_ROTATION_SINGLE_USER")
    def MARIADB_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS MariaDB using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "MARIADB_ROTATION_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MONGODB_ROTATION_MULTI_USER")
    def MONGODB_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for MongoDB using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "MONGODB_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MONGODB_ROTATION_SINGLE_USER")
    def MONGODB_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for MongoDB using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "MONGODB_ROTATION_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MYSQL_ROTATION_MULTI_USER")
    def MYSQL_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS MySQL using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "MYSQL_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MYSQL_ROTATION_SINGLE_USER")
    def MYSQL_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS MySQL using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "MYSQL_ROTATION_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ORACLE_ROTATION_MULTI_USER")
    def ORACLE_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS Oracle using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "ORACLE_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ORACLE_ROTATION_SINGLE_USER")
    def ORACLE_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS Oracle using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "ORACLE_ROTATION_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POSTGRES_ROTATION_MULTI_USER")
    def POSTGRES_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS PostgreSQL using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "POSTGRES_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POSTGRES_ROTATION_SINGLE_USER")
    def POSTGRES_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS PostgreSQL using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "POSTGRES_ROTATION_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="REDSHIFT_ROTATION_MULTI_USER")
    def REDSHIFT_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for Amazon Redshift using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "REDSHIFT_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="REDSHIFT_ROTATION_SINGLE_USER")
    def REDSHIFT_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for Amazon Redshift using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "REDSHIFT_ROTATION_SINGLE_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SQLSERVER_ROTATION_MULTI_USER")
    def SQLSERVER_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS SQL Server using the multi user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "SQLSERVER_ROTATION_MULTI_USER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SQLSERVER_ROTATION_SINGLE_USER")
    def SQLSERVER_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        '''(experimental) Conducts an AWS SecretsManager secret rotation for RDS SQL Server using the single user rotation scheme.

        :stability: experimental
        '''
        return typing.cast("SecretRotationApplication", jsii.sget(cls, "SQLSERVER_ROTATION_SINGLE_USER"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(deprecated) The application identifier of the rotation application.

        :deprecated: only valid when deploying to the 'aws' partition. Use ``applicationArnForPartition`` instead.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="semanticVersion")
    def semantic_version(self) -> builtins.str:
        '''(deprecated) The semantic version of the rotation application.

        :deprecated: only valid when deploying to the 'aws' partition. Use ``semanticVersionForPartition`` instead.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "semanticVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isMultiUser")
    def is_multi_user(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the rotation application uses the mutli user scheme.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "isMultiUser"))


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretRotationApplicationOptions",
    jsii_struct_bases=[],
    name_mapping={"is_multi_user": "isMultiUser"},
)
class SecretRotationApplicationOptions:
    def __init__(self, *, is_multi_user: typing.Optional[builtins.bool] = None) -> None:
        '''(experimental) Options for a SecretRotationApplication.

        :param is_multi_user: (experimental) Whether the rotation application uses the mutli user scheme. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if is_multi_user is not None:
            self._values["is_multi_user"] = is_multi_user

    @builtins.property
    def is_multi_user(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the rotation application uses the mutli user scheme.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("is_multi_user")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretRotationApplicationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretRotationProps",
    jsii_struct_bases=[],
    name_mapping={
        "application": "application",
        "secret": "secret",
        "target": "target",
        "vpc": "vpc",
        "automatically_after": "automaticallyAfter",
        "exclude_characters": "excludeCharacters",
        "master_secret": "masterSecret",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
    },
)
class SecretRotationProps:
    def __init__(
        self,
        *,
        application: SecretRotationApplication,
        secret: ISecret,
        target: _IConnectable_c1c0e72c,
        vpc: _IVpc_6d1f76c4,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        exclude_characters: typing.Optional[builtins.str] = None,
        master_secret: typing.Optional[ISecret] = None,
        security_group: typing.Optional[_ISecurityGroup_cdbba9d3] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''(experimental) Construction properties for a SecretRotation.

        :param application: (experimental) The serverless application for the rotation.
        :param secret: (experimental) The secret to rotate. It must be a JSON string with the following format:. Example:: { "engine": <required: database engine>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port will be used>, "masterarn": <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords> } This is typically the case for a secret referenced from an ``AWS::SecretsManager::SecretTargetAttachment`` or an ``ISecret`` returned by the ``attach()`` method of ``Secret``.
        :param target: (experimental) The target service or database.
        :param vpc: (experimental) The VPC where the Lambda rotation function will run.
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param exclude_characters: (experimental) Characters which should not appear in the generated password. Default: - no additional characters are explicitly excluded
        :param master_secret: (experimental) The master secret for a multi user rotation scheme. Default: - single user rotation scheme
        :param security_group: (experimental) The security group for the Lambda rotation function. Default: - a new security group is created
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _SubnetSelection_1284e62c(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "application": application,
            "secret": secret,
            "target": target,
            "vpc": vpc,
        }
        if automatically_after is not None:
            self._values["automatically_after"] = automatically_after
        if exclude_characters is not None:
            self._values["exclude_characters"] = exclude_characters
        if master_secret is not None:
            self._values["master_secret"] = master_secret
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def application(self) -> SecretRotationApplication:
        '''(experimental) The serverless application for the rotation.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(SecretRotationApplication, result)

    @builtins.property
    def secret(self) -> ISecret:
        '''(experimental) The secret to rotate. It must be a JSON string with the following format:.

        Example::

           {
              "engine": <required: database engine>,
              "host": <required: instance host name>,
              "username": <required: username>,
              "password": <required: password>,
              "dbname": <optional: database name>,
              "port": <optional: if not specified, default port will be used>,
              "masterarn": <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords>
           }

        This is typically the case for a secret referenced from an ``AWS::SecretsManager::SecretTargetAttachment``
        or an ``ISecret`` returned by the ``attach()`` method of ``Secret``.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(ISecret, result)

    @builtins.property
    def target(self) -> _IConnectable_c1c0e72c:
        '''(experimental) The target service or database.

        :stability: experimental
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(_IConnectable_c1c0e72c, result)

    @builtins.property
    def vpc(self) -> _IVpc_6d1f76c4:
        '''(experimental) The VPC where the Lambda rotation function will run.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_IVpc_6d1f76c4, result)

    @builtins.property
    def automatically_after(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

        :default: Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("automatically_after")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def exclude_characters(self) -> typing.Optional[builtins.str]:
        '''(experimental) Characters which should not appear in the generated password.

        :default: - no additional characters are explicitly excluded

        :stability: experimental
        '''
        result = self._values.get("exclude_characters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_secret(self) -> typing.Optional[ISecret]:
        '''(experimental) The master secret for a multi user rotation scheme.

        :default: - single user rotation scheme

        :stability: experimental
        '''
        result = self._values.get("master_secret")
        return typing.cast(typing.Optional[ISecret], result)

    @builtins.property
    def security_group(self) -> typing.Optional[_ISecurityGroup_cdbba9d3]:
        '''(experimental) The security group for the Lambda rotation function.

        :default: - a new security group is created

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_ISecurityGroup_cdbba9d3], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_SubnetSelection_1284e62c]:
        '''(experimental) The type of subnets in the VPC where the Lambda rotation function will run.

        :default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_SubnetSelection_1284e62c], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretRotationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretStringGenerator",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_characters": "excludeCharacters",
        "exclude_lowercase": "excludeLowercase",
        "exclude_numbers": "excludeNumbers",
        "exclude_punctuation": "excludePunctuation",
        "exclude_uppercase": "excludeUppercase",
        "generate_string_key": "generateStringKey",
        "include_space": "includeSpace",
        "password_length": "passwordLength",
        "require_each_included_type": "requireEachIncludedType",
        "secret_string_template": "secretStringTemplate",
    },
)
class SecretStringGenerator:
    def __init__(
        self,
        *,
        exclude_characters: typing.Optional[builtins.str] = None,
        exclude_lowercase: typing.Optional[builtins.bool] = None,
        exclude_numbers: typing.Optional[builtins.bool] = None,
        exclude_punctuation: typing.Optional[builtins.bool] = None,
        exclude_uppercase: typing.Optional[builtins.bool] = None,
        generate_string_key: typing.Optional[builtins.str] = None,
        include_space: typing.Optional[builtins.bool] = None,
        password_length: typing.Optional[jsii.Number] = None,
        require_each_included_type: typing.Optional[builtins.bool] = None,
        secret_string_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration to generate secrets such as passwords automatically.

        :param exclude_characters: (experimental) A string that includes characters that shouldn't be included in the generated password. The string can be a minimum of ``0`` and a maximum of ``4096`` characters long. Default: no exclusions
        :param exclude_lowercase: (experimental) Specifies that the generated password shouldn't include lowercase letters. Default: false
        :param exclude_numbers: (experimental) Specifies that the generated password shouldn't include digits. Default: false
        :param exclude_punctuation: (experimental) Specifies that the generated password shouldn't include punctuation characters. Default: false
        :param exclude_uppercase: (experimental) Specifies that the generated password shouldn't include uppercase letters. Default: false
        :param generate_string_key: (experimental) The JSON key name that's used to add the generated password to the JSON structure specified by the ``secretStringTemplate`` parameter. If you specify ``generateStringKey`` then ``secretStringTemplate`` must be also be specified.
        :param include_space: (experimental) Specifies that the generated password can include the space character. Default: false
        :param password_length: (experimental) The desired length of the generated password. Default: 32
        :param require_each_included_type: (experimental) Specifies whether the generated password must include at least one of every allowed character type. Default: true
        :param secret_string_template: (experimental) A properly structured JSON string that the generated password can be added to. The ``generateStringKey`` is combined with the generated random string and inserted into the JSON structure that's specified by this parameter. The merged JSON string is returned as the completed SecretString of the secret. If you specify ``secretStringTemplate`` then ``generateStringKey`` must be also be specified.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude_characters is not None:
            self._values["exclude_characters"] = exclude_characters
        if exclude_lowercase is not None:
            self._values["exclude_lowercase"] = exclude_lowercase
        if exclude_numbers is not None:
            self._values["exclude_numbers"] = exclude_numbers
        if exclude_punctuation is not None:
            self._values["exclude_punctuation"] = exclude_punctuation
        if exclude_uppercase is not None:
            self._values["exclude_uppercase"] = exclude_uppercase
        if generate_string_key is not None:
            self._values["generate_string_key"] = generate_string_key
        if include_space is not None:
            self._values["include_space"] = include_space
        if password_length is not None:
            self._values["password_length"] = password_length
        if require_each_included_type is not None:
            self._values["require_each_included_type"] = require_each_included_type
        if secret_string_template is not None:
            self._values["secret_string_template"] = secret_string_template

    @builtins.property
    def exclude_characters(self) -> typing.Optional[builtins.str]:
        '''(experimental) A string that includes characters that shouldn't be included in the generated password.

        The string can be a minimum
        of ``0`` and a maximum of ``4096`` characters long.

        :default: no exclusions

        :stability: experimental
        '''
        result = self._values.get("exclude_characters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_lowercase(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies that the generated password shouldn't include lowercase letters.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("exclude_lowercase")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exclude_numbers(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies that the generated password shouldn't include digits.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("exclude_numbers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exclude_punctuation(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies that the generated password shouldn't include punctuation characters.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("exclude_punctuation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exclude_uppercase(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies that the generated password shouldn't include uppercase letters.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("exclude_uppercase")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def generate_string_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) The JSON key name that's used to add the generated password to the JSON structure specified by the ``secretStringTemplate`` parameter.

        If you specify ``generateStringKey`` then ``secretStringTemplate``
        must be also be specified.

        :stability: experimental
        '''
        result = self._values.get("generate_string_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_space(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies that the generated password can include the space character.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("include_space")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def password_length(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The desired length of the generated password.

        :default: 32

        :stability: experimental
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def require_each_included_type(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether the generated password must include at least one of every allowed character type.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("require_each_included_type")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secret_string_template(self) -> typing.Optional[builtins.str]:
        '''(experimental) A properly structured JSON string that the generated password can be added to.

        The ``generateStringKey`` is
        combined with the generated random string and inserted into the JSON structure that's specified by this parameter.
        The merged JSON string is returned as the completed SecretString of the secret. If you specify ``secretStringTemplate``
        then ``generateStringKey`` must be also be specified.

        :stability: experimental
        '''
        result = self._values.get("secret_string_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretStringGenerator(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ISecretTargetAttachment, ISecret)
class SecretTargetAttachment(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_secretsmanager.SecretTargetAttachment",
):
    '''(experimental) An attached secret.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret: ISecret,
        target: ISecretAttachmentTarget,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: (experimental) The secret to attach to the target.
        :param target: (deprecated) The target to attach the secret to.

        :stability: experimental
        '''
        props = SecretTargetAttachmentProps(secret=secret, target=target)

        jsii.create(SecretTargetAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecretTargetAttachmentSecretArn") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_target_attachment_secret_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        secret_target_attachment_secret_arn: builtins.str,
    ) -> ISecretTargetAttachment:
        '''
        :param scope: -
        :param id: -
        :param secret_target_attachment_secret_arn: -

        :stability: experimental
        '''
        return typing.cast(ISecretTargetAttachment, jsii.sinvoke(cls, "fromSecretTargetAttachmentSecretArn", [scope, id, secret_target_attachment_secret_arn]))

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(
        self,
        id: builtins.str,
        *,
        automatically_after: typing.Optional[_Duration_070aa057] = None,
        hosted_rotation: typing.Optional[HostedRotation] = None,
        rotation_lambda: typing.Optional[_IFunction_6e14f09e] = None,
    ) -> RotationSchedule:
        '''(experimental) Adds a rotation schedule to the secret.

        :param id: -
        :param automatically_after: (experimental) Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: (experimental) Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: (experimental) A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        options = RotationScheduleOptions(
            automatically_after=automatically_after,
            hosted_rotation=hosted_rotation,
            rotation_lambda=rotation_lambda,
        )

        return typing.cast(RotationSchedule, jsii.invoke(self, "addRotationSchedule", [id, options]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the IAM resource policy associated with this secret.

        If this secret was created in this stack, a resource policy will be
        automatically created upon the first call to ``addToResourcePolicy``. If
        the secret is imported, then this is a no-op.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(_AddToResourcePolicyResult_0fd9d2a9, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="attach")
    def attach(self, target: ISecretAttachmentTarget) -> ISecret:
        '''(experimental) Attach a target to this secret.

        :param target: The target to attach.

        :return: An attached secret

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.invoke(self, "attach", [target]))

    @jsii.member(jsii_name="denyAccountRootDelete")
    def deny_account_root_delete(self) -> None:
        '''(experimental) Denies the ``DeleteSecret`` action to all principals within the current account.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "denyAccountRootDelete", []))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _IGrantable_4c5a91d1,
        version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grants reading the secret value to some role.

        :param grantee: -
        :param version_stages: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantRead", [grantee, version_stages]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grants writing and updating the secret value to some role.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantWrite", [grantee]))

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, json_field: builtins.str) -> _SecretValue_c18506ef:
        '''(experimental) Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        :param json_field: -

        :stability: experimental
        '''
        return typing.cast(_SecretValue_c18506ef, jsii.invoke(self, "secretValueFromJson", [json_field]))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''(experimental) Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnForPolicies")
    def _arn_for_policies(self) -> builtins.str:
        '''(experimental) Provides an identifier for this secret for use in IAM policies.

        If there is a full ARN, this is just the ARN;
        if we have a partial ARN -- due to either importing by secret name or partial ARN --
        then we need to add a suffix to capture the full ARN's format.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arnForPolicies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoCreatePolicy")
    def _auto_create_policy(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "autoCreatePolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) The ARN of the secret in AWS Secrets Manager.

        Will return the full ARN if available, otherwise a partial arn.
        For secrets imported by the deprecated ``fromSecretName``, it will return the ``secretName``.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        '''(experimental) The name of the secret.

        For "owned" secrets, this will be the full resource name (secret name + suffix), unless the
        '@aws-cdk/aws-secretsmanager:parseOwnedSecretName' feature flag is set.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretTargetAttachmentSecretArn")
    def secret_target_attachment_secret_arn(self) -> builtins.str:
        '''(experimental) Same as ``secretArn``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretTargetAttachmentSecretArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> _SecretValue_c18506ef:
        '''(experimental) Retrieve the value of the stored secret as a ``SecretValue``.

        :stability: experimental
        '''
        return typing.cast(_SecretValue_c18506ef, jsii.get(self, "secretValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_IKey_36930160], jsii.get(self, "encryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretFullArn")
    def secret_full_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The full ARN of the secret in AWS Secrets Manager, which is the ARN including the Secrets Manager-supplied 6-character suffix.

        This is equal to ``secretArn`` in most cases, but is undefined when a full ARN is not available (e.g., secrets imported by name).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretFullArn"))


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SecretTargetAttachmentProps",
    jsii_struct_bases=[AttachedSecretOptions],
    name_mapping={"target": "target", "secret": "secret"},
)
class SecretTargetAttachmentProps(AttachedSecretOptions):
    def __init__(self, *, target: ISecretAttachmentTarget, secret: ISecret) -> None:
        '''(experimental) Construction properties for an AttachedSecret.

        :param target: (deprecated) The target to attach the secret to.
        :param secret: (experimental) The secret to attach to the target.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
            "secret": secret,
        }

    @builtins.property
    def target(self) -> ISecretAttachmentTarget:
        '''(deprecated) The target to attach the secret to.

        :stability: deprecated
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(ISecretAttachmentTarget, result)

    @builtins.property
    def secret(self) -> ISecret:
        '''(experimental) The secret to attach to the target.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretTargetAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.SingleUserHostedRotationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "security_groups": "securityGroups",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class SingleUserHostedRotationOptions:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''(experimental) Single user hosted rotation options.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _SubnetSelection_1284e62c(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the Lambda created to rotate the secret.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[_ISecurityGroup_cdbba9d3]]:
        '''(experimental) A list of security groups for the Lambda created to rotate the secret.

        :default: - a new security group is created

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_ISecurityGroup_cdbba9d3]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_IVpc_6d1f76c4]:
        '''(experimental) The VPC where the Lambda rotation function will run.

        :default: - the Lambda is not deployed in a VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_IVpc_6d1f76c4], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_SubnetSelection_1284e62c]:
        '''(experimental) The type of subnets in the VPC where the Lambda rotation function will run.

        :default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_SubnetSelection_1284e62c], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SingleUserHostedRotationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_secretsmanager.MultiUserHostedRotationOptions",
    jsii_struct_bases=[SingleUserHostedRotationOptions],
    name_mapping={
        "function_name": "functionName",
        "security_groups": "securityGroups",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "master_secret": "masterSecret",
    },
)
class MultiUserHostedRotationOptions(SingleUserHostedRotationOptions):
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_ISecurityGroup_cdbba9d3]] = None,
        vpc: typing.Optional[_IVpc_6d1f76c4] = None,
        vpc_subnets: typing.Optional[_SubnetSelection_1284e62c] = None,
        master_secret: ISecret,
    ) -> None:
        '''(experimental) Multi user hosted rotation options.

        :param function_name: (experimental) A name for the Lambda created to rotate the secret. Default: - a CloudFormation generated name
        :param security_groups: (experimental) A list of security groups for the Lambda created to rotate the secret. Default: - a new security group is created
        :param vpc: (experimental) The VPC where the Lambda rotation function will run. Default: - the Lambda is not deployed in a VPC
        :param vpc_subnets: (experimental) The type of subnets in the VPC where the Lambda rotation function will run. Default: - the Vpc default strategy if not specified.
        :param master_secret: (experimental) The master secret for a multi user rotation scheme.

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _SubnetSelection_1284e62c(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "master_secret": master_secret,
        }
        if function_name is not None:
            self._values["function_name"] = function_name
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the Lambda created to rotate the secret.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[_ISecurityGroup_cdbba9d3]]:
        '''(experimental) A list of security groups for the Lambda created to rotate the secret.

        :default: - a new security group is created

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_ISecurityGroup_cdbba9d3]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_IVpc_6d1f76c4]:
        '''(experimental) The VPC where the Lambda rotation function will run.

        :default: - the Lambda is not deployed in a VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_IVpc_6d1f76c4], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_SubnetSelection_1284e62c]:
        '''(experimental) The type of subnets in the VPC where the Lambda rotation function will run.

        :default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_SubnetSelection_1284e62c], result)

    @builtins.property
    def master_secret(self) -> ISecret:
        '''(experimental) The master secret for a multi user rotation scheme.

        :stability: experimental
        '''
        result = self._values.get("master_secret")
        assert result is not None, "Required property 'master_secret' is missing"
        return typing.cast(ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MultiUserHostedRotationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AttachedSecretOptions",
    "AttachmentTargetType",
    "CfnResourcePolicy",
    "CfnResourcePolicyProps",
    "CfnRotationSchedule",
    "CfnRotationScheduleProps",
    "CfnSecret",
    "CfnSecretProps",
    "CfnSecretTargetAttachment",
    "CfnSecretTargetAttachmentProps",
    "HostedRotation",
    "HostedRotationType",
    "ISecret",
    "ISecretAttachmentTarget",
    "ISecretTargetAttachment",
    "MultiUserHostedRotationOptions",
    "ReplicaRegion",
    "ResourcePolicy",
    "ResourcePolicyProps",
    "RotationSchedule",
    "RotationScheduleOptions",
    "RotationScheduleProps",
    "Secret",
    "SecretAttachmentTargetProps",
    "SecretAttributes",
    "SecretProps",
    "SecretRotation",
    "SecretRotationApplication",
    "SecretRotationApplicationOptions",
    "SecretRotationProps",
    "SecretStringGenerator",
    "SecretTargetAttachment",
    "SecretTargetAttachmentProps",
    "SingleUserHostedRotationOptions",
]

publication.publish()

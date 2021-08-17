'''
# AWS Key Management Service Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

Define a KMS key:

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
from aws_cdk import aws_kms as kms


kms.Key(self, "MyKey",
    enable_key_rotation=True
)
```

Define a KMS key with waiting period:

Specifies the number of days in the waiting period before AWS KMS deletes a CMK that has been removed from a CloudFormation stack.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
key = kms.Key(self, "MyKey",
    pending_window=10
)
```

Add a couple of aliases:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
key = kms.Key(self, "MyKey")
key.add_alias("alias/foo")
key.add_alias("alias/bar")
```

Define a key with specific key spec and key usage:

Valid `keySpec` values depends on `keyUsage` value.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
key = kms.Key(self, "MyKey",
    key_spec=kms.KeySpec.ECC_SECG_P256K1, # Default to SYMMETRIC_DEFAULT
    key_usage=kms.KeyUsage.SIGN_VERIFY
)
```

## Sharing keys between stacks

To use a KMS key in a different stack in the same CDK application,
pass the construct to the other stack:

[sharing key between stacks](test/integ.key-sharing.lit.ts)

## Importing existing keys

To use a KMS key that is not defined in this CDK app, but is created through other means, use
`Key.fromKeyArn(parent, name, ref)`:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
my_key_imported = kms.Key.from_key_arn(self, "MyImportedKey", "arn:aws:...")

# you can do stuff with this imported key.
my_key_imported.add_alias("alias/foo")
```

Note that a call to `.addToPolicy(statement)` on `myKeyImported` will not have
an affect on the key's policy because it is not owned by your stack. The call
will be a no-op.

If a Key has an associated Alias, the Alias can be imported by name and used in place
of the Key as a reference. A common scenario for this is in referencing AWS managed keys.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
my_key_alias = kms.Alias.from_alias_name(self, "myKey", "alias/aws/s3")
trail = cloudtrail.Trail(self, "myCloudTrail",
    send_to_cloud_watch_logs=True,
    kms_key=my_key_alias
)
```

Note that calls to `addToResourcePolicy` and `grant*` methods on `myKeyAlias` will be
no-ops, and `addAlias` and `aliasTargetKey` will fail, as the imported alias does not
have a reference to the underlying KMS Key.

## Key Policies

Controlling access and usage of KMS Keys requires the use of key policies (resource-based policies attached to the key);
this is in contrast to most other AWS resources where access can be entirely controlled with IAM policies,
and optionally complemented with resource policies. For more in-depth understanding of KMS key access and policies, see

* https://docs.aws.amazon.com/kms/latest/developerguide/control-access-overview.html
* https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html

KMS keys can be created to trust IAM policies. This is the default behavior for both the KMS APIs and in
the console. This behavior is enabled by the '@aws-cdk/aws-kms:defaultKeyPolicies' feature flag,
which is set for all new projects; for existing projects, this same behavior can be enabled by
passing the `trustAccountIdentities` property as `true` when creating the key:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
kms.Key(stack, "MyKey", trust_account_identities=True)
```

With either the `@aws-cdk/aws-kms:defaultKeyPolicies` feature flag set,
or the `trustAccountIdentities` prop set, the Key will be given the following default key policy:

```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
  "Action": "kms:*",
  "Resource": "*"
}
```

This policy grants full access to the key to the root account user.
This enables the root account user -- via IAM policies -- to grant access to other IAM principals.
With the above default policy, future permissions can be added to either the key policy or IAM principal policy.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
key = kms.Key(stack, "MyKey")
user = iam.User(stack, "MyUser")
key.grant_encrypt(user)
```

Adopting the default KMS key policy (and so trusting account identities)
solves many issues around cyclic dependencies between stacks.
Without this default key policy, future permissions must be added to both the key policy and IAM principal policy,
which can cause cyclic dependencies if the permissions cross stack boundaries.
(For example, an encrypted bucket in one stack, and Lambda function that accesses it in another.)

### Appending to or replacing the default key policy

The default key policy can be amended or replaced entirely, depending on your use case and requirements.
A common addition to the key policy would be to add other key admins that are allowed to administer the key
(e.g., change permissions, revoke, delete). Additional key admins can be specified at key creation or after
via the `grantAdmin` method.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
my_trusted_admin_role = iam.Role.from_role_arn(stack, "TrustedRole", "arn:aws:iam:....")
key = kms.Key(stack, "MyKey",
    admins=[my_trusted_admin_role]
)

second_key = kms.Key(stack, "MyKey2")
second_key.grant_admin(my_trusted_admin_role)
```

Alternatively, a custom key policy can be specified, which will replace the default key policy.

> **Note**: In applications without the '@aws-cdk/aws-kms:defaultKeyPolicies' feature flag set
> and with `trustedAccountIdentities` set to false (the default), specifying a policy at key creation *appends* the
> provided policy to the default key policy, rather than *replacing* the default policy.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
my_trusted_admin_role = iam.Role.from_role_arn(stack, "TrustedRole", "arn:aws:iam:....")
# Creates a limited admin policy and assigns to the account root.
my_custom_policy = iam.PolicyDocument(
    statements=[iam.PolicyStatement(
        actions=["kms:Create*", "kms:Describe*", "kms:Enable*", "kms:List*", "kms:Put*"
        ],
        principals=[iam.AccountRootPrincipal()],
        resources=["*"]
    )]
)
key = kms.Key(stack, "MyKey",
    policy=my_custom_policy
)
```

> **Warning:** Replacing the default key policy with one that only grants access to a specific user or role
> runs the risk of the key becoming unmanageable if that user or role is deleted.
> It is highly recommended that the key policy grants access to the account root, rather than specific principals.
> See https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html for more information.
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
    TagManager as _TagManager_0b7ab120,
    TreeInspector as _TreeInspector_1cd1894e,
)
from ..aws_iam import (
    AddToResourcePolicyResult as _AddToResourcePolicyResult_0fd9d2a9,
    Grant as _Grant_bcb5eae7,
    IGrantable as _IGrantable_4c5a91d1,
    IPrincipal as _IPrincipal_93b48231,
    PolicyDocument as _PolicyDocument_b5de5177,
    PolicyStatement as _PolicyStatement_296fe8a3,
    PrincipalBase as _PrincipalBase_2c3968ff,
    PrincipalPolicyFragment as _PrincipalPolicyFragment_e6a0f9e3,
)


@jsii.data_type(
    jsii_type="monocdk.aws_kms.AliasAttributes",
    jsii_struct_bases=[],
    name_mapping={"alias_name": "aliasName", "alias_target_key": "aliasTargetKey"},
)
class AliasAttributes:
    def __init__(self, *, alias_name: builtins.str, alias_target_key: "IKey") -> None:
        '''(experimental) Properties of a reference to an existing KMS Alias.

        :param alias_name: (experimental) Specifies the alias name. This value must begin with alias/ followed by a name (i.e. alias/ExampleAlias)
        :param alias_target_key: (experimental) The customer master key (CMK) to which the Alias refers.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alias_name": alias_name,
            "alias_target_key": alias_target_key,
        }

    @builtins.property
    def alias_name(self) -> builtins.str:
        '''(experimental) Specifies the alias name.

        This value must begin with alias/ followed by a name (i.e. alias/ExampleAlias)

        :stability: experimental
        '''
        result = self._values.get("alias_name")
        assert result is not None, "Required property 'alias_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias_target_key(self) -> "IKey":
        '''(experimental) The customer master key (CMK) to which the Alias refers.

        :stability: experimental
        '''
        result = self._values.get("alias_target_key")
        assert result is not None, "Required property 'alias_target_key' is missing"
        return typing.cast("IKey", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AliasAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_kms.AliasProps",
    jsii_struct_bases=[],
    name_mapping={
        "alias_name": "aliasName",
        "target_key": "targetKey",
        "removal_policy": "removalPolicy",
    },
)
class AliasProps:
    def __init__(
        self,
        *,
        alias_name: builtins.str,
        target_key: "IKey",
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
    ) -> None:
        '''(experimental) Construction properties for a KMS Key Alias object.

        :param alias_name: (experimental) The name of the alias. The name must start with alias followed by a forward slash, such as alias/. You can't specify aliases that begin with alias/AWS. These aliases are reserved.
        :param target_key: (experimental) The ID of the key for which you are creating the alias. Specify the key's globally unique identifier or Amazon Resource Name (ARN). You can't specify another alias.
        :param removal_policy: (experimental) Policy to apply when the alias is removed from this stack. Default: - The alias will be deleted

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alias_name": alias_name,
            "target_key": target_key,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def alias_name(self) -> builtins.str:
        '''(experimental) The name of the alias.

        The name must start with alias followed by a
        forward slash, such as alias/. You can't specify aliases that begin with
        alias/AWS. These aliases are reserved.

        :stability: experimental
        '''
        result = self._values.get("alias_name")
        assert result is not None, "Required property 'alias_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_key(self) -> "IKey":
        '''(experimental) The ID of the key for which you are creating the alias.

        Specify the key's
        globally unique identifier or Amazon Resource Name (ARN). You can't
        specify another alias.

        :stability: experimental
        '''
        result = self._values.get("target_key")
        assert result is not None, "Required property 'target_key' is missing"
        return typing.cast("IKey", result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) Policy to apply when the alias is removed from this stack.

        :default: - The alias will be deleted

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AliasProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnAlias(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kms.CfnAlias",
):
    '''A CloudFormation ``AWS::KMS::Alias``.

    :cloudformationResource: AWS::KMS::Alias
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        alias_name: builtins.str,
        target_key_id: builtins.str,
    ) -> None:
        '''Create a new ``AWS::KMS::Alias``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param alias_name: ``AWS::KMS::Alias.AliasName``.
        :param target_key_id: ``AWS::KMS::Alias.TargetKeyId``.
        '''
        props = CfnAliasProps(alias_name=alias_name, target_key_id=target_key_id)

        jsii.create(CfnAlias, self, [scope, id, props])

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
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> builtins.str:
        '''``AWS::KMS::Alias.AliasName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-aliasname
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasName"))

    @alias_name.setter
    def alias_name(self, value: builtins.str) -> None:
        jsii.set(self, "aliasName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetKeyId")
    def target_key_id(self) -> builtins.str:
        '''``AWS::KMS::Alias.TargetKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-targetkeyid
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetKeyId"))

    @target_key_id.setter
    def target_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "targetKeyId", value)


@jsii.data_type(
    jsii_type="monocdk.aws_kms.CfnAliasProps",
    jsii_struct_bases=[],
    name_mapping={"alias_name": "aliasName", "target_key_id": "targetKeyId"},
)
class CfnAliasProps:
    def __init__(
        self,
        *,
        alias_name: builtins.str,
        target_key_id: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::KMS::Alias``.

        :param alias_name: ``AWS::KMS::Alias.AliasName``.
        :param target_key_id: ``AWS::KMS::Alias.TargetKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alias_name": alias_name,
            "target_key_id": target_key_id,
        }

    @builtins.property
    def alias_name(self) -> builtins.str:
        '''``AWS::KMS::Alias.AliasName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-aliasname
        '''
        result = self._values.get("alias_name")
        assert result is not None, "Required property 'alias_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_key_id(self) -> builtins.str:
        '''``AWS::KMS::Alias.TargetKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-targetkeyid
        '''
        result = self._values.get("target_key_id")
        assert result is not None, "Required property 'target_key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAliasProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnKey(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kms.CfnKey",
):
    '''A CloudFormation ``AWS::KMS::Key``.

    :cloudformationResource: AWS::KMS::Key
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        key_policy: typing.Any,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        enable_key_rotation: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        key_spec: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[builtins.str] = None,
        multi_region: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        pending_window_in_days: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::KMS::Key``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param key_policy: ``AWS::KMS::Key.KeyPolicy``.
        :param description: ``AWS::KMS::Key.Description``.
        :param enabled: ``AWS::KMS::Key.Enabled``.
        :param enable_key_rotation: ``AWS::KMS::Key.EnableKeyRotation``.
        :param key_spec: ``AWS::KMS::Key.KeySpec``.
        :param key_usage: ``AWS::KMS::Key.KeyUsage``.
        :param multi_region: ``AWS::KMS::Key.MultiRegion``.
        :param pending_window_in_days: ``AWS::KMS::Key.PendingWindowInDays``.
        :param tags: ``AWS::KMS::Key.Tags``.
        '''
        props = CfnKeyProps(
            key_policy=key_policy,
            description=description,
            enabled=enabled,
            enable_key_rotation=enable_key_rotation,
            key_spec=key_spec,
            key_usage=key_usage,
            multi_region=multi_region,
            pending_window_in_days=pending_window_in_days,
            tags=tags,
        )

        jsii.create(CfnKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrKeyId")
    def attr_key_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: KeyId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::KMS::Key.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPolicy")
    def key_policy(self) -> typing.Any:
        '''``AWS::KMS::Key.KeyPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keypolicy
        '''
        return typing.cast(typing.Any, jsii.get(self, "keyPolicy"))

    @key_policy.setter
    def key_policy(self, value: typing.Any) -> None:
        jsii.set(self, "keyPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::Key.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::Key.Enabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableKeyRotation")
    def enable_key_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::Key.EnableKeyRotation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enablekeyrotation
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "enableKeyRotation"))

    @enable_key_rotation.setter
    def enable_key_rotation(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "enableKeyRotation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keySpec")
    def key_spec(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::Key.KeySpec``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keyspec
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keySpec"))

    @key_spec.setter
    def key_spec(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "keySpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyUsage")
    def key_usage(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::Key.KeyUsage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keyusage
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyUsage"))

    @key_usage.setter
    def key_usage(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "keyUsage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiRegion")
    def multi_region(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::Key.MultiRegion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-multiregion
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "multiRegion"))

    @multi_region.setter
    def multi_region(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "multiRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pendingWindowInDays")
    def pending_window_in_days(self) -> typing.Optional[jsii.Number]:
        '''``AWS::KMS::Key.PendingWindowInDays``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-pendingwindowindays
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pendingWindowInDays"))

    @pending_window_in_days.setter
    def pending_window_in_days(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "pendingWindowInDays", value)


@jsii.data_type(
    jsii_type="monocdk.aws_kms.CfnKeyProps",
    jsii_struct_bases=[],
    name_mapping={
        "key_policy": "keyPolicy",
        "description": "description",
        "enabled": "enabled",
        "enable_key_rotation": "enableKeyRotation",
        "key_spec": "keySpec",
        "key_usage": "keyUsage",
        "multi_region": "multiRegion",
        "pending_window_in_days": "pendingWindowInDays",
        "tags": "tags",
    },
)
class CfnKeyProps:
    def __init__(
        self,
        *,
        key_policy: typing.Any,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        enable_key_rotation: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        key_spec: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[builtins.str] = None,
        multi_region: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        pending_window_in_days: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::KMS::Key``.

        :param key_policy: ``AWS::KMS::Key.KeyPolicy``.
        :param description: ``AWS::KMS::Key.Description``.
        :param enabled: ``AWS::KMS::Key.Enabled``.
        :param enable_key_rotation: ``AWS::KMS::Key.EnableKeyRotation``.
        :param key_spec: ``AWS::KMS::Key.KeySpec``.
        :param key_usage: ``AWS::KMS::Key.KeyUsage``.
        :param multi_region: ``AWS::KMS::Key.MultiRegion``.
        :param pending_window_in_days: ``AWS::KMS::Key.PendingWindowInDays``.
        :param tags: ``AWS::KMS::Key.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key_policy": key_policy,
        }
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_key_rotation is not None:
            self._values["enable_key_rotation"] = enable_key_rotation
        if key_spec is not None:
            self._values["key_spec"] = key_spec
        if key_usage is not None:
            self._values["key_usage"] = key_usage
        if multi_region is not None:
            self._values["multi_region"] = multi_region
        if pending_window_in_days is not None:
            self._values["pending_window_in_days"] = pending_window_in_days
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def key_policy(self) -> typing.Any:
        '''``AWS::KMS::Key.KeyPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keypolicy
        '''
        result = self._values.get("key_policy")
        assert result is not None, "Required property 'key_policy' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::Key.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::Key.Enabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enabled
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def enable_key_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::Key.EnableKeyRotation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enablekeyrotation
        '''
        result = self._values.get("enable_key_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def key_spec(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::Key.KeySpec``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keyspec
        '''
        result = self._values.get("key_spec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_usage(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::Key.KeyUsage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keyusage
        '''
        result = self._values.get("key_usage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_region(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::Key.MultiRegion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-multiregion
        '''
        result = self._values.get("multi_region")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def pending_window_in_days(self) -> typing.Optional[jsii.Number]:
        '''``AWS::KMS::Key.PendingWindowInDays``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-pendingwindowindays
        '''
        result = self._values.get("pending_window_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::KMS::Key.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnReplicaKey(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kms.CfnReplicaKey",
):
    '''A CloudFormation ``AWS::KMS::ReplicaKey``.

    :cloudformationResource: AWS::KMS::ReplicaKey
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        key_policy: typing.Any,
        primary_key_arn: builtins.str,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        pending_window_in_days: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::KMS::ReplicaKey``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param key_policy: ``AWS::KMS::ReplicaKey.KeyPolicy``.
        :param primary_key_arn: ``AWS::KMS::ReplicaKey.PrimaryKeyArn``.
        :param description: ``AWS::KMS::ReplicaKey.Description``.
        :param enabled: ``AWS::KMS::ReplicaKey.Enabled``.
        :param pending_window_in_days: ``AWS::KMS::ReplicaKey.PendingWindowInDays``.
        :param tags: ``AWS::KMS::ReplicaKey.Tags``.
        '''
        props = CfnReplicaKeyProps(
            key_policy=key_policy,
            primary_key_arn=primary_key_arn,
            description=description,
            enabled=enabled,
            pending_window_in_days=pending_window_in_days,
            tags=tags,
        )

        jsii.create(CfnReplicaKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrKeyId")
    def attr_key_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: KeyId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''``AWS::KMS::ReplicaKey.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPolicy")
    def key_policy(self) -> typing.Any:
        '''``AWS::KMS::ReplicaKey.KeyPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-keypolicy
        '''
        return typing.cast(typing.Any, jsii.get(self, "keyPolicy"))

    @key_policy.setter
    def key_policy(self, value: typing.Any) -> None:
        jsii.set(self, "keyPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryKeyArn")
    def primary_key_arn(self) -> builtins.str:
        '''``AWS::KMS::ReplicaKey.PrimaryKeyArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-primarykeyarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "primaryKeyArn"))

    @primary_key_arn.setter
    def primary_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "primaryKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::ReplicaKey.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::ReplicaKey.Enabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-enabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]],
    ) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pendingWindowInDays")
    def pending_window_in_days(self) -> typing.Optional[jsii.Number]:
        '''``AWS::KMS::ReplicaKey.PendingWindowInDays``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-pendingwindowindays
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pendingWindowInDays"))

    @pending_window_in_days.setter
    def pending_window_in_days(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "pendingWindowInDays", value)


@jsii.data_type(
    jsii_type="monocdk.aws_kms.CfnReplicaKeyProps",
    jsii_struct_bases=[],
    name_mapping={
        "key_policy": "keyPolicy",
        "primary_key_arn": "primaryKeyArn",
        "description": "description",
        "enabled": "enabled",
        "pending_window_in_days": "pendingWindowInDays",
        "tags": "tags",
    },
)
class CfnReplicaKeyProps:
    def __init__(
        self,
        *,
        key_policy: typing.Any,
        primary_key_arn: builtins.str,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        pending_window_in_days: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::KMS::ReplicaKey``.

        :param key_policy: ``AWS::KMS::ReplicaKey.KeyPolicy``.
        :param primary_key_arn: ``AWS::KMS::ReplicaKey.PrimaryKeyArn``.
        :param description: ``AWS::KMS::ReplicaKey.Description``.
        :param enabled: ``AWS::KMS::ReplicaKey.Enabled``.
        :param pending_window_in_days: ``AWS::KMS::ReplicaKey.PendingWindowInDays``.
        :param tags: ``AWS::KMS::ReplicaKey.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key_policy": key_policy,
            "primary_key_arn": primary_key_arn,
        }
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if pending_window_in_days is not None:
            self._values["pending_window_in_days"] = pending_window_in_days
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def key_policy(self) -> typing.Any:
        '''``AWS::KMS::ReplicaKey.KeyPolicy``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-keypolicy
        '''
        result = self._values.get("key_policy")
        assert result is not None, "Required property 'key_policy' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def primary_key_arn(self) -> builtins.str:
        '''``AWS::KMS::ReplicaKey.PrimaryKeyArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-primarykeyarn
        '''
        result = self._values.get("primary_key_arn")
        assert result is not None, "Required property 'primary_key_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::KMS::ReplicaKey.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
        '''``AWS::KMS::ReplicaKey.Enabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-enabled
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

    @builtins.property
    def pending_window_in_days(self) -> typing.Optional[jsii.Number]:
        '''``AWS::KMS::ReplicaKey.PendingWindowInDays``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-pendingwindowindays
        '''
        result = self._values.get("pending_window_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''``AWS::KMS::ReplicaKey.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-replicakey.html#cfn-kms-replicakey-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnReplicaKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="monocdk.aws_kms.IKey")
class IKey(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) A KMS Key, either managed by this CDK app, or imported.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> builtins.str:
        '''(experimental) The ARN of the key.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        '''(experimental) The ID of the key (the part that looks something like: 1234abcd-12ab-34cd-56ef-1234567890ab).

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias: builtins.str) -> "Alias":
        '''(experimental) Defines a new alias for the key.

        :param alias: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
        allow_no_op: typing.Optional[builtins.bool] = None,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the KMS key resource policy.

        :param statement: The policy statement to add.
        :param allow_no_op: If this is set to ``false`` and there is no policy defined (i.e. external key), the operation will fail. Otherwise, it will no-op.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _IGrantable_4c5a91d1,
        *actions: builtins.str,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grant the indicated permissions on this key to the given principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption and decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        ...


class _IKeyProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) A KMS Key, either managed by this CDK app, or imported.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_kms.IKey"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> builtins.str:
        '''(experimental) The ARN of the key.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "keyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        '''(experimental) The ID of the key (the part that looks something like: 1234abcd-12ab-34cd-56ef-1234567890ab).

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias: builtins.str) -> "Alias":
        '''(experimental) Defines a new alias for the key.

        :param alias: -

        :stability: experimental
        '''
        return typing.cast("Alias", jsii.invoke(self, "addAlias", [alias]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
        allow_no_op: typing.Optional[builtins.bool] = None,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the KMS key resource policy.

        :param statement: The policy statement to add.
        :param allow_no_op: If this is set to ``false`` and there is no policy defined (i.e. external key), the operation will fail. Otherwise, it will no-op.

        :stability: experimental
        '''
        return typing.cast(_AddToResourcePolicyResult_0fd9d2a9, jsii.invoke(self, "addToResourcePolicy", [statement, allow_no_op]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _IGrantable_4c5a91d1,
        *actions: builtins.str,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grant the indicated permissions on this key to the given principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantDecrypt", [grantee]))

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantEncrypt", [grantee]))

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption and decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantEncryptDecrypt", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IKey).__jsii_proxy_class__ = lambda : _IKeyProxy


@jsii.implements(IKey)
class Key(_Resource_abff4495, metaclass=jsii.JSIIMeta, jsii_type="monocdk.aws_kms.Key"):
    '''(experimental) Defines a KMS key.

    :stability: experimental
    :resource: AWS::KMS::Key
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        admins: typing.Optional[typing.Sequence[_IPrincipal_93b48231]] = None,
        alias: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        key_spec: typing.Optional["KeySpec"] = None,
        key_usage: typing.Optional["KeyUsage"] = None,
        pending_window: typing.Optional[_Duration_070aa057] = None,
        policy: typing.Optional[_PolicyDocument_b5de5177] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        trust_account_identities: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param admins: (experimental) A list of principals to add as key administrators to the key policy. Key administrators have permissions to manage the key (e.g., change permissions, revoke), but do not have permissions to use the key in cryptographic operations (e.g., encrypt, decrypt). These principals will be added to the default key policy (if none specified), or to the specified policy (if provided). Default: []
        :param alias: (experimental) Initial alias to add to the key. More aliases can be added later by calling ``addAlias``. Default: - No alias is added for the key.
        :param description: (experimental) A description of the key. Use a description that helps your users decide whether the key is appropriate for a particular task. Default: - No description.
        :param enabled: (experimental) Indicates whether the key is available for use. Default: - Key is enabled.
        :param enable_key_rotation: (experimental) Indicates whether AWS KMS rotates the key. Default: false
        :param key_spec: (experimental) The cryptographic configuration of the key. The valid value depends on usage of the key. IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion and a new key is created with the specified value. Default: KeySpec.SYMMETRIC_DEFAULT
        :param key_usage: (experimental) The cryptographic operations for which the key can be used. IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion and a new key is created with the specified value. Default: KeyUsage.ENCRYPT_DECRYPT
        :param pending_window: (experimental) Specifies the number of days in the waiting period before AWS KMS deletes a CMK that has been removed from a CloudFormation stack. When you remove a customer master key (CMK) from a CloudFormation stack, AWS KMS schedules the CMK for deletion and starts the mandatory waiting period. The PendingWindowInDays property determines the length of waiting period. During the waiting period, the key state of CMK is Pending Deletion, which prevents the CMK from being used in cryptographic operations. When the waiting period expires, AWS KMS permanently deletes the CMK. Enter a value between 7 and 30 days. Default: - 30 days
        :param policy: (experimental) Custom policy document to attach to the KMS key. NOTE - If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects), this policy will *override* the default key policy and become the only key policy for the key. If the feature flag is not set, this policy will be appended to the default key policy. Default: - A policy document with permissions for the account root to administer the key will be created.
        :param removal_policy: (experimental) Whether the encryption key should be retained when it is removed from the Stack. This is useful when one wants to retain access to data that was encrypted with a key that is being retired. Default: RemovalPolicy.Retain
        :param trust_account_identities: (deprecated) Whether the key usage can be granted by IAM policies. Setting this to true adds a default statement which delegates key access control completely to the identity's IAM policy (similar to how it works for other AWS resources). This matches the default behavior when creating KMS keys via the API or console. If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects), this flag will always be treated as 'true' and does not need to be explicitly set. Default: - false, unless the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set.

        :stability: experimental
        '''
        props = KeyProps(
            admins=admins,
            alias=alias,
            description=description,
            enabled=enabled,
            enable_key_rotation=enable_key_rotation,
            key_spec=key_spec,
            key_usage=key_usage,
            pending_window=pending_window,
            policy=policy,
            removal_policy=removal_policy,
            trust_account_identities=trust_account_identities,
        )

        jsii.create(Key, self, [scope, id, props])

    @jsii.member(jsii_name="fromCfnKey") # type: ignore[misc]
    @builtins.classmethod
    def from_cfn_key(cls, cfn_key: CfnKey) -> IKey:
        '''(experimental) Create a mutable {@link IKey} based on a low-level {@link CfnKey}.

        This is most useful when combined with the cloudformation-include module.
        This method is different than {@link fromKeyArn()} because the {@link IKey}
        returned from this method is mutable;
        meaning, calling any mutating methods on it,
        like {@link IKey.addToResourcePolicy()},
        will actually be reflected in the resulting template,
        as opposed to the object returned from {@link fromKeyArn()},
        on which calling those methods would have no effect.

        :param cfn_key: -

        :stability: experimental
        '''
        return typing.cast(IKey, jsii.sinvoke(cls, "fromCfnKey", [cfn_key]))

    @jsii.member(jsii_name="fromKeyArn") # type: ignore[misc]
    @builtins.classmethod
    def from_key_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        key_arn: builtins.str,
    ) -> IKey:
        '''(experimental) Import an externally defined KMS Key using its ARN.

        :param scope: the construct that will "own" the imported key.
        :param id: the id of the imported key in the construct tree.
        :param key_arn: the ARN of an existing KMS key.

        :stability: experimental
        '''
        return typing.cast(IKey, jsii.sinvoke(cls, "fromKeyArn", [scope, id, key_arn]))

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias_name: builtins.str) -> "Alias":
        '''(experimental) Defines a new alias for the key.

        :param alias_name: -

        :stability: experimental
        '''
        return typing.cast("Alias", jsii.invoke(self, "addAlias", [alias_name]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
        allow_no_op: typing.Optional[builtins.bool] = None,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the KMS key resource policy.

        :param statement: The policy statement to add.
        :param allow_no_op: If this is set to ``false`` and there is no policy defined (i.e. external key), the operation will fail. Otherwise, it will no-op.

        :stability: experimental
        '''
        return typing.cast(_AddToResourcePolicyResult_0fd9d2a9, jsii.invoke(self, "addToResourcePolicy", [statement, allow_no_op]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _IGrantable_4c5a91d1,
        *actions: builtins.str,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grant the indicated permissions on this key to the given principal.

        This modifies both the principal's policy as well as the resource policy,
        since the default CloudFormation setup for KMS keys is that the policy
        must not be empty and so default grants won't work.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantAdmin")
    def grant_admin(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant admins permissions using this key to the given principal.

        Key administrators have permissions to manage the key (e.g., change permissions, revoke), but do not have permissions
        to use the key in cryptographic operations (e.g., encrypt, decrypt).

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantAdmin", [grantee]))

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantDecrypt", [grantee]))

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantEncrypt", [grantee]))

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption and decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantEncryptDecrypt", [grantee]))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''(experimental) Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> builtins.str:
        '''(experimental) The ARN of the key.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "keyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        '''(experimental) The ID of the key (the part that looks something like: 1234abcd-12ab-34cd-56ef-1234567890ab).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustAccountIdentities")
    def _trust_account_identities(self) -> builtins.bool:
        '''(experimental) Optional property to control trusting account identities.

        If specified, grants will default identity policies instead of to both
        resource and identity policies. This matches the default behavior when creating
        KMS keys via the API or console.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "trustAccountIdentities"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def _policy(self) -> typing.Optional[_PolicyDocument_b5de5177]:
        '''(experimental) Optional policy document that represents the resource policy of this key.

        If specified, addToResourcePolicy can be used to edit this policy.
        Otherwise this method will no-op.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_PolicyDocument_b5de5177], jsii.get(self, "policy"))


@jsii.data_type(
    jsii_type="monocdk.aws_kms.KeyProps",
    jsii_struct_bases=[],
    name_mapping={
        "admins": "admins",
        "alias": "alias",
        "description": "description",
        "enabled": "enabled",
        "enable_key_rotation": "enableKeyRotation",
        "key_spec": "keySpec",
        "key_usage": "keyUsage",
        "pending_window": "pendingWindow",
        "policy": "policy",
        "removal_policy": "removalPolicy",
        "trust_account_identities": "trustAccountIdentities",
    },
)
class KeyProps:
    def __init__(
        self,
        *,
        admins: typing.Optional[typing.Sequence[_IPrincipal_93b48231]] = None,
        alias: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        key_spec: typing.Optional["KeySpec"] = None,
        key_usage: typing.Optional["KeyUsage"] = None,
        pending_window: typing.Optional[_Duration_070aa057] = None,
        policy: typing.Optional[_PolicyDocument_b5de5177] = None,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
        trust_account_identities: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Construction properties for a KMS Key object.

        :param admins: (experimental) A list of principals to add as key administrators to the key policy. Key administrators have permissions to manage the key (e.g., change permissions, revoke), but do not have permissions to use the key in cryptographic operations (e.g., encrypt, decrypt). These principals will be added to the default key policy (if none specified), or to the specified policy (if provided). Default: []
        :param alias: (experimental) Initial alias to add to the key. More aliases can be added later by calling ``addAlias``. Default: - No alias is added for the key.
        :param description: (experimental) A description of the key. Use a description that helps your users decide whether the key is appropriate for a particular task. Default: - No description.
        :param enabled: (experimental) Indicates whether the key is available for use. Default: - Key is enabled.
        :param enable_key_rotation: (experimental) Indicates whether AWS KMS rotates the key. Default: false
        :param key_spec: (experimental) The cryptographic configuration of the key. The valid value depends on usage of the key. IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion and a new key is created with the specified value. Default: KeySpec.SYMMETRIC_DEFAULT
        :param key_usage: (experimental) The cryptographic operations for which the key can be used. IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion and a new key is created with the specified value. Default: KeyUsage.ENCRYPT_DECRYPT
        :param pending_window: (experimental) Specifies the number of days in the waiting period before AWS KMS deletes a CMK that has been removed from a CloudFormation stack. When you remove a customer master key (CMK) from a CloudFormation stack, AWS KMS schedules the CMK for deletion and starts the mandatory waiting period. The PendingWindowInDays property determines the length of waiting period. During the waiting period, the key state of CMK is Pending Deletion, which prevents the CMK from being used in cryptographic operations. When the waiting period expires, AWS KMS permanently deletes the CMK. Enter a value between 7 and 30 days. Default: - 30 days
        :param policy: (experimental) Custom policy document to attach to the KMS key. NOTE - If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects), this policy will *override* the default key policy and become the only key policy for the key. If the feature flag is not set, this policy will be appended to the default key policy. Default: - A policy document with permissions for the account root to administer the key will be created.
        :param removal_policy: (experimental) Whether the encryption key should be retained when it is removed from the Stack. This is useful when one wants to retain access to data that was encrypted with a key that is being retired. Default: RemovalPolicy.Retain
        :param trust_account_identities: (deprecated) Whether the key usage can be granted by IAM policies. Setting this to true adds a default statement which delegates key access control completely to the identity's IAM policy (similar to how it works for other AWS resources). This matches the default behavior when creating KMS keys via the API or console. If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects), this flag will always be treated as 'true' and does not need to be explicitly set. Default: - false, unless the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if admins is not None:
            self._values["admins"] = admins
        if alias is not None:
            self._values["alias"] = alias
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_key_rotation is not None:
            self._values["enable_key_rotation"] = enable_key_rotation
        if key_spec is not None:
            self._values["key_spec"] = key_spec
        if key_usage is not None:
            self._values["key_usage"] = key_usage
        if pending_window is not None:
            self._values["pending_window"] = pending_window
        if policy is not None:
            self._values["policy"] = policy
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if trust_account_identities is not None:
            self._values["trust_account_identities"] = trust_account_identities

    @builtins.property
    def admins(self) -> typing.Optional[typing.List[_IPrincipal_93b48231]]:
        '''(experimental) A list of principals to add as key administrators to the key policy.

        Key administrators have permissions to manage the key (e.g., change permissions, revoke), but do not have permissions
        to use the key in cryptographic operations (e.g., encrypt, decrypt).

        These principals will be added to the default key policy (if none specified), or to the specified policy (if provided).

        :default: []

        :stability: experimental
        '''
        result = self._values.get("admins")
        return typing.cast(typing.Optional[typing.List[_IPrincipal_93b48231]], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''(experimental) Initial alias to add to the key.

        More aliases can be added later by calling ``addAlias``.

        :default: - No alias is added for the key.

        :stability: experimental
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the key.

        Use a description that helps your users decide
        whether the key is appropriate for a particular task.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether the key is available for use.

        :default: - Key is enabled.

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_key_rotation(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether AWS KMS rotates the key.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_key_rotation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def key_spec(self) -> typing.Optional["KeySpec"]:
        '''(experimental) The cryptographic configuration of the key. The valid value depends on usage of the key.

        IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion
        and a new key is created with the specified value.

        :default: KeySpec.SYMMETRIC_DEFAULT

        :stability: experimental
        '''
        result = self._values.get("key_spec")
        return typing.cast(typing.Optional["KeySpec"], result)

    @builtins.property
    def key_usage(self) -> typing.Optional["KeyUsage"]:
        '''(experimental) The cryptographic operations for which the key can be used.

        IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion
        and a new key is created with the specified value.

        :default: KeyUsage.ENCRYPT_DECRYPT

        :stability: experimental
        '''
        result = self._values.get("key_usage")
        return typing.cast(typing.Optional["KeyUsage"], result)

    @builtins.property
    def pending_window(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies the number of days in the waiting period before AWS KMS deletes a CMK that has been removed from a CloudFormation stack.

        When you remove a customer master key (CMK) from a CloudFormation stack, AWS KMS schedules the CMK for deletion
        and starts the mandatory waiting period. The PendingWindowInDays property determines the length of waiting period.
        During the waiting period, the key state of CMK is Pending Deletion, which prevents the CMK from being used in
        cryptographic operations. When the waiting period expires, AWS KMS permanently deletes the CMK.

        Enter a value between 7 and 30 days.

        :default: - 30 days

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-pendingwindowindays
        :stability: experimental
        '''
        result = self._values.get("pending_window")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def policy(self) -> typing.Optional[_PolicyDocument_b5de5177]:
        '''(experimental) Custom policy document to attach to the KMS key.

        NOTE - If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects),
        this policy will *override* the default key policy and become the only key policy for the key. If the
        feature flag is not set, this policy will be appended to the default key policy.

        :default:

        - A policy document with permissions for the account root to
        administer the key will be created.

        :stability: experimental
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[_PolicyDocument_b5de5177], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_RemovalPolicy_c97e7a20]:
        '''(experimental) Whether the encryption key should be retained when it is removed from the Stack.

        This is useful when one wants to
        retain access to data that was encrypted with a key that is being retired.

        :default: RemovalPolicy.Retain

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_RemovalPolicy_c97e7a20], result)

    @builtins.property
    def trust_account_identities(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether the key usage can be granted by IAM policies.

        Setting this to true adds a default statement which delegates key
        access control completely to the identity's IAM policy (similar
        to how it works for other AWS resources). This matches the default behavior
        when creating KMS keys via the API or console.

        If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects),
        this flag will always be treated as 'true' and does not need to be explicitly set.

        :default: - false, unless the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set.

        :deprecated: redundant with the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag

        :see: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html#key-policy-default-allow-root-enable-iam
        :stability: deprecated
        '''
        result = self._values.get("trust_account_identities")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_kms.KeySpec")
class KeySpec(enum.Enum):
    '''(experimental) The key spec, represents the cryptographic configuration of keys.

    :stability: experimental
    '''

    SYMMETRIC_DEFAULT = "SYMMETRIC_DEFAULT"
    '''(experimental) The default key spec.

    Valid usage: ENCRYPT_DECRYPT

    :stability: experimental
    '''
    RSA_2048 = "RSA_2048"
    '''(experimental) RSA with 2048 bits of key.

    Valid usage: ENCRYPT_DECRYPT and SIGN_VERIFY

    :stability: experimental
    '''
    RSA_3072 = "RSA_3072"
    '''(experimental) RSA with 3072 bits of key.

    Valid usage: ENCRYPT_DECRYPT and SIGN_VERIFY

    :stability: experimental
    '''
    RSA_4096 = "RSA_4096"
    '''(experimental) RSA with 4096 bits of key.

    Valid usage: ENCRYPT_DECRYPT and SIGN_VERIFY

    :stability: experimental
    '''
    ECC_NIST_P256 = "ECC_NIST_P256"
    '''(experimental) NIST FIPS 186-4, Section 6.4, ECDSA signature using the curve specified by the key and SHA-256 for the message digest.

    Valid usage: SIGN_VERIFY

    :stability: experimental
    '''
    ECC_NIST_P384 = "ECC_NIST_P384"
    '''(experimental) NIST FIPS 186-4, Section 6.4, ECDSA signature using the curve specified by the key and SHA-384 for the message digest.

    Valid usage: SIGN_VERIFY

    :stability: experimental
    '''
    ECC_NIST_P521 = "ECC_NIST_P521"
    '''(experimental) NIST FIPS 186-4, Section 6.4, ECDSA signature using the curve specified by the key and SHA-512 for the message digest.

    Valid usage: SIGN_VERIFY

    :stability: experimental
    '''
    ECC_SECG_P256K1 = "ECC_SECG_P256K1"
    '''(experimental) Standards for Efficient Cryptography 2, Section 2.4.1, ECDSA signature on the Koblitz curve.

    Valid usage: SIGN_VERIFY

    :stability: experimental
    '''


@jsii.enum(jsii_type="monocdk.aws_kms.KeyUsage")
class KeyUsage(enum.Enum):
    '''(experimental) The key usage, represents the cryptographic operations of keys.

    :stability: experimental
    '''

    ENCRYPT_DECRYPT = "ENCRYPT_DECRYPT"
    '''(experimental) Encryption and decryption.

    :stability: experimental
    '''
    SIGN_VERIFY = "SIGN_VERIFY"
    '''(experimental) Signing and verification.

    :stability: experimental
    '''


class ViaServicePrincipal(
    _PrincipalBase_2c3968ff,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kms.ViaServicePrincipal",
):
    '''(experimental) A principal to allow access to a key if it's being used through another AWS service.

    :stability: experimental
    '''

    def __init__(
        self,
        service_name: builtins.str,
        base_principal: typing.Optional[_IPrincipal_93b48231] = None,
    ) -> None:
        '''
        :param service_name: -
        :param base_principal: -

        :stability: experimental
        '''
        jsii.create(ViaServicePrincipal, self, [service_name, base_principal])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> _PrincipalPolicyFragment_e6a0f9e3:
        '''(experimental) Return the policy fragment that identifies this principal in a Policy.

        :stability: experimental
        '''
        return typing.cast(_PrincipalPolicyFragment_e6a0f9e3, jsii.get(self, "policyFragment"))


@jsii.interface(jsii_type="monocdk.aws_kms.IAlias")
class IAlias(IKey, typing_extensions.Protocol):
    '''(experimental) A KMS Key alias.

    An alias can be used in all places that expect a key.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> builtins.str:
        '''(experimental) The name of the alias.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasTargetKey")
    def alias_target_key(self) -> IKey:
        '''(experimental) The Key to which the Alias refers.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAliasProxy(
    jsii.proxy_for(IKey) # type: ignore[misc]
):
    '''(experimental) A KMS Key alias.

    An alias can be used in all places that expect a key.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_kms.IAlias"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> builtins.str:
        '''(experimental) The name of the alias.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasTargetKey")
    def alias_target_key(self) -> IKey:
        '''(experimental) The Key to which the Alias refers.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(IKey, jsii.get(self, "aliasTargetKey"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlias).__jsii_proxy_class__ = lambda : _IAliasProxy


@jsii.implements(IAlias)
class Alias(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kms.Alias",
):
    '''(experimental) Defines a display name for a customer master key (CMK) in AWS Key Management Service (AWS KMS).

    Using an alias to refer to a key can help you simplify key
    management. For example, when rotating keys, you can just update the alias
    mapping instead of tracking and changing key IDs. For more information, see
    Working with Aliases in the AWS Key Management Service Developer Guide.

    You can also add an alias for a key by calling ``key.addAlias(alias)``.

    :stability: experimental
    :resource: AWS::KMS::Alias
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias_name: builtins.str,
        target_key: IKey,
        removal_policy: typing.Optional[_RemovalPolicy_c97e7a20] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alias_name: (experimental) The name of the alias. The name must start with alias followed by a forward slash, such as alias/. You can't specify aliases that begin with alias/AWS. These aliases are reserved.
        :param target_key: (experimental) The ID of the key for which you are creating the alias. Specify the key's globally unique identifier or Amazon Resource Name (ARN). You can't specify another alias.
        :param removal_policy: (experimental) Policy to apply when the alias is removed from this stack. Default: - The alias will be deleted

        :stability: experimental
        '''
        props = AliasProps(
            alias_name=alias_name, target_key=target_key, removal_policy=removal_policy
        )

        jsii.create(Alias, self, [scope, id, props])

    @jsii.member(jsii_name="fromAliasAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_alias_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias_name: builtins.str,
        alias_target_key: IKey,
    ) -> IAlias:
        '''(experimental) Import an existing KMS Alias defined outside the CDK app.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param alias_name: (experimental) Specifies the alias name. This value must begin with alias/ followed by a name (i.e. alias/ExampleAlias)
        :param alias_target_key: (experimental) The customer master key (CMK) to which the Alias refers.

        :stability: experimental
        '''
        attrs = AliasAttributes(
            alias_name=alias_name, alias_target_key=alias_target_key
        )

        return typing.cast(IAlias, jsii.sinvoke(cls, "fromAliasAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromAliasName") # type: ignore[misc]
    @builtins.classmethod
    def from_alias_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        alias_name: builtins.str,
    ) -> IAlias:
        '''(experimental) Import an existing KMS Alias defined outside the CDK app, by the alias name.

        This method should be used
        instead of 'fromAliasAttributes' when the underlying KMS Key ARN is not available.
        This Alias will not have a direct reference to the KMS Key, so addAlias and grant* methods are not supported.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param alias_name: The full name of the KMS Alias (e.g., 'alias/aws/s3', 'alias/myKeyAlias').

        :stability: experimental
        '''
        return typing.cast(IAlias, jsii.sinvoke(cls, "fromAliasName", [scope, id, alias_name]))

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias: builtins.str) -> "Alias":
        '''(experimental) Defines a new alias for the key.

        :param alias: -

        :stability: experimental
        '''
        return typing.cast("Alias", jsii.invoke(self, "addAlias", [alias]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
        allow_no_op: typing.Optional[builtins.bool] = None,
    ) -> _AddToResourcePolicyResult_0fd9d2a9:
        '''(experimental) Adds a statement to the KMS key resource policy.

        :param statement: -
        :param allow_no_op: -

        :stability: experimental
        '''
        return typing.cast(_AddToResourcePolicyResult_0fd9d2a9, jsii.invoke(self, "addToResourcePolicy", [statement, allow_no_op]))

    @jsii.member(jsii_name="generatePhysicalName")
    def _generate_physical_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "generatePhysicalName", []))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _IGrantable_4c5a91d1,
        *actions: builtins.str,
    ) -> _Grant_bcb5eae7:
        '''(experimental) Grant the indicated permissions on this key to the given principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantDecrypt", [grantee]))

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantEncrypt", [grantee]))

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: _IGrantable_4c5a91d1) -> _Grant_bcb5eae7:
        '''(experimental) Grant encryption and decryption permissions using this key to the given principal.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(_Grant_bcb5eae7, jsii.invoke(self, "grantEncryptDecrypt", [grantee]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> builtins.str:
        '''(experimental) The name of the alias.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasTargetKey")
    def alias_target_key(self) -> IKey:
        '''(experimental) The Key to which the Alias refers.

        :stability: experimental
        '''
        return typing.cast(IKey, jsii.get(self, "aliasTargetKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> builtins.str:
        '''(experimental) The ARN of the key.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "keyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        '''(experimental) The ID of the key (the part that looks something like: 1234abcd-12ab-34cd-56ef-1234567890ab).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "keyId"))


__all__ = [
    "Alias",
    "AliasAttributes",
    "AliasProps",
    "CfnAlias",
    "CfnAliasProps",
    "CfnKey",
    "CfnKeyProps",
    "CfnReplicaKey",
    "CfnReplicaKeyProps",
    "IAlias",
    "IKey",
    "Key",
    "KeyProps",
    "KeySpec",
    "KeyUsage",
    "ViaServicePrincipal",
]

publication.publish()

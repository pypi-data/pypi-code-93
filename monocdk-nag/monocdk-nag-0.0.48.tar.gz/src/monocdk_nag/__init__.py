'''
<!--
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
-->

# cdk-nag

| Language   | cdk-nag                                                                                   | monocdk-nag                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Python     | [![PyPI version](https://badge.fury.io/py/cdk-nag.svg)](https://badge.fury.io/py/cdk-nag) | [![PyPI version](https://badge.fury.io/py/monocdk-nag.svg)](https://badge.fury.io/py/monocdk-nag) |
| TypeScript | [![npm version](https://badge.fury.io/js/cdk-nag.svg)](https://badge.fury.io/js/cdk-nag)  | [![npm version](https://badge.fury.io/js/monocdk-nag.svg)](https://badge.fury.io/js/monocdk-nag)  |

Check CDK applications for best practices using a combination of available rule packs. Inspired by [cfn_nag](https://github.com/stelligent/cfn_nag)

![](cdk_nag.gif)

## Available Packs

See [RULES](./RULES.md) for more information on all the available packs.

1. [AWS Solutions](./RULES.md#awssolutions)
2. [HIPAA Security](./RULES.md#hipaa-security) (In Progress)
3. [NIST 800-53](./RULES.md#nist-800-53) (In Progress)

## Usage

### cdk

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import App, Aspects
from ...lib.cdk_test_stack import CdkTestStack
from cdk_nag import AwsSolutionsChecks

app = App()
CdkTestStack(app, "CdkNagDemo")
# Simple rule informational messages
Aspects.of(app).add(AwsSolutionsChecks())
```

### monocdk

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from monocdk import App, Aspects
from monocdk_nag import AwsSolutionsChecks
from ...lib.my_stack import MyStack

app = App()
CdkTestStack(app, "CdkNagDemo")
# Simple rule informational messages
Aspects.of(app).add(AwsSolutionsChecks())
```

## Suppressing a Rule

<details>
  <summary>Example 1) Default Construct</summary>

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
test = SecurityGroup(self, "test",
    vpc=Vpc(self, "vpc")
)
test.add_ingress_rule(Peer.any_ipv4(), Port.all_traffic())
test_cfn = test.node.default_child
test_cfn.add_metadata("cdk_nag",
    rules_to_suppress=[{"id": "AwsSolutions-EC23", "reason": "at least 10 characters"}
    ]
)
```

</details><details>
  <summary>Example 2) Dependent Constructs</summary>

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
user = User(self, "rUser")
user.add_to_policy(
    PolicyStatement(
        actions=["s3:PutObject"],
        resources=[Bucket(self, "rBucket").arn_for_objects("*")]
    ))
cfn_user = user.node.children
for child in cfn_user:
    resource = child.node.default_child
    if resource != undefined && resource.cfn_resource_type == "AWS::IAM::Policy":
        resource.add_metadata("cdk_nag",
            rules_to_suppress=[{
                "id": "AwsSolutions-IAM5",
                "reason": "The user is allowed to put objects on all prefixes in the specified bucket."
            }
            ]
        )
```

</details>

## Rules and Property Overrides

In some cases L2 Constructs do not have a native option to remediate an issue and must be fixed via [Raw Overrides](https://docs.aws.amazon.com/cdk/latest/guide/cfn_layer.html#cfn_layer_raw). Since raw overrides take place after template synthesis these fixes are not caught by the cdk_nag. In this case you should remediate the issue and suppress the issue like in the following example.

<details>
  <summary>Example) Property Overrides</summary>

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
instance = Instance(stack, "rInstance",
    vpc=Vpc(stack, "rVpc"),
    instance_type=InstanceType(InstanceClass.T3),
    machine_image=MachineImage.latest_amazon_linux()
)
cfn_ins = instance.node.default_child
cfn_ins.add_property_override("DisableApiTermination", True)
cfn_ins.add_metadata("cdk_nag",
    rules_to_suppress=[{
        "id": "AwsSolutions-EC29",
        "reason": "Remediated through property override "
    }
    ]
)
```

</details>

## Contributing

See [CONTRIBUTING](./CONTRIBUTING.md) for more information.

## License

This project is licensed under the Apache-2.0 License.
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

import monocdk


@jsii.implements(monocdk.IAspect)
class NagPack(metaclass=jsii.JSIIAbstractClass, jsii_type="monocdk-nag.NagPack"):
    '''Base class for all rule sets.'''

    def __init__(self, *, verbose: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param verbose: Whether or not to enable extended explanatory descriptions on warning and error messages.
        '''
        props = NagPackProps(verbose=verbose)

        jsii.create(NagPack, self, [props])

    @jsii.member(jsii_name="createMessage")
    def create_message(
        self,
        rule_id: builtins.str,
        info: builtins.str,
        explanation: builtins.str,
    ) -> builtins.str:
        '''The message to output to the console when a rule is triggered.

        :param rule_id: the id of the rule.
        :param info: why the rule was triggered.
        :param explanation: why the rule exists.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "createMessage", [rule_id, info, explanation]))

    @jsii.member(jsii_name="ignoreRule")
    def ignore_rule(self, ignores: typing.Any, rule_id: builtins.str) -> builtins.bool:
        '''Check whether a specific rule should be ignored.

        :param ignores: ignores listed in cdkNag metadata.
        :param rule_id: the id of the rule to ignore.

        :return: boolean
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "ignoreRule", [ignores, rule_id]))

    @jsii.member(jsii_name="visit") # type: ignore[misc]
    @abc.abstractmethod
    def visit(self, node: monocdk.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verbose")
    def _verbose(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "verbose"))

    @_verbose.setter
    def _verbose(self, value: builtins.bool) -> None:
        jsii.set(self, "verbose", value)


class _NagPackProxy(NagPack):
    @jsii.member(jsii_name="visit")
    def visit(self, node: monocdk.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, NagPack).__jsii_proxy_class__ = lambda : _NagPackProxy


@jsii.data_type(
    jsii_type="monocdk-nag.NagPackProps",
    jsii_struct_bases=[],
    name_mapping={"verbose": "verbose"},
)
class NagPackProps:
    def __init__(self, *, verbose: typing.Optional[builtins.bool] = None) -> None:
        '''Interface for creating a Nag rule set.

        :param verbose: Whether or not to enable extended explanatory descriptions on warning and error messages.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if verbose is not None:
            self._values["verbose"] = verbose

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable extended explanatory descriptions on warning and error messages.'''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NagPackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsSolutionsChecks(
    NagPack,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk-nag.AwsSolutionsChecks",
):
    '''Check Best practices based on AWS Solutions Security Matrix.'''

    def __init__(self, *, verbose: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param verbose: Whether or not to enable extended explanatory descriptions on warning and error messages.
        '''
        props = NagPackProps(verbose=verbose)

        jsii.create(AwsSolutionsChecks, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: monocdk.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


class HIPAASecurityChecks(
    NagPack,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk-nag.HIPAASecurityChecks",
):
    '''Check for HIPAA Security compliance.

    Based on the HIPAA Security AWS operational best practices: https://docs.aws.amazon.com/config/latest/developerguide/operational-best-practices-for-hipaa_security.html
    '''

    def __init__(self, *, verbose: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param verbose: Whether or not to enable extended explanatory descriptions on warning and error messages.
        '''
        props = NagPackProps(verbose=verbose)

        jsii.create(HIPAASecurityChecks, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: monocdk.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


class NIST80053Checks(
    NagPack,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk-nag.NIST80053Checks",
):
    '''Check for NIST 800-53 compliance.

    Based on the NIST 800-53 AWS operational best practices: https://docs.aws.amazon.com/config/latest/developerguide/operational-best-practices-for-nist-800-53_rev_4.html
    '''

    def __init__(self, *, verbose: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param verbose: Whether or not to enable extended explanatory descriptions on warning and error messages.
        '''
        props = NagPackProps(verbose=verbose)

        jsii.create(NIST80053Checks, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: monocdk.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


__all__ = [
    "AwsSolutionsChecks",
    "HIPAASecurityChecks",
    "NIST80053Checks",
    "NagPack",
    "NagPackProps",
]

publication.publish()

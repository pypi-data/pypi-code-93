'''
[![NPM version](https://badge.fury.io/js/cdk-ecrpublic-gc.svg)](https://badge.fury.io/js/cdk-ecrpublic-gc)
[![PyPI version](https://badge.fury.io/py/cdk-ecrpublic-gc.svg)](https://badge.fury.io/py/cdk-ecrpublic-gc)
![Release](https://github.com/pahud/cdk-ecrpublic-gc/workflows/Release/badge.svg)

# cdk-ecrpublic-gc

CDK construct library that helps you build a garbage collector to delete all untagged images in Amazon ECR public with AWS CDK.

# Why

Amazon ECR public does not have lifecycle policy to clean up all untagged images at this moment(see [this issue](https://github.com/aws/containers-roadmap/issues/1268)). `cdk-ecrpublic-gc` allows you to deploy a **AWS Step Functions** state machine with [dynamic parallelism](https://aws.amazon.com/tw/blogs/aws/new-step-functions-support-for-dynamic-parallelism/) to invoke an arbitrary of Lambda functions to remove untagged images to release the storage.

# Schedule

By default, the state machine will be triggered **every 4 hours** and can be configured in the `schedule` property in the `TidyUp` construct.

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
from cdk_ecrpublic_gc import TidyUp

app = cdk.App()

stack = cdk.Stack(app, "ecr-public-gc")

TidyUp(stack, "TidyUp",
    repository=["vscode", "gitpod-workspace", "github-codespace"
    ],
    schedule=events.Schedule.cron(hour="*/4", minute="0")
)
```

# In Action

Step Function state machine with dynamic tasks in parallel
![](images/01.png)

![](images/02.png)
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

import aws_cdk.aws_events
import aws_cdk.aws_lambda
import aws_cdk.core


class Handler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecrpublic-gc.Handler",
):
    '''The default handler.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        repository: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param repository: 
        '''
        props = HandlerProps(repository=repository)

        jsii.create(Handler, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "function"))


@jsii.data_type(
    jsii_type="cdk-ecrpublic-gc.HandlerProps",
    jsii_struct_bases=[],
    name_mapping={"repository": "repository"},
)
class HandlerProps:
    def __init__(self, *, repository: typing.Sequence[builtins.str]) -> None:
        '''properties for the Handler.

        :param repository: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
        }

    @builtins.property
    def repository(self) -> typing.List[builtins.str]:
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HandlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TidyUp(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecrpublic-gc.TidyUp",
):
    '''The primary consruct to tidy up ECR public images.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        repository: typing.Sequence[builtins.str],
        function: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param repository: The ECR public repositories to check.
        :param function: your custom function to process the garbage collection. Default: - a default function will be created
        :param schedule: The schedule to trigger the state machine. Default: - every 4 hours
        '''
        props = TidyUpProps(
            repository=repository, function=function, schedule=schedule
        )

        jsii.create(TidyUp, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "repository"))


@jsii.data_type(
    jsii_type="cdk-ecrpublic-gc.TidyUpProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository": "repository",
        "function": "function",
        "schedule": "schedule",
    },
)
class TidyUpProps:
    def __init__(
        self,
        *,
        repository: typing.Sequence[builtins.str],
        function: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''Properties for TidyUp construct.

        :param repository: The ECR public repositories to check.
        :param function: your custom function to process the garbage collection. Default: - a default function will be created
        :param schedule: The schedule to trigger the state machine. Default: - every 4 hours
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
        }
        if function is not None:
            self._values["function"] = function
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def repository(self) -> typing.List[builtins.str]:
        '''The ECR public repositories to check.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def function(self) -> typing.Optional[aws_cdk.aws_lambda.IFunction]:
        '''your custom function to process the garbage collection.

        :default: - a default function will be created
        '''
        result = self._values.get("function")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IFunction], result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''The schedule to trigger the state machine.

        :default: - every 4 hours
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TidyUpProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Handler",
    "HandlerProps",
    "TidyUp",
    "TidyUpProps",
]

publication.publish()

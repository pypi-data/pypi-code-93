'''
# Lifecycle Hook for the CDK AWS AutoScaling Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains integration classes for AutoScaling lifecycle hooks.
Instances of these classes should be passed to the
`autoScalingGroup.addLifecycleHook()` method.

Lifecycle hooks can be activated in one of the following ways:

* Invoke a Lambda function
* Publish to an SNS topic
* Send to an SQS queue

For more information on using this library, see the README of the
`@aws-cdk/aws-autoscaling` library.

For more information about lifecycle hooks, see
[Amazon EC2 AutoScaling Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html) in the Amazon EC2 User Guide.
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
from ..aws_autoscaling import (
    ILifecycleHook as _ILifecycleHook_b73fe64f,
    ILifecycleHookTarget as _ILifecycleHookTarget_733c0e5a,
    LifecycleHookTargetConfig as _LifecycleHookTargetConfig_184f760b,
)
from ..aws_kms import IKey as _IKey_5f11635f
from ..aws_lambda import IFunction as _IFunction_6adb0ab8
from ..aws_sns import ITopic as _ITopic_9eca4852
from ..aws_sqs import IQueue as _IQueue_7ed6f679


@jsii.implements(_ILifecycleHookTarget_733c0e5a)
class FunctionHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_autoscaling_hooktargets.FunctionHook",
):
    '''(experimental) Use a Lambda Function as a hook target.

    Internally creates a Topic to make the connection.

    :stability: experimental
    '''

    def __init__(
        self,
        fn: _IFunction_6adb0ab8,
        encryption_key: typing.Optional[_IKey_5f11635f] = None,
    ) -> None:
        '''
        :param fn: Function to invoke in response to a lifecycle event.
        :param encryption_key: If provided, this key is used to encrypt the contents of the SNS topic.

        :stability: experimental
        '''
        jsii.create(FunctionHook, self, [fn, encryption_key])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        lifecycle_hook: _ILifecycleHook_b73fe64f,
    ) -> _LifecycleHookTargetConfig_184f760b:
        '''(experimental) Called when this object is used as the target of a lifecycle hook.

        :param scope: -
        :param lifecycle_hook: -

        :stability: experimental
        '''
        return typing.cast(_LifecycleHookTargetConfig_184f760b, jsii.invoke(self, "bind", [scope, lifecycle_hook]))


@jsii.implements(_ILifecycleHookTarget_733c0e5a)
class QueueHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_autoscaling_hooktargets.QueueHook",
):
    '''(experimental) Use an SQS queue as a hook target.

    :stability: experimental
    '''

    def __init__(self, queue: _IQueue_7ed6f679) -> None:
        '''
        :param queue: -

        :stability: experimental
        '''
        jsii.create(QueueHook, self, [queue])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        lifecycle_hook: _ILifecycleHook_b73fe64f,
    ) -> _LifecycleHookTargetConfig_184f760b:
        '''(experimental) Called when this object is used as the target of a lifecycle hook.

        :param _scope: -
        :param lifecycle_hook: -

        :stability: experimental
        '''
        return typing.cast(_LifecycleHookTargetConfig_184f760b, jsii.invoke(self, "bind", [_scope, lifecycle_hook]))


@jsii.implements(_ILifecycleHookTarget_733c0e5a)
class TopicHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_autoscaling_hooktargets.TopicHook",
):
    '''(experimental) Use an SNS topic as a hook target.

    :stability: experimental
    '''

    def __init__(self, topic: _ITopic_9eca4852) -> None:
        '''
        :param topic: -

        :stability: experimental
        '''
        jsii.create(TopicHook, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        lifecycle_hook: _ILifecycleHook_b73fe64f,
    ) -> _LifecycleHookTargetConfig_184f760b:
        '''(experimental) Called when this object is used as the target of a lifecycle hook.

        :param _scope: -
        :param lifecycle_hook: -

        :stability: experimental
        '''
        return typing.cast(_LifecycleHookTargetConfig_184f760b, jsii.invoke(self, "bind", [_scope, lifecycle_hook]))


__all__ = [
    "FunctionHook",
    "QueueHook",
    "TopicHook",
]

publication.publish()

'''
# CloudWatch Alarm Actions library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains a set of classes which can be used as CloudWatch Alarm actions.

The currently implemented actions are: EC2 Actions, SNS Actions, Autoscaling Actions and Aplication Autoscaling Actions

## EC2 Action Example

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk import aws_cloudwatch as cw

# Alarm must be configured with an EC2 per-instance metric
alarm =
# Attach a reboot when alarm triggers
alarm.add_alarm_action(
    Ec2Action(Ec2InstanceActions.REBOOT))
```

See `@aws-cdk/aws-cloudwatch` for more information.
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
from ..aws_applicationautoscaling import (
    StepScalingAction as _StepScalingAction_d79ca2c9
)
from ..aws_autoscaling import StepScalingAction as _StepScalingAction_24d17483
from ..aws_cloudwatch import (
    AlarmActionConfig as _AlarmActionConfig_f831c655,
    IAlarm as _IAlarm_ff3eabc0,
    IAlarmAction as _IAlarmAction_922c5aa8,
)
from ..aws_sns import ITopic as _ITopic_9eca4852


@jsii.implements(_IAlarmAction_922c5aa8)
class ApplicationScalingAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_cloudwatch_actions.ApplicationScalingAction",
):
    '''(experimental) Use an ApplicationAutoScaling StepScalingAction as an Alarm Action.

    :stability: experimental
    '''

    def __init__(self, step_scaling_action: _StepScalingAction_d79ca2c9) -> None:
        '''
        :param step_scaling_action: -

        :stability: experimental
        '''
        jsii.create(ApplicationScalingAction, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        _alarm: _IAlarm_ff3eabc0,
    ) -> _AlarmActionConfig_f831c655:
        '''(experimental) Returns an alarm action configuration to use an ApplicationScaling StepScalingAction as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_f831c655, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(_IAlarmAction_922c5aa8)
class AutoScalingAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_cloudwatch_actions.AutoScalingAction",
):
    '''(experimental) Use an AutoScaling StepScalingAction as an Alarm Action.

    :stability: experimental
    '''

    def __init__(self, step_scaling_action: _StepScalingAction_24d17483) -> None:
        '''
        :param step_scaling_action: -

        :stability: experimental
        '''
        jsii.create(AutoScalingAction, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        _alarm: _IAlarm_ff3eabc0,
    ) -> _AlarmActionConfig_f831c655:
        '''(experimental) Returns an alarm action configuration to use an AutoScaling StepScalingAction as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_f831c655, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(_IAlarmAction_922c5aa8)
class Ec2Action(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_cloudwatch_actions.Ec2Action",
):
    '''(experimental) Use an EC2 action as an Alarm action.

    :stability: experimental
    '''

    def __init__(self, instance_action: "Ec2InstanceAction") -> None:
        '''
        :param instance_action: -

        :stability: experimental
        '''
        jsii.create(Ec2Action, self, [instance_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        _alarm: _IAlarm_ff3eabc0,
    ) -> _AlarmActionConfig_f831c655:
        '''(experimental) Returns an alarm action configuration to use an EC2 action as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_f831c655, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.enum(jsii_type="aws-cdk-lib.aws_cloudwatch_actions.Ec2InstanceAction")
class Ec2InstanceAction(enum.Enum):
    '''(experimental) Types of EC2 actions available.

    :stability: experimental
    '''

    STOP = "STOP"
    '''(experimental) Stop the instance.

    :stability: experimental
    '''
    TERMINATE = "TERMINATE"
    '''(experimental) Terminatethe instance.

    :stability: experimental
    '''
    RECOVER = "RECOVER"
    '''(experimental) Recover the instance.

    :stability: experimental
    '''
    REBOOT = "REBOOT"
    '''(experimental) Reboot the instance.

    :stability: experimental
    '''


@jsii.implements(_IAlarmAction_922c5aa8)
class SnsAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_cloudwatch_actions.SnsAction",
):
    '''(experimental) Use an SNS topic as an alarm action.

    :stability: experimental
    '''

    def __init__(self, topic: _ITopic_9eca4852) -> None:
        '''
        :param topic: -

        :stability: experimental
        '''
        jsii.create(SnsAction, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        _alarm: _IAlarm_ff3eabc0,
    ) -> _AlarmActionConfig_f831c655:
        '''(experimental) Returns an alarm action configuration to use an SNS topic as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_f831c655, jsii.invoke(self, "bind", [_scope, _alarm]))


__all__ = [
    "ApplicationScalingAction",
    "AutoScalingAction",
    "Ec2Action",
    "Ec2InstanceAction",
    "SnsAction",
]

publication.publish()

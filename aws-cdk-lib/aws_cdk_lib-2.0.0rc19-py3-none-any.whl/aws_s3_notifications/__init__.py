'''
# S3 Bucket Notifications Destinations

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This module includes integration classes for using Topics, Queues or Lambdas
as S3 Notification Destinations.

## Example

The following example shows how to send a notification to an SNS
topic when an object is created in an S3 bucket:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_cdk import aws_s3_notifications as s3n


bucket = s3.Bucket(stack, "Bucket")
topic = sns.Topic(stack, "Topic")

bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, s3n.SnsDestination(topic))
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
from ..aws_lambda import IFunction as _IFunction_6adb0ab8
from ..aws_s3 import (
    BucketNotificationDestinationConfig as _BucketNotificationDestinationConfig_a4c4f83d,
    IBucket as _IBucket_42e086fd,
    IBucketNotificationDestination as _IBucketNotificationDestination_ae5ca51a,
)
from ..aws_sns import ITopic as _ITopic_9eca4852
from ..aws_sqs import IQueue as _IQueue_7ed6f679


@jsii.implements(_IBucketNotificationDestination_ae5ca51a)
class LambdaDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_s3_notifications.LambdaDestination",
):
    '''(experimental) Use a Lambda function as a bucket notification destination.

    :stability: experimental
    '''

    def __init__(self, fn: _IFunction_6adb0ab8) -> None:
        '''
        :param fn: -

        :stability: experimental
        '''
        jsii.create(LambdaDestination, self, [fn])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        bucket: _IBucket_42e086fd,
    ) -> _BucketNotificationDestinationConfig_a4c4f83d:
        '''(experimental) Registers this resource to receive notifications for the specified bucket.

        This method will only be called once for each destination/bucket
        pair and the result will be cached, so there is no need to implement
        idempotency in each destination.

        :param _scope: -
        :param bucket: -

        :stability: experimental
        '''
        return typing.cast(_BucketNotificationDestinationConfig_a4c4f83d, jsii.invoke(self, "bind", [_scope, bucket]))


@jsii.implements(_IBucketNotificationDestination_ae5ca51a)
class SnsDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_s3_notifications.SnsDestination",
):
    '''(experimental) Use an SNS topic as a bucket notification destination.

    :stability: experimental
    '''

    def __init__(self, topic: _ITopic_9eca4852) -> None:
        '''
        :param topic: -

        :stability: experimental
        '''
        jsii.create(SnsDestination, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        bucket: _IBucket_42e086fd,
    ) -> _BucketNotificationDestinationConfig_a4c4f83d:
        '''(experimental) Registers this resource to receive notifications for the specified bucket.

        This method will only be called once for each destination/bucket
        pair and the result will be cached, so there is no need to implement
        idempotency in each destination.

        :param _scope: -
        :param bucket: -

        :stability: experimental
        '''
        return typing.cast(_BucketNotificationDestinationConfig_a4c4f83d, jsii.invoke(self, "bind", [_scope, bucket]))


@jsii.implements(_IBucketNotificationDestination_ae5ca51a)
class SqsDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_s3_notifications.SqsDestination",
):
    '''(experimental) Use an SQS queue as a bucket notification destination.

    :stability: experimental
    '''

    def __init__(self, queue: _IQueue_7ed6f679) -> None:
        '''
        :param queue: -

        :stability: experimental
        '''
        jsii.create(SqsDestination, self, [queue])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        bucket: _IBucket_42e086fd,
    ) -> _BucketNotificationDestinationConfig_a4c4f83d:
        '''(experimental) Allows using SQS queues as destinations for bucket notifications.

        Use ``bucket.onEvent(event, queue)`` to subscribe.

        :param _scope: -
        :param bucket: -

        :stability: experimental
        '''
        return typing.cast(_BucketNotificationDestinationConfig_a4c4f83d, jsii.invoke(self, "bind", [_scope, bucket]))


__all__ = [
    "LambdaDestination",
    "SnsDestination",
    "SqsDestination",
]

publication.publish()

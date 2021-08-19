'''
# cdk-notify-bucket
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

import aws_cdk.aws_s3
import aws_cdk.aws_sns
import aws_cdk.core


class NotifyBucket(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-notify-bucket.NotifyBucket",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        email: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param email: 

        :stability: experimental
        '''
        props = NotifyBucketProps(email=email)

        jsii.create(NotifyBucket, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.Topic:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_sns.Topic, jsii.get(self, "topic"))


@jsii.data_type(
    jsii_type="cdk-notify-bucket.NotifyBucketProps",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class NotifyBucketProps:
    def __init__(self, *, email: typing.Sequence[builtins.str]) -> None:
        '''
        :param email: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotifyBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "NotifyBucket",
    "NotifyBucketProps",
]

publication.publish()

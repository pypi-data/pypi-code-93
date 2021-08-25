'''
[![NPM version](https://badge.fury.io/js/cdk-image-moderation.svg)](https://badge.fury.io/js/cdk-image-moderation)
[![PyPI version](https://badge.fury.io/py/cdk-image-moderation.svg)](https://badge.fury.io/py/cdk-image-moderation)
[![Release](https://github.com/pahud/cdk-image-moderation/actions/workflows/release.yml/badge.svg)](https://github.com/pahud/cdk-image-moderation/actions/workflows/release.yml)

# cdk-image-moderation

Event-driven image moderation and notification service with AWS CDK

![](images/cdk-image-moderation2.svg)

# Sample

This sample create a S3 bucket that will trigger image moderation check on object created and send notification to SNS when specific moderation labels are detected. The `SNS2Telegram` creates a Lambda function as the SNS topic subscription which fires the notification to a private Telegram chatroom with the image preview and moderation result.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_image_moderation import Moderation, SNS2Telegram

app = cdk.App()
env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}
stack = cdk.Stack(app, "moderation-demo", env=env)

# create the moderation
mod = Moderation(stack, "Mod",
    moderation_labels=[ModerationLabels.EXPLICIT_NUDITY, ModerationLabels.DRUGS, ModerationLabels.TOBACCO, ModerationLabels.ALCOHOL, ModerationLabels.VIOLENCE, ModerationLabels.RUDE_GESTURES
    ]
)

# send notification via sns to telegram
SNS2Telegram(stack, "SNS2TG",
    topic=mod.topic,
    chatid="-547476398"
)
```

# Deploy the CDK app

```sh
export TELEGRAM_TOKEN=<YOUR_TOKEN>
cdk diff
cdk deploy
```

# Deploy from this repository

```sh
export TELEGRAM_TOKEN=<YOUR_TOKEN>
# run `yarn build` or `yarn watch` to generate the lib
cdk --app lib/integ.default.js diff
cdk --app lib/integ.default.js deploy
```

On deploy completed, you will get the S3 bucket in the `Outputs`. Simply upload any images into this bucket and you should be able to get the notification from the Telegram chatroom.
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

import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_sns
import aws_cdk.core


class Moderation(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-image-moderation.Moderation",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_options: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        moderation_labels: typing.Optional[typing.Sequence["ModerationLabels"]] = None,
        preview_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_options: Options to create the S3 Bucket.
        :param moderation_labels: emit the notification when we detect these labels.
        :param preview_ttl: The TTL for the presigned URL of the preview image. Default: 60 seconds
        :param topic: The SNS Topic to send the image moderation result.
        '''
        props = ModerationProps(
            bucket_options=bucket_options,
            moderation_labels=moderation_labels,
            preview_ttl=preview_ttl,
            topic=topic,
        )

        jsii.create(Moderation, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.Bucket:
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.ITopic:
        return typing.cast(aws_cdk.aws_sns.ITopic, jsii.get(self, "topic"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketOptions")
    def bucket_options(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], jsii.get(self, "bucketOptions"))


@jsii.enum(jsii_type="cdk-image-moderation.ModerationLabels")
class ModerationLabels(enum.Enum):
    '''content moderation labels.

    :see: https://docs.aws.amazon.com/rekognition/latest/dg/moderation.html
    '''

    EXPLICIT_NUDITY = "EXPLICIT_NUDITY"
    NUDITY = "NUDITY"
    SEXUAL_ACTIVITY = "SEXUAL_ACTIVITY"
    SUGGESTIVE = "SUGGESTIVE"
    PARTIAL_NUDITY = "PARTIAL_NUDITY"
    VIOLENCE = "VIOLENCE"
    VISUALLY_DISTURBING = "VISUALLY_DISTURBING"
    RUDE_GESTURES = "RUDE_GESTURES"
    DRUGS = "DRUGS"
    TOBACCO = "TOBACCO"
    ALCOHOL = "ALCOHOL"
    GAMBLING = "GAMBLING"
    HATE_SYMBOLS = "HATE_SYMBOLS"


@jsii.data_type(
    jsii_type="cdk-image-moderation.ModerationProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_options": "bucketOptions",
        "moderation_labels": "moderationLabels",
        "preview_ttl": "previewTtl",
        "topic": "topic",
    },
)
class ModerationProps:
    def __init__(
        self,
        *,
        bucket_options: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        moderation_labels: typing.Optional[typing.Sequence[ModerationLabels]] = None,
        preview_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
    ) -> None:
        '''
        :param bucket_options: Options to create the S3 Bucket.
        :param moderation_labels: emit the notification when we detect these labels.
        :param preview_ttl: The TTL for the presigned URL of the preview image. Default: 60 seconds
        :param topic: The SNS Topic to send the image moderation result.
        '''
        if isinstance(bucket_options, dict):
            bucket_options = aws_cdk.aws_s3.BucketProps(**bucket_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_options is not None:
            self._values["bucket_options"] = bucket_options
        if moderation_labels is not None:
            self._values["moderation_labels"] = moderation_labels
        if preview_ttl is not None:
            self._values["preview_ttl"] = preview_ttl
        if topic is not None:
            self._values["topic"] = topic

    @builtins.property
    def bucket_options(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Options to create the S3 Bucket.'''
        result = self._values.get("bucket_options")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def moderation_labels(self) -> typing.Optional[typing.List[ModerationLabels]]:
        '''emit the notification when we detect these labels.'''
        result = self._values.get("moderation_labels")
        return typing.cast(typing.Optional[typing.List[ModerationLabels]], result)

    @builtins.property
    def preview_ttl(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The TTL for the presigned URL of the preview image.

        :default: 60 seconds
        '''
        result = self._values.get("preview_ttl")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def topic(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        '''The SNS Topic to send the image moderation result.'''
        result = self._values.get("topic")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.ITopic], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModerationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SNS2Telegram(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-image-moderation.SNS2Telegram",
):
    '''forward SNS messages to Telegram chat via Lambda.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        chatid: builtins.str,
        topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param chatid: The Telegram chat ID to send the message to.
        :param topic: The SNS topic to receive the inbound notification and forward to the downstream Telegram chat.
        '''
        props = SNS2TelegramProps(chatid=chatid, topic=topic)

        jsii.create(SNS2Telegram, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-image-moderation.SNS2TelegramProps",
    jsii_struct_bases=[],
    name_mapping={"chatid": "chatid", "topic": "topic"},
)
class SNS2TelegramProps:
    def __init__(
        self,
        *,
        chatid: builtins.str,
        topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
    ) -> None:
        '''
        :param chatid: The Telegram chat ID to send the message to.
        :param topic: The SNS topic to receive the inbound notification and forward to the downstream Telegram chat.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "chatid": chatid,
        }
        if topic is not None:
            self._values["topic"] = topic

    @builtins.property
    def chatid(self) -> builtins.str:
        '''The Telegram chat ID to send the message to.'''
        result = self._values.get("chatid")
        assert result is not None, "Required property 'chatid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        '''The SNS topic to receive the inbound notification and forward to the downstream Telegram chat.'''
        result = self._values.get("topic")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.ITopic], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SNS2TelegramProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Moderation",
    "ModerationLabels",
    "ModerationProps",
    "SNS2Telegram",
    "SNS2TelegramProps",
]

publication.publish()

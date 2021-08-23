import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .endpoint_service_base import EndpointServiceBase as _EndpointServiceBase_6aa74fa3


class CommonCheckVerify(
    _EndpointServiceBase_6aa74fa3,
    metaclass=jsii.JSIIMeta,
    jsii_type="@affinidi/common-check-widget-backend-lib.commonCheckVerify.CommonCheckVerify",
):
    def __init__(self, request_id: builtins.str) -> None:
        '''
        :param request_id: -
        '''
        jsii.create(CommonCheckVerify, self, [request_id])

    @jsii.member(jsii_name="fillEncryptionFile")
    def fill_encryption_file(self, encryption_file: typing.Any) -> None:
        '''
        :param encryption_file: -
        '''
        return typing.cast(None, jsii.invoke(self, "fillEncryptionFile", [encryption_file]))

    @jsii.member(jsii_name="generateOptions")
    def generate_options(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.ainvoke(self, "generateOptions", []))

    @jsii.member(jsii_name="generateResponse")
    def generate_response(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.ainvoke(self, "generateResponse", []))

    @jsii.member(jsii_name="generateToken")
    def generate_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.ainvoke(self, "generateToken", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionFile")
    def encryption_file(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "encryptionFile"))

    @encryption_file.setter
    def encryption_file(self, value: typing.Any) -> None:
        jsii.set(self, "encryptionFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Any) -> None:
        jsii.set(self, "options", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyFileName")
    def private_key_file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyFileName"))

    @private_key_file_name.setter
    def private_key_file_name(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyFileName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestID")
    def request_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestID"))

    @request_id.setter
    def request_id(self, value: builtins.str) -> None:
        jsii.set(self, "requestID", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretPassphrase")
    def secret_passphrase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretPassphrase"))

    @secret_passphrase.setter
    def secret_passphrase(self, value: builtins.str) -> None:
        jsii.set(self, "secretPassphrase", value)


__all__ = [
    "CommonCheckVerify",
]

publication.publish()

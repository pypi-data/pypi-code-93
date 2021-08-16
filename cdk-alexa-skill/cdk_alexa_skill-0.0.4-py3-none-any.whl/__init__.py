'''
# Alexa Skill CDK Construct

This is a CDK construct library for creating an Alexa Skill.

This library currently supports NodeJS and Python.

## Installation

Install with npm

```bash
$ npm install cdk-alexa-skill
```

Install with pip

```bash
$ pip install cdk-alexa-skill
```

## Usage/Examples

#### TypeScript:

```javascript
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import { Skill } from 'cdk-alexa-skill';

const skillBackendLambdaFunction = new lambda.Function(this, 'Function', {
    ...
});

const skill = new Skill(this, 'Skill', {
    endpointLambdaFunction: skillBackendLambdaFunction, // @aws-cdk/aws-lambda.IFunction object containing backend code for the Alexa Skill
    skillPackagePath: 'src/skill-package', // path to your skill package
    alexaVendorId: 'XXXXXXXXXX', // vendor ID of Alexa Developer account
    lwaClientId: 'XXXXXXXXXX', // client ID of LWA Security Profile
    lwaClientSecret: cdk.SecretValue.secretsManager('lwa-client-secret'), // @aws-cdk/core.SecretValue object containing client secret of LWA Security Profile
    lwaRefreshToken: cdk.SecretValue.secretsManager('lwa-refresh-token') // @aws-cdk/core.SecretValue object containing refresh token of LWA Security Profile
});
```

#### Python:

```python
from aws_cdk import core
from aws_cdk import aws_lambda as lambda_
from cdk_alexa_skill import Skill

skill_backend_lambda_function = lambda_.Function(self, 'Function',
    ...)

skill = Skill(self, 'Skill',
    endpoint_lambda_function=skill_backend_lambda_function, # aws_cdk.aws_lambda.IFunction object containing backend code for the Alexa Skill
    skill_package_path='src/skill_package', # path to your skill package
    alexa_vendor_id='XXXXXXXXXX', # vendor ID of Alexa Developer account
    lwa_client_id='XXXXXXXXXX', # client ID of LWA Security Profile
    lwa_client_secret=core.SecretValue.secrets_manager('lwa-client-secret'), # @aws-cdk/core.SecretValue object containing client secret of LWA Security Profile
    lwa_refresh_token=core.SecretValue.secrets_manager('lwa-refresh-token')) # @aws-cdk/core.SecretValue object containing refresh token of LWA Security Profile
```

See [example folder](./example) or [this blog post]() for a more complete example.

## Contributing

Contributions of all kinds are welcome and celebrated. Raise an issue, submit a PR, do the right thing.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contributing guidelines.

## License

[MIT](./LICENSE)
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
import aws_cdk.core


@jsii.interface(jsii_type="cdk-alexa-skill.ISkill")
class ISkill(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''An Alexa Skill, either managed by this CDK app, or imported.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skillId")
    def skill_id(self) -> builtins.str:
        '''The ID associated with this Skill.

        :attribute: true
        '''
        ...


class _ISkillProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''An Alexa Skill, either managed by this CDK app, or imported.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-alexa-skill.ISkill"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skillId")
    def skill_id(self) -> builtins.str:
        '''The ID associated with this Skill.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "skillId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISkill).__jsii_proxy_class__ = lambda : _ISkillProxy


@jsii.implements(ISkill)
class Skill(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-alexa-skill.Skill",
):
    '''Defines an Alexa Skill.

    :resource: Alexa::ASK::Skill
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        alexa_vendor_id: builtins.str,
        lwa_client_id: builtins.str,
        lwa_client_secret: aws_cdk.core.SecretValue,
        lwa_refresh_token: aws_cdk.core.SecretValue,
        skill_package_path: builtins.str,
        endpoint_lambda_function: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alexa_vendor_id: Vendor ID associated with Alexa Developer account.
        :param lwa_client_id: Client ID of Login with Amazon (LWA) Security Profile.
        :param lwa_client_secret: Client secret associated with Login with Amazon (LWA) Client ID.
        :param lwa_refresh_token: Refresh token associated with Login with Amazon (LWA) Security Profile.
        :param skill_package_path: The relative path to the skill package directory containing all configuration files for the Alexa Skill.
        :param endpoint_lambda_function: The Lambda Function to be configured as the endpoint for the Alexa Skill. Default: - No endpoint Lambda Function
        '''
        props = SkillProps(
            alexa_vendor_id=alexa_vendor_id,
            lwa_client_id=lwa_client_id,
            lwa_client_secret=lwa_client_secret,
            lwa_refresh_token=lwa_refresh_token,
            skill_package_path=skill_package_path,
            endpoint_lambda_function=endpoint_lambda_function,
        )

        jsii.create(Skill, self, [scope, id, props])

    @jsii.member(jsii_name="fromSkillId") # type: ignore[misc]
    @builtins.classmethod
    def from_skill_id(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        skill_id: builtins.str,
    ) -> ISkill:
        '''Reference an existing Skill, defined outside of the CDK code, by Skill ID.

        :param scope: -
        :param id: -
        :param skill_id: -
        '''
        return typing.cast(ISkill, jsii.sinvoke(cls, "fromSkillId", [scope, id, skill_id]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skillId")
    def skill_id(self) -> builtins.str:
        '''The Skill ID of this Alexa Skill.'''
        return typing.cast(builtins.str, jsii.get(self, "skillId"))


@jsii.data_type(
    jsii_type="cdk-alexa-skill.SkillProps",
    jsii_struct_bases=[],
    name_mapping={
        "alexa_vendor_id": "alexaVendorId",
        "lwa_client_id": "lwaClientId",
        "lwa_client_secret": "lwaClientSecret",
        "lwa_refresh_token": "lwaRefreshToken",
        "skill_package_path": "skillPackagePath",
        "endpoint_lambda_function": "endpointLambdaFunction",
    },
)
class SkillProps:
    def __init__(
        self,
        *,
        alexa_vendor_id: builtins.str,
        lwa_client_id: builtins.str,
        lwa_client_secret: aws_cdk.core.SecretValue,
        lwa_refresh_token: aws_cdk.core.SecretValue,
        skill_package_path: builtins.str,
        endpoint_lambda_function: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
    ) -> None:
        '''Construction properties for an Alexa Skill object.

        :param alexa_vendor_id: Vendor ID associated with Alexa Developer account.
        :param lwa_client_id: Client ID of Login with Amazon (LWA) Security Profile.
        :param lwa_client_secret: Client secret associated with Login with Amazon (LWA) Client ID.
        :param lwa_refresh_token: Refresh token associated with Login with Amazon (LWA) Security Profile.
        :param skill_package_path: The relative path to the skill package directory containing all configuration files for the Alexa Skill.
        :param endpoint_lambda_function: The Lambda Function to be configured as the endpoint for the Alexa Skill. Default: - No endpoint Lambda Function
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alexa_vendor_id": alexa_vendor_id,
            "lwa_client_id": lwa_client_id,
            "lwa_client_secret": lwa_client_secret,
            "lwa_refresh_token": lwa_refresh_token,
            "skill_package_path": skill_package_path,
        }
        if endpoint_lambda_function is not None:
            self._values["endpoint_lambda_function"] = endpoint_lambda_function

    @builtins.property
    def alexa_vendor_id(self) -> builtins.str:
        '''Vendor ID associated with Alexa Developer account.'''
        result = self._values.get("alexa_vendor_id")
        assert result is not None, "Required property 'alexa_vendor_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lwa_client_id(self) -> builtins.str:
        '''Client ID of Login with Amazon (LWA) Security Profile.'''
        result = self._values.get("lwa_client_id")
        assert result is not None, "Required property 'lwa_client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lwa_client_secret(self) -> aws_cdk.core.SecretValue:
        '''Client secret associated with Login with Amazon (LWA) Client ID.'''
        result = self._values.get("lwa_client_secret")
        assert result is not None, "Required property 'lwa_client_secret' is missing"
        return typing.cast(aws_cdk.core.SecretValue, result)

    @builtins.property
    def lwa_refresh_token(self) -> aws_cdk.core.SecretValue:
        '''Refresh token associated with Login with Amazon (LWA) Security Profile.'''
        result = self._values.get("lwa_refresh_token")
        assert result is not None, "Required property 'lwa_refresh_token' is missing"
        return typing.cast(aws_cdk.core.SecretValue, result)

    @builtins.property
    def skill_package_path(self) -> builtins.str:
        '''The relative path to the skill package directory containing all configuration files for the Alexa Skill.'''
        result = self._values.get("skill_package_path")
        assert result is not None, "Required property 'skill_package_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_lambda_function(self) -> typing.Optional[aws_cdk.aws_lambda.IFunction]:
        '''The Lambda Function to be configured as the endpoint for the Alexa Skill.

        :default: - No endpoint Lambda Function
        '''
        result = self._values.get("endpoint_lambda_function")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IFunction], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SkillProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ISkill",
    "Skill",
    "SkillProps",
]

publication.publish()

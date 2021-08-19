'''
# cdk-datalake-constructs  <!-- omit in toc -->

***Very experimental until version 1.0.***
This is my attempt at simplifying deploying various datalake strategies in AWS with the CDK.

[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)
[![Build](https://github.com/randyridgley/cdk-datalake-constructs/workflows/build/badge.svg)](https://github.com/randyridgley/cdk-datalake-constructs/workflows/build.yml)
[![Release](https://github.com/randyridgley/cdk-datalake-constructs/workflows/release/badge.svg)](https://github.com/randyridgley/cdk-datalake-constructs/workflows/release.yml)
[![Python](https://img.shields.io/pypi/pyversions/cdk-datalake-constructs)](https://pypi.org) [![pip](https://img.shields.io/badge/pip%20install-cdk--datalake--constructs-blue)](https://pypi.org/project/cdk-datalake-constructs/)
[![npm version](https://img.shields.io/npm/v/cdk-datalake-constructs)](https://www.npmjs.com/package/cdk-datalake-constructs) [![pypi version](https://img.shields.io/pypi/v/cdk-datalake-constructs)](https://pypi.org/project/cdk-datalake-constructs/) [![Maven](https://img.shields.io/maven-central/v/io.github.randyridgley/cdk-datalake-constructs)](https://search.maven.org/search?q=a:cdk-datalake-constructs) [![nuget](https://img.shields.io/nuget/v/Cdk.Datalake.Constructs)](https://www.nuget.org/packages/Cdk.Datalake.Constructs/)

**Table of Contents**

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)

  * [Basic](#basic)
  * [Data Mesh](#data-mesh)
* [Documentation](#documentation)

  * [Construct API Reference](#construct-api-reference)
* [Supporting this project](#supporting-this-project)
* [License](#license)

## Features

* Easy to Start - Create a Datalake in a few lines.
* Easy to Expand - Expand into multiple accounts and into a data mesh.
* Easy to Admin - Initial governance created on deploy.

## Installation

TypeScript/JavaScript

```sh
$ npm install @randyridgley/cdk-datalake-constructs
```

Python

```sh
$ pip install cdk-datalake-constructs.cdk-datalake-constructs
```

.Net

```sh
$ nuget install CDK.Datalake.Constructs

# See more: https://www.nuget.org/packages/CDK.Datalake.Constructs/
```

## Usage

### Basic

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from randyridgley.cdk_datalake_constructs import DataLake

taxi_pipes = [
    pipelines.YellowPipeline(),
    pipelines.GreenPipeline()
]

data_products = [{
    "pipelines": taxi_pipes,
    "account_id": lake_account_id,
    "data_catalog_account_id": "123456789012",
    "database_name": "taxi-product"
}]

# deploy to local account
dl.DataLake(self, "LocalDataLake",
    name="data-lake,",
    account_id=central_account_id,
    region="us-east-1",
    policy_tags={
        "classification": "public,confidential,highlyconfidential,restricted,critical",
        "owner": "product,central,consumer"
    },
    stage_name=Stage.PROD,
    data_products=data_products,
    create_default_database=False
)
```

### Data Mesh

You can setup cross account access and pre-created policy tags for TBAC access in Lake Formation

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
lake_account_id = app.node.try_get_context("lakeAccountId")
central_account_id = app.node.try_get_context("centralAccountId")
consumer_account_id = app.node.try_get_context("consumerAccountId")

taxi_pipes = [
    pipelines.YellowPipeline(),
    pipelines.GreenPipeline()
]

data_products = [{
    "pipelines": taxi_pipes,
    "account_id": lake_account_id,
    "data_catalog_account_id": central_account_id,
    "database_name": "taxi-product"
}]

# deploy to the central account
dl.DataLake(self, "CentralDataLake",
    name="central-lake,",
    account_id=central_account_id,
    region="us-east-1",
    policy_tags={
        "classification": "public,confidential,highlyconfidential,restricted,critical",
        "owner": "product,central,consumer"
    },
    stage_name=Stage.PROD,
    cross_account={
        "consumer_account_ids": [consumer_account_id, lake_account_id],
        "data_catalog_owner_account_id": central_account_id,
        "region": "us-east-1"
    },
    data_products=data_products,
    create_default_database=True
)

# deploy to the data product account
datalake = dl.DataLake(self, "LocalDataLake",
    name="local-lake",
    account_id=lake_account_id,
    region="us-east-1",
    stage_name=Stage.PROD,
    data_products=data_products,
    create_default_database=True
)

# Optionally add custom resource to download public data set products
datalake.create_downloader_custom_resource(account_id, region, props.stage_name)

# deploy to consumer account
datalake = dl.DataLake(self, "ConsumerDataLake",
    name="consumer-lake",
    account_id=consumer_account_id,
    region="us-east-1",
    stage_name=Stage.PROD,
    policy_tags={
        "access": "analyst,engineer,marketing"
    },
    create_default_database=True
)
```

## Documentation

### Construct API Reference

See [API.md](./API.md).

## Supporting this project

I'm working on this project in my free time, if you like my project, or found it helpful and would like to support me any contributions are much appreciated! ❤️

## License

This project is distributed under the [MIT](./LICENSE).
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

import aws_cdk.aws_athena
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_ec2
import aws_cdk.aws_events
import aws_cdk.aws_glue
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_sns
import aws_cdk.core


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.CompressionType")
class CompressionType(enum.Enum):
    '''
    :stability: experimental
    '''

    UNCOMPRESSED = "UNCOMPRESSED"
    '''
    :stability: experimental
    '''
    GZIP = "GZIP"
    '''
    :stability: experimental
    '''
    ZIP = "ZIP"
    '''
    :stability: experimental
    '''
    SNAPPY = "SNAPPY"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.CrossAccountProperties",
    jsii_struct_bases=[],
    name_mapping={
        "consumer_account_ids": "consumerAccountIds",
        "data_catalog_owner_account_id": "dataCatalogOwnerAccountId",
    },
)
class CrossAccountProperties:
    def __init__(
        self,
        *,
        consumer_account_ids: typing.Sequence[builtins.str],
        data_catalog_owner_account_id: builtins.str,
    ) -> None:
        '''
        :param consumer_account_ids: 
        :param data_catalog_owner_account_id: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "consumer_account_ids": consumer_account_ids,
            "data_catalog_owner_account_id": data_catalog_owner_account_id,
        }

    @builtins.property
    def consumer_account_ids(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("consumer_account_ids")
        assert result is not None, "Required property 'consumer_account_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def data_catalog_owner_account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_catalog_owner_account_id")
        assert result is not None, "Required property 'data_catalog_owner_account_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossAccountProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataCatalogOwner",
    jsii_struct_bases=[],
    name_mapping={"account_id": "accountId"},
)
class DataCatalogOwner:
    def __init__(self, *, account_id: builtins.str) -> None:
        '''
        :param account_id: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
        }

    @builtins.property
    def account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCatalogOwner(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLake(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLake",
):
    '''(experimental) A CDK construct to create a DataLake.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        create_default_database: builtins.bool,
        name: builtins.str,
        region: builtins.str,
        stage_name: "Stage",
        cross_account_access: typing.Optional[CrossAccountProperties] = None,
        datalake_admin_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        datalake_creator_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        data_products: typing.Optional[typing.Sequence["DataProduct"]] = None,
        glue_security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        log_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        policy_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.Vpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_id: (experimental) The AWS Account Id of the Datalake.
        :param create_default_database: 
        :param name: (experimental) The name of the DataLake.
        :param region: (experimental) The AWS Region the Datalake will be deployed.
        :param stage_name: (experimental) The Stage the DataLake will be deployed.
        :param cross_account_access: (experimental) Cross account AWS account IDs. Default: - No cross account ids
        :param datalake_admin_role: (experimental) Data Lake Admin role. Default: - Admin role created based on best practices
        :param datalake_creator_role: (experimental) Data Lake Database Creator role. Default: - Database creator role created based on best practices
        :param data_products: (experimental) The List of DataProducts for this account. Default: - No data products
        :param glue_security_group: (experimental) Security group to attach to Glue jobs. Default: - No security group
        :param log_bucket_props: 
        :param policy_tags: (experimental) List of Lake Formation TBAC policy tags. Default: - No tags
        :param vpc: (experimental) VPC for Glue jobs. Default: - No vpc

        :stability: experimental
        '''
        props = DataLakeProperties(
            account_id=account_id,
            create_default_database=create_default_database,
            name=name,
            region=region,
            stage_name=stage_name,
            cross_account_access=cross_account_access,
            datalake_admin_role=datalake_admin_role,
            datalake_creator_role=datalake_creator_role,
            data_products=data_products,
            glue_security_group=glue_security_group,
            log_bucket_props=log_bucket_props,
            policy_tags=policy_tags,
            vpc=vpc,
        )

        jsii.create(DataLake, self, [scope, id, props])

    @jsii.member(jsii_name="createDownloaderCustomResource")
    def create_downloader_custom_resource(
        self,
        account_id: builtins.str,
        region: builtins.str,
        stage_name: builtins.str,
    ) -> None:
        '''
        :param account_id: -
        :param region: -
        :param stage_name: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "createDownloaderCustomResource", [account_id, region, stage_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="athenaWorkgroup")
    def athena_workgroup(self) -> aws_cdk.aws_athena.CfnWorkGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_athena.CfnWorkGroup, jsii.get(self, "athenaWorkgroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databases")
    def databases(self) -> typing.Mapping[builtins.str, aws_cdk.aws_glue.Database]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_glue.Database], jsii.get(self, "databases"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datalakeAdminRole")
    def datalake_admin_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "datalakeAdminRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datalakeDbCreatorRole")
    def datalake_db_creator_role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "datalakeDbCreatorRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSets")
    def data_sets(self) -> typing.Mapping[builtins.str, "DataSet"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "DataSet"], jsii.get(self, "dataSets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataStreams")
    def data_streams(self) -> typing.Mapping[builtins.str, "KinesisStream"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "KinesisStream"], jsii.get(self, "dataStreams"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logBucket")
    def log_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "logBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> "Stage":
        '''
        :stability: experimental
        '''
        return typing.cast("Stage", jsii.get(self, "stageName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.Vpc]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.Vpc], jsii.get(self, "vpc"))


class DataLakeAdministrator(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeAdministrator",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 

        :stability: experimental
        '''
        props = DataLakeAdministratorProps(name=name)

        jsii.create(DataLakeAdministrator, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeAdministratorProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class DataLakeAdministratorProps:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeAdministratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLakeAnalyst(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeAnalyst",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        read_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
        write_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 
        :param read_access_buckets: 
        :param write_access_buckets: 

        :stability: experimental
        '''
        props = DataLakeAnalystProps(
            name=name,
            read_access_buckets=read_access_buckets,
            write_access_buckets=write_access_buckets,
        )

        jsii.create(DataLakeAnalyst, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> aws_cdk.aws_iam.User:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.User, jsii.get(self, "user"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeAnalystProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "read_access_buckets": "readAccessBuckets",
        "write_access_buckets": "writeAccessBuckets",
    },
)
class DataLakeAnalystProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        read_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
        write_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
    ) -> None:
        '''
        :param name: 
        :param read_access_buckets: 
        :param write_access_buckets: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if read_access_buckets is not None:
            self._values["read_access_buckets"] = read_access_buckets
        if write_access_buckets is not None:
            self._values["write_access_buckets"] = write_access_buckets

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def read_access_buckets(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("read_access_buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]], result)

    @builtins.property
    def write_access_buckets(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("write_access_buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeAnalystProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLakeBucket(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeBucket",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
        cross_account: builtins.bool,
        data_catalog_account_id: builtins.str,
        log_bucket: aws_cdk.aws_s3.Bucket,
        s3_properties: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: 
        :param cross_account: 
        :param data_catalog_account_id: 
        :param log_bucket: 
        :param s3_properties: 

        :stability: experimental
        '''
        props = DataLakeBucketProps(
            bucket_name=bucket_name,
            cross_account=cross_account,
            data_catalog_account_id=data_catalog_account_id,
            log_bucket=log_bucket,
            s3_properties=s3_properties,
        )

        jsii.create(DataLakeBucket, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "bucket"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeBucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "cross_account": "crossAccount",
        "data_catalog_account_id": "dataCatalogAccountId",
        "log_bucket": "logBucket",
        "s3_properties": "s3Properties",
    },
)
class DataLakeBucketProps:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        cross_account: builtins.bool,
        data_catalog_account_id: builtins.str,
        log_bucket: aws_cdk.aws_s3.Bucket,
        s3_properties: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
    ) -> None:
        '''
        :param bucket_name: 
        :param cross_account: 
        :param data_catalog_account_id: 
        :param log_bucket: 
        :param s3_properties: 

        :stability: experimental
        '''
        if isinstance(s3_properties, dict):
            s3_properties = aws_cdk.aws_s3.BucketProps(**s3_properties)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "cross_account": cross_account,
            "data_catalog_account_id": data_catalog_account_id,
            "log_bucket": log_bucket,
        }
        if s3_properties is not None:
            self._values["s3_properties"] = s3_properties

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        result = self._values.get("cross_account")
        assert result is not None, "Required property 'cross_account' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def data_catalog_account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_catalog_account_id")
        assert result is not None, "Required property 'data_catalog_account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("log_bucket")
        assert result is not None, "Required property 'log_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    @builtins.property
    def s3_properties(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_properties")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLakeCreator(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeCreator",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 

        :stability: experimental
        '''
        props = DataLakeCreatorProperties(name=name)

        jsii.create(DataLakeCreator, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeCreatorProperties",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class DataLakeCreatorProperties:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeCreatorProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataLakeProperties",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "create_default_database": "createDefaultDatabase",
        "name": "name",
        "region": "region",
        "stage_name": "stageName",
        "cross_account_access": "crossAccountAccess",
        "datalake_admin_role": "datalakeAdminRole",
        "datalake_creator_role": "datalakeCreatorRole",
        "data_products": "dataProducts",
        "glue_security_group": "glueSecurityGroup",
        "log_bucket_props": "logBucketProps",
        "policy_tags": "policyTags",
        "vpc": "vpc",
    },
)
class DataLakeProperties:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        create_default_database: builtins.bool,
        name: builtins.str,
        region: builtins.str,
        stage_name: "Stage",
        cross_account_access: typing.Optional[CrossAccountProperties] = None,
        datalake_admin_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        datalake_creator_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        data_products: typing.Optional[typing.Sequence["DataProduct"]] = None,
        glue_security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        log_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        policy_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.Vpc] = None,
    ) -> None:
        '''
        :param account_id: (experimental) The AWS Account Id of the Datalake.
        :param create_default_database: 
        :param name: (experimental) The name of the DataLake.
        :param region: (experimental) The AWS Region the Datalake will be deployed.
        :param stage_name: (experimental) The Stage the DataLake will be deployed.
        :param cross_account_access: (experimental) Cross account AWS account IDs. Default: - No cross account ids
        :param datalake_admin_role: (experimental) Data Lake Admin role. Default: - Admin role created based on best practices
        :param datalake_creator_role: (experimental) Data Lake Database Creator role. Default: - Database creator role created based on best practices
        :param data_products: (experimental) The List of DataProducts for this account. Default: - No data products
        :param glue_security_group: (experimental) Security group to attach to Glue jobs. Default: - No security group
        :param log_bucket_props: 
        :param policy_tags: (experimental) List of Lake Formation TBAC policy tags. Default: - No tags
        :param vpc: (experimental) VPC for Glue jobs. Default: - No vpc

        :stability: experimental
        '''
        if isinstance(cross_account_access, dict):
            cross_account_access = CrossAccountProperties(**cross_account_access)
        if isinstance(log_bucket_props, dict):
            log_bucket_props = aws_cdk.aws_s3.BucketProps(**log_bucket_props)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "create_default_database": create_default_database,
            "name": name,
            "region": region,
            "stage_name": stage_name,
        }
        if cross_account_access is not None:
            self._values["cross_account_access"] = cross_account_access
        if datalake_admin_role is not None:
            self._values["datalake_admin_role"] = datalake_admin_role
        if datalake_creator_role is not None:
            self._values["datalake_creator_role"] = datalake_creator_role
        if data_products is not None:
            self._values["data_products"] = data_products
        if glue_security_group is not None:
            self._values["glue_security_group"] = glue_security_group
        if log_bucket_props is not None:
            self._values["log_bucket_props"] = log_bucket_props
        if policy_tags is not None:
            self._values["policy_tags"] = policy_tags
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def account_id(self) -> builtins.str:
        '''(experimental) The AWS Account Id of the Datalake.

        :stability: experimental
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_default_database(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        result = self._values.get("create_default_database")
        assert result is not None, "Required property 'create_default_database' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the DataLake.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) The AWS Region the Datalake will be deployed.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage_name(self) -> "Stage":
        '''(experimental) The Stage the DataLake will be deployed.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast("Stage", result)

    @builtins.property
    def cross_account_access(self) -> typing.Optional[CrossAccountProperties]:
        '''(experimental) Cross account AWS account IDs.

        :default: - No cross account ids

        :see: https://aws.amazon.com/premiumsupport/knowledge-center/glue-data-catalog-cross-account-access/
        :stability: experimental
        :description: - The cross account ids needed for setting up the Glue resource policy
        '''
        result = self._values.get("cross_account_access")
        return typing.cast(typing.Optional[CrossAccountProperties], result)

    @builtins.property
    def datalake_admin_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        '''(experimental) Data Lake Admin role.

        :default: - Admin role created based on best practices

        :see: https://docs.aws.amazon.com/lake-formation/latest/dg/permissions-reference.html
        :stability: experimental
        :description: - IAM Role for DataLake admin access
        '''
        result = self._values.get("datalake_admin_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], result)

    @builtins.property
    def datalake_creator_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        '''(experimental) Data Lake Database Creator role.

        :default: - Database creator role created based on best practices

        :see: https://docs.aws.amazon.com/lake-formation/latest/dg/permissions-reference.html
        :stability: experimental
        :description: - IAM Role for DataLake database creator access
        '''
        result = self._values.get("datalake_creator_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], result)

    @builtins.property
    def data_products(self) -> typing.Optional[typing.List["DataProduct"]]:
        '''(experimental) The List of DataProducts for this account.

        :default: - No data products

        :stability: experimental
        '''
        result = self._values.get("data_products")
        return typing.cast(typing.Optional[typing.List["DataProduct"]], result)

    @builtins.property
    def glue_security_group(self) -> typing.Optional[aws_cdk.aws_ec2.SecurityGroup]:
        '''(experimental) Security group to attach to Glue jobs.

        :default: - No security group

        :see: https://docs.aws.amazon.com/glue/latest/dg/setup-vpc-for-glue-access.html
        :stability: experimental
        :description: - Security Group that will be used to allow port access in the VPC
        '''
        result = self._values.get("glue_security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def log_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("log_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def policy_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) List of Lake Formation TBAC policy tags.

        :default: - No tags

        :see: https://docs.aws.amazon.com/lake-formation/latest/dg/TBAC-section.html
        :stability: experimental
        :description: - Define the tag taxonomy needed for the DataLake
        '''
        result = self._values.get("policy_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.Vpc]:
        '''(experimental) VPC for Glue jobs.

        :default: - No vpc

        :stability: experimental
        :description: - The VPC that will be used if the Glue job needs access to resources within the account or internet access
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.DataPipelineType")
class DataPipelineType(enum.Enum):
    '''
    :stability: experimental
    '''

    STREAM = "STREAM"
    '''
    :stability: experimental
    '''
    JDBC = "JDBC"
    '''
    :stability: experimental
    '''
    S3 = "S3"
    '''
    :stability: experimental
    '''


class DataProduct(
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataProduct",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        account_id: builtins.str,
        database_name: builtins.str,
        pipelines: typing.Sequence["Pipeline"],
        data_catalog_account_id: typing.Optional[builtins.str] = None,
        s3_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
    ) -> None:
        '''
        :param account_id: 
        :param database_name: 
        :param pipelines: 
        :param data_catalog_account_id: 
        :param s3_bucket_props: 

        :stability: experimental
        '''
        props = DataProductProperties(
            account_id=account_id,
            database_name=database_name,
            pipelines=pipelines,
            data_catalog_account_id=data_catalog_account_id,
            s3_bucket_props=s3_bucket_props,
        )

        jsii.create(DataProduct, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelines")
    def pipelines(self) -> typing.List["Pipeline"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["Pipeline"], jsii.get(self, "pipelines"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCatalogAccountId")
    def data_catalog_account_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataCatalogAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketProps")
    def s3_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], jsii.get(self, "s3BucketProps"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataProductProperties",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "database_name": "databaseName",
        "pipelines": "pipelines",
        "data_catalog_account_id": "dataCatalogAccountId",
        "s3_bucket_props": "s3BucketProps",
    },
)
class DataProductProperties:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        database_name: builtins.str,
        pipelines: typing.Sequence["Pipeline"],
        data_catalog_account_id: typing.Optional[builtins.str] = None,
        s3_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
    ) -> None:
        '''
        :param account_id: 
        :param database_name: 
        :param pipelines: 
        :param data_catalog_account_id: 
        :param s3_bucket_props: 

        :stability: experimental
        '''
        if isinstance(s3_bucket_props, dict):
            s3_bucket_props = aws_cdk.aws_s3.BucketProps(**s3_bucket_props)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "database_name": database_name,
            "pipelines": pipelines,
        }
        if data_catalog_account_id is not None:
            self._values["data_catalog_account_id"] = data_catalog_account_id
        if s3_bucket_props is not None:
            self._values["s3_bucket_props"] = s3_bucket_props

    @builtins.property
    def account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipelines(self) -> typing.List["Pipeline"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pipelines")
        assert result is not None, "Required property 'pipelines' is missing"
        return typing.cast(typing.List["Pipeline"], result)

    @builtins.property
    def data_catalog_account_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_catalog_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProductProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataSet(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.DataSet",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        data_product: DataProduct,
        log_bucket: aws_cdk.aws_s3.Bucket,
        pipeline: "Pipeline",
        region: builtins.str,
        stage: "Stage",
        encryption_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        s3_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_id: 
        :param data_product: 
        :param log_bucket: 
        :param pipeline: 
        :param region: 
        :param stage: 
        :param encryption_key: 
        :param s3_bucket_props: 

        :stability: experimental
        '''
        props = DataSetProperties(
            account_id=account_id,
            data_product=data_product,
            log_bucket=log_bucket,
            pipeline=pipeline,
            region=region,
            stage=stage,
            encryption_key=encryption_key,
            s3_bucket_props=s3_bucket_props,
        )

        jsii.create(DataSet, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataProduct")
    def data_product(self) -> DataProduct:
        '''
        :stability: experimental
        '''
        return typing.cast(DataProduct, jsii.get(self, "dataProduct"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> "Pipeline":
        '''
        :stability: experimental
        '''
        return typing.cast("Pipeline", jsii.get(self, "pipeline"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rawBucketName")
    def raw_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "rawBucketName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refinedBucketName")
    def refined_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "refinedBucketName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustedBucketName")
    def trusted_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "trustedBucketName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="downloadLocations")
    def download_locations(self) -> typing.Optional["DataSetResult"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["DataSetResult"], jsii.get(self, "downloadLocations"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dropLocation")
    def drop_location(self) -> typing.Optional["DataSetLocation"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["DataSetLocation"], jsii.get(self, "dropLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], jsii.get(self, "encryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3NotificationTopic")
    def s3_notification_topic(self) -> typing.Optional[aws_cdk.aws_sns.Topic]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_sns.Topic], jsii.get(self, "s3NotificationTopic"))

    @s3_notification_topic.setter
    def s3_notification_topic(
        self,
        value: typing.Optional[aws_cdk.aws_sns.Topic],
    ) -> None:
        jsii.set(self, "s3NotificationTopic", value)


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.DataSetLocation")
class DataSetLocation(enum.Enum):
    '''
    :stability: experimental
    '''

    RAW = "RAW"
    '''
    :stability: experimental
    '''
    TRUSTED = "TRUSTED"
    '''
    :stability: experimental
    '''
    REFINED = "REFINED"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataSetProperties",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "data_product": "dataProduct",
        "log_bucket": "logBucket",
        "pipeline": "pipeline",
        "region": "region",
        "stage": "stage",
        "encryption_key": "encryptionKey",
        "s3_bucket_props": "s3BucketProps",
    },
)
class DataSetProperties:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        data_product: DataProduct,
        log_bucket: aws_cdk.aws_s3.Bucket,
        pipeline: "Pipeline",
        region: builtins.str,
        stage: "Stage",
        encryption_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        s3_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
    ) -> None:
        '''
        :param account_id: 
        :param data_product: 
        :param log_bucket: 
        :param pipeline: 
        :param region: 
        :param stage: 
        :param encryption_key: 
        :param s3_bucket_props: 

        :stability: experimental
        '''
        if isinstance(s3_bucket_props, dict):
            s3_bucket_props = aws_cdk.aws_s3.BucketProps(**s3_bucket_props)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "data_product": data_product,
            "log_bucket": log_bucket,
            "pipeline": pipeline,
            "region": region,
            "stage": stage,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if s3_bucket_props is not None:
            self._values["s3_bucket_props"] = s3_bucket_props

    @builtins.property
    def account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_product(self) -> DataProduct:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_product")
        assert result is not None, "Required property 'data_product' is missing"
        return typing.cast(DataProduct, result)

    @builtins.property
    def log_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("log_bucket")
        assert result is not None, "Required property 'log_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    @builtins.property
    def pipeline(self) -> "Pipeline":
        '''
        :stability: experimental
        '''
        result = self._values.get("pipeline")
        assert result is not None, "Required property 'pipeline' is missing"
        return typing.cast("Pipeline", result)

    @builtins.property
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage(self) -> "Stage":
        '''
        :stability: experimental
        '''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast("Stage", result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''
        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], result)

    @builtins.property
    def s3_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSetProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataSetResult",
    jsii_struct_bases=[],
    name_mapping={
        "destination_prefix": "destinationPrefix",
        "destination_bucket_name": "destinationBucketName",
        "source_bucket_name": "sourceBucketName",
        "source_keys": "sourceKeys",
    },
)
class DataSetResult:
    def __init__(
        self,
        *,
        destination_prefix: builtins.str,
        destination_bucket_name: typing.Optional[builtins.str] = None,
        source_bucket_name: typing.Optional[builtins.str] = None,
        source_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param destination_prefix: 
        :param destination_bucket_name: 
        :param source_bucket_name: 
        :param source_keys: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_prefix": destination_prefix,
        }
        if destination_bucket_name is not None:
            self._values["destination_bucket_name"] = destination_bucket_name
        if source_bucket_name is not None:
            self._values["source_bucket_name"] = source_bucket_name
        if source_keys is not None:
            self._values["source_keys"] = source_keys

    @builtins.property
    def destination_prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_prefix")
        assert result is not None, "Required property 'destination_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_bucket_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_bucket_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSetResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DataStreamProperties",
    jsii_struct_bases=[],
    name_mapping={
        "data_catalog_owner": "dataCatalogOwner",
        "destination_bucket_name": "destinationBucketName",
        "destination_prefix": "destinationPrefix",
        "lambda_data_generator": "lambdaDataGenerator",
        "name": "name",
        "stream_name": "streamName",
    },
)
class DataStreamProperties:
    def __init__(
        self,
        *,
        data_catalog_owner: DataCatalogOwner,
        destination_bucket_name: builtins.str,
        destination_prefix: builtins.str,
        lambda_data_generator: "LambdaDataGeneratorProperties",
        name: builtins.str,
        stream_name: builtins.str,
    ) -> None:
        '''
        :param data_catalog_owner: 
        :param destination_bucket_name: 
        :param destination_prefix: 
        :param lambda_data_generator: 
        :param name: 
        :param stream_name: 

        :stability: experimental
        '''
        if isinstance(data_catalog_owner, dict):
            data_catalog_owner = DataCatalogOwner(**data_catalog_owner)
        if isinstance(lambda_data_generator, dict):
            lambda_data_generator = LambdaDataGeneratorProperties(**lambda_data_generator)
        self._values: typing.Dict[str, typing.Any] = {
            "data_catalog_owner": data_catalog_owner,
            "destination_bucket_name": destination_bucket_name,
            "destination_prefix": destination_prefix,
            "lambda_data_generator": lambda_data_generator,
            "name": name,
            "stream_name": stream_name,
        }

    @builtins.property
    def data_catalog_owner(self) -> DataCatalogOwner:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_catalog_owner")
        assert result is not None, "Required property 'data_catalog_owner' is missing"
        return typing.cast(DataCatalogOwner, result)

    @builtins.property
    def destination_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_bucket_name")
        assert result is not None, "Required property 'destination_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_prefix")
        assert result is not None, "Required property 'destination_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_data_generator(self) -> "LambdaDataGeneratorProperties":
        '''
        :stability: experimental
        '''
        result = self._values.get("lambda_data_generator")
        assert result is not None, "Required property 'lambda_data_generator' is missing"
        return typing.cast("LambdaDataGeneratorProperties", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stream_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("stream_name")
        assert result is not None, "Required property 'stream_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataStreamProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.DeliveryStreamProperties",
    jsii_struct_bases=[],
    name_mapping={
        "kinesis_stream": "kinesisStream",
        "s3_bucket": "s3Bucket",
        "compression": "compression",
        "s3_prefix": "s3Prefix",
        "transform_function": "transformFunction",
    },
)
class DeliveryStreamProperties:
    def __init__(
        self,
        *,
        kinesis_stream: aws_cdk.aws_kinesis.Stream,
        s3_bucket: aws_cdk.aws_s3.IBucket,
        compression: typing.Optional[CompressionType] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        transform_function: typing.Optional[aws_cdk.aws_lambda.Function] = None,
    ) -> None:
        '''
        :param kinesis_stream: 
        :param s3_bucket: 
        :param compression: 
        :param s3_prefix: 
        :param transform_function: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "kinesis_stream": kinesis_stream,
            "s3_bucket": s3_bucket,
        }
        if compression is not None:
            self._values["compression"] = compression
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if transform_function is not None:
            self._values["transform_function"] = transform_function

    @builtins.property
    def kinesis_stream(self) -> aws_cdk.aws_kinesis.Stream:
        '''
        :stability: experimental
        '''
        result = self._values.get("kinesis_stream")
        assert result is not None, "Required property 'kinesis_stream' is missing"
        return typing.cast(aws_cdk.aws_kinesis.Stream, result)

    @builtins.property
    def s3_bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_bucket")
        assert result is not None, "Required property 's3_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def compression(self) -> typing.Optional[CompressionType]:
        '''
        :stability: experimental
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional[CompressionType], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transform_function(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transform_function")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.DeliveryStreamType")
class DeliveryStreamType(enum.Enum):
    '''
    :stability: experimental
    '''

    DIRECT_PUT = "DIRECT_PUT"
    '''
    :stability: experimental
    '''
    KINESIS_STREAM_AS_SOURCE = "KINESIS_STREAM_AS_SOURCE"
    '''
    :stability: experimental
    '''


class GlueCrawler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.GlueCrawler",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: "IGlueCrawlerProperties",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(GlueCrawler, self, [scope, id, props])

    @jsii.member(jsii_name="metricFailure")
    def metric_failure(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricFailure", [props]))

    @jsii.member(jsii_name="metricSuccess")
    def metric_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSuccess", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crawler")
    def crawler(self) -> aws_cdk.aws_glue.CfnCrawler:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.CfnCrawler, jsii.get(self, "crawler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricFailureRule")
    def metric_failure_rule(self) -> aws_cdk.aws_events.Rule:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "metricFailureRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricSuccessRule")
    def metric_success_rule(self) -> aws_cdk.aws_events.Rule:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "metricSuccessRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))


class GlueJob(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.GlueJob",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deployment_bucket: aws_cdk.aws_s3.IBucket,
        job_script: builtins.str,
        job_type: "GlueJobType",
        name: builtins.str,
        worker_type: "GlueWorkerType",
        description: typing.Optional[builtins.str] = None,
        glue_version: typing.Optional["GlueVersion"] = None,
        job_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_concurrent_runs: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        read_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
        role_name: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[jsii.Number] = None,
        write_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param deployment_bucket: 
        :param job_script: 
        :param job_type: 
        :param name: 
        :param worker_type: 
        :param description: 
        :param glue_version: 
        :param job_args: 
        :param max_capacity: 
        :param max_concurrent_runs: 
        :param max_retries: 
        :param number_of_workers: 
        :param read_access_buckets: 
        :param role_name: 
        :param timeout: 
        :param write_access_buckets: 

        :stability: experimental
        '''
        props = GlueJobProperties(
            deployment_bucket=deployment_bucket,
            job_script=job_script,
            job_type=job_type,
            name=name,
            worker_type=worker_type,
            description=description,
            glue_version=glue_version,
            job_args=job_args,
            max_capacity=max_capacity,
            max_concurrent_runs=max_concurrent_runs,
            max_retries=max_retries,
            number_of_workers=number_of_workers,
            read_access_buckets=read_access_buckets,
            role_name=role_name,
            timeout=timeout,
            write_access_buckets=write_access_buckets,
        )

        jsii.create(GlueJob, self, [scope, id, props])

    @jsii.member(jsii_name="diskSpaceUsedMbMetric")
    def disk_space_used_mb_metric(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "diskSpaceUsedMbMetric", [props]))

    @jsii.member(jsii_name="elapsedTimeMetric")
    def elapsed_time_metric(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "elapsedTimeMetric", [props]))

    @jsii.member(jsii_name="jvmHeapUsageMetric")
    def jvm_heap_usage_metric(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "jvmHeapUsageMetric", [props]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimension_type: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param metric_name: -
        :param dimension_type: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metric", [metric_name, dimension_type, props]))

    @jsii.member(jsii_name="metricAllExecutionAttemptsFailed")
    def metric_all_execution_attempts_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricAllExecutionAttemptsFailed", [props]))

    @jsii.member(jsii_name="metricFailure")
    def metric_failure(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricFailure", [props]))

    @jsii.member(jsii_name="metricSuccess")
    def metric_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSuccess", [props]))

    @jsii.member(jsii_name="metricTimeout")
    def metric_timeout(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricTimeout", [props]))

    @jsii.member(jsii_name="runTimeInMiliseconds")
    def run_time_in_miliseconds(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "runTimeInMiliseconds", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allExecutionAttemptsFailedEventDetailType")
    def all_execution_attempts_failed_event_detail_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "allExecutionAttemptsFailedEventDetailType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allExecutionAttemptsFailedEventSource")
    def all_execution_attempts_failed_event_source(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "allExecutionAttemptsFailedEventSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionFailureRule")
    def execution_failure_rule(self) -> aws_cdk.aws_events.Rule:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "executionFailureRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="job")
    def job(self) -> aws_cdk.aws_glue.CfnJob:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.CfnJob, jsii.get(self, "job"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.SingletonFunction:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.SingletonFunction, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricFailureRule")
    def metric_failure_rule(self) -> aws_cdk.aws_events.Rule:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "metricFailureRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricSuccessRule")
    def metric_success_rule(self) -> aws_cdk.aws_events.Rule:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "metricSuccessRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricTimeoutRule")
    def metric_timeout_rule(self) -> aws_cdk.aws_events.Rule:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "metricTimeoutRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))


class GlueJobOps(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.GlueJobOps",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: "IGlueOpsProperties",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(GlueJobOps, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmsSev2")
    def alarms_sev2(self) -> typing.List[aws_cdk.aws_cloudwatch.Alarm]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[aws_cdk.aws_cloudwatch.Alarm], jsii.get(self, "alarmsSev2"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmsSev3")
    def alarms_sev3(self) -> typing.List[aws_cdk.aws_cloudwatch.Alarm]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[aws_cdk.aws_cloudwatch.Alarm], jsii.get(self, "alarmsSev3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="job")
    def job(self) -> GlueJob:
        '''
        :stability: experimental
        '''
        return typing.cast(GlueJob, jsii.get(self, "job"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmHeapSizeExceeding80PercentAlarm")
    def jvm_heap_size_exceeding80_percent_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "jvmHeapSizeExceeding80PercentAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmHeapSizeExceeding90PercentAlarm")
    def jvm_heap_size_exceeding90_percent_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "jvmHeapSizeExceeding90PercentAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricAllExecutionAttemptsFailedAlarm")
    def metric_all_execution_attempts_failed_alarm(
        self,
    ) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "metricAllExecutionAttemptsFailedAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricExecutionFailureAlarm")
    def metric_execution_failure_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "metricExecutionFailureAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> aws_cdk.aws_cloudwatch.Dashboard:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Dashboard, jsii.get(self, "dashboard"))

    @dashboard.setter
    def dashboard(self, value: aws_cdk.aws_cloudwatch.Dashboard) -> None:
        jsii.set(self, "dashboard", value)


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.GlueJobProperties",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_bucket": "deploymentBucket",
        "job_script": "jobScript",
        "job_type": "jobType",
        "name": "name",
        "worker_type": "workerType",
        "description": "description",
        "glue_version": "glueVersion",
        "job_args": "jobArgs",
        "max_capacity": "maxCapacity",
        "max_concurrent_runs": "maxConcurrentRuns",
        "max_retries": "maxRetries",
        "number_of_workers": "numberOfWorkers",
        "read_access_buckets": "readAccessBuckets",
        "role_name": "roleName",
        "timeout": "timeout",
        "write_access_buckets": "writeAccessBuckets",
    },
)
class GlueJobProperties:
    def __init__(
        self,
        *,
        deployment_bucket: aws_cdk.aws_s3.IBucket,
        job_script: builtins.str,
        job_type: "GlueJobType",
        name: builtins.str,
        worker_type: "GlueWorkerType",
        description: typing.Optional[builtins.str] = None,
        glue_version: typing.Optional["GlueVersion"] = None,
        job_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_concurrent_runs: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        read_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
        role_name: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[jsii.Number] = None,
        write_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
    ) -> None:
        '''
        :param deployment_bucket: 
        :param job_script: 
        :param job_type: 
        :param name: 
        :param worker_type: 
        :param description: 
        :param glue_version: 
        :param job_args: 
        :param max_capacity: 
        :param max_concurrent_runs: 
        :param max_retries: 
        :param number_of_workers: 
        :param read_access_buckets: 
        :param role_name: 
        :param timeout: 
        :param write_access_buckets: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_bucket": deployment_bucket,
            "job_script": job_script,
            "job_type": job_type,
            "name": name,
            "worker_type": worker_type,
        }
        if description is not None:
            self._values["description"] = description
        if glue_version is not None:
            self._values["glue_version"] = glue_version
        if job_args is not None:
            self._values["job_args"] = job_args
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if max_concurrent_runs is not None:
            self._values["max_concurrent_runs"] = max_concurrent_runs
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if number_of_workers is not None:
            self._values["number_of_workers"] = number_of_workers
        if read_access_buckets is not None:
            self._values["read_access_buckets"] = read_access_buckets
        if role_name is not None:
            self._values["role_name"] = role_name
        if timeout is not None:
            self._values["timeout"] = timeout
        if write_access_buckets is not None:
            self._values["write_access_buckets"] = write_access_buckets

    @builtins.property
    def deployment_bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("deployment_bucket")
        assert result is not None, "Required property 'deployment_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def job_script(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("job_script")
        assert result is not None, "Required property 'job_script' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def job_type(self) -> "GlueJobType":
        '''
        :stability: experimental
        '''
        result = self._values.get("job_type")
        assert result is not None, "Required property 'job_type' is missing"
        return typing.cast("GlueJobType", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def worker_type(self) -> "GlueWorkerType":
        '''
        :stability: experimental
        '''
        result = self._values.get("worker_type")
        assert result is not None, "Required property 'worker_type' is missing"
        return typing.cast("GlueWorkerType", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def glue_version(self) -> typing.Optional["GlueVersion"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("glue_version")
        return typing.cast(typing.Optional["GlueVersion"], result)

    @builtins.property
    def job_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("job_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_concurrent_runs(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_concurrent_runs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("number_of_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def read_access_buckets(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("read_access_buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def write_access_buckets(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("write_access_buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlueJobProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.GlueJobType")
class GlueJobType(enum.Enum):
    '''
    :stability: experimental
    '''

    GLUE_ETL = "GLUE_ETL"
    '''
    :stability: experimental
    '''
    GLUE_STREAMING = "GLUE_STREAMING"
    '''
    :stability: experimental
    '''


class GlueTable(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.GlueTable",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: "IGlueTableProperties",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(GlueTable, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_glue.CfnTable:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.CfnTable, jsii.get(self, "table"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableName"))


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.GlueVersion")
class GlueVersion(enum.Enum):
    '''
    :stability: experimental
    '''

    V_0 = "V_0"
    '''
    :stability: experimental
    '''
    V_1 = "V_1"
    '''
    :stability: experimental
    '''
    V_2 = "V_2"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.GlueWorkerType")
class GlueWorkerType(enum.Enum):
    '''
    :stability: experimental
    '''

    STANDARD = "STANDARD"
    '''
    :stability: experimental
    '''
    G1_X = "G1_X"
    '''
    :stability: experimental
    '''
    G2_X = "G2_X"
    '''
    :stability: experimental
    '''


@jsii.interface(
    jsii_type="@randyridgley/cdk-datalake-constructs.IGlueCrawlerProperties"
)
class IGlueCrawlerProperties(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @bucket_prefix.setter
    def bucket_prefix(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @role_name.setter
    def role_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> typing.Optional[aws_cdk.aws_glue.CfnTrigger]:
        '''
        :stability: experimental
        '''
        ...

    @trigger.setter
    def trigger(self, value: typing.Optional[aws_cdk.aws_glue.CfnTrigger]) -> None:
        ...


class _IGlueCrawlerPropertiesProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@randyridgley/cdk-datalake-constructs.IGlueCrawlerProperties"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketPrefix"))

    @bucket_prefix.setter
    def bucket_prefix(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "bucketPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "roleName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> typing.Optional[aws_cdk.aws_glue.CfnTrigger]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_glue.CfnTrigger], jsii.get(self, "trigger"))

    @trigger.setter
    def trigger(self, value: typing.Optional[aws_cdk.aws_glue.CfnTrigger]) -> None:
        jsii.set(self, "trigger", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGlueCrawlerProperties).__jsii_proxy_class__ = lambda : _IGlueCrawlerPropertiesProxy


@jsii.interface(jsii_type="@randyridgley/cdk-datalake-constructs.IGlueOpsProperties")
class IGlueOpsProperties(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="job")
    def job(self) -> GlueJob:
        '''
        :stability: experimental
        '''
        ...

    @job.setter
    def job(self, value: GlueJob) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmHeapSizeExceeding80percent")
    def jvm_heap_size_exceeding80percent(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @jvm_heap_size_exceeding80percent.setter
    def jvm_heap_size_exceeding80percent(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmHeapSizeExceeding90percent")
    def jvm_heap_size_exceeding90percent(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @jvm_heap_size_exceeding90percent.setter
    def jvm_heap_size_exceeding90percent(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricAllExecutionAttemptsFailed")
    def metric_all_execution_attempts_failed(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @metric_all_execution_attempts_failed.setter
    def metric_all_execution_attempts_failed(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricExecutionFailure")
    def metric_execution_failure(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @metric_execution_failure.setter
    def metric_execution_failure(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...


class _IGlueOpsPropertiesProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@randyridgley/cdk-datalake-constructs.IGlueOpsProperties"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="job")
    def job(self) -> GlueJob:
        '''
        :stability: experimental
        '''
        return typing.cast(GlueJob, jsii.get(self, "job"))

    @job.setter
    def job(self, value: GlueJob) -> None:
        jsii.set(self, "job", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmHeapSizeExceeding80percent")
    def jvm_heap_size_exceeding80percent(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "jvmHeapSizeExceeding80percent"))

    @jvm_heap_size_exceeding80percent.setter
    def jvm_heap_size_exceeding80percent(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "jvmHeapSizeExceeding80percent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmHeapSizeExceeding90percent")
    def jvm_heap_size_exceeding90percent(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "jvmHeapSizeExceeding90percent"))

    @jvm_heap_size_exceeding90percent.setter
    def jvm_heap_size_exceeding90percent(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "jvmHeapSizeExceeding90percent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricAllExecutionAttemptsFailed")
    def metric_all_execution_attempts_failed(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "metricAllExecutionAttemptsFailed"))

    @metric_all_execution_attempts_failed.setter
    def metric_all_execution_attempts_failed(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "metricAllExecutionAttemptsFailed", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricExecutionFailure")
    def metric_execution_failure(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "metricExecutionFailure"))

    @metric_execution_failure.setter
    def metric_execution_failure(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "metricExecutionFailure", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGlueOpsProperties).__jsii_proxy_class__ = lambda : _IGlueOpsPropertiesProxy


@jsii.interface(jsii_type="@randyridgley/cdk-datalake-constructs.IGlueTableProperties")
class IGlueTableProperties(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="columns")
    def columns(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]]:
        '''
        :stability: experimental
        '''
        ...

    @columns.setter
    def columns(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> aws_cdk.aws_glue.Database:
        '''
        :stability: experimental
        '''
        ...

    @database.setter
    def database(self, value: aws_cdk.aws_glue.Database) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @description.setter
    def description(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputFormat")
    def input_format(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @input_format.setter
    def input_format(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        ...

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionKeys")
    def partition_keys(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]]:
        '''
        :stability: experimental
        '''
        ...

    @partition_keys.setter
    def partition_keys(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Location")
    def s3_location(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @s3_location.setter
    def s3_location(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serdeParameters")
    def serde_parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        ...

    @serde_parameters.setter
    def serde_parameters(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serializationLibrary")
    def serialization_library(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @serialization_library.setter
    def serialization_library(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        ...


class _IGlueTablePropertiesProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@randyridgley/cdk-datalake-constructs.IGlueTableProperties"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogId"))

    @catalog_id.setter
    def catalog_id(self, value: builtins.str) -> None:
        jsii.set(self, "catalogId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="columns")
    def columns(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]], jsii.get(self, "columns"))

    @columns.setter
    def columns(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]],
    ) -> None:
        jsii.set(self, "columns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> aws_cdk.aws_glue.Database:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.Database, jsii.get(self, "database"))

    @database.setter
    def database(self, value: aws_cdk.aws_glue.Database) -> None:
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputFormat")
    def input_format(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputFormat"))

    @input_format.setter
    def input_format(self, value: builtins.str) -> None:
        jsii.set(self, "inputFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "outputFormat"))

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        jsii.set(self, "outputFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionKeys")
    def partition_keys(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]], jsii.get(self, "partitionKeys"))

    @partition_keys.setter
    def partition_keys(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]],
    ) -> None:
        jsii.set(self, "partitionKeys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Location")
    def s3_location(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "s3Location"))

    @s3_location.setter
    def s3_location(self, value: builtins.str) -> None:
        jsii.set(self, "s3Location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serdeParameters")
    def serde_parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "serdeParameters"))

    @serde_parameters.setter
    def serde_parameters(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        jsii.set(self, "serdeParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serializationLibrary")
    def serialization_library(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serializationLibrary"))

    @serialization_library.setter
    def serialization_library(self, value: builtins.str) -> None:
        jsii.set(self, "serializationLibrary", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGlueTableProperties).__jsii_proxy_class__ = lambda : _IGlueTablePropertiesProxy


@jsii.interface(
    jsii_type="@randyridgley/cdk-datalake-constructs.IKinesisOpsProperties"
)
class IKinesisOpsProperties(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(self) -> "S3DeliveryStream":
        '''
        :stability: experimental
        '''
        ...

    @delivery_stream.setter
    def delivery_stream(self, value: "S3DeliveryStream") -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stream")
    def stream(self) -> "KinesisStream":
        '''
        :stability: experimental
        '''
        ...

    @stream.setter
    def stream(self, value: "KinesisStream") -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseDeliveryToS3Critical")
    def firehose_delivery_to_s3_critical(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @firehose_delivery_to_s3_critical.setter
    def firehose_delivery_to_s3_critical(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseDeliveryToS3Warning")
    def firehose_delivery_to_s3_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @firehose_delivery_to_s3_warning.setter
    def firehose_delivery_to_s3_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamGetRecordsWarning")
    def input_stream_get_records_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @input_stream_get_records_warning.setter
    def input_stream_get_records_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamIteratorAgeCritical")
    def input_stream_iterator_age_critical(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @input_stream_iterator_age_critical.setter
    def input_stream_iterator_age_critical(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamIteratorAgeWarning")
    def input_stream_iterator_age_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @input_stream_iterator_age_warning.setter
    def input_stream_iterator_age_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamPutRecordsWarning")
    def input_stream_put_records_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @input_stream_put_records_warning.setter
    def input_stream_put_records_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamReadThroughputWarning")
    def input_stream_read_throughput_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @input_stream_read_throughput_warning.setter
    def input_stream_read_throughput_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamWriteThroughputWarning")
    def input_stream_write_throughput_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        ...

    @input_stream_write_throughput_warning.setter
    def input_stream_write_throughput_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        ...


class _IKinesisOpsPropertiesProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@randyridgley/cdk-datalake-constructs.IKinesisOpsProperties"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(self) -> "S3DeliveryStream":
        '''
        :stability: experimental
        '''
        return typing.cast("S3DeliveryStream", jsii.get(self, "deliveryStream"))

    @delivery_stream.setter
    def delivery_stream(self, value: "S3DeliveryStream") -> None:
        jsii.set(self, "deliveryStream", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stream")
    def stream(self) -> "KinesisStream":
        '''
        :stability: experimental
        '''
        return typing.cast("KinesisStream", jsii.get(self, "stream"))

    @stream.setter
    def stream(self, value: "KinesisStream") -> None:
        jsii.set(self, "stream", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseDeliveryToS3Critical")
    def firehose_delivery_to_s3_critical(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "firehoseDeliveryToS3Critical"))

    @firehose_delivery_to_s3_critical.setter
    def firehose_delivery_to_s3_critical(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "firehoseDeliveryToS3Critical", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseDeliveryToS3Warning")
    def firehose_delivery_to_s3_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "firehoseDeliveryToS3Warning"))

    @firehose_delivery_to_s3_warning.setter
    def firehose_delivery_to_s3_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "firehoseDeliveryToS3Warning", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamGetRecordsWarning")
    def input_stream_get_records_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "inputStreamGetRecordsWarning"))

    @input_stream_get_records_warning.setter
    def input_stream_get_records_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "inputStreamGetRecordsWarning", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamIteratorAgeCritical")
    def input_stream_iterator_age_critical(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "inputStreamIteratorAgeCritical"))

    @input_stream_iterator_age_critical.setter
    def input_stream_iterator_age_critical(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "inputStreamIteratorAgeCritical", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamIteratorAgeWarning")
    def input_stream_iterator_age_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "inputStreamIteratorAgeWarning"))

    @input_stream_iterator_age_warning.setter
    def input_stream_iterator_age_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "inputStreamIteratorAgeWarning", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamPutRecordsWarning")
    def input_stream_put_records_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "inputStreamPutRecordsWarning"))

    @input_stream_put_records_warning.setter
    def input_stream_put_records_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "inputStreamPutRecordsWarning", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamReadThroughputWarning")
    def input_stream_read_throughput_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "inputStreamReadThroughputWarning"))

    @input_stream_read_throughput_warning.setter
    def input_stream_read_throughput_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "inputStreamReadThroughputWarning", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamWriteThroughputWarning")
    def input_stream_write_throughput_warning(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions], jsii.get(self, "inputStreamWriteThroughputWarning"))

    @input_stream_write_throughput_warning.setter
    def input_stream_write_throughput_warning(
        self,
        value: typing.Optional[aws_cdk.aws_cloudwatch.CreateAlarmOptions],
    ) -> None:
        jsii.set(self, "inputStreamWriteThroughputWarning", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IKinesisOpsProperties).__jsii_proxy_class__ = lambda : _IKinesisOpsPropertiesProxy


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.JDBCProperties",
    jsii_struct_bases=[],
    name_mapping={"jdbc": "jdbc", "password": "password", "username": "username"},
)
class JDBCProperties:
    def __init__(
        self,
        *,
        jdbc: builtins.str,
        password: builtins.str,
        username: builtins.str,
    ) -> None:
        '''
        :param jdbc: 
        :param password: 
        :param username: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "jdbc": jdbc,
            "password": password,
            "username": username,
        }

    @builtins.property
    def jdbc(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("jdbc")
        assert result is not None, "Required property 'jdbc' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JDBCProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.JobProperties",
    jsii_struct_bases=[],
    name_mapping={
        "job_script": "jobScript",
        "job_type": "jobType",
        "name": "name",
        "worker_type": "workerType",
        "description": "description",
        "destination_location": "destinationLocation",
        "glue_version": "glueVersion",
        "job_args": "jobArgs",
        "max_capacity": "maxCapacity",
        "max_concurrent_runs": "maxConcurrentRuns",
        "max_retries": "maxRetries",
        "number_of_workers": "numberOfWorkers",
        "read_access_buckets": "readAccessBuckets",
        "role_name": "roleName",
        "timeout": "timeout",
        "write_access_buckets": "writeAccessBuckets",
    },
)
class JobProperties:
    def __init__(
        self,
        *,
        job_script: builtins.str,
        job_type: GlueJobType,
        name: builtins.str,
        worker_type: GlueWorkerType,
        description: typing.Optional[builtins.str] = None,
        destination_location: typing.Optional[DataSetLocation] = None,
        glue_version: typing.Optional[GlueVersion] = None,
        job_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_concurrent_runs: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        number_of_workers: typing.Optional[jsii.Number] = None,
        read_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
        role_name: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[jsii.Number] = None,
        write_access_buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.IBucket]] = None,
    ) -> None:
        '''
        :param job_script: 
        :param job_type: 
        :param name: 
        :param worker_type: 
        :param description: 
        :param destination_location: 
        :param glue_version: 
        :param job_args: 
        :param max_capacity: 
        :param max_concurrent_runs: 
        :param max_retries: 
        :param number_of_workers: 
        :param read_access_buckets: 
        :param role_name: 
        :param timeout: 
        :param write_access_buckets: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "job_script": job_script,
            "job_type": job_type,
            "name": name,
            "worker_type": worker_type,
        }
        if description is not None:
            self._values["description"] = description
        if destination_location is not None:
            self._values["destination_location"] = destination_location
        if glue_version is not None:
            self._values["glue_version"] = glue_version
        if job_args is not None:
            self._values["job_args"] = job_args
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if max_concurrent_runs is not None:
            self._values["max_concurrent_runs"] = max_concurrent_runs
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if number_of_workers is not None:
            self._values["number_of_workers"] = number_of_workers
        if read_access_buckets is not None:
            self._values["read_access_buckets"] = read_access_buckets
        if role_name is not None:
            self._values["role_name"] = role_name
        if timeout is not None:
            self._values["timeout"] = timeout
        if write_access_buckets is not None:
            self._values["write_access_buckets"] = write_access_buckets

    @builtins.property
    def job_script(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("job_script")
        assert result is not None, "Required property 'job_script' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def job_type(self) -> GlueJobType:
        '''
        :stability: experimental
        '''
        result = self._values.get("job_type")
        assert result is not None, "Required property 'job_type' is missing"
        return typing.cast(GlueJobType, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def worker_type(self) -> GlueWorkerType:
        '''
        :stability: experimental
        '''
        result = self._values.get("worker_type")
        assert result is not None, "Required property 'worker_type' is missing"
        return typing.cast(GlueWorkerType, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_location(self) -> typing.Optional[DataSetLocation]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_location")
        return typing.cast(typing.Optional[DataSetLocation], result)

    @builtins.property
    def glue_version(self) -> typing.Optional[GlueVersion]:
        '''
        :stability: experimental
        '''
        result = self._values.get("glue_version")
        return typing.cast(typing.Optional[GlueVersion], result)

    @builtins.property
    def job_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("job_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_concurrent_runs(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_concurrent_runs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_workers(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("number_of_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def read_access_buckets(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("read_access_buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def write_access_buckets(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("write_access_buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.IBucket]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KinesisOps(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.KinesisOps",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: IKinesisOpsProperties,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(KinesisOps, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmsSev2")
    def alarms_sev2(self) -> typing.List[aws_cdk.aws_cloudwatch.Alarm]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[aws_cdk.aws_cloudwatch.Alarm], jsii.get(self, "alarmsSev2"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmsSev3")
    def alarms_sev3(self) -> typing.List[aws_cdk.aws_cloudwatch.Alarm]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[aws_cdk.aws_cloudwatch.Alarm], jsii.get(self, "alarmsSev3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(self) -> "S3DeliveryStream":
        '''
        :stability: experimental
        '''
        return typing.cast("S3DeliveryStream", jsii.get(self, "deliveryStream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseDeliveryToS3CriticalAlarm")
    def firehose_delivery_to_s3_critical_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "firehoseDeliveryToS3CriticalAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseDeliveryToS3WarningAlarm")
    def firehose_delivery_to_s3_warning_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "firehoseDeliveryToS3WarningAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamGetRecordsWarningAlarm")
    def input_stream_get_records_warning_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "inputStreamGetRecordsWarningAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamIteratorAgeCriticalAlarm")
    def input_stream_iterator_age_critical_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "inputStreamIteratorAgeCriticalAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamIteratorAgeWarningAlarm")
    def input_stream_iterator_age_warning_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "inputStreamIteratorAgeWarningAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamPutRecordsWarningAlarm")
    def input_stream_put_records_warning_alarm(self) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "inputStreamPutRecordsWarningAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamReadThroughputWarningAlarm")
    def input_stream_read_throughput_warning_alarm(
        self,
    ) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "inputStreamReadThroughputWarningAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputStreamWriteThroughputWarningAlarm")
    def input_stream_write_throughput_warning_alarm(
        self,
    ) -> aws_cdk.aws_cloudwatch.Alarm:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Alarm, jsii.get(self, "inputStreamWriteThroughputWarningAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stream")
    def stream(self) -> "KinesisStream":
        '''
        :stability: experimental
        '''
        return typing.cast("KinesisStream", jsii.get(self, "stream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamName")
    def stream_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> aws_cdk.aws_cloudwatch.Dashboard:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.Dashboard, jsii.get(self, "dashboard"))

    @dashboard.setter
    def dashboard(self, value: aws_cdk.aws_cloudwatch.Dashboard) -> None:
        jsii.set(self, "dashboard", value)


class KinesisStream(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.KinesisStream",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        parent: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        encryption: typing.Optional[aws_cdk.aws_kinesis.StreamEncryption] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        retention_period: typing.Optional[aws_cdk.core.Duration] = None,
        shard_count: typing.Optional[jsii.Number] = None,
        stream_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param parent: -
        :param name: -
        :param encryption: The kind of server-side encryption to apply to this stream. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - StreamEncryption.KMS if encrypted Streams are supported in the region or StreamEncryption.UNENCRYPTED otherwise. StreamEncryption.KMS if an encryption key is supplied through the encryptionKey property
        :param encryption_key: External KMS key to use for stream encryption. The 'encryption' property must be set to "Kms". Default: - Kinesis Data Streams master key ('/alias/aws/kinesis'). If encryption is set to StreamEncryption.KMS and this property is undefined, a new KMS key will be created and associated with this stream.
        :param retention_period: The number of hours for the data records that are stored in shards to remain accessible. Default: Duration.hours(24)
        :param shard_count: The number of shards for the stream. Default: 1
        :param stream_name: Enforces a particular physical stream name. Default: 

        :stability: experimental
        '''
        props = aws_cdk.aws_kinesis.StreamProps(
            encryption=encryption,
            encryption_key=encryption_key,
            retention_period=retention_period,
            shard_count=shard_count,
            stream_name=stream_name,
        )

        jsii.create(KinesisStream, self, [parent, name, props])

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricGetRecordsBytes")
    def metric_get_records_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricGetRecordsBytes", [props]))

    @jsii.member(jsii_name="metricGetRecordsIteratorAgeMilliseconds")
    def metric_get_records_iterator_age_milliseconds(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricGetRecordsIteratorAgeMilliseconds", [props]))

    @jsii.member(jsii_name="metricGetRecordsLatency")
    def metric_get_records_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricGetRecordsLatency", [props]))

    @jsii.member(jsii_name="metricGetRecordsRecords")
    def metric_get_records_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricGetRecordsRecords", [props]))

    @jsii.member(jsii_name="metricGetRecordsSuccess")
    def metric_get_records_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricGetRecordsSuccess", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

    @jsii.member(jsii_name="metricPutRecordBytes")
    def metric_put_record_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordBytes", [props]))

    @jsii.member(jsii_name="metricPutRecordLatency")
    def metric_put_record_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordLatency", [props]))

    @jsii.member(jsii_name="metricPutRecordsBytes")
    def metric_put_records_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordsBytes", [props]))

    @jsii.member(jsii_name="metricPutRecordsLatency")
    def metric_put_records_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordsLatency", [props]))

    @jsii.member(jsii_name="metricPutRecordsRecords")
    def metric_put_records_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordsRecords", [props]))

    @jsii.member(jsii_name="metricPutRecordsSuccess")
    def metric_put_records_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordsSuccess", [props]))

    @jsii.member(jsii_name="metricPutRecordSuccess")
    def metric_put_record_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricPutRecordSuccess", [props]))

    @jsii.member(jsii_name="metricReadProvisionedThroughputExceeded")
    def metric_read_provisioned_throughput_exceeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricReadProvisionedThroughputExceeded", [props]))

    @jsii.member(jsii_name="metricSubscribeToShardEventBytes")
    def metric_subscribe_to_shard_event_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSubscribeToShardEventBytes", [props]))

    @jsii.member(jsii_name="metricSubscribeToShardEventMillisBehindLatest")
    def metric_subscribe_to_shard_event_millis_behind_latest(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSubscribeToShardEventMillisBehindLatest", [props]))

    @jsii.member(jsii_name="metricSubscribeToShardEventRecords")
    def metric_subscribe_to_shard_event_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSubscribeToShardEventRecords", [props]))

    @jsii.member(jsii_name="metricSubscribeToShardEventSuccess")
    def metric_subscribe_to_shard_event_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSubscribeToShardEventSuccess", [props]))

    @jsii.member(jsii_name="metricSubscribeToShardRateExceeded")
    def metric_subscribe_to_shard_rate_exceeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSubscribeToShardRateExceeded", [props]))

    @jsii.member(jsii_name="metricSubscribeToShardSuccess")
    def metric_subscribe_to_shard_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricSubscribeToShardSuccess", [props]))

    @jsii.member(jsii_name="metricWriteProvisionedThroughputExceeded")
    def metric_write_provisioned_throughput_exceeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricWriteProvisionedThroughputExceeded", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stream")
    def stream(self) -> aws_cdk.aws_kinesis.Stream:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_kinesis.Stream, jsii.get(self, "stream"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.LambdaDataGeneratorProperties",
    jsii_struct_bases=[],
    name_mapping={
        "code": "code",
        "function_name": "functionName",
        "handler": "handler",
        "rule_name": "ruleName",
        "runtime": "runtime",
        "schedule": "schedule",
        "timeout": "timeout",
    },
)
class LambdaDataGeneratorProperties:
    def __init__(
        self,
        *,
        code: aws_cdk.aws_lambda.Code,
        function_name: builtins.str,
        handler: builtins.str,
        rule_name: builtins.str,
        runtime: aws_cdk.aws_lambda.Runtime,
        schedule: aws_cdk.aws_events.Schedule,
        timeout: aws_cdk.core.Duration,
    ) -> None:
        '''
        :param code: 
        :param function_name: 
        :param handler: 
        :param rule_name: 
        :param runtime: 
        :param schedule: 
        :param timeout: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "function_name": function_name,
            "handler": handler,
            "rule_name": rule_name,
            "runtime": runtime,
            "schedule": schedule,
            "timeout": timeout,
        }

    @builtins.property
    def code(self) -> aws_cdk.aws_lambda.Code:
        '''
        :stability: experimental
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(aws_cdk.aws_lambda.Code, result)

    @builtins.property
    def function_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("rule_name")
        assert result is not None, "Required property 'rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime(self) -> aws_cdk.aws_lambda.Runtime:
        '''
        :stability: experimental
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(aws_cdk.aws_lambda.Runtime, result)

    @builtins.property
    def schedule(self) -> aws_cdk.aws_events.Schedule:
        '''
        :stability: experimental
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(aws_cdk.aws_events.Schedule, result)

    @builtins.property
    def timeout(self) -> aws_cdk.core.Duration:
        '''
        :stability: experimental
        '''
        result = self._values.get("timeout")
        assert result is not None, "Required property 'timeout' is missing"
        return typing.cast(aws_cdk.core.Duration, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaDataGeneratorProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.NameBuilderParameters",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "account_id": "accountId",
        "region": "region",
        "resource_use": "resourceUse",
        "stage": "stage",
    },
)
class NameBuilderParameters:
    def __init__(
        self,
        *,
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        resource_use: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param account_id: 
        :param region: 
        :param resource_use: 
        :param stage: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if region is not None:
            self._values["region"] = region
        if resource_use is not None:
            self._values["resource_use"] = resource_use
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_use(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("resource_use")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NameBuilderParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.Permissions")
class Permissions(enum.Enum):
    '''
    :stability: experimental
    '''

    ALTER = "ALTER"
    '''
    :stability: experimental
    '''
    CREATE_DATABASE = "CREATE_DATABASE"
    '''
    :stability: experimental
    '''
    CREATE_TABLE = "CREATE_TABLE"
    '''
    :stability: experimental
    '''
    DATA_LOCATION_ACCESS = "DATA_LOCATION_ACCESS"
    '''
    :stability: experimental
    '''
    DELETE = "DELETE"
    '''
    :stability: experimental
    '''
    DESCRIBE = "DESCRIBE"
    '''
    :stability: experimental
    '''
    DROP = "DROP"
    '''
    :stability: experimental
    '''
    INSERT = "INSERT"
    '''
    :stability: experimental
    '''
    SELECT = "SELECT"
    '''
    :stability: experimental
    '''
    ASSOCIATE = "ASSOCIATE"
    '''
    :stability: experimental
    '''


class Pipeline(
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.Pipeline",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        data_set_drop_location: DataSetLocation,
        destination_prefix: builtins.str,
        name: builtins.str,
        type: DataPipelineType,
        jdbc_properties: typing.Optional[JDBCProperties] = None,
        job: typing.Optional[JobProperties] = None,
        s3_notification_props: typing.Optional["S3NotificationProperties"] = None,
        s3_properties: typing.Optional["S3Properties"] = None,
        stream_properties: typing.Optional["StreamProperties"] = None,
        table: typing.Optional["TableProps"] = None,
    ) -> None:
        '''
        :param data_set_drop_location: 
        :param destination_prefix: 
        :param name: 
        :param type: 
        :param jdbc_properties: 
        :param job: 
        :param s3_notification_props: 
        :param s3_properties: 
        :param stream_properties: 
        :param table: 

        :stability: experimental
        '''
        props = PipelineProperties(
            data_set_drop_location=data_set_drop_location,
            destination_prefix=destination_prefix,
            name=name,
            type=type,
            jdbc_properties=jdbc_properties,
            job=job,
            s3_notification_props=s3_notification_props,
            s3_properties=s3_properties,
            stream_properties=stream_properties,
            table=table,
        )

        jsii.create(Pipeline, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSetDropLocation")
    def data_set_drop_location(self) -> DataSetLocation:
        '''
        :stability: experimental
        '''
        return typing.cast(DataSetLocation, jsii.get(self, "dataSetDropLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPrefix")
    def destination_prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "destinationPrefix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> DataPipelineType:
        '''
        :stability: experimental
        '''
        return typing.cast(DataPipelineType, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jdbcProperties")
    def jdbc_properties(self) -> typing.Optional[JDBCProperties]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[JDBCProperties], jsii.get(self, "jdbcProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="job")
    def job(self) -> typing.Optional[JobProperties]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[JobProperties], jsii.get(self, "job"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3NotificationProps")
    def s3_notification_props(self) -> typing.Optional["S3NotificationProperties"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["S3NotificationProperties"], jsii.get(self, "s3NotificationProps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Properties")
    def s3_properties(self) -> typing.Optional["S3Properties"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["S3Properties"], jsii.get(self, "s3Properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamProperties")
    def stream_properties(self) -> typing.Optional["StreamProperties"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["StreamProperties"], jsii.get(self, "streamProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> typing.Optional["TableProps"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["TableProps"], jsii.get(self, "table"))


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.PipelineProperties",
    jsii_struct_bases=[],
    name_mapping={
        "data_set_drop_location": "dataSetDropLocation",
        "destination_prefix": "destinationPrefix",
        "name": "name",
        "type": "type",
        "jdbc_properties": "jdbcProperties",
        "job": "job",
        "s3_notification_props": "s3NotificationProps",
        "s3_properties": "s3Properties",
        "stream_properties": "streamProperties",
        "table": "table",
    },
)
class PipelineProperties:
    def __init__(
        self,
        *,
        data_set_drop_location: DataSetLocation,
        destination_prefix: builtins.str,
        name: builtins.str,
        type: DataPipelineType,
        jdbc_properties: typing.Optional[JDBCProperties] = None,
        job: typing.Optional[JobProperties] = None,
        s3_notification_props: typing.Optional["S3NotificationProperties"] = None,
        s3_properties: typing.Optional["S3Properties"] = None,
        stream_properties: typing.Optional["StreamProperties"] = None,
        table: typing.Optional["TableProps"] = None,
    ) -> None:
        '''
        :param data_set_drop_location: 
        :param destination_prefix: 
        :param name: 
        :param type: 
        :param jdbc_properties: 
        :param job: 
        :param s3_notification_props: 
        :param s3_properties: 
        :param stream_properties: 
        :param table: 

        :stability: experimental
        '''
        if isinstance(jdbc_properties, dict):
            jdbc_properties = JDBCProperties(**jdbc_properties)
        if isinstance(job, dict):
            job = JobProperties(**job)
        if isinstance(s3_notification_props, dict):
            s3_notification_props = S3NotificationProperties(**s3_notification_props)
        if isinstance(s3_properties, dict):
            s3_properties = S3Properties(**s3_properties)
        if isinstance(stream_properties, dict):
            stream_properties = StreamProperties(**stream_properties)
        if isinstance(table, dict):
            table = TableProps(**table)
        self._values: typing.Dict[str, typing.Any] = {
            "data_set_drop_location": data_set_drop_location,
            "destination_prefix": destination_prefix,
            "name": name,
            "type": type,
        }
        if jdbc_properties is not None:
            self._values["jdbc_properties"] = jdbc_properties
        if job is not None:
            self._values["job"] = job
        if s3_notification_props is not None:
            self._values["s3_notification_props"] = s3_notification_props
        if s3_properties is not None:
            self._values["s3_properties"] = s3_properties
        if stream_properties is not None:
            self._values["stream_properties"] = stream_properties
        if table is not None:
            self._values["table"] = table

    @builtins.property
    def data_set_drop_location(self) -> DataSetLocation:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_set_drop_location")
        assert result is not None, "Required property 'data_set_drop_location' is missing"
        return typing.cast(DataSetLocation, result)

    @builtins.property
    def destination_prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_prefix")
        assert result is not None, "Required property 'destination_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> DataPipelineType:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(DataPipelineType, result)

    @builtins.property
    def jdbc_properties(self) -> typing.Optional[JDBCProperties]:
        '''
        :stability: experimental
        '''
        result = self._values.get("jdbc_properties")
        return typing.cast(typing.Optional[JDBCProperties], result)

    @builtins.property
    def job(self) -> typing.Optional[JobProperties]:
        '''
        :stability: experimental
        '''
        result = self._values.get("job")
        return typing.cast(typing.Optional[JobProperties], result)

    @builtins.property
    def s3_notification_props(self) -> typing.Optional["S3NotificationProperties"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_notification_props")
        return typing.cast(typing.Optional["S3NotificationProperties"], result)

    @builtins.property
    def s3_properties(self) -> typing.Optional["S3Properties"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_properties")
        return typing.cast(typing.Optional["S3Properties"], result)

    @builtins.property
    def stream_properties(self) -> typing.Optional["StreamProperties"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("stream_properties")
        return typing.cast(typing.Optional["StreamProperties"], result)

    @builtins.property
    def table(self) -> typing.Optional["TableProps"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("table")
        return typing.cast(typing.Optional["TableProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.ProcessorType")
class ProcessorType(enum.Enum):
    '''
    :stability: experimental
    '''

    LAMBDA = "LAMBDA"
    '''
    :stability: experimental
    '''


class S3DeliveryStream(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@randyridgley/cdk-datalake-constructs.S3DeliveryStream",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        parent: aws_cdk.core.Construct,
        name: builtins.str,
        *,
        kinesis_stream: aws_cdk.aws_kinesis.Stream,
        s3_bucket: aws_cdk.aws_s3.IBucket,
        compression: typing.Optional[CompressionType] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        transform_function: typing.Optional[aws_cdk.aws_lambda.Function] = None,
    ) -> None:
        '''
        :param parent: -
        :param name: -
        :param kinesis_stream: 
        :param s3_bucket: 
        :param compression: 
        :param s3_prefix: 
        :param transform_function: 

        :stability: experimental
        '''
        props = DeliveryStreamProperties(
            kinesis_stream=kinesis_stream,
            s3_bucket=s3_bucket,
            compression=compression,
            s3_prefix=s3_prefix,
            transform_function=transform_function,
        )

        jsii.create(S3DeliveryStream, self, [parent, name, props])

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricBackupToS3Success")
    def metric_backup_to_s3_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Success", [props]))

    @jsii.member(jsii_name="metricDataReadFromKinesisStreamBytes")
    def metric_data_read_from_kinesis_stream_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricDataReadFromKinesisStreamBytes", [props]))

    @jsii.member(jsii_name="metricDataReadFromKinesisStreamRecords")
    def metric_data_read_from_kinesis_stream_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricDataReadFromKinesisStreamRecords", [props]))

    @jsii.member(jsii_name="metricDeliveryToS3Bytes")
    def metric_delivery_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricDeliveryToS3Bytes", [props]))

    @jsii.member(jsii_name="metricDeliveryToS3DataFreshness")
    def metric_delivery_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricDeliveryToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricDeliveryToS3Records")
    def metric_delivery_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricDeliveryToS3Records", [props]))

    @jsii.member(jsii_name="metricDeliveryToS3Success")
    def metric_delivery_to_s3_success(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricDeliveryToS3Success", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.core.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "s3Bucket"))

    @s3_bucket.setter
    def s3_bucket(self, value: aws_cdk.aws_s3.IBucket) -> None:
        jsii.set(self, "s3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchLogsRole")
    def _cloud_watch_logs_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], jsii.get(self, "cloudWatchLogsRole"))

    @_cloud_watch_logs_role.setter
    def _cloud_watch_logs_role(
        self,
        value: typing.Optional[aws_cdk.aws_iam.Role],
    ) -> None:
        jsii.set(self, "cloudWatchLogsRole", value)


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.S3NotificationProperties",
    jsii_struct_bases=[],
    name_mapping={"event": "event", "prefix": "prefix", "suffix": "suffix"},
)
class S3NotificationProperties:
    def __init__(
        self,
        *,
        event: aws_cdk.aws_s3.EventType,
        prefix: builtins.str,
        suffix: builtins.str,
    ) -> None:
        '''
        :param event: 
        :param prefix: 
        :param suffix: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event": event,
            "prefix": prefix,
            "suffix": suffix,
        }

    @builtins.property
    def event(self) -> aws_cdk.aws_s3.EventType:
        '''
        :stability: experimental
        '''
        result = self._values.get("event")
        assert result is not None, "Required property 'event' is missing"
        return typing.cast(aws_cdk.aws_s3.EventType, result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def suffix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("suffix")
        assert result is not None, "Required property 'suffix' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3NotificationProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.S3Properties",
    jsii_struct_bases=[],
    name_mapping={
        "source_bucket_name": "sourceBucketName",
        "source_keys": "sourceKeys",
    },
)
class S3Properties:
    def __init__(
        self,
        *,
        source_bucket_name: builtins.str,
        source_keys: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param source_bucket_name: 
        :param source_keys: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source_bucket_name": source_bucket_name,
            "source_keys": source_keys,
        }

    @builtins.property
    def source_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("source_bucket_name")
        assert result is not None, "Required property 'source_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_keys(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source_keys")
        assert result is not None, "Required property 'source_keys' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3Properties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@randyridgley/cdk-datalake-constructs.Stage")
class Stage(enum.Enum):
    '''
    :stability: experimental
    '''

    ALPHA = "ALPHA"
    '''
    :stability: experimental
    '''
    BETA = "BETA"
    '''
    :stability: experimental
    '''
    GAMMA = "GAMMA"
    '''
    :stability: experimental
    '''
    PROD = "PROD"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.StreamProperties",
    jsii_struct_bases=[],
    name_mapping={
        "stream_name": "streamName",
        "lambda_data_generator": "lambdaDataGenerator",
    },
)
class StreamProperties:
    def __init__(
        self,
        *,
        stream_name: builtins.str,
        lambda_data_generator: typing.Optional[LambdaDataGeneratorProperties] = None,
    ) -> None:
        '''
        :param stream_name: 
        :param lambda_data_generator: 

        :stability: experimental
        '''
        if isinstance(lambda_data_generator, dict):
            lambda_data_generator = LambdaDataGeneratorProperties(**lambda_data_generator)
        self._values: typing.Dict[str, typing.Any] = {
            "stream_name": stream_name,
        }
        if lambda_data_generator is not None:
            self._values["lambda_data_generator"] = lambda_data_generator

    @builtins.property
    def stream_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("stream_name")
        assert result is not None, "Required property 'stream_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_data_generator(self) -> typing.Optional[LambdaDataGeneratorProperties]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lambda_data_generator")
        return typing.cast(typing.Optional[LambdaDataGeneratorProperties], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@randyridgley/cdk-datalake-constructs.TableProps",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_id": "catalogId",
        "columns": "columns",
        "description": "description",
        "input_format": "inputFormat",
        "output_format": "outputFormat",
        "parameters": "parameters",
        "partition_keys": "partitionKeys",
        "serde_parameters": "serdeParameters",
        "serialization_library": "serializationLibrary",
        "table_name": "tableName",
    },
)
class TableProps:
    def __init__(
        self,
        *,
        catalog_id: builtins.str,
        columns: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]],
        description: builtins.str,
        input_format: builtins.str,
        output_format: builtins.str,
        parameters: typing.Mapping[builtins.str, typing.Any],
        partition_keys: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]],
        serde_parameters: typing.Mapping[builtins.str, typing.Any],
        serialization_library: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''
        :param catalog_id: 
        :param columns: 
        :param description: 
        :param input_format: 
        :param output_format: 
        :param parameters: 
        :param partition_keys: 
        :param serde_parameters: 
        :param serialization_library: 
        :param table_name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "catalog_id": catalog_id,
            "columns": columns,
            "description": description,
            "input_format": input_format,
            "output_format": output_format,
            "parameters": parameters,
            "partition_keys": partition_keys,
            "serde_parameters": serde_parameters,
            "serialization_library": serialization_library,
            "table_name": table_name,
        }

    @builtins.property
    def catalog_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("catalog_id")
        assert result is not None, "Required property 'catalog_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def columns(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("columns")
        assert result is not None, "Required property 'columns' is missing"
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]], result)

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input_format(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("input_format")
        assert result is not None, "Required property 'input_format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_format(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("output_format")
        assert result is not None, "Required property 'output_format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        result = self._values.get("parameters")
        assert result is not None, "Required property 'parameters' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def partition_keys(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("partition_keys")
        assert result is not None, "Required property 'partition_keys' is missing"
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.aws_glue.CfnTable.ColumnProperty, aws_cdk.core.IResolvable]]], result)

    @builtins.property
    def serde_parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        result = self._values.get("serde_parameters")
        assert result is not None, "Required property 'serde_parameters' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def serialization_library(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("serialization_library")
        assert result is not None, "Required property 'serialization_library' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TableProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CompressionType",
    "CrossAccountProperties",
    "DataCatalogOwner",
    "DataLake",
    "DataLakeAdministrator",
    "DataLakeAdministratorProps",
    "DataLakeAnalyst",
    "DataLakeAnalystProps",
    "DataLakeBucket",
    "DataLakeBucketProps",
    "DataLakeCreator",
    "DataLakeCreatorProperties",
    "DataLakeProperties",
    "DataPipelineType",
    "DataProduct",
    "DataProductProperties",
    "DataSet",
    "DataSetLocation",
    "DataSetProperties",
    "DataSetResult",
    "DataStreamProperties",
    "DeliveryStreamProperties",
    "DeliveryStreamType",
    "GlueCrawler",
    "GlueJob",
    "GlueJobOps",
    "GlueJobProperties",
    "GlueJobType",
    "GlueTable",
    "GlueVersion",
    "GlueWorkerType",
    "IGlueCrawlerProperties",
    "IGlueOpsProperties",
    "IGlueTableProperties",
    "IKinesisOpsProperties",
    "JDBCProperties",
    "JobProperties",
    "KinesisOps",
    "KinesisStream",
    "LambdaDataGeneratorProperties",
    "NameBuilderParameters",
    "Permissions",
    "Pipeline",
    "PipelineProperties",
    "ProcessorType",
    "S3DeliveryStream",
    "S3NotificationProperties",
    "S3Properties",
    "Stage",
    "StreamProperties",
    "TableProps",
]

publication.publish()

# -*- coding: utf-8 -*-

import boto3
import base64
import time

from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_lmd.model.aws_operator import AWSOperator
from phcli.ph_lmd.model.ph_layer import PhLayer
from phcli.ph_lmd import define_value as dv
from phcli.ph_lmd.runtime.rt_util import get_short_rt, get_rt_inst


class PhLambda(AWSOperator):
    """
    lambda 的源代码
    """

    phsts = PhSts().assume_role(
        base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        dv.ASSUME_ROLE_EXTERNAL_ID,
    )
    phs3 = PhS3(phsts=phsts)

    def __sync_file(self, data):
        bucket_name, object_name = self.phs3.sync_file_local_to_s3(
            data["lambda_path"],
            bucket_name=data.get("bucket", dv.DEFAULT_BUCKET),
            dir_name=dv.CLI_VERSION + dv.DEFAULT_LAMBDA_DIR
                .replace("#runtime#", get_short_rt(data["runtime"]))
                .replace("#name#", data["name"]),
            version=data.get("version", ""),
        )
        return bucket_name, object_name

    def __create_func(self, data, lambda_client):
        bucket_name, object_name = self.__sync_file(data)

        role_arn = base64.b64decode(dv.ASSUME_ROLE_ARN).decode()

        vpc_config = data['vpc_config'] if 'vpc_config' in data.keys() else {}

        layers_arn = []
        ph_layer = PhLayer()
        for layer_name in data["lambda_layers"].split(","):
            layers_arn.append(ph_layer.get({"name": layer_name})["LayerVersions"][0]["LayerVersionArn"])

        lambda_response = lambda_client.create_function(
            FunctionName=data["name"],
            Runtime=data["runtime"].split(",")[0],
            Role=role_arn,
            Handler=data["lambda_handler"],
            Code={
                'S3Bucket': bucket_name,
                'S3Key': object_name,
            },
            Description=data.get("lambda_desc", "phcli create " + data['name'] + " lambda function"),
            Timeout=data.get("lambda_timeout", 30),
            MemorySize=data.get("lambda_memory_size", 128),
            # Publish=True|False,
            VpcConfig=vpc_config,
            # DeadLetterConfig={
            #     'TargetArn': 'string'
            # },
            Environment={
                'Variables': data.get("lambda_env", {}),
            },
            # KMSKeyArn='string',
            # TracingConfig={
            #     'Mode': 'Active'|'PassThrough'
            # },
            Tags=data.get("lambda_tag", {}),
            Layers=layers_arn,
        )
        return lambda_response

    def __apply_version(self, data, lambda_client):
        def create_version():
            response = lambda_client.publish_version(
                FunctionName=data["name"],
                # CodeSha256='string',
                # Description='string',
                # RevisionId='string'
            )
            return response

        return create_version()

    def __apply_alias(self, data, lambda_client, create_version_response):

        def create_alias(name, function_version):
            response = lambda_client.create_alias(
                FunctionName=data["name"],
                Name=name,
                FunctionVersion=function_version,
                Description=data.get("lambda_desc", "phcli create " + data['name'] + " lambda function alias"),
                # RoutingConfig={
                #     'AdditionalVersionWeights': {
                #         'string': 123.0
                #     }
                # }
            )
            return response

        def delete_alias(name):
            response = lambda_client.delete_alias(
                FunctionName=data["name"],
                Name=name,
            )
            return response

        def cur2prev(aliases):
            if dv.LAMBDA_FUNCTION_ALIAS_NAME_PREV in aliases.keys():
                delete_alias(dv.LAMBDA_FUNCTION_ALIAS_NAME_PREV)

            version = aliases[dv.LAMBDA_FUNCTION_ALIAS_NAME_CUR]['FunctionVersion']
            create_alias(dv.LAMBDA_FUNCTION_ALIAS_NAME_PREV, version)
            return delete_alias(dv.LAMBDA_FUNCTION_ALIAS_NAME_CUR)

        resp = self.get(data)
        aliases = resp['Aliases'] if resp else []
        aliases = dict([(alias['Name'], alias) for alias in aliases])

        # 如果版本没变化
        if aliases and aliases[dv.LAMBDA_FUNCTION_ALIAS_NAME_CUR]['FunctionVersion'] == create_version_response["Version"]:
            return aliases[dv.LAMBDA_FUNCTION_ALIAS_NAME_CUR]['FunctionVersion']

        if aliases:
            cur2prev(aliases)

        return create_alias(dv.LAMBDA_FUNCTION_ALIAS_NAME_CUR, create_version_response["Version"])

    def package(self, data):
        """
        对 lambda 源代码打包
        :param data:
            :arg runtime 运行时字符串，“python” 或者 “nodejs” 或者 “go”
            :arg code_path: lambda 代码位置
            :arg package_name 打包的名称
        """
        runtime_inst = get_rt_inst(data['runtime'])
        return runtime_inst.pkg_code(data)

    def create(self, data):
        """
        创建 lambda, 并发布一个新版本，然后使用 version 定义一个别名
        :param data:
            :arg name: 创建的 lambda 函数的名字
            :arg version: lambda 函数别名版本，默认为 alpha
            :arg runtime: lambda 函数适用的运行时，如果多个请使用 “,” 分割, 但是实际使用以第一个为准
            :arg lambda_path: lambda zip 的位置
                            可以是本地（file/ph_lmd/python-lambda-example-code.zip，会先被传到 S3）或
                            s3 上的文件（s3://ph-platform/2020-08-10/functions/python/test_ph_lambda_create/python-lambda-example-code.zip）
            :arg lambda_handler: lambda 的入口函数
            :arg lambda_layers: lambda 函数依赖的层名称，如果多个请使用 “,” 分割
            :arg lambda_desc: lambda 函数的描述
            :arg lambda_timeout: [int] lambda 的超时时间，默认30s（官方是3s）
            :arg lambda_memory_size: [int] lambda 的使用内存，默认128
            :arg lambda_env: [dict] lambda 的环境变量
            :arg lambda_tag: [dict] lambda 的标签
            :arg vpc_config: [dict] lambda VPC 配置
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        self.__create_func(data, lambda_client)

        # 首次创建并且配置 VPC 的情况下，function 会有一段 pending 时间，因此等待 30 s
        if 'vpc_config' in data.keys():
            for i in range(30):
                time.sleep(1)

        response = self.__apply_version(data, lambda_client)

        response = self.__apply_alias(data, lambda_client, response)

        return response

    def lists(self, data):
        """
        获取所有 lambda 实例
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        response = lambda_client.list_functions(
            # MasterRegion='string',
            FunctionVersion='ALL',
            # Marker='string',
            MaxItems=50,
        )

        return response

    def get(self, data):
        """
        获取指定 lambda 实例
        :param data:
            :arg name: 要查询的 lambda 函数的名字
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        try:
            response = lambda_client.get_function(
                FunctionName=data["name"],
                # Qualifier='string',
            )

            versions = lambda_client.list_versions_by_function(
                FunctionName=data["name"],
                # Marker='string',
                # MaxItems=123
            )["Versions"]
            versions.reverse()
            response["Versions"] = versions

            aliases = lambda_client.list_aliases(
                FunctionName=data["name"],
            )["Aliases"]
            aliases.reverse()
            response["Aliases"] = aliases
        except:
            response = {}

        return response

    def update(self, data):
        """
        更新 lambda, 并发布一个新版本，然后使用 version 定义一个别名
        :param data:
            :arg name: 创建的 lambda 函数的名字 【必需】
            :arg version: lambda 函数别名版本
            :arg runtime: lambda 函数适用的运行时，如果多个请使用 “,” 分割, 但是实际使用以第一个为准
            :arg lambda_path: lambda zip 的位置
                            可以是本地（file/ph_lmd/python-lambda-example-code.zip，会先被传到 S3）或
                            s3 上的文件（s3://ph-platform/2020-08-10/functions/python/test_ph_lambda_create/python-lambda-example-code.zip)
            :arg lambda_handler: lambda 的入口函数
            :arg lambda_layers: lambda 函数依赖的层名称，如果多个请使用 “,” 分割
            :arg lambda_desc: lambda 函数的描述
            :arg lambda_timeout: [int] lambda 的超时时间，默认30s（官方是3s）
            :arg lambda_memory_size: [int] lambda 的使用内存，默认128
            :arg lambda_env: [dict] lambda 的环境变量
            :arg vpc_config: [dict] lambda VPC 配置
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        # 更新代码
        if "lambda_path" in data.keys():
            bucket_name, object_name = self.__sync_file(data)

            lambda_client.update_function_code(
                FunctionName=data["name"],
                # ZipFile=b'bytes',
                S3Bucket=bucket_name,
                S3Key=object_name,
                # S3ObjectVersion='string',
                # Publish=True|False,
                # DryRun=True|False,
                # RevisionId='string'
            )
            del data["lambda_path"]
            return self.update(data)

        # 更新配置
        else:
            response = self.get(data)

            role_arn = base64.b64decode(dv.ASSUME_ROLE_ARN).decode()

            layers_arn = []
            if "lambda_layers" in data.keys():
                ph_layer = PhLayer()
                for layer_name in data["lambda_layers"].split(","):
                    layers_arn.append(ph_layer.get({"name": layer_name})["LayerVersions"][0]["LayerVersionArn"])
            else:
                for layer_name in response["Configuration"]["Layers"]:
                    layers_arn.append(layer_name["Arn"])

            vpc_config = data['vpc_config'] if 'vpc_config' in data.keys() else {}

            lambda_response = lambda_client.update_function_configuration(
                FunctionName=data["name"],
                Role=role_arn,
                Handler=data.get("lambda_handler", response["Configuration"]["Handler"]),
                Description=data.get("lambda_desc", response["Configuration"]["Description"]),
                Timeout=data.get("lambda_timeout", response["Configuration"]["Timeout"]),
                MemorySize=data.get("lambda_memory_size", response["Configuration"]["MemorySize"]),
                VpcConfig=vpc_config,
                Environment={
                    'Variables': data.get("lambda_env", response["Configuration"].get("Environment", {}).get("Variables", {})),
                },
                Runtime=data.get("runtime", [response["Configuration"]["Runtime"]]).split(",")[0],
                # DeadLetterConfig={
                #     'TargetArn': 'string'
                # },
                # KMSKeyArn='string',
                # TracingConfig={
                #     'Mode': 'Active'|'PassThrough'
                # },
                # RevisionId='string',
                Layers=layers_arn
            )

        response = self.__apply_version(data, lambda_client)

        response = self.__apply_alias(data, lambda_client, response)

        return response

    def apply(self, data):
        """
        发布或更新 lambda, 并发布一个新版本，然后使用 version 定义一个别名
        :param data:
            :arg name: 创建的 lambda 函数的名字
            :arg version: lambda 函数别名版本
            :arg runtime: lambda 函数适用的运行时，如果多个请使用 “,” 分割, 但是实际使用以第一个为准
            :arg lambda_path: lambda zip 的位置
                            可以是本地（file/ph_lmd/python-lambda-example-code.zip，会先被传到 S3）或
                            s3 上的文件（s3://ph-platform/2020-08-10/functions/python/test_ph_lambda_create/python-lambda-example-code.zip）
            :arg lambda_handler: lambda 的入口函数
            :arg lambda_layers: lambda 函数依赖的层名称，如果多个请使用 “,” 分割
            :arg lambda_desc: lambda 函数的描述
            :arg lambda_timeout: [int] lambda 的超时时间，默认30s（官方是3s）
            :arg lambda_memory_size: [int] lambda 的使用内存，默认128
            :arg lambda_env: [dict] lambda 的环境变量
            :arg lambda_tag: [dict] lambda 的标
        """
        if self.get(data) == {}:
            return self.create(data)
        else:
            return self.update(data)

    def stop(self, data):
        """
        停止 lambda 继续处理请求，并发数设置为 0
        :param data:
            :arg name: 创建的 lambda 函数的名字 【必需】
        """
        data["lambda_concurrent"] = 0
        return self.start(data)

    def start(self, data):
        """
        重新激活 lambda，使其可以接受请求，并发数设置为指定值或默认值
        :param data:
            :arg name: 创建的 lambda 函数的名字 【必需】
            :arg lambda_concurrent: 分配给别名的预留并发值, 不指定则使用非预留账户并发
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        if "lambda_concurrent" in data.keys():
            response = lambda_client.put_function_concurrency(
                FunctionName=data["name"],
                ReservedConcurrentExecutions=data["lambda_concurrent"],
            )
        else:
            response = lambda_client.delete_function_concurrency(
                FunctionName=data["name"],
            )

        return response

    def delete(self, data):
        """
        删除 lambda, 版本 或 别名
        :param data:
            :arg name: 创建的 lambda 函数的名字 【必需】
            :arg version: lambda 函数版本, 不传或传 #ALL# 则删除整个 lambda 函数
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        if "version" not in data.keys() or data["version"] == "#ALL#":
            response = lambda_client.delete_function(
                FunctionName=data["name"],
            )
        else:
            response = lambda_client.delete_function(
                FunctionName=data["name"],
                Qualifier=data["version"],
            )

        return response



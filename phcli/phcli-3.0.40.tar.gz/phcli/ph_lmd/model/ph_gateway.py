# -*- coding: utf-8 -*-

import boto3
import yaml
import base64

from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_lmd.model.aws_operator import AWSOperator
from phcli.ph_lmd.model.ph_lambda import PhLambda
from phcli.ph_lmd import define_value as dv


class PhGateway(AWSOperator):
    """
    lambda 的 API Gateway 代理
    """

    phsts = PhSts().assume_role(
        base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        dv.ASSUME_ROLE_EXTERNAL_ID,
    )
    phs3 = PhS3(phsts=phsts)

    def __put_resource_by_template(self, rest_api_id, project_name, paths, lambda_arn, role_arn):
        api_gateway_client = boto3.client('apigateway', **self.phsts.get_cred())

        def put_integration(rest_api_id, resource_id, method, lambda_arn, role_arn):
            response = api_gateway_client.put_integration(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=method.upper(),
                type='AWS_PROXY',
                integrationHttpMethod="POST",
                uri='arn:aws-cn:apigateway:cn-northwest-1:lambda:path/2015-03-31/functions/' + lambda_arn + '/invocations',
                # connectionType='INTERNET'|'VPC_LINK',
                # connectionId='string',
                credentials=role_arn,
                # requestParameters={
                #     'string': 'string'
                # },
                # requestTemplates={
                #     'string': 'string'
                # },
                # passthroughBehavior='string',
                # cacheNamespace='string',
                # cacheKeyParameters=[
                #     'string',
                # ],
                # contentHandling='CONVERT_TO_BINARY'|'CONVERT_TO_TEXT',
                # timeoutInMillis=123,
                # tlsConfig={
                #     'insecureSkipVerification': True|False
                # }
            )
            return response

        path_id_dict = {}
        for reso in api_gateway_client.get_resources(restApiId=rest_api_id, limit=9999)["items"]:
            path_id_dict[reso["path"]] = reso["id"]

        for path, methods in sorted(paths.items()):
            path = path.replace("{project_name}", project_name)
            prefix = []

            # 添加资源
            for sub_path in path.split("/")[1:]:
                parent_id = path_id_dict.get("/" + "/".join(prefix))
                prefix.append(sub_path)
                path = "/" + "/".join(prefix)
                if path not in path_id_dict.keys():
                    resource_id = api_gateway_client.create_resource(
                        restApiId=rest_api_id,
                        parentId=parent_id,
                        pathPart=sub_path,
                    )["id"]
                    path_id_dict[path] = resource_id

            # 为资源添加方法并集成 lambda
            for method, params in methods.items():
                api_gateway_client.put_method(
                    restApiId=rest_api_id,
                    resourceId=path_id_dict.get(path),
                    httpMethod=method,
                    authorizationType='AWS_IAM',
                    # authorizerId='string',
                    # apiKeyRequired=True|False,
                    # operationName='string',
                    requestParameters={
                        'method.request.header.Accept': True,
                        'method.request.header.Content-Type': True,
                    },
                    # requestModels={
                    #     'string': 'string'
                    # },
                    # requestValidatorId='string',
                    # authorizationScopes=[
                    #     'string',
                    # ]
                )

                put_integration(
                    rest_api_id=rest_api_id,
                    resource_id=path_id_dict.get(path),
                    method=method,
                    lambda_arn=lambda_arn,
                    role_arn=role_arn
                )

    def __create_deployment(self, rest_api_id, version, gateway_desc):
        api_gateway_client = boto3.client('apigateway', **self.phsts.get_cred())
        response = api_gateway_client.create_deployment(
            restApiId=rest_api_id,
            stageName=version,
            stageDescription=gateway_desc,
            description=gateway_desc,
            # cacheClusterEnabled=True|False,
            # cacheClusterSize='0.5'|'1.6'|'6.1'|'13.5'|'28.4'|'58.2'|'118'|'237',
            # variables={
            #     'string': 'string'
            # },
            # canarySettings={
            #     'percentTraffic': 123.0,
            #     'stageVariableOverrides': {
            #         'string': 'string'
            #     },
            #     'useStageCache': True|False
            # },
            # tracingEnabled=True|False
        )
        return response

    def package(self, data):
        """
        API Gateway 代理 不可打包
        """
        return self.package.__doc__

    def create(self, data):
        """
        创建 lambda 的 API Gateway 的根资源
        :param data:
            :arg name: API Gateway 的根资源名称
            :arg rest_api_id: rest API Gateway 的 ID
            :arg api_template: API Gateway 定义的符合 OpenAPI 规范的模板文档位置
                        可以是本地（file/ph_lmd/jsonapi-openapi-template.yaml，会先被传到 S3）或
                        s3 上的文件（s3://ph-platform/2020-08-10/template/python/phcli/lmd/jsonapi-openapi-template.yaml）
            :arg lambda_name: API Gateway 调用的 Lambda 函数
            :arg alias_version: 代理的 lambda function 的别名版本
        """
        rest_api_id = data["rest_api_id"]
        project_name = data["name"]

        bucket_name, object_name = self.phs3.sync_file_local_to_s3(
            data["api_template"],
            bucket_name=data.get("bucket", dv.DEFAULT_BUCKET),
            dir_name=dv.CLI_VERSION + dv.DEFAULT_TEMPLATE_DIR,
        )
        buf = self.phs3.open_object(bucket_name, object_name)
        gateway_conf = yaml.safe_load(buf)

        self.__put_resource_by_template(
            rest_api_id=rest_api_id,
            project_name=project_name,
            paths=gateway_conf["paths"],
            lambda_arn=PhLambda().get({"name": data["lambda_name"]})["Configuration"]["FunctionArn"] + ":" + data["alias_version"],
            role_arn=base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        )

        return rest_api_id + "/" + project_name + " 生成成功"

    def lists(self, data):
        """
        获取所有 lambda 的 API Gateway 代理实例
        :param data:
            :arg rest_api_id: rest API Gateway 的 ID
        """
        api_gateway_client = boto3.client('apigateway', **self.phsts.get_cred())

        if "rest_api_id" in data.keys():
            response = api_gateway_client.get_rest_api(
                restApiId=data["rest_api_id"]
            )
        else:
            response = api_gateway_client.get_rest_apis(
                # position='string',
                limit=9999,
            )
        return response

    def get(self, data):
        """
        获取指定 lambda 的 API Gateway 根资源名称
        :param data:
            :arg name: API Gateway 的名称【可能会查出多个】
            :arg rest_api_id: rest API Gateway 的 ID
        """
        api_gateway_client = boto3.client('apigateway', **self.phsts.get_cred())

        response = api_gateway_client.get_resources(
            restApiId=data["rest_api_id"],
            # position='string',
            limit=9999,
            # embed=[
            #     'string',
            # ]
        )

        items = []
        for api in response["items"]:
            if data["name"] in api["path"]:
                items.append(api)

        if not len(items):
            return {}

        response["items"] = items
        return response

    def update(self, data):
        """
        更新指定 lambda 的 API Gateway 的根资源, 操作等于是 create
        :param data:
            :arg name: API Gateway 的根资源名称
            :arg rest_api_id: rest API Gateway 的 ID
            :arg api_template: API Gateway 定义的符合 OpenAPI 规范的模板文档位置
                        可以是本地（file/ph_lmd/jsonapi-openapi-template.yaml，会先被传到 S3）或
                        s3 上的文件（s3://ph-platform/2020-08-10/template/python/phcli/lmd/jsonapi-openapi-template.yaml）
            :arg lambda_name: API Gateway 调用的 Lambda 函数
            :arg alias_version: 代理的 lambda function 的别名版本
        """
        return self.create(data)

    def apply(self, data):
        """
        创建或更新 lambda 的 API Gateway 的根资源, 操作等于是 create
        :param data:
            :arg name: API Gateway 的根资源名称
            :arg rest_api_id: rest API Gateway 的 ID
            :arg api_template: API Gateway 定义的符合 OpenAPI 规范的模板文档位置
                        可以是本地（file/ph_lmd/jsonapi-openapi-template.yaml，会先被传到 S3）或
                        s3 上的文件（s3://ph-platform/2020-08-10/template/python/phcli/lmd/jsonapi-openapi-template.yaml）
            :arg lambda_name: API Gateway 调用的 Lambda 函数
            :arg alias_version: 代理的 lambda function 的别名版本
        """
        if self.get(data) == {}:
            return self.create(data)
        else:
            return self.update(data)

    def stop(self, data):
        """
        API Gateway 代理实例不可停止
        """
        return self.stop.__doc__

    def start(self, data):
        """
        API Gateway 代理实例不可启动
        """
        return self.start.__doc__

    def delete(self, data):
        """
        删除 API Gateway 中的指定根资源
        :param data:
            :arg name: API Gateway 根资源名称
            :arg rest_api_id: rest API Gateway 的 ID
        """
        api_gateway_client = boto3.client('apigateway', **self.phsts.get_cred())

        response = {}
        for item in self.get(data)["items"]:
            if "/" + data["name"] == item["path"]:
                response = api_gateway_client.delete_resource(
                    restApiId=data['rest_api_id'],
                    resourceId=item["id"]
                )
        return response

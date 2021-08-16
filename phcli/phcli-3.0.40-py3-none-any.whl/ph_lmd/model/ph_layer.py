# -*- coding: utf-8 -*-

import boto3
import base64

from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_lmd.model.aws_operator import AWSOperator
from phcli.ph_lmd import define_value as dv
from phcli.ph_lmd.runtime.rt_util import get_short_rt, get_rt_inst


class PhLayer(AWSOperator):
    """
    lambda 的依赖层
    """
    phsts = PhSts().assume_role(
        base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        dv.ASSUME_ROLE_EXTERNAL_ID,
    )
    phs3 = PhS3(phsts=phsts)

    def package(self, data):
        """
        对 lambda layer 按照 runtime 打包
        :param data:
            :arg runtime 运行时字符串，“python” 或者 “nodejs” 或者 “go”
            :arg lib_path: python 运行时，仅当 is_pipenv = False 时有效，指定 python 的 lib 位置
            :arg package_name 打包的名称
            :arg is_pipenv: 是否使用的 pipenv 构建的项目，默认为 False
        """
        runtime_inst = get_rt_inst(data['runtime'])
        return runtime_inst.pkg_layer(data)

    def create(self, data):
        """
        创建 lambda 的 layer
        :param data:
            :arg name: layer 名字
            :arg version: layer 版本
            :arg layer_path: layer zip 的位置
                            可以是本地（file/ph_lmd/python-lambda-example-layer.zip，会先被传到 S3）或
                            s3 上的文件（s3://ph-platform/2020-08-10/layers/python/test_ph_layer_create/python-lambda-example-layer.zip）
            :arg runtime: layer 适用的运行时，如果多个请使用 “,” 分割
            :arg layer_desc: layer 的描述
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        bucket_name, object_name = self.phs3.sync_file_local_to_s3(
            path=data["layer_path"],
            bucket_name=data.get("bucket", dv.DEFAULT_BUCKET),
            dir_name=dv.CLI_VERSION + dv.DEFAULT_LAYER_DIR
                .replace("#runtime#", get_short_rt(data["runtime"]))
                .replace("#name#", data["name"]),
            version=data.get("version", ""),
        )

        response = lambda_client.publish_layer_version(
            LayerName=data["name"],
            Description=data.get("layer_desc", "phcli create " + data["name"] + " layer"),
            Content={
                'S3Bucket': bucket_name,
                'S3Key': object_name,
            },
            CompatibleRuntimes=data["runtime"].split(","),
            LicenseInfo='MIT'
        )

        return response

    def lists(self, data):
        """
        获取所有 layer 实例
        :param data:
            :arg runtime: layer 适用的运行时，只可指定一个【不强制】
            :arg name: layer 名字
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        if "name" in data.keys():
            response = lambda_client.list_layer_versions(
                LayerName=data["name"],
            )
        elif "runtime" in data.keys():
            response = lambda_client.list_layers(
                CompatibleRuntime=data["runtime"],
            )
        else:
            response = lambda_client.list_layers()

        return response

    def get(self, data):
        """
        获取指定的 layer 实例
        :param data:
            :arg name: layer 名字可加版本
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        response = lambda_client.list_layer_versions(
            LayerName=data["name"].split(":")[0],
        )

        if not response["LayerVersions"]:
            return {}

        version = data["name"].split(":")[1:2]
        if version:
            for layer in response["LayerVersions"]:
                if int(version[0]) == layer["Version"]:
                    response["LayerVersions"] = [layer]
                    break

        return response

    def update(self, data):
        """
        更新 lambda 的 layer，等于 create layer
        """
        return self.create(data)

    def apply(self, data):
        """
        发布或更新 lambda 的 layer, 等于 create layer
        """
        if self.get(data) == {}:
            return self.create(data)
        else:
            return self.update(data)

    def stop(self, data):
        """
        lambda 的 layer 不可停止
        """
        return self.stop.__doc__

    def start(self, data):
        """
        lambda 的 layer 不可启动
        """
        return self.start.__doc__

    def delete(self, data):
        """
        删除 lambda 的 layer
        :param data:
            :arg name: 要删除的 layer 名字
            :arg version: 要删除的 layer 版本
        """
        lambda_client = boto3.client('lambda', **self.phsts.get_cred())

        response = lambda_client.delete_layer_version(
            LayerName=data["name"],
            VersionNumber=data["version"],
        )

        return response

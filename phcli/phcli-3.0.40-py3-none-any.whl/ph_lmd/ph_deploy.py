# -*- coding: utf-8 -*-

import os
import yaml
import click
import base64
import time

from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_lmd import define_value as dv
from phcli.ph_lmd.model import ph_layer
from phcli.ph_lmd.model import ph_lambda
from phcli.ph_lmd.model import ph_gateway


@click.group("deploy")
def deploy():
    """
    自动化部署一系列 Lambda 技术栈
    """
    pass


@deploy.command("init")
@click.option('-n', '--name', prompt='项目名称', help='项目名称')
@click.option('-R', '--runtime', prompt='项目使用的运行时', help='项目使用的运行时',
              type=click.Choice(['python3.6', 'python3.8', 'nodejs10.x', 'go1.x']))
@click.option('-D', '--desc', prompt='项目描述', help='项目描述')
@click.option('-L', '--lib_path', prompt='layer 依赖目录'
                                         '(Python 如".venv/lib/python3.8/site-packages", Nodejs 如"node_modules")',
              help='layer 依赖目录')
@click.option('-C', '--code_path', prompt='function 代码目录（如 "src"）', help='function 代码目录')
@click.option('-H', '--handler', prompt='lambda function 入口', help='lambda function 入口')
def init(name, runtime, desc, lib_path, code_path, handler):
    """
    初始化环境，关联本地项目和 lambda function
    """

    phsts = PhSts().assume_role(
        base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        dv.ASSUME_ROLE_EXTERNAL_ID,
    )
    phs3 = PhS3(phsts=phsts)

    buf = phs3.open_object(
            bucket_name=dv.DEFAULT_BUCKET,
            object_name=dv.CLI_VERSION+dv.DEFAULT_TEMPLATE_DIR+dv.DEPLOY_FILE_TEMPLATE_NAME,
        ) \
        .replace("#name#", name) \
        .replace("#runtime#", runtime) \
        .replace("#desc#", desc) \
        .replace("#lib_path#", lib_path) \
        .replace("#code_path#", code_path) \
        .replace("#handler#", handler)

    if os.path.exists(dv.DEPLOY_FILE_LOCAL_NAME):
        with open(dv.DEPLOY_FILE_LOCAL_NAME) as f:
            deploy_conf = yaml.safe_load(f)
            if name in deploy_conf.keys():
                click.secho("Init Error，name '%s' is exists" % name, fg='red', blink=True, bold=True)
                return
            f.write(buf)
            click.secho("Append Init Success", fg='green', blink=True, bold=True)
            return
    else:
        with open(dv.DEPLOY_FILE_LOCAL_NAME, "wt") as wt:
            wt.write(buf)
        click.secho("Download Init Success", fg='green', blink=True, bold=True)
        return


@deploy.command("push", short_help='发布function并自动关联到API Gateway')
@click.option('-n', '--name', prompt='指定提交的项目，如果只代理一个项目则无需传入', default='', help='指定提交的项目')
@click.option('-o', '--oper', prompt='执行操作',
              type=click.Choice(['defalut', 'all', 'lib', 'code', 'api']),
              default='defalut', help='要执行的操作')
def push(name, oper):
    """
    【请在项目的根目录执行】

    \b
    发布依赖到 lambda layer, 发布项目代码到 lambda function, 并在 API Gateway 中关联到当前 lambda function 别名

    \b
    :arg oper:
        :arg default: 默认不传参数，按照预计使用频率，所以只发布 function + gateway
        :arg all: 发布全部资源 （layer、function、gateway）
        :arg lib: 只发布 layer
        :arg code: 只发布 function
        :arg api: 只发布 gateway
    """

    def apply(deploy_conf):
        if "layer" in deploy_conf.keys():
            layer = ph_layer.PhLayer()
            args = deploy_conf["metadata"]
            args.update(deploy_conf["layer"])

            if "lib_path" in deploy_conf["layer"]:
                click.secho("开始打包本地依赖: " + deploy_conf["layer"]["lib_path"] + "\t->\t" +
                            deploy_conf["layer"]["package_name"], blink=True, bold=True)
                layer.package(args)
                click.secho("本地依赖打包完成", fg='green', blink=True, bold=True)

            response = layer.apply(args)
            click.secho("layer 更新完成: " + response["LayerVersionArn"], fg='green', blink=True, bold=True)
            click.secho()

        if "lambda" in deploy_conf.keys():
            lambda_function = ph_lambda.PhLambda()
            args = deploy_conf["metadata"]
            args.update(deploy_conf["lambda"])

            if "code_path" in deploy_conf["lambda"]:
                click.secho("开始打包本地代码: " + deploy_conf["lambda"]["code_path"] + "\t->\t" +
                            deploy_conf["lambda"]["package_name"], blink=True, bold=True)
                lambda_function.package(args)
                click.secho("本地代码打包完成", fg='green', blink=True, bold=True)

            response = lambda_function.apply(args)
            click.secho("lambda 更新完成: " + response["AliasArn"], fg='green', blink=True, bold=True)
            click.secho()

        if "gateway" in deploy_conf.keys():
            gateway = ph_gateway.PhGateway()
            args = deploy_conf["metadata"]
            args.update(deploy_conf["gateway"])
            response = gateway.apply(args)
            click.secho("gateway 更新完成: " + response, fg='green', blink=True, bold=True)
            click.secho()

    def clean_cache(deploy_conf):
        click.secho("开始清理执行缓存", blink=True, bold=True)

        project_name = deploy_conf['metadata']['name']

        if "layer" in deploy_conf.keys():
            if os.path.exists(deploy_conf["layer"]["package_name"]):
                os.remove(deploy_conf["layer"]["package_name"])

            def keep_num():
                phlayer = ph_layer.PhLayer()
                resp = phlayer.get({'name': project_name})
                versions = resp['LayerVersions'] if resp else []
                versions = [version['Version'] for version in versions]

                if len(versions) > dv.LAMBDA_LAYER_MAX_VERSION_NUM:
                    for version in versions[dv.LAMBDA_LAYER_MAX_VERSION_NUM:]:
                        phlayer.delete({'name': project_name, 'version': version})

            keep_num()

        if "lambda" in deploy_conf.keys():
            if os.path.exists(deploy_conf["lambda"]["package_name"]):
                os.remove(deploy_conf["lambda"]["package_name"])

            def keep_num():
                phlambda = ph_lambda.PhLambda()

                resp = phlambda.get({'name': project_name})
                versions = resp['Versions'] if resp else []
                versions = [version['Version'] for version in versions]

                if len(versions) > dv.LAMBDA_FUNCTION_MAX_VERSION_NUM:
                    versions.remove('$LATEST')
                    for version in versions[dv.LAMBDA_FUNCTION_MAX_VERSION_NUM:]:
                        phlambda.delete({'name': project_name, 'version': version})

            keep_num()

        click.secho("执行缓存清理完成", fg='green', blink=True, bold=True)
        click.secho()

    with open(dv.DEPLOY_FILE_LOCAL_NAME) as f:
        all_conf = yaml.safe_load(f)

    # ensure project name
    if name == "":
        project_name = list(all_conf.keys())[0]
    elif name in all_conf.keys():
        project_name = name
    else:
        click.secho("project '%s' is not exists" % name, fg='red', blink=True, bold=True)
        return

    click.secho("开始部署 '%s'" % project_name, fg='green', blink=True, bold=True)

    deploy_conf = all_conf[project_name]
    deploy_conf['metadata']['version'] = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())

    # filter operator
    all_operator = {"lib": "layer", "code": "lambda", "api": "gateway"}
    if "defalut" == oper:
        data = {"code": "", "api": ""}
    elif "all" == oper:
        data = {"lib": "", "code": "", "api": ""}
    else:
        data = {oper: ""}

    for not_oper in all_operator.keys() - set(data.keys()):
        del deploy_conf[all_operator[not_oper]]

    apply(deploy_conf)
    clean_cache(deploy_conf)

    click.secho("部署成功 '%s'" % project_name, fg='green', blink=True, bold=True)

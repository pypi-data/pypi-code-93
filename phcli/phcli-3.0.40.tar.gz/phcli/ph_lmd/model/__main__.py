# -*- coding: utf-8 -*-

import sys
import click
from phcli.ph_lmd.model import ph_layer, ph_lambda, ph_gateway
from phcli.ph_errs.ph_err import PhException


@click.command('model', short_help='专项部署特定资源')
@click.option('-o', '--operation', required=True, help='执行行为',
              type=click.Choice(['package', 'create', 'lists', 'get',
                                 'update', 'apply', 'stop', 'start', 'delete']))
@click.option('-m', '--model', required=True, help='操作行为',
              type=click.Choice(['layer', 'lambda', 'gateway']))
@click.argument('argv', nargs=-1)
def model(operation, model, argv):
    """
    用于快速打包和部署 AWS Lambda 和 API Gateway

\b
操作名有如下：
    package : 对 lambda 的 layer 或者 code 打成 zip 包
    create  : 创建 lambda 的 role, layer 或者 code 或者 API Gateway 的一级资源
    lists   : 获取所有资源实例
    get     : 获取指定资源实例
    update  : 更新 lambda 的 layer 或者 code 或者 API Gateway 的一级资源
    apply   : 发布或更新 lambda 的 layer 或者 code 或者 API Gateway 的一级资源
    stop    : 使 lambda 或者 API Gateway 停止接受请求
    start   : 重新使 lambda 或者 API Gateway 接受请求
    delete  : 删除 lambda 的 layer 或者 code, 或者 API Gateway 的一级资源

\b
资源名有如下：
    layer   : lambda 的依赖层
    lambda  : lambda 的源代码
    gateway : lambda 的触发器 API Gateway
    """
    return fineness_func(operation, model, argv)


def fineness_func(operator, model, argv):
    """
    粒度功能使用
    :return:
    """

    def get_model_inst(model):
        model_switcher = {
            "layer": ph_layer.PhLayer,
            "lambda": ph_lambda.PhLambda,
            "gateway": ph_gateway.PhGateway,
        }
        return model_switcher.get(model, "Invalid model")()

    def get_oper_inst(model_inst, oper):
        if oper == "package":
            return model_inst.package
        elif oper == "create":
            return model_inst.create
        elif oper == "lists":
            return model_inst.lists
        elif oper == "get":
            return model_inst.get
        elif oper == "update":
            return model_inst.update
        elif oper == "apply":
            return model_inst.apply
        elif oper == "stop":
            return model_inst.stop
        elif oper == "start":
            return model_inst.start
        elif oper == "delete":
            return model_inst.delete
        else:
            raise PhException("Invalid operator")

    def argv2map(argv):
        for arg in argv:
            arr = arg.split('=', 1)

            if len(arr) == 1:
                yield arr[0], ''
            else:
                yield arr[0], arr[1]

    argv = dict(argv2map(argv))

    inst = get_oper_inst(get_model_inst(model), operator)

    if 'h' in argv.keys() or 'help' in argv.keys():
        click.secho(inst.__doc__, fg='green', blink=True, bold=True)
        sys.exit(2)

    click.secho(inst(argv), fg='green', blink=True, bold=True)

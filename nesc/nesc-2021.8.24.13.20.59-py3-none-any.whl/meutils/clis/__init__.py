#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : __init__.py
# @Time         : 2021/1/31 10:20 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : python meutils/clis/__init__.py


import typer

from meutils.pipe import *
from meutils.zk_utils import get_zk_config, register_ip as _register_ip
from meutils.notice.feishu import send_feishu

cli = typer.Typer(name="MeUtils CLI")


@cli.command()
def hello(name: str):
    typer.echo(f"Hello {name}")


@cli.command()
def zk2file(zk_path, mode='yaml', filename=None):
    """本地可再同步到hdfs

     mecli zk2file /mipush/zk2yaml/train.yaml --mode yaml --filename new.yaml

    :param zk_path:
    :param mode:
    :param filename: 不为空可覆盖
    :return:
    """
    zk_conf = get_zk_config(zk_path, mode=mode)

    if filename is None:
        filename = zk_path.split('/')[-1]

    with open(filename, 'w') as f:
        if mode == 'yaml':
            yaml.dump(zk_conf, f)
        else:
            f.write(zk_conf)


@cli.command()
def push_docker(ContainerID, ImageName='app:latest', author='yuanjie', message='update'):
    """自定义镜像"""
    url = 'eijnauy/ten.imoaix.d.rc'[::-1]
    cmd = f"docker commit  -a {author} -m {message} {ContainerID} {url}/{ImageName} && docker push {url}/{ImageName}"
    magic_cmd(cmd)


@cli.command()
def hdfs_success_date(
        cmd="/home/work/tools/infra-client/bin/hdfs dfs -ls /user/s_feeds/dev/user_growth/push/dnn/mitv/impression/*/_SUCCESS"
):
    """
    ~/liuke3/anaconda3/bin/mecli hdfs-success-date --cmd 'hdfs dfs -ls /user/h_data_platform/platform/push/mipush/data/mitvpush/v1'
    """
    l = magic_cmd(cmd)[1].split()

    r = []
    for s in l:
        if 'date' in s:
            _ = s.split('date=')[1].split('/')[0][:8]
            if _ not in r:
                r.append(_)
    print(r | xjoin(','))


@cli.command()
def spark_submit(dates='20201228,20201229,20201230'):
    dates = dates.split(',')
    for start_day in dates:
        start_day = pd.to_datetime(start_day).date().__str__()
        cmd = f"sh /home/work/yuanjie/zk2file/spark_submit.sh {start_day}"
        magic_cmd(cmd, print_output=True)


@cli.command()
def loop_cmd(cmd, args: str, sep=','):
    """"mecli loop-cmd 'ls {arg}' ".,.."""

    for arg in tqdm(args.split(sep)):
        magic_cmd(cmd.format(arg=arg), print_output=True)


@cli.command()
def register_ip(path, sleep_time: int = -1):
    """"mecli register-ip /mipush/ann/ips --sleep-time 10"""
    _register_ip(path, sleep_time)


@cli.command()
def notice(title, text='', hook_url='logger'):
    """"sh管道传参 echo args | xargs -I {} mecli notice {}"""
    send_feishu(title, text, hook_url)
    return 'ok'


# while True:
#     schedule.run_pending()

if __name__ == '__main__':
    cli()

import click
from yucebio_wdladaptor.backend import SUPPORTTED_BACKENDS, create_adaptor, PLACEHOLDER_SIMG_PATH, PLACEHOLDER_GLOBAL_PATH, BaseAdaptor


@click.group()
def cli():
    pass


@cli.command()
@click.option("--input", "-i", required=False, help="input json file include project information")
@click.option("--platform", "-p", required=True, type=click.Choice(list(SUPPORTTED_BACKENDS)), help="platform")
@click.option("--submit", "-s", is_flag=True, default=False, help="auto submit to cromwell server")
@click.option('--runtimes', '-r', help=f"配置需要自动添加到task.runtime中的属性", type=str)
@click.argument("wdl")
def convert(**kw):
    """根据不同平台具有的基础设施转换通用WDL，并自动适配json和task
    """
    adaptor = create_adaptor(kw['platform'])
    adaptor.parse(wdl_path=kw['wdl'], input_path=kw['input'], runtimes=kw["runtimes"])

    adaptor.convert()

    if not kw['submit']:
        adaptor.generate_file()
    else:
        jobid = adaptor.submit()
        click.secho(f"submit success: {jobid}", fg="green")



@cli.command()
@click.option("--platform", "-p", type=click.Choice(list(SUPPORTTED_BACKENDS)), help="platform")
@click.option('--host', '-h', help="cromwell server 地址")
@click.option('--global_path', '-g', help=f"公共文件路径，用于自动替换json中的[{PLACEHOLDER_GLOBAL_PATH}]", type=str)
@click.option('--simg_path', '-s', help=f"singulartiy镜像路径，用于自动替换json中的[{PLACEHOLDER_SIMG_PATH}]", type=str)
@click.option('--runtimes', '-r', help=f"配置当前服务支持的自定义RUNTIME属性，多个属性之间使用逗号分隔", type=str)
def config(**kw):
    """查看或更新计算平台配置"""
    platform = kw['platform']
    adaptor = create_adaptor(platform)
    
    if kw['runtimes']:
        kw['runtimes'] = kw['runtimes'].split(',')
    cfg = {k: kw[k] for k in kw if k != 'platform' and kw[k]}
    if cfg:
        adaptor.config(platform, cfg)
    
    cfg2 = adaptor.config()
    adaptor.pp({k : v for k,v in cfg2.items() if k in SUPPORTTED_BACKENDS})


@cli.command()
def version():
    """显示版本信息
    """
    from yucebio_wdladaptor.version import __version__
    print("Version: ", __version__)


@cli.command()
@click.option("--access_id", "-i", help="阿里云ACCESS KEY ID")
@click.option('--access_secrect', '-s', help="阿里云ACCESS KEY SECRECT")
def update_bcs_instance(access_id, access_secrect):
    """更新阿里云可用类型
    """
    import batchcompute, datetime
    bNeedUpdateAccess = True
    adaptor = BaseAdaptor()
    if not (access_id and access_secrect):
        # 从配置文件中获取
        cfg = adaptor.config("bcs_access", {})
        if not cfg:
            click.secho("请提供ACCESS_KEY_ID和ACCESS_KEY_SECRECT", fg='yellow')
            return
        access_id, access_secrect = cfg.get("access_id", ""), cfg.get("access_secrect", "")
        bNeedUpdateAccess = True

    if not (access_id and access_id):
        return

    try:
        client = batchcompute.Client(batchcompute.CN_SHENZHEN, access_id, access_secrect)
        response = client.get_available_resource()
    except Exception as e:
        click.secho(f"Error: {e.code} 请检查ACCESS_KEY_ID[{repr(access_id)}]和ACCESS_KEY_SECRECT[{repr(access_secrect)}]是否正确", fg='red')
        return

    if bNeedUpdateAccess:
        adaptor.config("bcs_access", {"access_id": access_id, "access_secrect": access_secrect}, quiet=True)
    data = response.content
    data['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d")
    adaptor.config("available_bcs_rescource", data)


if __name__ == "__main__":
    cli()
